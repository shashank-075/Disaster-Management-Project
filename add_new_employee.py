import sqlite3

# --- Employee Details ---
NEW_NAME = "Name"
NEW_EMAIL = "email"
NEW_PHONE = "phone number" # Use E.164 format for Twilio
# --------------------------

def add_employee():
    conn = None
    try:
        conn = sqlite3.connect('disaster_safety.db')
        cursor = conn.cursor()
        status = 'Pending'
        
        cursor.execute("""
            INSERT OR IGNORE INTO employees (name, phone_number, email, status, alert_count) 
            VALUES (?, ?, ?, ?, 0)
        """, (NEW_NAME, NEW_PHONE, NEW_EMAIL, status))
        
        conn.commit()

        if cursor.rowcount > 0:
            print(f"✅ Successfully added '{NEW_NAME}' to the database.")
        else:
            print(f"⚠️ '{NEW_NAME}' (or email '{NEW_EMAIL}') already exists.")

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("Attempting to add new employee...")
    add_employee()