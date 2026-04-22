# Disaster Management Project

A Python-based application designed to help organizations manage employee safety during disaster events. This tool allows sending alerts via Email and SMS, tracking employee responses, and maintaining a dashboard overview.

## Features

*   **Employee Management**: Add new employees to the system.
*   **Alert System**: Send custom alerts to all or specific groups of employees ('All', 'Pending', 'Safe').
*   **Multi-channel Communication**: Delivers alerts via both Email (Gmail) and SMS (Twilio).
*   **Response Tracking**: Automatically checks for and processes employee replies.
*   **Automated Follow-ups**: Sends reminders to employees who have not yet responded.
*   **Dashboard**: A Streamlit-based dashboard to visualize employee status and manage alerts.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/shashank-075/Disaster-Management-Project.git
    cd Disaster-Management-Project
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Install dependencies:**
    The required Python packages are not listed in a `requirements.txt` file. Based on the project structure, you would need to install them manually. The following packages are likely required:
    `google-api-python-client`
    `google-auth-httplib2`
    `google-auth-oauthlib`
    `twilio`
    `streamlit`
    `pandas`
    `toml`

    You can install them using pip:
    ```bash
    pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib twilio streamlit pandas toml
    ```

4.  **Configure the application:**
    -   Update `config.toml` with your Twilio credentials.
    -   You will need `credentials.json` for the Gmail API. Follow the Google Workspace documentation to create OAuth 2.0 credentials.
    -   The first time you run a script that uses the Gmail API, you will be prompted to authorize the application. This will create a `token.json` file.

## Usage

*   **Initialize the database:**
    ```bash
    python initiallise_database.py
    ```

*   **Run the dashboard:**
    ```bash
    streamlit run dashboard.py
    ```

*   The dashboard provides an interface to send alerts and view employee status.
