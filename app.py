from flask import Flask, render_template, request, jsonify
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)

# 🛠️ Configuration
DB_PATH = os.environ.get("DB_PATH", os.path.join(os.getcwd(), "attendance.db"))
BACKUP_PATH = os.path.join(os.getcwd(), "attendance_backup")
os.makedirs(BACKUP_PATH, exist_ok=True)

print("[INFO] Starting Flask Attendance Server...")
print(f"[INFO] Database Path: {DB_PATH}")
print(f"[INFO] Backup Directory: {BACKUP_PATH}")

# 🔎 Fetch attendance records from DB
def fetch_attendance():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name, day, login_logout, total_hours FROM attendance ORDER BY day DESC, name ASC")
        records = cursor.fetchall()
        conn.close()

        formatted_records = []
        for i, (name, day, log_times, total_hours) in enumerate(records, start=1):
            name = name.capitalize()
            if not log_times or log_times.lower() == "no record":
                formatted_records.append((i, name, day, "No Record", "00:00:00"))
            else:
                time_list = log_times.split(", ")
                login_time = time_list[0]
                logout_time = time_list[-1]
                formatted_records.append((i, name, day, f"{login_time} - {logout_time}", total_hours))
        return formatted_records

    except Exception as e:
        print(f"[ERROR] Failed to fetch attendance: {e}")
        return []

# 🌐 Homepage - Show attendance
@app.route('/')
def index():
    records = fetch_attendance()
    print("[DEBUG] Attendance Records Retrieved:", len(records))
    return render_template('attendance.html', attendance=records)

# 🔁 Raspberry Pi calls this to push data
@app.route('/upload', methods=['POST'])
def upload_attendance():
    try:
        data = request.get_json()

        name = data.get('name')
        date = data.get('date')
        login_logout = data.get('login_logout')
        total_hours = data.get('total_hours')

        if not all([name, date, login_logout, total_hours]):
            return jsonify({'error': 'Missing fields'}), 400

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Upsert logic: insert or update based on name+day
        cursor.execute('''
            INSERT INTO attendance (name, day, login_logout, total_hours)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(name, day) DO UPDATE SET
                login_logout = excluded.login_logout,
                total_hours = excluded.total_hours
        ''', (name, date, login_logout, total_hours))

        conn.commit()
        conn.close()
        print(f"[INFO] Updated attendance for: {name} on {date}")

        return jsonify({'status': 'success'}), 200

    except Exception as e:
        print(f"[ERROR] Upload failed: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500

# ✅ Start the app
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
