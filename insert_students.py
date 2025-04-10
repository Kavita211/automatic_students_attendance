import sqlite3

DB_PATH = "attendance.db"

def fetch_students():
    """Fetch all student records from the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()

    conn.close()
    return students

# Fetch and print student records
students = fetch_students()

print("\n📌 Student Records:")
print("-------------------------------------------------")
print("ID  | Name      | Image Path")
print("-------------------------------------------------")
for student in students:
    print(f"{student[0]:<3} | {student[1]:<10} | {student[2]}")

print("\n[INFO] Fetched student records successfully.")
