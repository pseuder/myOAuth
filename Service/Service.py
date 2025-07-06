import inspect
import os
from functools import wraps
from datetime import timedelta
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity

from log_module import setup_logger
import business_module
import db_module
import api_module
from auth_module import auth_bp

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

app = Flask(__name__)
# In a real app, this should be a long, random, secret string
app.secret_key = os.urandom(24)

# --- JWT Configuration ---
# It's recommended to set a strong secret key in your config file
# and load it here, for example:
# app.config["JWT_SECRET_KEY"] = get_config().get('SECURITY', 'jwt_secret_key', fallback='default-super-secret-key')
app.config["JWT_SECRET_KEY"] = "your-super-secret-key-change-me"  # Change this!
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=15)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=7)
# Tells Flask-JWT-Extended to expect JWTs in the 'cookies' and 'headers'
app.config["JWT_TOKEN_LOCATION"] = ["headers", "cookies"]
app.config["JWT_COOKIE_SECURE"] = False # Set True in production with HTTPS
app.config["JWT_COOKIE_CSRF_PROTECT"] = True # Recommended for security
app.config["JWT_COOKIE_SAMESITE"] = "Lax" # Or "Strict"

jwt = JWTManager(app)
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
@jwt_required()
def create_event():
    data = request.get_json()
    user_identity = get_jwt_identity()
    return jsonify({"status": "info", "message": "Create event endpoint needs DB integration to determine provider."})


if __name__ == "__main__":
    LOGGER = setup_logger("service", "logs/service")
    
    with app.app_context():
        db_module.create_user_table()

    LOGGER.info("Server is running")
    app.run(host="0.0.0.0", port=5000, debug=True)
