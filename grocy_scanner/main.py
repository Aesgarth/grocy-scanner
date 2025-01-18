from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import requests
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info(f"Environment variables: {os.environ}")

# Check if the SUPERVISOR_TOKEN environment variable is available
supervisor_token = os.getenv("SUPERVISOR_TOKEN")
logger.info("SUPERVISOR_TOKEN is available" if supervisor_token else "SUPERVISOR_TOKEN is missing")

# Get the ingress path from the environment variable
ingress_path = os.getenv("INGRESS_PATH", "/")
logger.info(f"Ingress path: {ingress_path}")

# Set the absolute path for the web directory
static_folder_path = os.path.join(os.getcwd(), 'web')

# Initialize FastAPI app with the ingress path
app = FastAPI(root_path=ingress_path)

# Mount the 'web' directory to serve static files
app.mount("/", StaticFiles(directory=static_folder_path), name="static")

# Configuration model
class Config(BaseModel):
    grocy_api_key: str

# In-memory storage for configuration
config = Config(grocy_api_key="")

@app.get("/")
def read_root():
    # Redirect root URL to the frontend
    return RedirectResponse(url="/index.html")

@app.get("/health")
def health_check():
    # Basic health check endpoint
    return {"status": "healthy"}

@app.post("/config")
def set_config(new_config: Config):
    # Update the configuration
    global config
    config = new_config
    return {"message": "Configuration updated successfully"}

@app.get("/scan/{barcode}")
def scan_barcode(barcode: str):
    # Check if Grocy API key is set
    if not config.grocy_api_key:
        raise HTTPException(status_code=400, detail="Grocy API key not set")
    # Example: Fetch product data from OpenFoodFacts
    response = requests.get(f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json")
    if response.status_code == 200:
        product = response.json()
        return {"barcode": barcode, "product": product}
    raise HTTPException(status_code=404, detail="Product not found")
