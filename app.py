from flask import Flask, render_template, request, jsonify, abort
import sqlite3
import os
import socket
from datetime import datetime, timedelta
import requests
import threading
import time
from smbus2 import SMBus
from RPLCD.i2c import CharLCD

app = Flask(__name__)

# Configuration
DB_PATH = os.environ.get("DB_PATH", os.path.join(os.getcwd(), "attendance.db"))
BACKUP_PATH = os.path.join(os.getcwd(), "attendance_backup")
os.makedirs(BACKUP_PATH, exist_ok=True)

# LCD Setup (adjust address if needed)
lcd = CharLCD('PCF8574', 0x27)

# Function to get the local IP address
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0)
        s.connect(("10.255.255.255", 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = "127.0.0.1"
    finally:
        s.close()
    return IP

# Function to scroll long text on LCD
def scroll_text(text, delay=0.3):
    lcd.clear()
    lcd.write_string("Flask Server IP:")
    time.sleep(2)
    for i in range(len(text) - 15):
        lcd.clear()
        lcd.write_string(text[i:i+16])
        time.sleep(delay)

# Background thread to update and scroll IP
def update_lcd_ip():
    last_ip = ""
    while True:
        current_ip = get_local_ip()
        if current_ip != last_ip:
            lcd.clear()
            lcd.write_string("Flask IP:")
            lcd.crlf()
            lcd.write_string(current_ip[:16])
            print(f"[LCD] Updated IP on LCD: {current_ip}")
            last_ip = current_ip
        time.sleep(5)

# Start LCD IP update thread
threading.Thread(target=update_lcd_ip, daemon=True).start()

# Scroll IP on startup once
scroll_text("Flask Server IP: " + get_local_ip())

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

@app.route('/')
def index():
    records = fetch_attendance()
    print(f"[DEBUG] {len(records)} attendance records retrieved.")
    return render_template('attendance.html', attendance=records)

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
            cursor.execute("SELECT login_logout FROM attendance WHERE name = ? AND day = ?", (name, date))
            result = cursor.fetchone()

            if result:
                previous_times = result[0]
                time_list = previous_times.split(", ") if previous_times.lower() != "no record" else []
                time_list.append(current_time)

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
                updated_login_logout = current_time
                total_hours = "00:00:00"
                cursor.execute('''
                    INSERT INTO attendance (name, day, login_logout, total_hours)
                    VALUES (?, ?, ?, ?)
                ''', (name, date, updated_login_logout, total_hours))

            conn.commit()

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
