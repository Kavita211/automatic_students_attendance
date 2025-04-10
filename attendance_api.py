import sqlite3
from datetime import datetime

DB_PATH = "/home/pi/attendance_system/attendance.db"

def mark_attendance(name, status):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Check last entry for the user
        cursor.execute("SELECT status FROM attendance WHERE student_name=? ORDER BY id DESC LIMIT 1", (name,))
        last_entry = cursor.fetchone()

        # Avoid duplicate IN entries
        if last_entry and last_entry[0] == status:
            print(f"[INFO] {name} is already marked {status}. No duplicate entry.")
            conn.close()
            return

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO attendance (name, status, time) VALUES (?, ?, ?)", (name, status, timestamp))

        conn.commit()
        conn.close()
        print(f"[INFO] Attendance recorded: {name} marked {status} at {timestamp}")

    except Exception as e:
        print(f"[ERROR] Database error: {e}")
