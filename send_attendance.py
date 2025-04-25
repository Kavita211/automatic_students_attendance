import requests

# Sample test data – you can dynamically update these later in your project
data = {
    'name': 'Trupti',
    'date': '2025-04-25',
    'login_logout': '08:39:32 - 08:40:02',
    'total_hours': '0:00:13'
}

# Replace with your actual deployed Render link
API_URL = "https://automatic-attendance-17.onrender.com/upload"

try:
    response = requests.post(API_URL, json=data)
    if response.status_code == 200:
        print("[✅] Attendance successfully sent!")
    else:
        print(f"[❌] Failed to send attendance. Status: {response.status_code}")
        print("Response:", response.text)
except Exception as e:
    print("[⚠️] Error sending data:", e)
