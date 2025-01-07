from __future__ import print_function  # Ensures compatibility with Python 2 and 3
import os.path  # Provides functions for interacting with the file system
import base64  # Provides functions for encoding and decoding binary data
import json  # Provides functions for working with JSON data
from google.auth.transport.requests import Request  # Provides a request object for OAuth 2.0
from google.oauth2.credentials import Credentials  # Provides OAuth 2.0 credentials
from google_auth_oauthlib.flow import InstalledAppFlow  # Provides OAuth 2.0 flow for installed apps
from googleapiclient.discovery import build  # Provides functions for building Google API clients

# If modifying these SCOPES, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']  # Defines the scope of access required to read emails

def authenticate_gmail():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None  # Initialize credentials to None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('credentials/token.json'):  # Check if the token.json file exists
        os.remove('credentials/token.json')  # Delete the existing token to force re-authentication
    if os.path.exists('credentials/token.json'):  # Check again if the token.json file exists
        creds = Credentials.from_authorized_user_file('credentials/token.json', SCOPES)  # Load credentials from token.json
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:  # Check if credentials are not available or not valid
        if creds and creds.expired and creds.refresh_token:  # Check if credentials are expired and can be refreshed
            creds.refresh(Request())  # Refresh the credentials
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials/credentials-gmail.json', SCOPES)  # Create an OAuth 2.0 flow object
            creds = flow.run_local_server(port=0)  # Run the local server to complete the OAuth 2.0 flow
        # Save the credentials for the next run
        with open('credentials/token.json', 'w') as token:  # Open the token.json file for writing
            token.write(creds.to_json())  # Write the credentials to token.json
    return creds  # Return the credentials

def read_emails(service):
    # Call the Gmail API to list messages in the inbox
    results = service.users().messages().list(userId='me', labelIds=['INBOX']).execute()  # List messages in the inbox
    messages = results.get('messages', [])  # Get the list of messages

    with open("Output-Emails/reademails.txt", "w", encoding="utf-8") as f:  # Open the output file for writing
        if not messages:  # Check if there are no messages
            print('No messages found.')  # Print a message indicating no messages were found
        else:
            print('Messages:')  # Print a message indicating messages were found
            for message in messages:  # Iterate over each message
                # Fetch each message by ID
                msg = service.users().messages().get(userId='me', id=message['id']).execute()  # Get the message by ID
                subject = ''  # Initialize the subject to an empty string
                body = ''  # Initialize the body to an empty string
                # Extract the subject from the email headers
                for header in msg['payload']['headers']:  # Iterate over the headers
                    if header['name'] == 'Subject':  # Check if the header is the subject
                        subject = header['value']  # Set the subject to the header value
                # Extract the body from the email payload
                if 'data' in msg['payload']['body']:  # Check if the body contains data
                    body = base64.urlsafe_b64decode(msg['payload']['body']['data']).decode('utf-8')  # Decode the body data
                else:
                    for part in msg['payload']['parts']:  # Iterate over the parts of the payload
                        if part['mimeType'] == 'text/plain':  # Check if the part is plain text
                            body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')  # Decode the part data
                
                # Extract relevant parts of the email body
                relevant_body = extract_relevant_body(body)  # Extract relevant parts of the body
                
                # Write the subject and relevant body to the file
                f.write(f"{relevant_body}")  # Write the relevant body to the file
                f.write("\n" + "="*50 + "\n\n")  # Write a separator to the file

def extract_relevant_body(body):
    # Split the body into lines
    lines = body.split('\n')  # Split the body into lines
    relevant_lines = []  # Initialize a list to store relevant lines
    
    for line in lines:  # Iterate over each line
        if "Técnicos:" in line:  # Check if the line contains "Técnicos:"
            break  # Break the loop if the line contains "Técnicos:"
        if any(keyword in line for keyword in ["Aberto", "Estado", "Prioridade", "Problema"]):  # Check if the line contains any relevant keywords
            if relevant_lines and relevant_lines[-1] != "":  # Check if the last line in relevant_lines is not empty
                relevant_lines.append("")  # Add an empty line to relevant_lines
        relevant_lines.append(line.strip())  # Add the stripped line to relevant_lines
    # Remove any leading or trailing empty lines
    while relevant_lines and relevant_lines[0] == "":  # Remove leading empty lines
        relevant_lines.pop(0)  # Remove the first line
    while relevant_lines and relevant_lines[-1] == "":  # Remove trailing empty lines
        relevant_lines.pop()  # Remove the last line
    
    # Join the relevant lines back into a single string
    return '\n'.join(relevant_lines)  # Join the relevant lines into a single string

if __name__ == '__main__':
    # Authenticate the Gmail account
    creds = authenticate_gmail()  # Authenticate the Gmail account
    # Build the Gmail API service
    service = build('gmail', 'v1', credentials=creds)  # Build the Gmail API service
    # Read emails and save them to reademails.txt
    read_emails(service)  # Read emails and save them to reademails.txt