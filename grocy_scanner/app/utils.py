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
    Check if a product exists in Grocy by its barcode and process data for the frontend.
    """
    try:
        headers = {"GROCY-API-KEY": api_key}
        url = f"{grocy_url}/api/stock/products/by-barcode/{barcode}"
        response = requests.get(url, headers=headers)

        logging.info(f"Checking barcode {barcode} at {url}")
        logging.info(f"Response Status Code: {response.status_code}")
        logging.info(f"Response Body: {response.text}")

        if response.status_code == 200:
            data = response.json()
            product = data.get("product", {})
            stock_amount = data.get("stock_amount", 0)
            location = data.get("location", {}).get("name", "Unknown location")

            return True, {
                "product_name": product.get("name", "Unnamed Product"),
                "stock_amount": stock_amount,
                "unit": product.get("quantity_unit_stock", {}).get("name", "units"),
                "location": location,
            }

        elif response.status_code == 404:
            return False, "Product not found in Grocy."
        else:
            return False, f"Grocy API error: {response.status_code}"

    except Exception as e:
        logging.error(f"Unexpected error while checking barcode: {str(e)}")
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
        
def purchase_product_in_grocy(barcode, grocy_url, api_key, quantity):
    """
    Purchase a product in Grocy.
    """
    try:
        headers = {"GROCY-API-KEY": api_key}
        url = f"{grocy_url}/api/stock/products/by-barcode/{barcode}/add"
        response = requests.post(url, headers=headers, json={"amount": quantity})

        if response.status_code == 200:
            return True, f"Purchased {quantity} units of product with barcode {barcode}."
        else:
            return False, f"Grocy API error: {response.status_code}"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"


def consume_product_in_grocy(barcode, grocy_url, api_key, quantity):
    """
    Consume a product in Grocy.
    """
    try:
        headers = {"GROCY-API-KEY": api_key}
        url = f"{grocy_url}/api/stock/products/by-barcode/{barcode}/consume"
        response = requests.post(url, headers=headers, json={"amount": quantity})

        if response.status_code == 200:
            return True, f"Consumed {quantity} units of product with barcode {barcode}."
        else:
            return False, f"Grocy API error: {response.status_code}"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"


def open_product_in_grocy(barcode, grocy_url, api_key):
    """
    Mark a product as opened in Grocy.
    """
    try:
        headers = {"GROCY-API-KEY": api_key}
        url = f"{grocy_url}/api/stock/products/by-barcode/{barcode}/open"
        response = requests.post(url, headers=headers, json={"amount": 1})

        if response.status_code == 200:
            return True, f"Marked product with barcode {barcode} as opened."
        else:
            return False, f"Grocy API error: {response.status_code}"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"
