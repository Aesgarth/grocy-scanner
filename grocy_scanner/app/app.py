from flask import Flask, jsonify, request
import os
import requests

app = Flask(__name__)

SUPERVISOR_API = "http://supervisor"
HASSIO_TOKEN = os.getenv("HASSIO_TOKEN")
HEADERS = {"Authorization": f"Bearer {HASSIO_TOKEN}"}

@app.route('/')
def home():
    return {"message": "Grocy Item Scanner is running!"}

@app.route('/api/supervisor', methods=['GET'])
def get_supervisor_info():
    response = requests.get(f"{SUPERVISOR_API}/addons", headers=HEADERS)
    return jsonify(response.json())

@app.route('/api/scan', methods=['POST'])
def scan_item():
    data = request.json
    # Handle barcode scanning logic here
    return jsonify({"status": "success", "message": "Item scanned!"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3456)
