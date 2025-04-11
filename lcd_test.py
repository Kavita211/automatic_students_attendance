from flask import Flask, render_template
import sqlite3
import os
from datetime import datetime, timedelta

app = Flask(__name__)

# Detect if running on Railway
IS_RAILWAY = os.environ.get("RAILWAY_ENVIRONMENT", False)

# Dynamic database and backup paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_PATH = os.path.join(BASE_DIR, "attendance.db")
BACKUP_PATH = os.path.join(BASE_DIR, "backup")

# Ensure backup directory exists
os.makedirs(BACKUP_PATH, exist_ok=True)

print("[INFO] Running in Railway mode." if IS_RAILWAY else "[INFO] Running in Local mode.")
print("[INFO] Database Path:", DB_PATH)

def fetch_attendance():
    """Fetch attendance data from the database and correctly calculate total time."""
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
    records = fetch_attendance()
    print("[DEBUG] Attendance Data:", records)
    return render_template('attendance.html', attendance=records)

if __name__ == '__main__':
    if IS_RAILWAY:
        # Railway runs on 0.0.0.0 and a dynamic port
        port = int(os.environ.get("PORT", 5000))
        app.run(host="0.0.0.0", port=port)
    else:
        # Local development
        app.run(debug=True)
