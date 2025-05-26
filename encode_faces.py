import cv2
import face_recognition
import sqlite3
import os
import numpy as np
import smbus
import time

# ✅ LCD Setup
I2C_ADDR = 0x27
bus = smbus.SMBus(1)
LCD_WIDTH = 16
LCD_LINE_1 = 0x80
LCD_LINE_2 = 0xC0
LCD_BACKLIGHT = 0x08
ENABLE = 0b00000100

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

def lcd_init():
    lcd_send_byte(0x33, 0)
    lcd_send_byte(0x32, 0)
    lcd_send_byte(0x06, 0)
    lcd_send_byte(0x0C, 0)
    lcd_send_byte(0x28, 0)
    lcd_send_byte(0x01, 0)
    time.sleep(0.0005)

def lcd_display(message, line):
    message = message.ljust(LCD_WIDTH)
    lcd_send_byte(line, 0)
    for char in message:
        lcd_send_byte(ord(char), 1)

# ✅ Paths
DB_PATH = "/home/pi/attendance_system/attendance.db"
IMAGE_DIR = "/home/pi/attendance_system/student_images"

# ✅ Ensure database is set up
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS student_faces (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        encoding BLOB NOT NULL
    )
""")
conn.commit()

def encode_faces():
    face_encodings = []
    face_names = []

    for file in os.listdir(IMAGE_DIR):
        if file.endswith((".jpg", ".png", ".jpeg")):
            path = os.path.join(IMAGE_DIR, file)
            name = os.path.splitext(file)[0].capitalize()

            image = face_recognition.load_image_file(path)
            encodings = face_recognition.face_encodings(image)

            if encodings:
                encoding = encodings[0]
                face_encodings.append(encoding)
                face_names.append(name)

                cursor.execute("INSERT OR REPLACE INTO student_faces (name, encoding) VALUES (?, ?)", 
                               (name, encoding.tobytes()))
                conn.commit()
                print(f"[INFO] Encoded & stored: {name}")
            else:
                print(f"[WARNING] No face detected in {file}. Skipping.")

    conn.close()
    print("[INFO] Face encoding completed for all students.")

    # ✅ Show LCD message
    lcd_init()
    lcd_display("Face Encoding", LCD_LINE_1)
    lcd_display("Done ", LCD_LINE_2)

if __name__ == "__main__":
    encode_faces()
