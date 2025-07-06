import configparser
import msal
import os
import requests
from flask import Blueprint, request, jsonify, redirect, session, make_response
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    set_refresh_cookies,
    unset_jwt_cookies
)


import db_module
from log_module import setup_logger


# Setup logger
LOGGER = setup_logger("auth", "logs/service")

auth_bp = Blueprint('auth_bp', __name__)

def get_config():
    """Reads configuration from myConfig.ini."""
    config = configparser.ConfigParser()
    # Assuming myConfig.ini is in the same directory or a known path
    config.read("myConfig.ini", encoding="utf-8")
    return config

# --- Google OAuth ---
def get_google_flow():
    """Initializes and returns a Google OAuth Flow instance."""
    config = get_config()
    client_secrets_file = config['GOOGLE']['client_secret_file']
    scopes = config['GOOGLE']['scopes'].split()
    redirect_uri = config['GOOGLE']['redirect_uri']

    # The google_state is used to prevent CSRF attacks.
    # It's stored in the session to be verified in the callback.
    flow = Flow.from_client_secrets_file(
        client_secrets_file,
        scopes=scopes,
        redirect_uri=redirect_uri
    )
    return flow

@auth_bp.route("/google/login")
def google_login():
    """
    Generates a Google authorization URL and redirects the user.
    """
    flow = get_google_flow()
    authorization_url, google_state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    session['google_state'] = google_state
    return jsonify({'authorization_url': authorization_url})

@auth_bp.route("/google/callback")
def google_callback():
    """
    Handles Google callback, creates tokens, and sets refresh token in cookie.
    """
    google_state = session.pop('google_state', None)
    flow = get_google_flow()
    
    try:
        flow.fetch_token(authorization_response=request.url, state=google_state)
    except Exception as e:
        LOGGER.error(f"Failed to fetch Google token: {e}")
        return jsonify({"status": "error", "message": "Authentication failed."}), 400

    credentials = flow.credentials
    user_info_service = build('oauth2', 'v2', credentials=credentials)
    user_info = user_info_service.userinfo().get().execute()
    email = user_info.get('email')

    if not email:
        return jsonify({"status": "error", "message": "Email not found in Google profile."}), 400

    session['google_credentials'] = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }

    config = get_config()
    frontend_url = config['WEB']['frontend_url']
    
    # The response will be a script that sends tokens to the parent window
    response_html = f"""
    <script>
      window.opener.postMessage({{
        status: 'success', 
        provider: 'google',
        accessToken: '{credentials.token}',
        userInfo: {{
          email: '{user_info.get("email")}',
          name: '{user_info.get("name")}',
          picture: '{user_info.get("picture")}'
        }}
      }}, '{frontend_url}');
      window.close();
    </script>
    """
    response = make_response(response_html)
    return response

@auth_bp.route("/google/logout", methods=["POST"])
def google_logout():
    """
    Logs out the user from Google by clearing the session.
    """
    session.pop('google_state', None)
    session.clear()

# --- Microsoft (MSAL) OAuth ---
def get_msal_app():
    """Initializes and returns an MSAL ConfidentialClientApplication."""
    config = get_config()
    app = msal.ConfidentialClientApplication(
        config['AZURE']['client_id'],
        authority=config['MSAL']['authority'],
        client_credential=config['AZURE']['client_secret'],
    )
    return app

@auth_bp.route("/microsoft/login")
def microsoft_login():
    """
    Generates a Microsoft authorization URL.
    """
    config = get_config()
    scopes = config['MSAL']['scopes'].split()
    redirect_uri = config['MSAL']['redirect_uri']
    
    app = get_msal_app()
    auth_url = app.get_authorization_request_url(
        scopes,
        redirect_uri=redirect_uri
    )
    return jsonify({'authorization_url': auth_url})

@auth_bp.route("/microsoft/callback")
def microsoft_callback():
    import json
    import base64
    """
    Handles Microsoft callback, creates tokens, and sets refresh token in cookie.
    """
    config = get_config()
    scopes = config['MSAL']['scopes'].split()
    redirect_uri = config['MSAL']['redirect_uri']
    
    app = get_msal_app()
    result = app.acquire_token_by_authorization_code(
        request.args['code'],
        scopes=scopes,
        redirect_uri=redirect_uri
    )

    if "error" in result:
        LOGGER.error(f"MSAL Error: {result.get('error_description')}")
        return jsonify({"status": "error", "message": "Authentication failed."}), 400

    # Get user profile information from Microsoft Graph
    ms_access_token = result['access_token']
    graph_api_url = 'https://graph.microsoft.com/v1.0/me'
    user_info = requests.get(
        graph_api_url,
        headers={'Authorization': 'Bearer ' + ms_access_token}
    ).json()

    email = user_info.get('mail') or user_info.get('userPrincipalName')
    if not email:
        return jsonify({"status": "error", "message": "Email not found in Microsoft profile."}), 400


    # Get user's profile image
    photo_url = 'https://graph.microsoft.com/v1.0/me/photo/$value'
    photo_response = requests.get(
        photo_url,
        headers={'Authorization': 'Bearer ' + ms_access_token}
    )
    photo_data_url = None
    if photo_response.status_code == 200:
        photo_content_b64 = base64.b64encode(photo_response.content).decode('utf-8')
        photo_data_url = f"data:image/jpeg;base64,{photo_content_b64}"

    frontend_url = config['WEB']['frontend_url']

    access_token = result['access_token']
    refresh_token = result.get('refresh_token', None)

    session['microsoft_credentials'] = {
        'access_token': access_token,
        'refresh_token': refresh_token
    }

    response_html = f"""
    <script>
      window.opener.postMessage({{
        status: 'success', 
        provider: 'microsoft',
        accessToken: '{access_token}',
        userInfo: {{
          email: '{email}',
          name: '{user_info.get("displayName")}',
          picture: '{photo_data_url or ''}'
        }}
      }}, '{frontend_url}');
      window.close();
    </script>
    """
    response = make_response(response_html)
    return response

@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    """
    Refreshes the access token using a valid refresh token.
    The refresh token is expected to be in an HttpOnly cookie.
    """
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return jsonify(access_token=access_token)

@auth_bp.route("/logout", methods=["POST"])
def logout():
    """
    Logs out the user by clearing the session and the JWT cookie.
    """
    session.clear()
    response = jsonify({"status": "success", "message": "Logged out successfully."})
    unset_jwt_cookies(response)
    return response

@auth_bp.route("/me")
@jwt_required()
def me():
    """
    Returns the profile of the currently logged-in user.
    The user's identity is retrieved from the JWT.
    """
    current_user_identity = get_jwt_identity()
    
    # In a real application, you would fetch user details from the database
    # using the identity (e.g., user's email or ID).
    # user = db_module.get_user_by_email(current_user_identity)
    # For now, we'll just return the identity from the token.
    
    return jsonify({
        "status": "success",
        "data": {
            "email": current_user_identity
            # Add other user details here after fetching from DB
        }
    })
