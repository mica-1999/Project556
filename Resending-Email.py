import os
import base64
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these SCOPES, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def authenticate_gmail():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('credentials/token.json'):
        os.remove('credentials/token.json')  # Delete the existing token to force re-authentication
    if os.path.exists('credentials/token.json'):
        creds = Credentials.from_authorized_user_file('credentials/token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials/credentials-gmail.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('credentials/token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def send_eml_files(service, directory, recipient_email):
    """Send .eml files as separate emails."""
    for filename in os.listdir(directory):
        if filename.endswith('.eml'):
            filepath = os.path.join(directory, filename)
            with open(filepath, 'r') as eml_file:
                eml_data = eml_file.read()
                msg = email.message_from_string(eml_data)
                subject = msg['subject']
                body = ''
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == 'text/plain' and part.get_payload(decode=True):
                            try:
                                body = part.get_payload(decode=True).decode('utf-8')
                            except UnicodeDecodeError:
                                body = part.get_payload(decode=True).decode('latin1')
                            break
                else:
                    try:
                        body = msg.get_payload(decode=True).decode('utf-8')
                    except UnicodeDecodeError:
                        body = msg.get_payload(decode=True).decode('latin1')
                
                # Create a new email message
                message = MIMEMultipart()
                message['to'] = recipient_email
                message['subject'] = subject
                message.attach(MIMEText(body, 'plain'))
                
                # Attach the .eml file
                with open(filepath, 'rb') as attachment:
                    part = MIMEApplication(attachment.read(), Name=filename)
                    part['Content-Disposition'] = f'attachment; filename="{filename}"'
                    message.attach(part)
                
                # Encode the message
                raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
                message_body = {'raw': raw_message}
                
                # Send the email
                service.users().messages().send(userId='me', body=message_body).execute()
                print(f'Sent: {filename}')

if __name__ == '__main__':
    # Authenticate the Gmail account
    creds = authenticate_gmail()
    # Build the Gmail API service
    service = build('gmail', 'v1', credentials=creds)
    # Directory containing .eml files
    eml_directory = 'email-messages'
    # Recipient email address (your Gmail account)
    recipient_email = '123dontmindme123@gmail.com'  # Update this line with the correct email address
    # Send .eml files as separate emails
    send_eml_files(service, eml_directory, recipient_email)
    print("All emails have been sent.")
