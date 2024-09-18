import asyncio
import csv
import meraki.aio
from colorama import Fore, Style, init
from prettytable import PrettyTable

# Initialize colorama
init(autoreset=True)

# Set your API key here
API_KEY = ''

# Define the hub IDs and other VPN configuration details. Put the Hubs in order of priority top down
HUBS = [
    {"hubId": "", "useDefaultRoute": False},
    # Add other hubs here

    #{"hubId": "hub id here", "useDefaultRoute": False or True}
    #{"hubId": "hub id here", "useDefaultRoute": False}
]

# Function to read network IDs and subnets from a CSV file
def read_networks_and_subnets_from_csv(file_path):
    networks = []
    with open(file_path, mode='r') as file:
        csv_reader = csv.reader(file)
        for _ in range(2):  # Skip the first two rows (headers)
            next(csv_reader)
        current_network = None
        for row in csv_reader:
            if row[1]:  # If Network ID is present
                if current_network:
                    networks.append(current_network)
                current_network = {
                    "network_name": row[0],
                    "network_id": row[1].strip(),  # Strip any extra spaces
                    "subnets": []
                }
                if row[2]:  # If Subnet is present
                    current_network["subnets"].append({"localSubnet": row[2].strip(), "useVpn": True})
            elif current_network and row[2]:  # If Subnet is present for the current network
                current_network["subnets"].append({"localSubnet": row[2].strip(), "useVpn": True})
        if current_network:
            networks.append(current_network)
    return networks

# Function to fetch network name using hub ID
async def get_network_name(aiomeraki, hub_id):
    try:
        network = await aiomeraki.networks.getNetwork(hub_id)
        return network['name']
    except meraki.AsyncAPIError as e:
        print(Fore.RED + f"Error fetching network name for hub ID {hub_id}: {e}")
        return hub_id  # Fallback to hub ID if name cannot be fetched

# Function to create a pretty table from JSON data
async def create_pretty_table(aiomeraki, network_name, data):
    table = PrettyTable()
    table.field_names = ["Field", "Value", "Use Default Route", "Use VPN"]
    
    # Add hubs to the table
    for hub in data.get("hubs", []):
        hub_name = await get_network_name(aiomeraki, hub["hubId"])
        table.add_row(["Hub ID", f"{hub_name} ({hub['hubId']})", hub["useDefaultRoute"], ""])
    
    # Add subnets to the table
    for subnet in data.get("subnets", []):
        table.add_row(["Subnet", subnet["localSubnet"], "", subnet["useVpn"]])
    
    return table

# Function to update VPN configuration for a network
async def update_vpn_configuration(aiomeraki, network):
    try:
        vpn_config = {
            "mode": "spoke",
            "hubs": HUBS
        }
        if network["subnets"]:
            vpn_config["subnets"] = network["subnets"]

        print(Fore.YELLOW + f"Updating network {network['network_name']} with ID {network['network_id']}...")  # Debugging output

        response = await aiomeraki.appliance.updateNetworkApplianceVpnSiteToSiteVpn(
            network["network_id"],
            **vpn_config
        )
        table = await create_pretty_table(aiomeraki, network["network_name"], response)
        print(Fore.GREEN + "Success:" + Style.RESET_ALL + " Updated VPN configuration for network " + "\033[94m" + f"{network['network_name']}:")
        print(Fore.MAGENTA + f"{table}")
    except meraki.AsyncAPIError as e:
        print(Fore.RED + f"Error updating network {network['network_name']} with ID {network['network_id']}: {e}")

# Main function to orchestrate the updates
async def main():
    # Initialize the Meraki client
    async with meraki.aio.AsyncDashboardAPI(API_KEY, output_log=False) as aiomeraki:
        # Read network IDs and subnets from the CSV file
        networks = read_networks_and_subnets_from_csv('vpnupdate.csv')
        
        # Create a list of tasks to update VPN configurations concurrently
        tasks = [update_vpn_configuration(aiomeraki, network) for network in networks]
        
        # Run the tasks concurrently
        await asyncio.gather(*tasks)

# Run the main function
if __name__ == '__main__':
    asyncio.run(main())
