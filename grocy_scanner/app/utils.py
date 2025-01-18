import os
import requests
import json
from flask import jsonify, request

SUPERVISOR_API = "http://supervisor"
SUPERVISOR_TOKEN = os.getenv("SUPERVISOR_TOKEN")  # Updated token variable
HEADERS = {"Authorization": f"Bearer {SUPERVISOR_TOKEN}"}  # Updated header


def fetch_addons(headers):
    """
    Fetch all addons using the Supervisor API.
    """
    response = requests.get(f"{SUPERVISOR_API}/addons", headers=headers)
    response.raise_for_status()
    return response.json()


def get_grocy_addon_info(headers):
    """
    Locate the Grocy addon and fetch detailed information.
    """
    addons_data = fetch_addons(headers)
    for addon in addons_data.get('data', {}).get('addons', []):
        if "grocy" in addon.get('slug', '') and addon['slug'] != "grocy_scanner":
            return addon['slug']
    raise ValueError("Grocy addon not found")


def get_addon_ip_and_port(addon_slug, headers):
    """
    Fetch the IP address and port for the specified addon.
    """
    response = requests.get(f"{SUPERVISOR_API}/addons/{addon_slug}/info", headers=headers)
    response.raise_for_status()
    addon_info = response.json()
    grocy_ip = addon_info.get('data', {}).get('ip_address')
    grocy_port = 80  # Default HTTP port
    if not grocy_ip:
        raise ValueError("Grocy addon IP address not found")
    return grocy_ip, grocy_port



def test_grocy_connection_handler():
    """
    Handle the Grocy connection testing process via an API endpoint.
    """
    try:
        data = request.json
        api_key = data.get("apiKey")

        if not api_key:
            return jsonify({"status": "error", "message": "API key is required"}), 400

        # Resolve the Grocy addon
        grocy_slug = get_grocy_addon_info()
        grocy_ip, grocy_port = get_addon_ip_and_port(grocy_slug)

        # Test the connection
        internal_grocy_url = f"http://{grocy_ip}:{grocy_port}/api/system/info"
        response = requests.get(internal_grocy_url, headers={"GROCY-API-KEY": api_key})

        if response.status_code == 200:
            # Save the resolved URL
            with open('/data/options.json', 'r') as options_file:
                options = json.load(options_file)

            options['resolved_grocy_url'] = internal_grocy_url

            with open('/data/options.json', 'w') as options_file:
                json.dump(options, options_file)

            return jsonify({
                "status": "success",
                "message": "Connected to Grocy via internal network!",
                "resolved_url": internal_grocy_url
            })
        elif response.status_code == 401:
            return jsonify({"status": "error", "message": "Unauthorized. Check your API key."}), 401
        else:
            return jsonify({"status": "error", "message": f"Failed with status {response.status_code}"}), response.status_code

    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 404
    except requests.RequestException as e:
        return jsonify({"status": "error", "message": f"Error querying Supervisor API: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": f"Unexpected error: {str(e)}"}), 500


def test_grocy_connection(api_key, grocy_url):
    """
    Test connection to the Grocy API using the provided API key.
    """
    try:
        headers = {"GROCY-API-KEY": api_key}
        response = requests.get(grocy_url, headers=headers)
        if response.status_code == 200:
            return True, "Connection successful"
        elif response.status_code == 401:
            return False, "Unauthorized. Check your API key."
        else:
            return False, f"Unexpected status code: {response.status_code}"
    except requests.RequestException as e:
        return False, str(e)
