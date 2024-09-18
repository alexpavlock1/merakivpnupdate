Prerequisites:

This has been tested and used on mac OS 14.6.1 and python version 3.12.3

You will need to be an organization admin with either full write permissions or write permissions to the networks you are trying to update with this script.

This script uses a few different python modules. If you are running on a mac use these commands to install the necessary modules before running the script:

pip3 install asyncio  meraki colorama prettytable


Use case:
This script can be used to update Meraki MX Auto VPN configurations. You can configure if an MX will be in hub or spoke mode, if in spoke mode you can configure which hubs and in what priority the spoke will connect to, if we are going to use the auto vpn default route option per hub, and which subnets will be included in auto vpn sdwan.

Usage:

Line 11 you can input your API Key. The script currently has the key hard coded in for simplicity however for security purposes it is advised to pull in your API key from a file.

Line 15 is where you will add the Hubs that will be configured for your spokes. The hub ID will be the same as the network ID for that hub. The first hub listed in the script will be priority 1 in dashboard, 2nd hub in the script will be #2 priority in dashboard so on and so forth. If you wish to use the auto vpn default route feature change the useDefaultRoute to True for the hubs you wish to enable this feature.

Line 76 is where you will configure if you are setting the networks to hubs or spokes. If you are configuring as hub then the list in line 15 should be blank

The script will pull in a CSV file and loop through the networks included. We will start processing starting on row 3 of the CSV to allow a header and titles within the CSV. Line 99 has the name of the CSV it is pulling in. By default the script is set to use filename vpnupdate.csv. Under the subnets column only include the subnets that you wish to “enable” in VPN. Make sure your CSV file is in the same directory where this script is stored. Attached is a sample CSV of what it should look like. You can also use another script within my depository called apavlock/Merakicsvvpnsubnets. This script creates you a CSV of all the networks within your organization that have an MX and the networks being advertised or enabled to vpn and then you can edit this csv to include the networks you want and subnets to include within vpn.

The script uses asyncio to protect against rate limiting and other errors. It will also provide you a success or failure message per network. In the success message it will print you a table with the configurations that were pushed.


![image](https://github.com/user-attachments/assets/e18edad4-e808-4ff8-98d2-f4ba845f890e)
