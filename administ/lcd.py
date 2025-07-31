import LCD1602

def init_lcd():
    LCD1602.init(0x3f, 1)

def display_message(message):
    LCD1602.clear()
    LCD1602.write(0,0,message)

def display_minute(minutes):
    LCD1602.clear()
    LCD1602.write(1, 1, f"{minutes} minutes left")

def display_second(seconds):
    LCD1602.clear()
    LCD1602.write(1, 1, f"{seconds} seconds left")