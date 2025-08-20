import os
import csv
import meraki

# Your Meraki API key
api_key = 'KEY'

# Create dashboard object
dash = meraki.DashboardAPI(api_key, suppress_logging=True)

# Define CSV file name
csv_file = 'Meraki_AP_export.csv'

# Write header if file doesn't exist
if not os.path.exists(csv_file):
    with open(csv_file, 'w', newline='') as file:
        writer = csv.writer(file)
        header = [
            'Network Name',
            'Device Name',
            'BSSID',
            'SSID Name',
            'Band',
            'Device Notes',
            'Device Tags',
            'CDP Device ID',
            'CDP Port ID'
        ]
        writer.writerow(header)

# Loop through orgs
for org in dash.organizations.getOrganizations():
    print(f"Processing organization: {org['id']}...")
    # Loop through networks
    for net in dash.organizations.getOrganizationNetworks(org['id']):
        print(f"  Processing network: {net['id']} ({net['name']})...")
        # Loop through devices
        for device in dash.networks.getNetworkDevices(net['id']):
            # Check if device is an AP
            if 'MR' in device.get('model', '') or 'CW' in device.get('model', ''):
                # Get device details (for notes and tags)
                device_details = dash.devices.getDevice(device['serial'])
                notes = device_details.get('notes', 'None').replace('\n', ' ').replace('\r', ' ')
                tags = device_details.get('tags', [])
                tag_str = ', '.join(tags) if tags else 'None'

                print(f"    Processing AP device: {device['serial']} | Tags: {tag_str}")

                # Get BSSID list
                status = dash.wireless.getDeviceWirelessStatus(device['serial'])

                # Get LLDP/CDP info
                lldp_info = dash.devices.getDeviceLldpCdp(device['serial'])
                ports = lldp_info.get('ports', {})

                # CDP info from wired0
                wired0_cdp = ports.get('wired0', {}).get('cdp', {})
                cdp_device_id = wired0_cdp.get('deviceId', 'None')
                cdp_port_id = wired0_cdp.get('portId', 'None')

                # Loop through all BSSID sets
                for bssid_set in status.get('basicServiceSets', []):
                    if bssid_set.get('enabled'):
                        print(f"      Processing BSSID: {bssid_set['bssid']}...")
                        row = [
                            net.get('name', 'None'),
                            device.get('name', 'None'),
                            bssid_set.get('bssid', 'None'),
                            bssid_set.get('ssidName', 'None'),
                            bssid_set.get('band', 'None'),
                            notes,
                            tag_str,
                            cdp_device_id,
                            cdp_port_id
                        ]
                        with open(csv_file, 'a', newline='') as file:
                            writer = csv.writer(file)
                            writer.writerow(row)

print("Processing completed.")
