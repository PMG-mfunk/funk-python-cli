import requests
import pandas as pd
from datetime import datetime
import json
import subprocess

organizationId = subprocess.run(['op','item', 'get', 'meraki', '--vault', 'dev-cred', '--fields', 'orgID'], capture_output=True, text=True).stdout.strip()
bearer_token = subprocess.run(['op','item', 'get', 'meraki', '--vault', 'dev-cred', '--fields', 'bearer'], capture_output=True, text=True).stdout.strip()

def get_networks():
    url = f"https://api.meraki.com/api/v1/organizations/{organizationId}/networks"
    headers = {
        'Authorization': f'Bearer {bearer_token}'
    }
    response = requests.request("GET", url, headers=headers)
    
    try:
        response.raise_for_status()  # Check for any HTTP errors
        networks = response.json()  # Try to parse JSON data
        return networks
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred: {err}")
    except json.decoder.JSONDecodeError as err:
        print(f"JSON decoding error occurred: {err}")
        return {}  # Return an empty dictionary in case of JSON decoding error

def get_firewall_rules(network_id):
    url = f"https://api.meraki.com/api/v1/networks/{network_id}/appliance/firewall/l3FirewallRules"
    headers = {
        'Authorization': f'Bearer {bearer_token}'
    }
    response = requests.request("GET", url, headers=headers)
    return response.json()

def main():
    networks = get_networks()
    print("Available Networks:")
    for i, network in enumerate(networks):
        print(f"{i + 1}. {network['name']}")

    choice = int(input("Select a network by number: ")) - 1
    selected_network_id = networks[choice]['id']

    fw_rules = get_firewall_rules(selected_network_id)
    fw_rules_df = pd.DataFrame(fw_rules)
    fw_rules_df = pd.json_normalize(fw_rules, 'rules')
    current_date = datetime.now().strftime("%Y-%m-%d")
    output_folder = "outputs"
    try:
        fw_rules_df.to_csv(f'{output_folder}/fw_rules_{current_date}.csv', index=False)
        print(f"File '{output_folder}/fw_rules_{current_date}.csv' created successfully.")
    except Exception as e:
        print(f"Failed to create 'fw_rules_{current_date}.csv': {e}")

if __name__ == "__main__":
    main()
