from RPLCD.i2c import CharLCD 
from time import sleep
from datetime import datetime

# Initialize the LCD (16x2) with I2C address 0x27
lcd = CharLCD(i2c_expander='PCF8574', address=0x27, port=1, cols=16, rows=2)

# Function to display attendance info

def display_attendance(name, status):
    lcd.clear()

    # Get current time (HH:MM:SS format)
    time_now = datetime.now().strftime("%H:%M:%S") 

    # First row: Display the name (max 16 characters)
    lcd.write_string(name[:16])  # Truncate if too long
    sleep(2)  # Pause before showing status

    lcd.clear()
    
    # Second row: Display IN/OUT and time
    lcd.write_string(f"{status}: {time_now}")
    sleep(3)  # Keep it visible for 3 seconds

    lcd.clear()
