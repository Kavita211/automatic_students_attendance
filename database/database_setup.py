import sqlite3

DB_PATH = "attendance.db"  # Ensure this path is correct

def setup_database():
    """Create database and necessary tables if they do not exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create the students table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            image_path TEXT NOT NULL
        )
    ''')

    # Create the attendance table with correct column names
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            day TEXT NOT NULL,  -- Date of attendance entry
            log_times TEXT NOT NULL,  -- Stores all login/logout times in one row per day
            total_hours TEXT NOT NULL,    -- Stores total hours for the day
            UNIQUE(name, day)  -- Ensure each student has only one row per day
        )
    ''')

    conn.commit()
    conn.close()
    print("[INFO] Database setup completed.")

if __name__ == "__main__":
    setup_database()
