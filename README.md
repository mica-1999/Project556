# Project556

## Overview

This project reads emails from a Gmail account and saves them to a file called `reademails.txt`. It uses the Gmail API to access the emails and formats the content for easy reading and processing by AI. Additionally, it includes a script to resend `.eml` files as separate emails to the Gmail account for processing.

## Setup

### Prerequisites

1. **Python**: Ensure you have Python installed on your system.
2. **Google Cloud Project**: Create a project in the [Google Cloud Console](https://console.cloud.google.com/).
3. **Enable Gmail API**: Enable the Gmail API for your project.
4. **OAuth 2.0 Credentials**: Create OAuth 2.0 Client IDs and download the `credentials.json` file.

### Install Required Libraries

Install the required libraries using pip:

```sh
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### Place the `credentials.json` File

Save the `credentials.json` file in the `credentials` directory.

## Running the Scripts

### Resending `.eml` Files

The `Resending-Email.py` script reads `.eml` files from a specified directory and sends each one as a separate email to your Gmail account.

1. **Update the Recipient Email**: Open `Resending-Email.py` and update the `recipient_email` variable with your Gmail address.
2. **Run the Script**: Execute the script to resend the `.eml` files.

```sh
python Resending-Email.py
```

### Reading Emails

The `main.py` script reads emails from your Gmail account and saves them to `reademails.txt`.

1. **Run the Script**: Execute the script to read emails and save them to `reademails.txt`.

```sh
python main.py
```

The first time you run the script, it will open a browser window for you to log in to your Google account and authorize access. This will generate a `token.json` file that stores your access and refresh tokens.

## Code Explanation

### Resending-Email.py

This script reads `.eml` files from a specified directory and sends each one as a separate email to your Gmail account.

#### Import Libraries

```python
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
```

#### Define Scopes

```python
SCOPES = ['https://www.googleapis.com/auth/gmail.send']
```

Defines the scope of access required to send emails.

#### Authenticate Gmail

```python
def authenticate_gmail():
    creds = None
    if os.path.exists('credentials/token.json'):
        os.remove('credentials/token.json')  # Delete the existing token to force re-authentication
    if os.path.exists('credentials/token.json'):
        creds = Credentials.from_authorized_user_file('credentials/token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials/credentials-gmail.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('credentials/token.json', 'w') as token:
            token.write(creds.to_json())
    return creds
```

#### Send `.eml` Files

```python
def send_eml_files(service, directory, recipient_email):
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
                
                message = MIMEMultipart()
                message['to'] = recipient_email
                message['subject'] = subject
                message.attach(MIMEText(body, 'plain'))
                
                with open(filepath, 'rb') as attachment:
                    part = MIMEApplication(attachment.read(), Name=filename)
                    part['Content-Disposition'] = f'attachment; filename="{filename}"'
                    message.attach(part)
                
                raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
                message_body = {'raw': raw_message}
                
                service.users().messages().send(userId='me', body=message_body).execute()
                print(f'Sent: {filename}')
```

#### Main Execution

```python
if __name__ == '__main__':
    creds = authenticate_gmail()
    service = build('gmail', 'v1', credentials=creds)
    eml_directory = 'email-messages'
    recipient_email = 'your-email@gmail.com'  # Update this line with the correct email address
    send_eml_files(service, eml_directory, recipient_email)
    print("All emails have been sent.")
```

### main.py

This script reads emails from your Gmail account and saves them to `reademails.txt`.

#### Import Libraries

```python
from __future__ import print_function
import os.path
import base64
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
```

#### Define Scopes

```python
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
```

Defines the scope of access required to read emails.

#### Authenticate Gmail

```python
def authenticate_gmail():
    creds = None
    if os.path.exists('credentials/token.json'):
        os.remove('credentials/token.json')  # Delete the existing token to force re-authentication
    if os.path.exists('credentials/token.json'):
        creds = Credentials.from_authorized_user_file('credentials/token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials/credentials-gmail.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('credentials/token.json', 'w') as token:
            token.write(creds.to_json())
    return creds
```

#### Read Emails

```python
def read_emails(service):
    results = service.users().messages().list(userId='me', labelIds=['INBOX']).execute()
    messages = results.get('messages', [])

    with open("Output-Emails/reademails.txt", "w", encoding="utf-8") as f:
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
                
                relevant_body = extract_relevant_body(body)
                
                f.write(f"{relevant_body}")
                f.write("\n" + "="*50 + "\n\n")
```

#### Extract Relevant Body

```python
def extract_relevant_body(body):
    lines = body.split('\n')
    relevant_lines = []
    
    for line in lines:
        if "Técnicos:" in line:
            break
        if any(keyword in line for keyword in ["Aberto", "Estado", "Prioridade", "Problema"]):
            if relevant_lines and relevant_lines[-1] != "":
                relevant_lines.append("")
        relevant_lines.append(line.strip())
    
    while relevant_lines and relevant_lines[0] == "":
        relevant_lines.pop(0)
    while relevant_lines and relevant_lines[-1] == "":
        relevant_lines.pop()
    
    return '\n'.join(relevant_lines)
```

#### Main Execution

```python
if __name__ == '__main__':
    creds = authenticate_gmail()
    service = build('gmail', 'v1', credentials=creds)
    read_emails(service)
```

## Conclusion

This project demonstrates how to use the Gmail API to read emails and save them to a file. It includes setting up OAuth 2.0 authentication, calling the Gmail API, and processing email data. Additionally, it includes a script to resend `.eml` files as separate emails to the Gmail account for processing.
