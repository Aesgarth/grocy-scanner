import os
import requests
import json
import logging
from flask import jsonify, request

SUPERVISOR_API = "http://supervisor"
SUPERVISOR_TOKEN = os.getenv("SUPERVISOR_TOKEN")  # Supervisor token from environment
HEADERS = {"Authorization": f"Bearer {SUPERVISOR_TOKEN}"}  # Authorization header for Supervisor API

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetch_addons(headers):
    """
    Fetch all addons using the Supervisor API.
    """
    try:
        response = requests.get(f"{SUPERVISOR_API}/addons", headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Error fetching addons: {e}")
        raise

def get_grocy_addon_info(headers):
    """
    Locate the Grocy addon and fetch detailed information.
    """
    addons_data = fetch_addons(headers)
    for addon in addons_data.get("data", {}).get("addons", []):
        if "grocy" in addon.get("slug", "") and addon["slug"] != "grocy_scanner":
            logger.info(f"Found Grocy addon with slug: {addon['slug']}")
            return addon["slug"]
    logger.error("Grocy addon not found")
    raise ValueError("Grocy addon not found")

def get_addon_ip_and_port(addon_slug, headers):
    """
    Fetch the IP address and port for the specified addon.
    """
    try:
        response = requests.get(f"{SUPERVISOR_API}/addons/{addon_slug}/info", headers=headers)
        response.raise_for_status()
        addon_info = response.json()
        grocy_ip = addon_info.get("data", {}).get("ip_address")
        grocy_port = 80  # Default HTTP port
        if not grocy_ip:
            raise ValueError("Grocy addon IP address not found")
        logger.info(f"Grocy IP: {grocy_ip}, Port: {grocy_port}")
        return grocy_ip, grocy_port
    except requests.RequestException as e:
        logger.error(f"Error fetching Grocy addon info: {e}")
        raise

def test_grocy_connection(api_key, grocy_url):
    """
    Test connection to the Grocy API using the provided API key.
    """
    try:
        headers = {"GROCY-API-KEY": api_key}
        response = requests.get(grocy_url, headers=headers)
        if response.status_code == 200:
            logger.info("Grocy connection successful")
            return True, "Connection successful"
        elif response.status_code == 401:
            logger.warning("Unauthorized. Check your API key.")
            return False, "Unauthorized. Check your API key."
        else:
            logger.error(f"Unexpected status code: {response.status_code}")
            return False, f"Unexpected status code: {response.status_code}"
    except requests.RequestException as e:
        logger.error(f"Error connecting to Grocy: {e}")
        return False, str(e)

def check_barcode_in_grocy(barcode, grocy_url, api_key):
    """
    Check if a product exists in Grocy by its barcode.
    """
    try:
        headers = {"GROCY-API-KEY": api_key}
        url = f"{grocy_url}/api/stock/products/by-barcode/{barcode}"
        logger.info(f"Checking barcode {barcode} at {url}")

        response = requests.get(url, headers=headers)
        logger.info(f"Response Status Code: {response.status_code}")

        if response.status_code == 200:
            logger.info(f"Product found for barcode {barcode}")
            return True, response.json()  # Product found
        elif response.status_code == 404:
            logger.warning(f"Product not found for barcode {barcode}")
            return False, "Product not found in Grocy."
        else:
            logger.error(f"Grocy API error: {response.status_code}")
            return False, f"Grocy API error: {response.status_code}"
    except requests.RequestException as e:
        logger.error(f"Error checking barcode in Grocy: {e}")
        return False, f"Unexpected error: {str(e)}"

def test_grocy_connection_handler():
    """
    Handle the Grocy connection testing process via an API endpoint.
    """
    try:
        data = request.json
        api_key = data.get("apiKey")

        if not api_key:
            return jsonify({"status": "error", "message": "API key is required"}), 400

        grocy_slug = get_grocy_addon_info(headers=HEADERS)
        grocy_ip, grocy_port = get_addon_ip_and_port(grocy_slug, headers=HEADERS)
        internal_grocy_url = f"http://{grocy_ip}:{grocy_port}/api/system/info"

        success, message = test_grocy_connection(api_key, internal_grocy_url)
        if success:
            return jsonify({"status": "success", "message": message, "resolved_url": internal_grocy_url})
        else:
            return jsonify({"status": "error", "message": message}), 400
    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 404
    except Exception as e:
        logger.error(f"Unexpected error during connection test: {str(e)}")
        return jsonify({"status": "error", "message": f"Unexpected error: {str(e)}"}), 500
