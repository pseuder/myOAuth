import base64
import configparser
import json
import requests
from flask import session, jsonify, request
from email.mime.text import MIMEText

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from log_module import setup_logger

LOGGER = setup_logger("api", "logs/service")

def get_config():
    """Reads configuration from myConfig.ini."""
    config = configparser.ConfigParser()
    config.read("myConfig.ini", encoding="utf-8")
    return config

# --- Google API Functions ---

def get_google_credentials():
    """Creates Google credentials object from session."""
    credentials = session.get('google_credentials')
    if not credentials:
        return None
    
    return Credentials(
        token=credentials.get('token'),
        refresh_token=credentials.get('refresh_token'),
        token_uri=credentials.get('token_uri'),
        client_id=credentials.get('client_id'),
        client_secret=credentials.get('client_secret'),
        scopes=credentials.get('scopes', [])
    )

def send_google_email(recipient, subject, body):
    """Sends an email using the Gmail API."""
    # Get Google credentials from session
    creds = get_google_credentials()
    try:
        service = build('gmail', 'v1', credentials=creds)
        message = MIMEText(body)
        message['to'] = recipient
        message['subject'] = subject
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        create_message = {'raw': encoded_message}
        send_message = (service.users().messages().send(userId="me", body=create_message).execute())
        LOGGER.info(f"Sent message to {recipient}, Message Id: {send_message['id']}")
        return {"status": "success", "data": send_message}
    except HttpError as error:
        LOGGER.error(f"An error occurred: {error}")
        return {"status": "error", "message": str(error)}

def create_google_event(user, title, start_time, end_time):
    """Creates a calendar event using the Google Calendar API."""
    creds = get_google_credentials(user)
    try:
        service = build('calendar', 'v3', credentials=creds)
        event = {
            'summary': title,
            'start': {'dateTime': start_time, 'timeZone': 'UTC'},
            'end': {'dateTime': end_time, 'timeZone': 'UTC'},
        }
        event = service.events().insert(calendarId='primary', body=event).execute()
        LOGGER.info(f"Event created: {event.get('htmlLink')}")
        return {"status": "success", "data": event}
    except HttpError as error:
        LOGGER.error(f"An error occurred: {error}")
        return {"status": "error", "message": str(error)}

# --- Microsoft Graph API Functions ---

def send_microsoft_email(recipient, subject, body):
    """Sends an email using the Microsoft Graph API."""
    microsoft_credentials = session.get('microsoft_credentials')
    graph_api_url = 'https://graph.microsoft.com/v1.0/me/sendMail'
    headers = {'Authorization': 'Bearer ' + microsoft_credentials['access_token']}
    email_msg = {
        'message': {
            'subject': subject,
            'body': {'contentType': 'Text', 'content': body},
            'toRecipients': [{'emailAddress': {'address': recipient}}]
        },
        'saveToSentItems': 'true'
    }
    response = requests.post(graph_api_url, headers=headers, json=email_msg)
    if response.status_code == 202:
        LOGGER.info(f"Successfully sent email to {recipient}")
        return {"status": "success"}
    else:
        LOGGER.error(f"Error sending email: {response.json()}")
        return {"status": "error", "message": response.json().get('error', {}).get('message', 'Unknown error')}

def create_microsoft_event(user, title, start_time, end_time):
    """Creates a calendar event using the Microsoft Graph API."""
    graph_api_url = 'https://graph.microsoft.com/v1.0/me/events'
    headers = {'Authorization': 'Bearer ' + user['access_token']}
    event = {
        "subject": title,
        "start": {"dateTime": start_time, "timeZone": "UTC"},
        "end": {"dateTime": end_time, "timeZone": "UTC"}
    }
    response = requests.post(graph_api_url, headers=headers, json=event)
    if response.status_code == 201:
        LOGGER.info(f"Successfully created event: {response.json().get('webLink')}")
        return {"status": "success", "data": response.json()}
    else:
        LOGGER.error(f"Error creating event: {response.json()}")
        return {"status": "error", "message": response.json().get('error', {}).get('message', 'Unknown error')}
