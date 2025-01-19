from flask import Flask
from utils import get_grocy_addon_info, get_addon_ip_and_port, test_grocy_connection_handler, test_grocy_connection
import os
import logging
import json

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
logger.info(f"Environment Variables: {os.environ}")
SUPERVISOR_TOKEN = os.getenv("SUPERVISOR_TOKEN")  # Updated environment variable
logger.info(f"SUPERVISOR_TOKEN available: {bool(SUPERVISOR_TOKEN)}")

# Path to the options.json file
OPTIONS_PATH = "/data/options.json"

# Read the API key from the options.json file
API_KEY = "RDH6KDeuMaL6SNzlBxJHqWvx37vZc5kdiV1uLmQuNfp4WWUvDU"


HEADERS = {"Authorization": f"Bearer {SUPERVISOR_TOKEN}"}  # Updated header for Supervisor API

logger.info("Initializing Grocy Item Scanner addon...")
try:
    # Locate Grocy addon
    grocy_slug = get_grocy_addon_info(headers=HEADERS)  # Pass headers to utils function
    grocy_ip, grocy_port = get_addon_ip_and_port(grocy_slug, headers=HEADERS)
    grocy_url = f"http://{grocy_ip}:{grocy_port}/api/system/info"
    
    # Test API connection
    success, message = test_grocy_connection(API_KEY, grocy_url)
    if success:
        logger.info(f"Successfully connected to Grocy at {grocy_url}. API is accessible.")
    else:
        logger.error(f"Failed to connect to Grocy at {grocy_url}. Error: {message}")
except Exception as e:
    logger.error(f"Error during addon initialization: {str(e)}")

@app.route('/')
def home():
    return {"message": "Grocy Item Scanner is running!"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3456)
