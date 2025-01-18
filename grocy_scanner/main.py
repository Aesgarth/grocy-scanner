from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests

app = FastAPI()

# Configuration model
class Config(BaseModel):
    grocy_api_key: str

# In-memory storage for configuration
config = Config(grocy_api_key="")

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/config")
def set_config(new_config: Config):
    global config
    config = new_config
    return {"message": "Configuration updated successfully"}

@app.get("/scan/{barcode}")
def scan_barcode(barcode: str):
    if not config.grocy_api_key:
        raise HTTPException(status_code=400, detail="Grocy API key not set")
    # Mock request to Grocy or OpenFoodFacts
    response = requests.get(f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json")
    if response.status_code == 200:
        product = response.json()
        return {"barcode": barcode, "product": product}
    raise HTTPException(status_code=404, detail="Product not found")
