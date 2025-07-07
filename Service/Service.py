import os
from functools import wraps
from datetime import timedelta
from flask import Flask, request, jsonify, session
from flask_cors import CORS

from log_module import setup_logger
import api_module
from auth_module import auth_bp

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

app = Flask(__name__)
# In a real app, this should be a long, random, secret string
app.secret_key = os.urandom(24)

# --- End JWT Configuration ---

CORS(app, supports_credentials=True)

# Register Blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')

global LOGGER
LOGGER = None

def get_config():
    import configparser
    configs = configparser.ConfigParser()
    configs.read("myConfig.ini", encoding="utf-8")
    return configs

@app.before_request
def log_request_info():
    user_ip = request.remote_addr
    request_path = request.path
    request_method = request.method
    LOGGER.debug(f"Request by {user_ip} - {request_method} {request_path}")

@app.route("/")
def index():
    """check server status"""
    return "server is running"

@app.route("/api/send_google_email", methods=["POST"])
def send_google_email():
    data = request.get_json()
    result = api_module.send_google_email(data['recipient'], data['subject'], data['body'])
    return jsonify(result)

@app.route("/api/send_microsoft_email", methods=["POST"])
def send_microsoft_email():
    data = request.get_json()
    result = api_module.send_microsoft_email(data['recipient'], data['subject'], data['body'])
    return jsonify(result)

@app.route("/api/create-event", methods=["POST"])
def create_event():
    data = request.get_json()
    return jsonify({"status": "info", "message": "Create event endpoint needs DB integration to determine provider."})


if __name__ == "__main__":
    LOGGER = setup_logger("service", "logs/service")
    LOGGER.info("Server is running")
    app.run(host="0.0.0.0", port=5000, debug=True)
