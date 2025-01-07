# Project556

## Overview

This project reads emails from a Gmail account and saves them to a file called `reademails.txt`. It uses the Gmail API to access the emails and formats the content for easy reading and processing by AI.

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
                
                relevant_body = extract_relevant_body(body)
                
                f.write(f"{relevant_body}")
                f.write("\n" + "="*50 + "\n\n")
```

- Calls the Gmail API to list messages in the inbox.
- Fetches each message and extracts the subject and body.
- Formats the body to remove unnecessary empty lines and adds newlines before specific keywords.
- Writes the formatted content to `reademails.txt`, with a separator between emails.

### Extract Relevant Body

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

- Splits the body into lines and processes each line.
- Adds a newline before lines containing specific keywords.
- Trims leading and trailing whitespace from each line.
- Removes any leading or trailing empty lines.
- Joins the relevant lines back into a single string.

## Usual Email Format Received in Company
Pedido de assistência nº: 90840
Aberto em: 1/6/2025 4:36:34 PM
Estado atual: Aberto
Prioridade: Normal
Problema: [GRM|SC #792] [TLP: AMBER] – Código Malicioso - Sistema Infetado [TAG000054021] Agradecemos a sua colaboração e cooperação, e solicitamos que nas comunicações subsequentes mantenha o assunto desta mensagem. Identificámos um sistema informático da sua responsabilidade envolvido em incidente de segurança classificado como: Classe de Incidente: Código Malicioso Objeto: TAG000054021 Foi detetado um alerta no dia 27/12/2024 pelas 15:28 onde foram acedidos os seguintes sites categorizados como Malware, hxxp://mailshunt[.]com e hxxp://survey-smiles[.]com Descrição: Os nossos sistemas lançaram um alerta com registo de eventos potencialmente maliciosos que poderão comprometer equipamento e/ou rede num dos serviços do GRM. Vimos por este meio solicitar que desenvolvam as seguintes ações: • Verificação dos factos apresentados; • Verificação dos updates /segurança SO; • Verificação de AV completo (full scan); • Informar a necessidade de alterações de senhas de acesso, utilizadores incluídos; • Resposta a esta mensagem com indicação das ações adotadas; OBS: Esta mensagem está classificada TLP:AMBER - Distribuição Limitada. O destinatário pode compartilhar informações com outras pessoas dentro da sua organização, mas apenas numa lógica de "necessidade de saber". 

Local de trabalho: SRETC - DREC - Direção Regional da Economia
Funcionário: Rui Alberto Teixeira Lira
Contactos: 
Email: rui.at.lira@madeira.gov.pt
Localização: Laboratório de Metrologia da Madeira
TelefoneFixo: 291 930 120
Email: rui.at.lira@madeira.gov.pt
TelefoneFixo: 291 930 120
Localização: Laboratório de Metrologia da Madeira

Equipamentos Associados: 
Computador: 8CG0093K31 - HP ProOne 440 G5 23.8 ALL-IN-ONE - HP

Técnicos:
Recebido por: Ricardina Paula Castro Abreu Luiz
Técnico responsável: Antonio Luz Nunes Castro
Técnicos associados:Antonio Luz Nunes Castro; Duarte Costa Nobrega; Duarte Miguel Pereira Correia da Silva Camara; Dulce Maria Conceicao Camara e Silva; Emanuel Emiliano Spinola Goncalves; Fernando Manuel Brazao Drumond; Filipe Gomes; Jethferandre Agostinho Mendes Hernandes; João Carlos de Jesus Gonçalves; José Micael Gonçalves Ribeiro; Ligia Maria Vasconcelos Gouveia; Luísa Andreia Fernandes Câmara; Mario de Ornelas Matias; Nuno Gonçalo Nunes Ornelas Perry Gomes; Nuno Silvestre Oliveira Faria; Paula Cristina Martins de Freitas Silva; Paulo Diogo; Ricardina Paula Castro Abreu Luiz; Rita Maria Ferreira de Sousa; Sérgio Gonçalo Nunes Silva; Vitor Miguel Rocha Serrao



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

<<<<<<< HEAD
This project demonstrates how to use the Gmail API to read emails and save them to a file. It includes setting up OAuth 2.0 authentication, calling the Gmail API, and processing email data to format it for easy reading and AI processing.
=======
This project demonstrates how to use the Gmail API to read emails and save them to a file. It includes setting up OAuth 2.0 authentication, calling the Gmail API, and processing email data.
>>>>>>> 89a5e5a670762c99db324f52e511f42ab13c93cc
