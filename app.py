from flask import Flask, render_template
import sqlite3
import os
from datetime import datetime, timedelta

app = Flask(__name__)

DB_PATH = "/home/pi/attendance_system/attendance.db"
BACKUP_PATH = "/home/pi/attendance_system/backup"

# Ensure backup directory exists
os.makedirs(BACKUP_PATH, exist_ok=True)

# Face detection is now disabled from auto-starting.
# If needed, you can start it manually by running: python3 detect_faces.py
print("[INFO] Auto face detection is DISABLED.")

def fetch_attendance():
    """Fetch attendance data from the database and correctly calculate total time."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT name, day, login_logout FROM attendance ORDER BY day DESC, name ASC")
    records = cursor.fetchall()
    
    formatted_records = []

    for i, (name, day, log_times) in enumerate(records, start=1):
        # Capitalize the first letter of the name
        name = name.capitalize()

        # Extract login and logout times
        time_list = log_times.split(", ") if log_times else []
        
        if len(time_list) < 2:
            formatted_records.append((i, name, day, "No Record", "00:00:00"))
            continue  # Skip to next person

        # First and last timestamp
        login_time = time_list[0]  
        logout_time = time_list[-1]  

        total_duration = timedelta()

        try:
            t1 = datetime.strptime(login_time, "%H:%M:%S")
            t2 = datetime.strptime(logout_time, "%H:%M:%S")

            # Handle cases where logout is before login (crossing midnight)
            if t2 < t1:
                t2 += timedelta(days=1)

            total_duration = t2 - t1

        except ValueError:
            total_duration = timedelta()  # In case of errors

        # Convert total time to HH:MM:SS format
        total_hours = str(total_duration) if total_duration else "00:00:00"

        # Append formatted record
        formatted_records.append((i, name, day, f"{login_time} - {logout_time}", total_hours))

    conn.close()
    return formatted_records

@app.route('/')
def index():
    """Render the attendance web page."""
    records = fetch_attendance()
    print("[DEBUG] Attendance Data:", records)  # Debug print
    return render_template('attendance.html', attendance=records)

if __name__ == '__main__':
   # app.run(host="0.0.0.0", port=5000, ssl_context=('/home/pi/ssl/attendpi.crt', '/home/pi/ssl/attendpi.key'))
   #app.run(host="0.0.0.0", port=5000, debug=True)
   app.run(host="0.0.0.0", port=5000)

