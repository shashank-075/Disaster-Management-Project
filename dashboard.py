import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import subprocess
import plotly.express as px

DB_NAME = 'disaster_safety.db'

def get_status_dataframe():
    """Gets all employee data and returns it as a Pandas DataFrame."""
    try:
        conn = sqlite3.connect(DB_NAME)
        df = pd.read_sql_query("SELECT * FROM employees", conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Database error: {e}")
        return pd.DataFrame()

# --- Page Config ---
st.set_page_config(page_title="Disaster Control", layout="wide")

# --- Sidebar ---
with st.sidebar:
    st.title("Disaster Control Panel")
    
    st.markdown("---")
    
    # --- PHASE 2: Custom Broadcast ---
    st.header("Send Custom Broadcast")
    broadcast_subject = st.text_input("Subject", "Employee Safety Check")
    broadcast_message = st.text_area("Message", "Please reply 'Safe' or 'Need Help' ASAP.")
    broadcast_target = st.selectbox("Target Group", ('Pending', 'All', 'Safe'))
    
    if st.button(f"🚀 Send Broadcast to '{broadcast_target}'"):
        st.info(f"Sending broadcast to {broadcast_target}...")
        try:
            subprocess.run([
                "python", "send_alert.py", 
                broadcast_subject, 
                broadcast_message, 
                broadcast_target
            ], check=True)
            st.success("Broadcast Sent!")
            st.rerun() # Refresh to show new alert_count
        except Exception as e:
            st.error(f"Failed to send broadcast: {e}")
    
    st.markdown("---")
    
    # --- System Actions ---
    st.header("System Actions")
    if st.button("📥 Check for Replies"):
        st.info("Checking for replies... (See terminal)")
        try:
            subprocess.run(["python", "check_replies.py"], check=True)
            st.success("Inbox checked!")
            st.rerun() 
        except Exception as e:
            st.error(f"Failed to check replies: {e}")
    
    # --- PHASE 3: Automated Follow-up Button ---
    if st.button("⏰ Send Follow-up to 'Pending'"):
        st.info("Sending 'nudge' to all pending employees...")
        try:
            subprocess.run(["python", "automated_followup.py"], check=True)
            st.success("Follow-ups sent!")
            st.rerun() # Refresh to show new alert_count
        except Exception as e:
            st.error(f"Failed to send follow-ups: {e}")
    
    if st.button("🔄 Refresh Data"):
        st.rerun()

    # --- Credits ---
    st.markdown("---") 
    st.header("About")
    st.info(
        """
        **Project by:** Shashank Kotni and Jayanth K Kumar
        **Contact:** shashank.kotni2024@vitstudent.ac.in
        """
    )

# --- Main Dashboard Page ---
st.title("Employee Safety Status Dashboard")
st.write(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

data_df = get_status_dataframe()

if data_df.empty:
    st.warning("No data found in database. Run initialize_database.py")
    st.stop()

# --- Key Metrics (with Response Rate) ---
st.header("Key Metrics")
total_employees = len(data_df)
safe_count = len(data_df[data_df['status'] == 'Safe'])
pending_count = len(data_df[data_df['status'] == 'Pending'])
help_count = len(data_df[data_df['status'] == 'Help Needed'])
replied_count = safe_count + help_count
response_rate = (replied_count / total_employees) * 100 if total_employees > 0 else 0

# Now 5 columns for metrics
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Employees", total_employees)
col2.metric("Replied", replied_count)
col3.metric("Pending", pending_count)
if help_count > 0:
    col4.metric("Needs Help", help_count, delta=f"{help_count} Critical", delta_color="inverse")
else:
    col4.metric("Needs Help", help_count)
# NEW: Response Rate Metric
col5.metric("Response Rate", f"{response_rate:.1f}%")

st.markdown("---") 

# --- Graphs and Data Table ---
st.header("Status Breakdown")
col_chart, col_data = st.columns([1, 2]) 

with col_chart:
    st.subheader("By Status")
    status_counts = data_df['status'].value_counts().reset_index()
    status_counts.columns = ['status', 'count']
    
    fig_pie = px.pie(status_counts, 
                 values='count', names='status', title='Employee Status', hole=0.4,
                 color='status',
                 color_discrete_map={
                     'Safe': '#5cb85c',
                     'Pending': '#f0ad4e',
                     'Help Needed': '#d9534f',
                     'Unclear': '#777777'
                 })
    st.plotly_chart(fig_pie, use_container_width=True)

with col_data:
    st.subheader("Detailed Employee List")
    st.dataframe(data_df, use_container_width=True, height=400)

st.markdown("---")

# --- NEW: Bar Chart for Alert Counts ---
st.header("Follow-up & Alert Analysis")
pending_df = data_df[data_df['status'] == 'Pending']

if pending_df.empty:
    st.success("All employees have replied! No 'Pending' users to show.")
else:
    st.subheader("Alerts Sent to 'Pending' Employees")
    # Create the bar chart
    fig_bar = px.bar(pending_df, 
                     x='name', 
                     y='alert_count',
                     title="Alert Count for Unresponsive Employees",
                     labels={'name': 'Employee Name', 'alert_count': 'Number of Alerts Sent'},
                     color='alert_count',
                     color_continuous_scale='OrRd') # Red scale for high counts
    
    st.plotly_chart(fig_bar, use_container_width=True)