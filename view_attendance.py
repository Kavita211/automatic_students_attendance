import sqlite3
from datetime import datetime, timedelta

def fetch_attendance():
    db_path = "/home/pi/attendance_system/attendance.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    query = "SELECT name, login_logout FROM attendance WHERE day = DATE('now');"
    cursor.execute(query)
    data = cursor.fetchall()
    conn.close()
    
    return data

def process_attendance(data):
    attendance_records = []
    for idx, (name, timestamps) in enumerate(data, start=1):
        times = timestamps.split(", ")
        if len(times) < 2:
            continue  # Ignore incomplete records
        
        first_entry = times[0]
        last_entry = times[-1]
        
        time_format = "%H:%M:%S"
        login_time = datetime.strptime(first_entry, time_format)
        logout_time = datetime.strptime(last_entry, time_format)
        total_duration = logout_time - login_time
        
        attendance_records.append((idx, name, datetime.now().date(), first_entry, last_entry, str(total_duration)))
    
    return attendance_records

def display_attendance(attendance_records):
    print("\n\U0001F4CC Today's Attendance:")
    print("-" * 75)
    print("S.No | Name      | Date       | Login Time | Logout Time | Total Hours")
    print("-" * 75)
    for record in attendance_records:
        print("{:4} | {:9} | {} | {} | {} | {}".format(*record))
    print("-" * 75)

data = fetch_attendance()
attendance_records = process_attendance(data)
display_attendance(attendance_records)