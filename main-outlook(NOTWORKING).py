from __future__ import print_function
import os
import json
import requests
from msal import ConfidentialClientApplication

# Load the credentials from a JSON file
with open('credentials/credentials-outlook.json', 'r') as f:
    credentials = json.load(f)

CLIENT_ID = credentials['client_id']
CLIENT_SECRET = credentials['client_secret']
TENANT_ID = credentials['tenant_id']

# Define the scope and authority
SCOPES = ['https://graph.microsoft.com/.default']
AUTHORITY = f'https://login.microsoftonline.com/{TENANT_ID}'

def authenticate_outlook():
    """Authenticate to the Microsoft Graph API."""
    app = ConfidentialClientApplication(
        CLIENT_ID,
        authority=AUTHORITY,
        client_credential=CLIENT_SECRET
    )
    result = app.acquire_token_for_client(scopes=SCOPES)
    if 'access_token' in result:
        return result['access_token']
    else:
        raise Exception('Could not acquire access token')

def read_emails(access_token):
    """Read emails from the Outlook account."""
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json'
    }
    response = requests.get(
        'https://graph.microsoft.com/v1.0/me/messages',
        headers=headers
    )
    response.raise_for_status()
    messages = response.json().get('value', [])

    with open("reademails.txt", "w", encoding="utf-8") as f:
        if not messages:
            print('No messages found.')
        else:
            print('Messages:')
            for message in messages:
                subject = message.get('subject', '')
                body = message.get('body', {}).get('content', '')
                
                # Extract relevant parts of the email body
                relevant_body = extract_relevant_body(body)
                
                # Write the subject and relevant body to the file
                f.write(f"Subject: {subject}\n")
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
    # Authenticate to the Microsoft Graph API
    access_token = authenticate_outlook()
    # Read emails and save them to reademails.txt
    read_emails(access_token)
