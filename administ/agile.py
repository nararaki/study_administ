from scheduler import minute_scheduler
from lcd import display_minute
from lcd import init_lcd
from gpiocontroller import get_minute_btn
from gpiocontroller import get_start_btn
from gpiocontroller import get_buzzer
from scheduler import over_minute
from scheduler import time_check
from scheduler import elapse_minute
from scheduler import elapse_second
from lcd import display_message
from lcd import display_second
from ultralytics import YOLO
import asyncio
import time
import discord
import os
import random
import subprocess
from gpiozero import OutputDevice, InputDevice
from dotenv import load_dotenv

client = discord.Client(intents=discord.Intents.default())
@client.event
async def on_ready():
    target_channel_id = os.getenv('TARGET_CHANNEL_ID')

    try:
        channel = client.get_channel(int(target_channel_id))
        await channel.send('Hello World!')
        print("Message sent to discord")
    except ValueError:
        print("Error: TARGET_CHANNEL_ID in .env is invalid.")

async def send_Discord(message):
    target_cahnnel_id = os.getenv('TARGET_CHANNEL_ID')
    try:
        channel = client.get_channel(int(target_cahnnel_id))
        if channel:
            await channel.send(message)
            print("Message sent correctly")
        else:
            print("cannot find channel")
    except ValueError:
        print("Error")
    

def initialize():
    load_dotenv() 
    btn = get_minute_btn()   #pin22
    start_btn = get_start_btn() #pin21
    interval = 0
    init_lcd()
    dht11 = DHT11(14)
    humidity, temperature = dht11.read_data()
    print(f"Humidity: {humidity}, Temperature: {temperature}")
    if humidity <= 50 and humidity >= 30 and  temperature >= 21 and temperature <= 26:
        display_message("Good condition")
    else:
        display_message("Bad condition")
    try:
        while True:
            if start_btn.value == 1:
                print("Start button pressed")
                btn.close()
                start_btn.close()
                break
            if btn.value == 1:
                print("minute button pressed")
                interval = minute_scheduler(interval)
                display_minute(interval // 60)
                time.sleep(0.5)  
    except KeyboardInterrupt:
        print("Exiting...")
        btn.close()
        start_btn.close()
    
    asyncio.run(gather(interval))
    
async def main_logic(interval,ditect_task, discord_task):
    try:

        while True:
            if over_minute(interval):
                #LCDに残り時間を表示
                display_minute(interval // 60)
                #1分経過
                interval = elapse_minute(interval)
                await asyncio.sleep(60)
            else:
                #LCDに残り時間を表示
                display_second(interval)
                #1秒経過
                interval = elapse_second(interval)
                if time_check(interval):
                    await asyncio.sleep(1)
                else:
                    print("finished")
                    buzzer = get_buzzer()
                    buzzer.on()
                    await send_Discord("Finished")
                    #LCDに終了メッセージを表示
                    display_message("Finished")
                    discord_task.cancel()
                    ditect_task.cancel()
                    await client.close()
                    break
        pass
    except KeyboardInterrupt:
        print("Exiting...")
        pass 

async def ditect_studying():
    model = YOLO("best.pt")
    try:
        while True:
            results = await asyncio.to_thread(predict, model)
            if results:
                print("person is detected")
            else:
                print ("person is not detected")
                #Discordに通知する
                await send_Discord("勉強に集中できてません!")
            time_wait = random.randint(0,60)
            await asyncio.sleep(time_wait)
    except KeyboardInterrupt:
        print("Exiting...")
        pass


def predict(model):
    cmd = ['fswebcam', '-d', '/dev/video0', '-r', '640x480','--no-banner',  'study.jpg']
    subprocess.run(cmd)
    results = model.predict('study.jpg',save=True,save_txt=True,project="result")
    if len(results[0].boxes) > 0:
        return True
    else:
        return False

async def gather(interval):
    discord_task = asyncio.create_task(client.start(os.getenv('TOKEN')))
    ditect_task = asyncio.create_task(ditect_studying())
    main_task = asyncio.create_task(main_logic(interval,discord_task,ditect_task))
    await asyncio.gather(discord_task, main_task, ditect_task)

class DHT11():
    MAX_DELAY_COUINT = 100
    BIT_1_DELAY_COUNT = 10
    BITS_LEN = 40

    def __init__(self, pin, pull_up=False):
        self._pin = pin
        self._pull_up = pull_up


    def read_data(self):
        bit_count = 0
        delay_count = 0
        bits = ""

        # -------------- send start --------------
        gpio = OutputDevice(self._pin)
        gpio.off()
        time.sleep(0.02)

        gpio.close()
        gpio = InputDevice(self._pin, pull_up=self._pull_up)

        # -------------- wait response --------------
        while gpio.value == 1:
            pass
        
        # -------------- read data --------------
        while bit_count < self.BITS_LEN:
            while gpio.value == 0:
                pass

            # st = time.time()
            while gpio.value == 1:
                delay_count += 1
                # break
                if delay_count > self.MAX_DELAY_COUINT:
                    break
            if delay_count > self.BIT_1_DELAY_COUNT:
                bits += "1"
            else:
                bits += "0"

            delay_count = 0
            bit_count += 1

        # -------------- verify --------------
        humidity_integer = int(bits[0:8], 2)
        humidity_decimal = int(bits[8:16], 2)
        temperature_integer = int(bits[16:24], 2)
        temperature_decimal = int(bits[24:32], 2)
        check_sum = int(bits[32:40], 2)

        _sum = humidity_integer + humidity_decimal + temperature_integer + temperature_decimal

        # print(bits)
        # print(humidity_integer, humidity_decimal, temperature_integer, temperature_decimal)
        # print(f'sum:{_sum}, check_sum:{check_sum}')
        # print()

        if check_sum != _sum:
            humidity = 0.0
            temperature = 0.0
        else:
            humidity = float(f'{humidity_integer}.{humidity_decimal}')
            temperature = float(f'{temperature_integer}.{temperature_decimal}')

        # -------------- return --------------
        return humidity, temperature
    
initialize()