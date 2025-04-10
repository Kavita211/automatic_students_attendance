import sqlite3

DB_PATH = "attendance.db"

# Connect to database
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Create the students table if it does not exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        image_path TEXT NOT NULL
    )
''')

conn.commit()
conn.close()

print("[INFO] Students table created successfully.")
