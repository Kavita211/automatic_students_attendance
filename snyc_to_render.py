import sqlite3
import requests
import datetime

# Connect to your local Pi database
conn = sqlite3.connect('attendance.db')
cursor = conn.cursor()

# Get today's date in YYYY-MM-DD format
today = datetime.datetime.now().strftime("%Y-%m-%d")

# Read today's attendance records
cursor.execute("SELECT name, day, login_logout, total_hours FROM attendance WHERE day = ?", (today,))
rows = cursor.fetchall()

# Loop through and send each record to the server
for row in rows:
    data = {
        "name": row[0],
        "day": row[1],  # use 'day' to match your DB column and API structure
        "login_logout": row[2],
        "total_hours": row[3]
    }

    try:
        response = requests.post("https://automatic-attendance-17.onrender.com/update", json=data)
        print(f"Sent for {row[0]}: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error sending for {row[0]}: {e}")

# Close the DB connection
conn.close()
