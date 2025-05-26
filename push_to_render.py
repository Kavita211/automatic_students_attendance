import sqlite3
import requests
from datetime import datetime

def push_data():
    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()
    today = datetime.now().strftime('%Y-%m-%d')

    cursor.execute("SELECT name, day, login_logout, total_hours FROM attendance WHERE day = ?", (today,))
    rows = cursor.fetchall()

    for row in rows:
        # Clean the login_logout string to remove labels
        raw_times = row[2].replace("Login: ", "").replace("Logout: ", "")

        data = {
            "name": row[0],
            "day": row[1],
            "login_logout": raw_times,  # Cleaned format
            "total_hours": row[3]
        }

        print(f"Sending this data: {data}")

        try:
            response = requests.post("https://automatic-attendance-17.onrender.com/upload", json=data)
            if response.status_code == 200:
                print(f"✅ Sent for {row[0]}")
            else:
                print(f"❌ Failed for {row[0]}: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ Error sending for {row[0]}: {e}")

    conn.close()

if __name__ == "__main__":
    push_data()
