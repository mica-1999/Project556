from __future__ import print_function
import os.path
import base64
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these SCOPES, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def authenticate_gmail():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def read_emails(service):
    # Call the Gmail API
    results = service.users().messages().list(userId='me', labelIds=['INBOX']).execute()
    messages = results.get('messages', [])

    with open("reademails.txt", "w", encoding="utf-8") as f:
        if not messages:
            print('No messages found.')
        else:
            print('Messages:')
            for message in messages:
                msg = service.users().messages().get(userId='me', id=message['id']).execute()
                subject = ''
                body = ''
                for header in msg['payload']['headers']:
                    if header['name'] == 'Subject':
                        subject = header['value']
                if 'data' in msg['payload']['body']:
                    body = base64.urlsafe_b64decode(msg['payload']['body']['data']).decode('utf-8')
                else:
                    for part in msg['payload']['parts']:
                        if part['mimeType'] == 'text/plain':
                            body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                f.write(f"Subject: {subject}\n")
                f.write(f"Body: {body}\n")
                f.write("\n" + "="*50 + "\n\n")

if __name__ == '__main__':
    creds = authenticate_gmail()
    service = build('gmail', 'v1', credentials=creds)
    read_emails(service)
