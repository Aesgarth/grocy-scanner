from flask import Flask, jsonify, request
from utils import fetch_addons, get_grocy_addon_info, get_addon_ip_and_port, test_grocy_connection_handler

app = Flask(__name__)

@app.route('/')
def home():
    return {"message": "Grocy Item Scanner is running!"}

@app.route('/api/supervisor', methods=['GET'])
def get_supervisor_info():
    try:
        addons_data = fetch_addons()
        return jsonify(addons_data)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/test-grocy-connection', methods=['POST'])
def test_grocy_connection():
    return test_grocy_connection_handler()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3456)
