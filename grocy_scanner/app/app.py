from flask import Flask
from utils import get_grocy_addon_info, get_addon_ip_and_port, test_grocy_connection_handler
import os
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
HASSIO_TOKEN = os.getenv("HASSIO_TOKEN")
API_KEY = os.getenv("API_KEY")  # Pass the Grocy API key in the addon configuration

@app.before_first_request
def initialize_addon():
    """
    Initialize the addon: find Grocy address, test API connection, and log results.
    """
    try:
        logger.info("Initializing Grocy Item Scanner addon...")
        
        # Locate Grocy addon
        grocy_slug = get_grocy_addon_info()
        grocy_ip, grocy_port = get_addon_ip_and_port(grocy_slug)
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
