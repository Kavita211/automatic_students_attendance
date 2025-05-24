import cv2
import face_recognition
import pickle
import datetime
import gc
import smbus
import time
import threading
import requests
import re
from queue import Queue
import sqlite3

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
    high_bits = mode | (bits & 0xF0) | LCD_BACKLIGHT
    low_bits = mode | ((bits << 4) & 0xF0) | LCD_BACKLIGHT
    bus.write_byte(I2C_ADDR, high_bits)
    lcd_toggle_enable(high_bits)
    bus.write_byte(I2C_ADDR, low_bits)
    lcd_toggle_enable(low_bits)

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

# ✅ LCD Startup
lcd_init()
lcd_display("Starting...", LCD_LINE_1)
lcd_display("System Ready!", LCD_LINE_2)
time.sleep(1)

# ✅ Webcam Setup
video_capture = cv2.VideoCapture(0)
if not video_capture.isOpened():
    lcd_display("Cam Error!", LCD_LINE_1)
    print("[ERROR] Unable to access webcam.")
    exit()

# ✅ Load encodings
with open("/home/pi/attendance_system/encodings.pickle", "rb") as f:
    data = pickle.load(f)
    known_face_encodings = data["encodings"]
    known_face_names = data["names"]

TOLERANCE = 0.55
db_path = "/home/pi/attendance_system/attendance.db"
attendance_queue = Queue()
gc.enable()
last_seen = {}

def handle_unknown_user():
    lcd_display("New User", LCD_LINE_1)
    lcd_display("Enter Details", LCD_LINE_2)
    time.sleep(3)

def update_attendance(name):
    attendance_queue.put(name)

def db_writer():
    conn = sqlite3.connect(db_path, check_same_thread=False)
    cursor = conn.cursor()

    # ✅ Backup yesterday's records
    try:
        yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        cursor.execute("SELECT * FROM attendance WHERE day = ?", (yesterday,))
        rows = cursor.fetchall()

        for row in rows:
            id_, name, day, login_logout, total_hours = row
            payload = {
                "name": name,
                "day": day,
                "login_logout": login_logout,
                "total_hours": total_hours
            }
            headers = {"Content-Type": "application/json"}
            try:
                response = requests.post(PUBLIC_SERVER_URL, json=payload, headers=headers, timeout=10)
                if response.status_code == 200:
                    print(f"[SYNCED] {name} from {day}")
            except Exception as e:
                print(f"[ERROR] Sync failed: {e}")

        cursor.execute("DELETE FROM attendance WHERE day = ?", (yesterday,))
        conn.commit()
        print(f"[INFO] Deleted yesterday's data: {yesterday}")

    except Exception as e:
        print(f"[ERROR] During backup: {e}")

    # ✅ Real-time attendance updates
    while True:
        name = attendance_queue.get()
        if name is None:
            break

        try:
            current_date = datetime.date.today().strftime("%Y-%m-%d")
            current_time = datetime.datetime.now().strftime("%H:%M:%S")

            cursor.execute("SELECT login_logout FROM attendance WHERE name = ? AND day = ?", (name, current_date))
            result = cursor.fetchone()

            if result:
                timestamps = [ts.strip() for ts in result[0].split(",") if ts.strip()]
                if not timestamps or timestamps[-1].startswith("Logout"):
                    timestamps.append(f"Login: {current_time}")
                else:
                    timestamps.append(f"Logout: {current_time}")

                total_seconds = 0
                for i in range(0, len(timestamps) - 1, 2):
                    login_match = re.search(r"Login: (\d{2}:\d{2}:\d{2})", timestamps[i])
                    logout_match = re.search(r"Logout: (\d{2}:\d{2}:\d{2})", timestamps[i + 1])
                    if login_match and logout_match:
                        t1 = datetime.datetime.strptime(login_match.group(1), "%H:%M:%S")
                        t2 = datetime.datetime.strptime(logout_match.group(1), "%H:%M:%S")
                        total_seconds += (t2 - t1).seconds

                total_hours = str(datetime.timedelta(seconds=total_seconds))
                login_logout_str = ", ".join(timestamps)

                cursor.execute("""
                    UPDATE attendance SET login_logout = ?, total_hours = ? WHERE name = ? AND day = ?
                """, (login_logout_str, total_hours, name, current_date))
            else:
                login_logout_str = f"Login: {current_time}"
                total_hours = "00:00:00"
                cursor.execute("""
                    INSERT INTO attendance (name, day, login_logout, total_hours)
                    VALUES (?, ?, ?, ?)
                """, (name, current_date, login_logout_str, total_hours))

            conn.commit()

            # ✅ Sync today's record
            payload = {
                "name": name,
                "day": current_date,
                "login_logout": login_logout_str,
                "total_hours": total_hours
            }
            try:
                response = requests.post(PUBLIC_SERVER_URL, json=payload, timeout=10)
                if response.status_code == 200:
                    print(f"[SYNCED] {name}")
            except requests.exceptions.RequestException as e:
                print(f"[ERROR] Sync failed: {e}")

        except Exception as e:
            print(f"[DB ERROR] {e}")

    conn.close()

def detect_faces():
    try:
        while True:
            ret, frame = video_capture.read()
            if not ret:
                #print("camera error");
                lcd_display("Camera Error!", LCD_LINE_1)
                break

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_frame)

            if not face_locations:
                lcd_display("No Face Found", LCD_LINE_1)
                lcd_display("Waiting...", LCD_LINE_2)
            else:
                lcd_display(f"Faces: {len(face_locations)}", LCD_LINE_1)
                lcd_display("Scanning...", LCD_LINE_2)

            for face_location in face_locations:
                encodings = face_recognition.face_encodings(rgb_frame, [face_location])
                if not encodings:
                    continue

                face_encoding = encodings[0]
                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                best_match_index = face_distances.argmin()

                if best_match_index is not None and face_distances[best_match_index] < TOLERANCE:
                    name = known_face_names[best_match_index]

                    now = time.time()
                    if name not in last_seen or now - last_seen[name] > 10:
                        last_seen[name] = now
                        print(f"[MATCH] {name}")
                        lcd_display(f"Name: {name}", LCD_LINE_1)
                        lcd_display("Marked ✅", LCD_LINE_2)
                        update_attendance(name)
                    else:
                        print(f"[SKIP] {name} seen recently.")
                else:
                    handle_unknown_user()

            time.sleep(0.1)
            gc.collect()
            cv2.waitKey(1)
    except KeyboardInterrupt:
        print("\n[INFO] Face detection stopped.")

# ✅ Start Threads
db_thread = threading.Thread(target=db_writer)
face_thread = threading.Thread(target=detect_faces)

db_thread.start()
face_thread.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n[INFO] Shutting down.")
    attendance_queue.put(None)
    db_thread.join()
    video_capture.release()
    lcd_display("System Off", LCD_LINE_1)
    lcd_display("Goodbye!", LCD_LINE_2)
    print("[INFO] Cleanup complete.")
