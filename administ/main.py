from scheduler import minute_scheduler
from scheduler import over_minute
from scheduler import second_scheduler
from scheduler import time_check
from scheduler import elapse_minute
from scheduler import elapse_second
from lcd import display_message
from lcd import display_minute
from lcd import display_second
from lcd import init_lcd
from gpiocontroller import get_minute_btn
from gpiocontroller import get_second_btn
from gpiocontroller import get_start_btn
from DHT11 import DHT11
from ultralytics import YOLO
import discord
import os
from dotenv import load_dotenv
import asyncio
import subprocess
import time
# .envファイルから環境変数を読み込む
load_dotenv()

async def send_Discord():
    intents = discord.Intents.default()
    client = discord.Client(intents=intents)
    target_channel_id = os.getenv('TARGET_CHANNEL_ID')

    try:
        channel = client.get_channel(int(target_channel_id))
        await channel.send('Hello World!')
        print("Message sent to discord")
    except ValueError:
        print("Error: TARGET_CHANNEL_ID in .env is invalid.")

def initialize():
    btn  = get_minute_btn()
    second_btn = get_second_btn()
    start_btn = get_start_btn()
    interval = 0
    init_lcd()
    while True:
        try:
            if start_btn.value == 1:
                print("Start button pressed")
                btn.close()
                second_btn.close()
                start_btn.close()
                break
            if btn.value == 1:
                interval += minute_scheduler(interval)
                display_minute(interval // 60)
                time.sleep(0.5)  
            if second_btn.value == 1:
                interval += second_scheduler(interval)
                display_second(interval)
                time.sleep(0.5)  
        except KeyboardInterrupt:
            print("Exiting...")
            break
    main_logic(interval)

async def main_logic(interval):
    model = YOLO('best.pt')
    while True:
        if over_minute(interval):
            interval = elapse_minute(interval)
            display_minute(interval // 60)
        else:
            interval = elapse_second(interval)
            #LCDに残り時間を表示
            display_second(interval)
        if time_check(interval):
            if over_minute(interval):
                #ここで画像認識をし、人がいなければDiscordに通知する
                cmd = ['fswebcam', '-d', '/dev/video0', '-r', '640x480','--no-banner',  '/study.jpg']
                try:
                    subprocess.run(cmd)
                except Exception as e:
                    print(e)
                    print("Error taking picture")
                finally:
                    results = model.predict('/study.jpg', save=True, save_txt=True, save_conf=True, project = 'result')
                    if int(results[0].boxes[0].cls) == 0:
                        print("person is detected")
                    else:
                        print ("person is not detected")
                        #Discordに通知する
                        await send_Discord()
                #湿度・温度センサーを使って適切な範囲になければLCDに表示
                dht11 = DHT11(14)
                humidity, temperature = dht11.read_data()
                if not (humidity > 50 and humidity < 60 and temperature > 23 and temperature < 28): 
                    display_message("humidity or temperature is out of range")
                else:
                    display_message("humidity and temperature are in range")
                await asyncio.sleep(60)
            else:
                await asyncio.sleep(1)
        else:
            print("finished")
            #LCDに終了メッセージを表示
            display_message("Finished")
            break
    initialize() 

initialize()