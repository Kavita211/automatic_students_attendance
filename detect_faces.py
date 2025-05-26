import cv2
import face_recognition
import pickle
import datetime
import gc
import smbus
import time
import threading
import requests
import sqlite3
from queue import Queue

# ✅ Server URL
PUBLIC_SERVER_URL = "https://automatic-attendance-17.onrender.com/upload"

# ✅ I2C LCD Setup
I2C_ADDR = 0x27
bus = smbus.SMBus(1)
LCD_WIDTH = 16
LCD_LINE_1 = 0x80
LCD_LINE_2 = 0xC0
LCD_BACKLIGHT = 0x08
ENABLE = 0b00000100

def lcd_init():
    lcd_send_byte(0x33, 0)
    lcd_send_byte(0x32, 0)
    lcd_send_byte(0x06, 0)
    lcd_send_byte(0x0C, 0)
    lcd_send_byte(0x28, 0)
    lcd_send_byte(0x01, 0)
    time.sleep(0.0005)

def lcd_send_byte(bits, mode):
    high = mode | (bits & 0xF0) | LCD_BACKLIGHT
    low = mode | ((bits << 4) & 0xF0) | LCD_BACKLIGHT
    bus.write_byte(I2C_ADDR, high)
    lcd_toggle_enable(high)
    bus.write_byte(I2C_ADDR, low)
    lcd_toggle_enable(low)

def lcd_toggle_enable(bits):
    time.sleep(0.0005)
    bus.write_byte(I2C_ADDR, bits | ENABLE)
    time.sleep(0.0005)
    bus.write_byte(I2C_ADDR, bits & ~ENABLE)
    time.sleep(0.0005)

def lcd_display(message, line):
    message = message.ljust(LCD_WIDTH)
    lcd_send_byte(line, 0)
    for char in message:
        lcd_send_byte(ord(char), 1)

# ✅ Startup LCD
lcd_init()
lcd_display("Starting...", LCD_LINE_1)
lcd_display("System Ready!", LCD_LINE_2)
time.sleep(1)

# ✅ Camera Setup
video_capture = cv2.VideoCapture(0)
if not video_capture.isOpened():
    lcd_display("Cam Error!", LCD_LINE_1)
    print("[ERROR] Webcam access failed.")
    exit()

# ✅ Load Encodings
with open("/home/pi/attendance_system/encodings.pickle", "rb") as f:
    data = pickle.load(f)
    known_face_encodings = data["encodings"]
    known_face_names = data["names"]

# ✅ Constants
TOLERANCE = 0.55
attendance_queue = Queue()
last_seen = {}
db_path = "/home/pi/attendance_system/attendance.db"
gc.enable()
stop_event = threading.Event()

def update_attendance(name):
    attendance_queue.put(name)

def handle_unknown():
    lcd_display("New User", LCD_LINE_1)
    lcd_display("Enter Details", LCD_LINE_2)
    time.sleep(2)

def db_writer():
    conn = sqlite3.connect(db_path, check_same_thread=False)
    cursor = conn.cursor()

    # ✅ Backup yesterday's data
    try:
        yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        cursor.execute("SELECT * FROM attendance WHERE day = ?", (yesterday,))
        for row in cursor.fetchall():
            payload = {
                "name": row[1],
                "day": row[2],
                "login_logout": row[3],
                "total_hours": row[4]
            }
            try:
                response = requests.post(PUBLIC_SERVER_URL, json=payload, timeout=10)
                if response.status_code == 200:
                    print(f"[BACKUP SYNCED] {row[1]} - {row[2]}")
            except Exception as e:
                print(f"[SYNC ERROR] {e}")
        cursor.execute("DELETE FROM attendance WHERE day = ?", (yesterday,))
        conn.commit()
    except Exception as e:
        print(f"[ERROR] During backup: {e}")

    # ✅ Real-time attendance processing
    while True:
        name = attendance_queue.get()
        if name is None:
            break

        try:
            today = datetime.date.today().strftime("%Y-%m-%d")
            now = datetime.datetime.now().strftime("%H:%M:%S")

            cursor.execute("SELECT login_logout FROM attendance WHERE name = ? AND day = ?", (name, today))
            result = cursor.fetchone()

            if result:
                logs = result[0].split(", ")
                login_time = None
                logout_time = now
                for entry in logs:
                    if entry.startswith("Login:"):
                        login_time = entry.split("Login: ")[-1]
                        break

                if not login_time:
                    login_time = now

                login_logout = f"Login: {login_time}, Logout: {logout_time}"
                t1 = datetime.datetime.strptime(login_time, "%H:%M:%S")
                t2 = datetime.datetime.strptime(logout_time, "%H:%M:%S")
                total_seconds = (t2 - t1).seconds
                total_hours = str(datetime.timedelta(seconds=total_seconds))

                cursor.execute("""
                    UPDATE attendance SET login_logout = ?, total_hours = ? WHERE name = ? AND day = ?
                """, (login_logout, total_hours, name, today))
            else:
                login_logout = f"Login: {now}"
                total_hours = "00:00:00"
                cursor.execute("""
                    INSERT INTO attendance (name, day, login_logout, total_hours)
                    VALUES (?, ?, ?, ?)
                """, (name, today, login_logout, total_hours))

            conn.commit()

            payload = {
                "name": name,
                "day": today,
                "login_logout": login_logout,
                "total_hours": total_hours
            }
            try:
                response = requests.post(PUBLIC_SERVER_URL, json=payload, timeout=10)
                if response.status_code == 200:
                    print(f"[SYNCED] {name}")
            except Exception as e:
                print(f"[SYNC FAIL] {e}")
        except Exception as e:
            print(f"[DB ERROR] {e}")

    conn.close()

def detect_faces():
    while not stop_event.is_set():
        ret, frame = video_capture.read()
        if not ret:
            break

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        locations = face_recognition.face_locations(rgb)

        if not locations:
            lcd_display("No Face Found", LCD_LINE_1)
            lcd_display("Waiting...", LCD_LINE_2)
        else:
            lcd_display(f"Faces: {len(locations)}", LCD_LINE_1)
            lcd_display("Scanning...", LCD_LINE_2)

        for location in locations:
            encoding = face_recognition.face_encodings(rgb, [location])
            if not encoding:
                continue

            face_encoding = encoding[0]
            distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match = distances.argmin()

            if best_match is not None and distances[best_match] < TOLERANCE:
                name = known_face_names[best_match]
                now = time.time()
                if name not in last_seen or now - last_seen[name] > 10:
                    last_seen[name] = now
                    lcd_display(f"Name: {name}", LCD_LINE_1)
                    lcd_display("Marked ", LCD_LINE_2)
                    print(f" {name} marked attendance")
                    update_attendance(name)
            else:
                handle_unknown()

        time.sleep(0.1)
        gc.collect()
        cv2.waitKey(1)

    # ✅ Show completion message once
    lcd_display("Detection", LCD_LINE_1)
    lcd_display("Completed", LCD_LINE_2)

# ✅ Start Threads
db_thread = threading.Thread(target=db_writer)
face_thread = threading.Thread(target=detect_faces)

db_thread.start()
face_thread.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("[INFO] Stopping system...")
    stop_event.set()
    attendance_queue.put(None)
    face_thread.join()
    db_thread.join()
    video_capture.release()
    print("[INFO] System exited.")
