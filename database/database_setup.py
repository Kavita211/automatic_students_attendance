import sqlite3
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

def lcd_scroll_message(message, line, delay=0.3):
    message = " " * LCD_WIDTH + message + " " * LCD_WIDTH
    for i in range(len(message) - LCD_WIDTH + 1):
        lcd_display(message[i:i+LCD_WIDTH], line)
        time.sleep(delay)

# ✅ Show welcome message
lcd_init()
lcd_scroll_message("Automatic Attendance System", LCD_LINE_1, delay=0.2)

# ✅ Database Setup
DB_PATH = "/home/pi/attendance_system/attendance.db"  # Update this if needed

def setup_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # students table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            image_path TEXT NOT NULL
        )
    ''')

    # attendance table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            day TEXT NOT NULL,
            log_times TEXT NOT NULL,
            total_hours TEXT NOT NULL,
            UNIQUE(name, day)
        )
    ''')

    conn.commit()
    conn.close()
    print("[INFO] Database setup completed.")
    lcd_display("Database Setup", LCD_LINE_1)
    lcd_display("Completed ", LCD_LINE_2)

if __name__ == "__main__":
    setup_database()
