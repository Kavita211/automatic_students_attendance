import sqlite3
import cv2
import face_recognition
import pickle
import datetime
import gc
import smbus
import time
import threading

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

# ✅ Initialize LCD
lcd_init()
lcd_display("Starting...", LCD_LINE_1)
lcd_display("System Ready!", LCD_LINE_2)
time.sleep(2)

# ✅ Initialize webcam
video_capture = cv2.VideoCapture(0)
if not video_capture.isOpened():
    lcd_display("Cam Error!", LCD_LINE_1)
    print("[ERROR] Unable to access webcam.")
    exit()

gc.enable()

# ✅ Connect to SQLite database
db_path = "/home/pi/attendance_system/attendance.db"
conn = sqlite3.connect(db_path, check_same_thread=False)
cursor = conn.cursor()

# ✅ Load known face encodings
with open("/home/pi/attendance_system/encodings.pickle", "rb") as f:
    data = pickle.load(f)
    known_face_encodings = data["encodings"]
    known_face_names = data["names"]

# ✅ Set a stricter tolerance for better accuracy
TOLERANCE = 0.55  # Adjust as needed (lower = stricter, higher = more lenient)

def update_attendance(name):
    current_date = datetime.date.today().strftime("%Y-%m-%d")
    current_time = datetime.datetime.now().strftime("%H:%M:%S")
    
    cursor.execute("SELECT login_logout FROM attendance WHERE name = ? AND day = ?", (name, current_date))
    existing_entry = cursor.fetchone()

    if existing_entry:
        timestamps = existing_entry[0].split(", ")
        
        if len(timestamps) % 2 == 1:  # Last was login, now logout
            timestamps.append(current_time)
        else:  # Last was logout, now new login
            timestamps.append(current_time)
        
        # Compute total hours for all login-logout pairs
        total_seconds = 0
        for i in range(0, len(timestamps) - 1, 2):
            login_time = datetime.datetime.strptime(timestamps[i], "%H:%M:%S")
            logout_time = datetime.datetime.strptime(timestamps[i+1], "%H:%M:%S")
            total_seconds += (logout_time - login_time).seconds
        
        total_hours = str(datetime.timedelta(seconds=total_seconds))
        new_login_logout = ", ".join(timestamps)
        cursor.execute("UPDATE attendance SET login_logout = ?, total_hours = ? WHERE name = ? AND day = ?", 
                       (new_login_logout, total_hours, name, current_date))
    else:
        cursor.execute("INSERT INTO attendance (name, day, login_logout, total_hours) VALUES (?, ?, ?, ?)", 
                       (name, current_date, current_time, "00:00:00"))
    
    conn.commit()

def handle_unknown_user():
    lcd_display("New User", LCD_LINE_1)
    lcd_display("Enter Details", LCD_LINE_2)
    time.sleep(3)

# ✅ Face detection thread
def detect_faces():
    try:
        while True:
            ret, frame = video_capture.read()
            if not ret:
                lcd_display("Camera Error!", LCD_LINE_1)
                print("[ERROR] Failed to grab frame from webcam.")
                break

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_frame)

            lcd_display(f"Faces: {len(face_locations)}", LCD_LINE_1)
            lcd_display("Scanning...", LCD_LINE_2)

            for face_location in face_locations:
                encodings = face_recognition.face_encodings(rgb_frame, [face_location])
                if encodings:
                    face_encoding = encodings[0]
                    matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=TOLERANCE)

                    if any(matches):
                        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                        best_match_index = min(range(len(face_distances)), key=lambda i: face_distances[i])
                        
                        if matches[best_match_index]:
                            name = known_face_names[best_match_index]
                            update_attendance(name)
                            lcd_display(f"Name: {name}", LCD_LINE_1)
                            lcd_display("Attendance Marked", LCD_LINE_2)
                            print(f"[INFO] {name} - Attendance marked.")
                        else:
                            handle_unknown_user()
                    else:
                        handle_unknown_user()

                time.sleep(2)  # Prevents duplicate detection in short intervals

            gc.collect()
            cv2.waitKey(1)  # Allows OpenCV to process events properly

    except KeyboardInterrupt:
        print("\n[INFO] System shutdown successfully.")

# ✅ Attendance update thread
def update_attendance_loop():
    try:
        while True:
            # Here you can add functionality to periodically check for new attendance data, upload it to a server, or perform any other tasks
            time.sleep(5)
            # For example: Upload attendance data to server

    except KeyboardInterrupt:
        print("\n[INFO] Attendance update loop shutdown.")

# ✅ Run face detection and attendance update in parallel using threads
face_thread = threading.Thread(target=detect_faces)
attendance_thread = threading.Thread(target=update_attendance_loop)

face_thread.start()
attendance_thread.start()

# ✅ Main program termination handling
try:
    while True:
        time.sleep(1)  # Main thread keeps running
except KeyboardInterrupt:
    print("\n[INFO] Main program shutdown.")
    video_capture.release()
    conn.close()
    lcd_display("System Off", LCD_LINE_1)
    lcd_display("Goodbye!", LCD_LINE_2)
    print("[INFO] Cleanup complete.")
