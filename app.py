from flask import Flask, render_template
import sqlite3
import os
from datetime import datetime, timedelta

app = Flask(__name__)

# Use relative paths for Railway deployment
DB_PATH = "attendance.db"
BACKUP_PATH = "backup"

# Ensure backup directory exists
os.makedirs(BACKUP_PATH, exist_ok=True)

print("[INFO] Auto face detection is DISABLED.")

def fetch_attendance():
    """Fetch attendance data from the database and calculate total time."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT name, day, login_logout FROM attendance ORDER BY day DESC, name ASC")
    records = cursor.fetchall()
    
    formatted_records = []

    for i, (name, day, log_times) in enumerate(records, start=1):
        name = name.capitalize()
        time_list = log_times.split(", ") if log_times else []

        if len(time_list) < 2:
            formatted_records.append((i, name, day, "No Record", "00:00:00"))
            continue

        login_time = time_list[0]
        logout_time = time_list[-1]
        total_duration = timedelta()

        try:
            t1 = datetime.strptime(login_time, "%H:%M:%S")
            t2 = datetime.strptime(logout_time, "%H:%M:%S")
            if t2 < t1:
                t2 += timedelta(days=1)
            total_duration = t2 - t1
        except ValueError:
            total_duration = timedelta()

        total_hours = str(total_duration) if total_duration else "00:00:00"
        formatted_records.append((i, name, day, f"{login_time} - {logout_time}", total_hours))

    conn.close()
    return formatted_records

@app.route('/')
def index():
    """Render the attendance web page."""
    records = fetch_attendance()
    print("[DEBUG] Attendance Data:", records)
    return render_template('attendance.html', attendance=records)

#if __name__ == '__main__':
    # Use host=0.0.0.0 and port from Railway
    app.run(host="0.0.0.0", port=5000)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
