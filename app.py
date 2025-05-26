from flask import Flask, render_template, request, jsonify, abort 
import sqlite3
import os
from datetime import datetime, timedelta
import requests

app = Flask(__name__)

# Configuration
DB_PATH = os.environ.get("DB_PATH", os.path.join(os.getcwd(), "attendance.db"))
BACKUP_PATH = os.path.join(os.getcwd(), "attendance_backup")
os.makedirs(BACKUP_PATH, exist_ok=True)

print("[INFO] Starting Flask Attendance Server...")
print(f"[INFO] Database Path: {DB_PATH}")
print(f"[INFO] Backup Directory: {BACKUP_PATH}")

# Initialize DB & table
def initialize_db():
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS attendance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    day TEXT NOT NULL,
                    login_logout TEXT DEFAULT 'No Record',
                    total_hours TEXT DEFAULT '00:00:00'
                )
            ''')
            conn.commit()
        print("[INFO] Database initialized successfully.")
    except Exception as e:
        print(f"[ERROR] Database initialization failed: {e}")
        raise

initialize_db()

# Fetch attendance records for homepage
def fetch_attendance():
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name, day, login_logout, total_hours FROM attendance ORDER BY day DESC, name ASC")
            records = cursor.fetchall()

        formatted_records = []
        for i, (name, day, log_times, total_hours) in enumerate(records, start=1):
            name = name.capitalize()
            if not log_times or log_times.lower() == "no record":
                formatted_records.append((i, name, day, "No Record", "00:00:00"))
            else:
                time_list = log_times.split(", ")
                login_time = time_list[0].replace("Login:", "").replace("Logout:", "").strip()
                logout_time = time_list[-1].replace("Login:", "").replace("Logout:", "").strip()
                formatted_records.append((i, name, day, f"{login_time} - {logout_time}", total_hours))
        return formatted_records

    except Exception as e:
        print(f"[ERROR] Failed to fetch attendance: {e}")
        return []

# Homepage route
@app.route('/')
def index():
    records = fetch_attendance()
    print(f"[DEBUG] {len(records)} attendance records retrieved.")
    return render_template('attendance.html', attendance=records)

# Upload attendance and push to Render
@app.route('/upload', methods=['POST'])
def upload_attendance():
    try:
        data = request.get_json(force=True)

        if not data:
            abort(400, description="No data provided")

        name = data.get('name')
        timestamp = data.get('timestamp')

        if not all([name, timestamp]):
            abort(400, description="Missing fields")

        try:
            dt_obj = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            abort(400, description="Invalid timestamp format. Expected: YYYY-MM-DD HH:MM:SS")

        date = dt_obj.strftime("%Y-%m-%d")
        current_time = dt_obj.strftime("%H:%M:%S")

        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()

            # Check if record exists for this user and date
            cursor.execute("SELECT login_logout FROM attendance WHERE name = ? AND day = ?", (name, date))
            result = cursor.fetchone()

            if result:
                previous_times = result[0]
                time_list = previous_times.split(", ") if previous_times.lower() != "no record" else []
                time_list.append(current_time)

                # Calculate total worked hours
                total_seconds = 0
                for i in range(0, len(time_list) - 1, 2):
                    try:
                        t1 = datetime.strptime(time_list[i], "%H:%M:%S")
                        t2 = datetime.strptime(time_list[i+1], "%H:%M:%S")
                        total_seconds += (t2 - t1).seconds
                    except Exception as e:
                        print(f"[WARN] Incomplete pair found: {e}")
                        continue

                total_hours = str(timedelta(seconds=total_seconds))
                updated_login_logout = ", ".join(time_list)

                cursor.execute('''
                    UPDATE attendance 
                    SET login_logout = ?, total_hours = ?
                    WHERE name = ? AND day = ?
                ''', (updated_login_logout, total_hours, name, date))
            else:
                # First time entry
                updated_login_logout = current_time
                total_hours = "00:00:00"
                cursor.execute('''
                    INSERT INTO attendance (name, day, login_logout, total_hours)
                    VALUES (?, ?, ?, ?)
                ''', (name, date, current_time, total_hours))

            conn.commit()

        # Push to Render server
        data_to_push = {
            "name": name,
            "day": date,
            "login_logout": updated_login_logout,
            "total_hours": total_hours
        }

        try:
            render_response = requests.post(
                "https://automatic-attendance-17.onrender.com/upload",
                json=data_to_push,
                timeout=5
            )
            if render_response.status_code == 200:
                print(f"[INFO] Successfully pushed attendance for {name} to Render.")
            else:
                print(f"[WARN] Failed to push attendance for {name} to Render: "
                      f"{render_response.status_code} - {render_response.text}")
        except Exception as e:
            print(f"[ERROR] Exception while pushing attendance to Render: {e}")

        return jsonify({'status': 'success'}), 200

    except Exception as e:
        print(f"[ERROR] Upload failed: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
