import cv2
import face_recognition
import sqlite3
import os
import numpy as np

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
    """Encodes all student faces and stores them in the database."""
    face_encodings = []
    face_names = []

    for file in os.listdir(IMAGE_DIR):
        if file.endswith((".jpg", ".png", ".jpeg")):
            path = os.path.join(IMAGE_DIR, file)
            name = os.path.splitext(file)[0].capitalize()  # Extract name from filename

            # ✅ Load and encode image
            image = face_recognition.load_image_file(path)
            encodings = face_recognition.face_encodings(image)

            if encodings:
                encoding = encodings[0]  # Use first detected face
                face_encodings.append(encoding)
                face_names.append(name)

                # ✅ Store in database
                cursor.execute("INSERT OR REPLACE INTO student_faces (name, encoding) VALUES (?, ?)", 
                               (name, encoding.tobytes()))
                conn.commit()
                print(f"[INFO] Encoded & stored: {name}")

            else:
                print(f"[WARNING] No face detected in {file}. Skipping.")

    conn.close()
    print("[INFO] Face encoding completed for all students.")

if __name__ == "__main__":
    encode_faces()
