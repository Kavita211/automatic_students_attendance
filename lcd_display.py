import smbus
import time

# I2C Address of the LCD (use `i2cdetect -y 1` to confirm)
I2C_ADDR = 0x27  
LCD_WIDTH = 16  # Max characters per line

# LCD Commands
LCD_CHR = 1  # Data mode
LCD_CMD = 0  # Command mode
LCD_LINE_1 = 0x80  # First line address
LCD_LINE_2 = 0xC0  # Second line address

ENABLE = 0b00000100  # Enable bit
bus = smbus.SMBus(1)  # Use I2C bus 1

def lcd_init():
    lcd_write(0x33, LCD_CMD)  # Initialize
    lcd_write(0x32, LCD_CMD)  # Set to 4-bit mode
    lcd_write(0x06, LCD_CMD)  # Cursor move direction
    lcd_write(0x0C, LCD_CMD)  # Turn display on
    lcd_write(0x28, LCD_CMD)  # 2-line mode
    lcd_write(0x01, LCD_CMD)  # Clear display
    time.sleep(0.002)

def lcd_write(bits, mode):
    high_bits = mode | (bits & 0xF0) | ENABLE
    low_bits = mode | ((bits << 4) & 0xF0) | ENABLE
    for bits in [high_bits, high_bits & ~ENABLE, low_bits, low_bits & ~ENABLE]:
        bus.write_byte(I2C_ADDR, bits)
        time.sleep(0.0005)

def lcd_string(message, line):
    message = message.ljust(LCD_WIDTH, " ")
    lcd_write(line, LCD_CMD)
    for char in message:
        lcd_write(ord(char), LCD_CHR)

def lcd_clear():
    lcd_write(0x01, LCD_CMD)
    time.sleep(0.002)

def lcd_write_message(line1="", line2=""):
    lcd_clear()
    lcd_string(line1, LCD_LINE_1)
    lcd_string(line2, LCD_LINE_2)

# ✅ This function will be used in detect_faces.py
def display_message(line1="", line2=""):
    lcd_write_message(line1, line2)

# Optional: test run
if __name__ == "__main__":
    lcd_init()
    display_message("LCD Ready", "Test OK")
    time.sleep(2)
    lcd_clear()
