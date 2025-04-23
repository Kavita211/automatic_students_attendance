from flask import Flask, render_template
import sqlite3
import os
from datetime import datetime, timedelta

app = Flask(__name__)

# Use environment variable if set, fallback to local Raspberry Pi path
DB_PATH = os.environ.get("DB_PATH", os.path.join(os.getcwd(), "attendance.db"))

# Store backups inside the current working directory (safe for cloud deployment)
BACKUP_PATH = os.path.join(os.getcwd(), "attendance_backup")
os.makedirs(BACKUP_PATH, exist_ok=True)

print("[INFO] Auto face detection is DISABLED.")
print(f"[INFO] Using database at: {DB_PATH}")
print(f"[INFO] Backup path set to: {BACKUP_PATH}")

def fetch_attendance():
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

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
