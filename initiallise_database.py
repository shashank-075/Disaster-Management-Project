import sqlite3
import os

DB_NAME = 'disaster_safety.db'

def initialize_database():
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)
        print(f"Removed old database file: {DB_NAME}")

    conn = None
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        print("Creating new database...")

        # --- NEW SCHEMA ---
        # We've added last_alert_timestamp and alert_count for the "Nudger"
        cursor.execute("""
        CREATE TABLE employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone_number TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            status TEXT NOT NULL,
            last_reply_timestamp TEXT,
            last_alert_timestamp TEXT,
            alert_count INTEGER DEFAULT 0
        );
        """)
        print("Created 'employees' table with NEW schema.")

        # --- Add your test employees ---
        # You are admin
        cursor.execute("""
            INSERT INTO employees (name, phone_number, email, status) 
            VALUES (?, ?, ?, ?)
        """, ('Shashank Kotni (Admin)', 'YOUR_PHONE_NUMBER', 'shashank.kotni2024@vitstudent.ac.in', 'Safe'))
        
        # Co-author
        cursor.execute("""
            INSERT INTO employees (name, phone_number, email, status) 
            VALUES (?, ?, ?, ?)
        """, ('Jayanth K Kumar', 'FRIENDS_PHONE_NUMBER', 'jayanths.email@example.com', 'Pending'))
        
        print(f"Successfully added test employees to the database.")
        print("---")
        print("IMPORTANT: Open this file and edit the placeholder phone numbers!")
        print("---")

        conn.commit()
        print("Database initialization complete.")

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    initialize_database()