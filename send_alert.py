import os.path
import sqlite3
import sys
import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from email.mime.text import MIMEText
import base64

import toml
from twilio.rest import Client

# --- PHASE 4: TWILIO (SMS) INTEGRATION ---

# Load configuration from config.toml
try:
    with open('config.toml', 'r') as f:
        config = toml.load(f)
    TWILIO_ACCOUNT_SID = config.get('twilio', {}).get('account_sid')
    TWILIO_AUTH_TOKEN = config.get('twilio', {}).get('auth_token')
    TWILIO_PHONE_NUMBER = config.get('twilio', {}).get('phone_number')
except (FileNotFoundError, toml.TomlDecodeError) as e:
    print(f"Error loading config.toml: {e}")
    TWILIO_ACCOUNT_SID = None
    TWILIO_AUTH_TOKEN = None
    TWILIO_PHONE_NUMBER = None
# ----------------------------------------

# --- GMAIL API ---
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
DB_NAME = 'disaster_safety.db'
ADMIN_EMAIL = 'disasterproject7@gmail.com' # Your admin email

def _get_gmail_service():
    """Builds and returns a Gmail API service object."""
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

def _send_email_internal(service, subject, message_text, to_email):
    """Internal function to send a single email."""
    try:
        message = MIMEText(message_text)
        message['to'] = to_email
        message['from'] = ADMIN_EMAIL
        message['subject'] = subject
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        message_body = {'raw': raw_message}
        
        send_message = service.users().messages().send(userId="me", body=message_body).execute()
        print(f"  > [Email] Successfully sent to {to_email}.")
    except Exception as e:
        print(f"  > [Email] FAILED to send to {to_email}: {e}")

def _send_sms_internal(subject, message_text, to_phone):
    """Internal function to send a single SMS via Twilio."""
    try:
        # Check if Twilio credentials are not set or are still placeholders
        if not TWILIO_ACCOUNT_SID or "YOUR_TWILIO_ACCOUNT_SID" in TWILIO_ACCOUNT_SID:
            print("  > [SMS] FAILED: Twilio credentials are not set up in config.toml")
            return

        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        body = f"{subject}\n\n{message_text}"
        
        message = client.messages.create(
            body=body,
            from_=TWILIO_PHONE_NUMBER,
            to=to_phone  # Must be in E.164 format, e.g., +14155552671
        )
        print(f"  > [SMS] Successfully sent to {to_phone}. SID: {message.sid}")
    except Exception as e:
        print(f"  > [SMS] FAILED to send to {to_phone}: {e}")

def send_custom_alert(subject, message, target_group):
    """
    Sends a custom alert to a target group via Email and SMS.
    target_group can be 'All', 'Pending', or 'Safe'.
    """
    print(f"--- Initiating Custom Alert ---")
    print(f"Target: {target_group} | Subject: {subject}")

    conn = None
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        query = "SELECT email, phone_number FROM employees"
        if target_group == 'Pending':
            query += " WHERE status = 'Pending'"
        elif target_group == 'Safe':
            query += " WHERE status = 'Safe'"
        # If 'All', no WHERE clause is needed
        
        cursor.execute(query)
        recipients = cursor.fetchall()
        
    except Exception as e:
        print(f"Database error: {e}")
        return
    finally:
        if conn:
            conn.close()

    if not recipients:
        print(f"No recipients found in group '{target_group}'.")
        return

    print(f"Found {len(recipients)} recipient(s). Building services...")
    
    # Get services
    gmail_service = _get_gmail_service()
    
    # Get current time
    timestamp = datetime.datetime.now().isoformat()

    for (email, phone) in recipients:
        print(f"Processing: {email} | {phone}")
        # --- Send to both channels ---
        _send_email_internal(gmail_service, subject, message, email)
        _send_sms_internal(subject, message, phone)
        
        # --- Update the database ---
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE employees
                SET last_alert_timestamp = ?, alert_count = alert_count + 1
                WHERE email = ?
            """, (timestamp, email))
            conn.commit()
        except Exception as e:
            print(f"DB update failed for {email}: {e}")
        finally:
            if conn:
                conn.close()

    print("--- Alert Send Complete ---")

if __name__ == '__main__':
    """
    This allows the script to be run from the command line (e.g., by the dashboard).
    We expect 3 arguments: python send_alert.py "Subject" "Message" "TargetGroup"
    """
    if len(sys.argv) == 4:
        subject = sys.argv[1]
        message = sys.argv[2]
        target_group = sys.argv[3]
        send_custom_alert(subject, message, target_group)
    else:
        print("Invalid arguments. Running a test alert to 'Pending'...")
        send_custom_alert(
            "Default Test Alert", 
            "This is a default test message.", 
            "Pending"
        )sage, target_group)
    else:
        print("Invalid arguments. Running a test alert to 'Pending'...")
        send_custom_alert(
            "Default Test Alert", 
            "This is a default test message.", 
            "Pending"
        )