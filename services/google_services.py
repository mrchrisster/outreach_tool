# services/google_services.py

import os
import base64
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from config import SCOPES

def authenticate_google():
    """Authenticate with Google API for Gmail and Sheets."""
    creds = None
    # Load existing credentials from file
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no valid credentials available, log in and save them
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def fetch_sheet_data(sheet_id, range_name):
    """Fetch data from Google Sheets."""
    creds = authenticate_google()
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=sheet_id, range=range_name).execute()
    return result.get('values', [])
    
def update_sheet_with_contact_info(sheet_id, row_number, contact_method, message):
    """Update Google Sheets with contact method and message for a specific row."""
    creds = authenticate_google()
    service = build('sheets', 'v4', credentials=creds)
    
    # Define the range for updating the "Contacted via" (Column H) and message (Column I)
    contact_range = f'Sheet1!H{row_number}:I{row_number}'
    
    # Create the values to update: Contact Method in Column H, Message in Column I
    values = [
        [contact_method, message]
    ]
    
    body = {
        'values': values
    }
    
    # Perform the update
    result = service.spreadsheets().values().update(
        spreadsheetId=sheet_id, range=contact_range,
        valueInputOption='RAW', body=body
    ).execute()
    

def create_draft(subject, body, recipient_email):
    """Create and save a draft email in Gmail."""
    creds = authenticate_google()
    service = build('gmail', 'v1', credentials=creds)

    # Create the email message
    message = MIMEText(body)
    message['to'] = recipient_email
    message['subject'] = subject
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    # Create draft
    draft = {'message': {'raw': raw_message}}
    try:
        draft_response = service.users().drafts().create(userId='me', body=draft).execute()
        print(f"Draft ID: {draft_response['id']} created successfully.")
        return draft_response
    except Exception as error:
        print(f"An error occurred: {error}")
        return None

def send_email(subject, body, recipient_email):
    """Send an email using Gmail API."""
    creds = authenticate_google()
    service = build('gmail', 'v1', credentials=creds)

    # Create the email message
    message = MIMEText(body)
    message['to'] = recipient_email
    message['subject'] = subject
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    # Send the email
    try:
        send_message = {'raw': raw_message}
        message_response = service.users().messages().send(userId='me', body=send_message).execute()
        print(f"Message ID: {message_response['id']} sent successfully.")
        return message_response
    except Exception as error:
        print(f"An error occurred: {error}")
        return None
