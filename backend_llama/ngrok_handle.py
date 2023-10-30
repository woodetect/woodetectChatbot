import os
import time
import base64
from email.mime.text import MIMEText
import requests
from requests import HTTPError
import json
#from google_auth_oauthlib.flow import InstalledAppFlow
#from googleapiclient.discovery import build
import subprocess

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

users_key = ['bb83a791-552b-44df-bf48-d5652bf8844a']
mail_address = ['mlg.fcu@gmail.com']

#flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
#creds = flow.run_local_server(port=0)
#service = build('gmail', 'v1', credentials=creds)

def notify_phone(message, description):
    for key in users_key:
        requests.post('https://api.mynotifier.app', {
            "apiKey": key,
            "message": message,
            "description": description,
            "type": "info", # info, error, warning or success
        })

def send_email(subject, description):
    for target in mail_address:
        message = MIMEText(description)
        message['to'] = target
        message['subject'] = subject
        create_message = {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}
        try:
            # Send the email using the Gmail API
            _ = service.users().messages().send(userId='me', body=create_message).execute()
            print('Email sent successfully')
        except Exception as e:
            print(f'Error sending email: {e}')
            pass

def run_ngrok():
    print("Starting ngrok")
    _ = subprocess.Popen(["ngrok", "http", "5000"], stdout=subprocess.PIPE)

def get_ngrok_url_with_curl():
    try:
        result = subprocess.run(["curl", "-s", "http://localhost:4040/api/tunnels"], stdout=subprocess.PIPE, text=True)
        if result.returncode == 0:
            tunnel_info = json.loads(result.stdout)
            tunnels = tunnel_info["tunnels"]
            if tunnels:
                return tunnels[0]["public_url"]
            else:
                return None
        else:
            print(f"Error running curl command: {result.stderr}")
            return None
    except Exception as e:
        print(f"Error retrieving ngrok URL: {str(e)}")
        return None

def main():
    run_ngrok()
    time.sleep(5)
    addr = get_ngrok_url_with_curl()
    print("sedning :", addr)
    if addr is None:
        addr = "Ngrok URL not found"
    try:
        notify_phone("Ngrok URL", addr)
        #send_email("Ngrok URL", addr)
    except Exception as e:
        print(f'Error sending notification: {e}')
        pass

if __name__ == '__main__':
    main()