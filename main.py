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
    # Call the Gmail API to list messages in the inbox
    results = service.users().messages().list(userId='me', labelIds=['INBOX']).execute()
    messages = results.get('messages', [])

    with open("reademails.txt", "w", encoding="utf-8") as f:
        if not messages:
            print('No messages found.')
        else:
            print('Messages:')
            for message in messages:
                # Fetch each message by ID
                msg = service.users().messages().get(userId='me', id=message['id']).execute()
                subject = ''
                body = ''
                # Extract the subject from the email headers
                for header in msg['payload']['headers']:
                    if header['name'] == 'Subject':
                        subject = header['value']
                # Extract the body from the email payload
                if 'data' in msg['payload']['body']:
                    body = base64.urlsafe_b64decode(msg['payload']['body']['data']).decode('utf-8')
                else:
                    for part in msg['payload']['parts']:
                        if part['mimeType'] == 'text/plain':
                            body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                
                # Extract relevant parts of the email body
                relevant_body = extract_relevant_body(body)
                
                # Write the subject and relevant body to the file
                f.write(f"{relevant_body}")
                f.write("\n" + "="*50 + "\n\n")

def extract_relevant_body(body):
    # Split the body into lines
    lines = body.split('\n')
    relevant_lines = []
    
    for line in lines:
        if "Técnicos:" in line:
            break
        if any(keyword in line for keyword in ["Aberto", "Estado", "Prioridade", "Problema"]):
            if relevant_lines and relevant_lines[-1] != "":
                relevant_lines.append("")
        relevant_lines.append(line.strip())
    
    # Remove any leading or trailing empty lines
    while relevant_lines and relevant_lines[0] == "":
        relevant_lines.pop(0)
    while relevant_lines and relevant_lines[-1] == "":
        relevant_lines.pop()
    
    # Join the relevant lines back into a single string
    return '\n'.join(relevant_lines)

if __name__ == '__main__':
    # Authenticate the Gmail account
    creds = authenticate_gmail()
    # Build the Gmail API service
    service = build('gmail', 'v1', credentials=creds)
    # Read emails and save them to reademails.txt
    read_emails(service)