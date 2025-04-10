import board
import busio
import adafruit_character_lcd.character_lcd_i2c as character_lcd

# Set LCD size (Change 16,2 to match your LCD dimensions)
lcd_columns = 16
lcd_rows = 2

# Initialize I2C interface
i2c = busio.I2C(board.SCL, board.SDA)

# Define LCD
lcd = character_lcd.Character_LCD_I2C(i2c, lcd_columns, lcd_rows)

# Display test message
lcd.message = "Hello, Trupti!\nLCD is Working! 😊"
