# Project556

## Overview

This project reads emails from a Gmail account and saves them to a file called `reademails.txt`. It uses the Gmail API to access the emails.

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

Save the `credentials.json` file in the same directory as your script.

## Running the Script

Run the script to read emails and save them to `reademails.txt`:

```sh
python main.py
```

The first time you run the script, it will open a browser window for you to log in to your Google account and authorize access. This will generate a `token.json` file that stores your access and refresh tokens.

## Code Explanation

### Import Libraries

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

- `os.path`: Provides functions for interacting with the file system.
- `base64`: Provides functions for encoding and decoding data.
- `json`: Provides functions for working with JSON data.
- `google.auth.transport.requests.Request`: Used for making HTTP requests.
- `google.oauth2.credentials.Credentials`: Manages OAuth 2.0 credentials.
- `google_auth_oauthlib.flow.InstalledAppFlow`: Manages the OAuth 2.0 authorization flow.
- `googleapiclient.discovery.build`: Creates a resource object for interacting with the Gmail API.

### Define Scopes

```python
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
```

Defines the scope of access required. In this case, read-only access to Gmail.

### Authenticate Gmail

```python
def authenticate_gmail():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds
```

- Checks if `token.json` exists and loads credentials from it.
- If credentials are not valid, initiates the OAuth 2.0 authorization flow.
- Saves the credentials to `token.json` for future use.

### Read Emails

```python
def read_emails(service):
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
```

- Calls the Gmail API to list messages in the inbox.
- Fetches each message and extracts the subject and body.
- Writes the subject and body to `reademails.txt`, with a separator between emails.

### Main Execution

```python
if __name__ == '__main__':
    creds = authenticate_gmail()
    service = build('gmail', 'v1', credentials=creds)
    read_emails(service)
```

- Authenticates the Gmail account.
- Builds the Gmail API service.
- Reads emails and saves them to `reademails.txt`.

## Conclusion

This project demonstrates how to use the Gmail API to read emails and save them to a file. It includes setting up OAuth 2.0 authentication, calling the Gmail API, and processing email data.