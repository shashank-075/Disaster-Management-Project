import os.path
import base64
import re
import sqlite3
import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.mime.text import MIMEText
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# --- Setup ---
sid = SentimentIntensityAnalyzer()
URGENT_KEYWORDS = ['fire', 'bleeding', 'injured', 'trapped', 'stuck', 'help me', 'danger', 'emergency']
ADMIN_EMAIL = "disasterproject7@gmail.com"
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
DB_NAME = 'disaster_safety.db'

def extract_email(from_header):
    match = re.search(r'<([^>]+)>', from_header)
    if match:
        return match.group(1)
    return from_header.strip()

def send_escalation_alert(service, original_sender, original_body, urgent_word):
    try:
        subject = f"!!! URGENT TRIAGE ALERT: {urgent_word.upper()} reported by {original_sender}"
        message_text = (
            f"A new reply from {original_sender} has been flagged as URGENT.\n\n"
            f"Keyword Detected: {urgent_word.upper()}\n\n"
            f"--- Original Message ---\n"
            f"{original_body}\n"
            f"------------------------\n\n"
            f"Please take immediate action and check the dashboard."
        )
        message = MIMEText(message_text)
        message['to'] = ADMIN_EMAIL
        message['from'] = ADMIN_EMAIL
        message['subject'] = subject
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        message_body = {'raw': raw_message}
        service.users().messages().send(userId="me", body=message_body).execute()
        print(f"  [TRIAGE] URGENT: Escalation alert sent to admin about '{urgent_word}'.")
    except Exception as e:
        print(f"  [TRIAGE] FAILED to send escalation alert: {e}")

def parse_status(body):
    body_lower = body.lower()
    for keyword in URGENT_KEYWORDS:
        if keyword in body_lower:
            return 'Help Needed', True, keyword 
    
    scores = sid.polarity_scores(body_lower)
    compound_score = scores['compound']
    print(f"  > VADER Score: {compound_score}")

    if compound_score > 0.1:
        return 'Safe', False, None
    if compound_score < -0.1:
        return 'Help Needed', False, None
    return 'Unclear', False, None

def log_reply_to_db(sender_email, status):
    conn = None
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        timestamp = datetime.datetime.now().isoformat()
        
        # Reset alert_count to 0 since they replied
        cursor.execute("""
            UPDATE employees 
            SET status = ?, last_reply_timestamp = ?, alert_count = 0 
            WHERE email = ?
        """, (status, timestamp, sender_email))
        conn.commit()
        
        if cursor.rowcount > 0:
            print(f"  [DB_LOG] Updated status for {sender_email} to '{status}'.")
        else:
            print(f"  [DB_LOG] WARN: {sender_email} not found in database.")
    except Exception as e:
        print(f"  [DB_LOG] An error occurred: {e}")
    finally:
        if conn:
            conn.close()

def main():
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

    try:
        service = build('gmail', 'v1', credentials=creds)
        result = service.users().messages().list(userId='me', q='is:unread label:inbox').execute()
        messages = result.get('messages', [])

        if not messages:
            print("No new messages found.")
            return
        print(f"Found {len(messages)} new message(s).")
        print("---")

        for msg in messages:
            txt = service.users().messages().get(userId='me', id=msg['id']).execute()
            payload = txt['payload']
            headers = payload['headers']
            
            subject = "No Subject"
            sender_header = "Unknown Sender"
            for header in headers:
                if header['name'] == 'Subject': subject = header['value']
                if header['name'] == 'From': sender_header = header['value']

            body = "No Body"
            if 'parts' in payload:
                for part in payload['parts']:
                    if part['mimeType'] == 'text/plain':
                        data = part['body']['data']
                        body = base64.urlsafe_b64decode(data).decode('utf-8')
                        break
            else:
                data = payload['body']['data']
                body = base64.urlsafe_b64decode(data).decode('utf-8')

            clean_body = re.sub(r'\s+', ' ', body).strip()
            parsed_body = clean_body.split("On ")[0].strip() # Better email thread removal
            if not parsed_body: parsed_body = clean_body 
                
            print(f"From: {sender_header}")
            print(f"Subject: {subject}")
            print(f"Body: {parsed_body[:100]}...")
            
            sender_email = extract_email(sender_header)
            reply_status, is_urgent, urgent_word = parse_status(parsed_body)
            
            print(f"  > Parsed Status: {reply_status}")
            log_reply_to_db(sender_email, reply_status)
            
            if is_urgent:
                send_escalation_alert(service, sender_email, parsed_body, urgent_word)

            service.users().messages().modify(userId='me', id=msg['id'], body={'removeLabelIds': ['UNREAD']}).execute()
            print(f" (Message {msg['id']} marked as read.)")
            print("---")

    except HttpError as error:
        print(f'An error occurred: {error}')

if __name__ == '__main__':
    main()