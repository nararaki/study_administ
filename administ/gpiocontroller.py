import gpiozero


def get_minute_btn():
    btn = gpiozero.DigitalInputDevice(pin=25,pull_up=False)# Pin 22
    return btn

def get_start_btn():
    btn = gpiozero.DigitalInputDevice(pin=9,pull_up=False) # Pin 21
    return btn

def get_buzzer():
    buzzer = gpiozero.DigitalOutputDevice(pin=11,pull_up=False)#pin 23
    return buzzer