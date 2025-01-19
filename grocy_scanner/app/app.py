from flask import Flask, send_from_directory, jsonify, request
from utils import get_grocy_addon_info, get_addon_ip_and_port, test_grocy_connection
import os
import logging
import json

app = Flask(__name__)

# Define the path to your web directory
WEB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
logger.info(f"Environment Variables: {os.environ}")
SUPERVISOR_TOKEN = os.getenv("SUPERVISOR_TOKEN")
logger.info(f"SUPERVISOR_TOKEN available: {bool(SUPERVISOR_TOKEN)}")

# Path to the options.json file
OPTIONS_PATH = "/data/options.json"

# Read the API key
try:
    with open(OPTIONS_PATH, 'r') as options_file:
        options = json.load(options_file)
        API_KEY = options.get("grocy_api_key")  # Match the correct key name
        logger.info(f"API_KEY loaded: {'Yes' if API_KEY else 'No'}")
except FileNotFoundError:
    logger.error(f"{OPTIONS_PATH} not found.")
    API_KEY = None
except json.JSONDecodeError as e:
    logger.error(f"Error parsing {OPTIONS_PATH}: {e}")
    API_KEY = None

HEADERS = {"Authorization": f"Bearer {SUPERVISOR_TOKEN}"}  # Updated header for Supervisor API

# Use supervisor API to locate the grocy URL on the internal network
logger.info("Initializing Grocy Item Scanner addon...")
try:
    grocy_slug = get_grocy_addon_info(headers=HEADERS)
    grocy_ip, grocy_port = get_addon_ip_and_port(grocy_slug, headers=HEADERS)
    grocy_url = f"http://{grocy_ip}:{grocy_port}"  # Base URL for Grocy
    system_info_url = f"{grocy_url}/api/system/info"

    success, message = test_grocy_connection(API_KEY, system_info_url)
    if success:
        logger.info(f"Successfully connected to Grocy at {grocy_url}. API is accessible.")
    else:
        logger.error(f"Failed to connect to Grocy at {grocy_url}. Error: {message}")
except Exception as e:
    logger.error(f"Error during addon initialization: {str(e)}")
    grocy_url = None  # Ensure this variable exists even on failure


@app.route("/")
def index():
    """
    Serve the main index.html page.
    """
    return send_from_directory(WEB_DIR, "index.html")


@app.route("/<path:filename>")
def serve_static(filename):
    """
    Serve static files (CSS, JS, audio, etc.) from the web directory.
    """
    return send_from_directory(WEB_DIR, filename)


@app.route("/api/check-barcode", methods=["POST"])
def check_barcode():
    """
    Endpoint to handle barcode scanning and check against Grocy using the stock "by-barcode" API.
    """
    if not grocy_url:
        return jsonify({"status": "error", "message": "Grocy URL is not resolved. Please check the configuration."}), 500

    data = request.json
    barcode = data.get("barcode")

    if not barcode:
        return jsonify({"status": "error", "message": "No barcode provided"}), 400

    success, result = check_barcode_in_grocy(barcode, grocy_url, API_KEY)

    if success:
        return jsonify({"status": "success", "product": result})
    elif "not found" in result.lower():
        return jsonify({"status": "not_found", "message": result})
    else:
        return jsonify({"status": "error", "message": result}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3456)
