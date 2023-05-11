import asyncio
import datetime
import threading
import logging
import time
import requests
import discord
from bot import bot
import gpiozero
import collections

# Pin list
RED_LED = 2
GREEN_LED = 3
ARMING_SWITCH = 4
BUTTON = 17
MOTION_SENSOR = 27

TIME_BETWEEN_MESSAGES = 60 # How many seconds must elapse until a new discord message is sent

class MotionDetector():
    def __init__(self):       
        self.RedLED = gpiozero.LED(RED_LED)
        self.GreenLED = gpiozero.LED(GREEN_LED)
        self.ArmingSwitch = gpiozero.Button(ARMING_SWITCH)
        self.Button = gpiozero.Button(BUTTON)
        self.MotionSensor = gpiozero.MotionSensor(MOTION_SENSOR)
        
        self.Armed = self.ArmingSwitch.is_active
        self.Last_Message_Timestamp = 0
        self.RecentMotions = collections.deque(maxlen=10000)
        self.MotionsSinceLastSent = 0
        if self.Armed:
            logging.info("Bomb armed")
            self.GreenLED.off()
            self.RedLED.on()
        else:
            logging.info("Bomb disarmed")
            self.RedLED.off()
            self.GreenLED.on()
        time.sleep(10)
        bot.set_presence(armed=self.Armed)
    def button_pressed(self):
        """
        Sends the last 24 hours of motion detections in a formatted string
        """
        self.GreenLED.blink(on_time=1,off_time=1,n=1)
        self.RedLED.blink(on_time=1,off_time=1,n=1)
        if self.Armed:
            self.GreenLED.off()
            self.RedLED.on()
        else:
            self.RedLED.off()
            self.GreenLED.on
        embed = self.create_daily_output()
        bot.send_message(embed=embed)
    
    def arm_switch_on(self):
        """
        Arms the device
        """
        self.Armed = True
        self.GreenLED.off()
        self.RedLED.on()
        logging.info("Bomb armed")
        bot.set_presence(armed=self.Armed)
        
        bot.send_message("I AM ARMED")
        
        
    def arm_switch_off(self):
        """
        Disarms the device
        """
        self.Armed = False
        self.GreenLED.on()
        self.RedLED.off()
        logging.info("Bomb disarmed")
        bot.set_presence(armed=self.Armed)
        
        bot.send_message("I AM DISARMED")
        
    def motion_detected(self):
        """
        
        """
        current_timestamp = datetime.datetime.today().timestamp()
        
        if self.Armed:
            logging.info("MOTION DETECTED")
            self.RecentMotions.append(int(current_timestamp))
            self.GreenLED.blink(on_time=1,off_time=1,n=1)
            if current_timestamp - self.Last_Message_Timestamp > TIME_BETWEEN_MESSAGES:
                embed = self.create_embed_output()
                bot.send_message(embed=embed)
                self.Last_Message_Timestamp = current_timestamp
                self.MotionsSinceLastSent = 0
            else: # If this is another motion detection in the last TIME_BETWEEN_MESSAGES
                self.MotionsSinceLastSent += 1
    def create_daily_output(self):
        """
        Creates an output embed showing how many motions have been
        detected in the last 24 hours, as well as the last 15 motion detections
        """
        current_datetime = datetime.datetime.today()
        yesterday_datetime = current_datetime - datetime.timedelta(days=1)
        last_10 = list(self.RecentMotions)[-10:]
        last_10.reverse()
        last_day_motions = [i for i in list(self.RecentMotions) if i >= int(yesterday_datetime.timestamp())]
        title = "Showing recent detections"
        description = f"There have been `{len(last_day_motions):,}` motion detections in the last 24 hours.\n"
        for item in last_10:
            description += f"> <t:{item}:D> - <t:{item}:R>\n"
        embed = discord.Embed(
            title=title,
            description=description,
            colour=discord.Color.blue()
        )
        return embed
    def create_embed_output(self):
        """
        Creates an embed output for a given motion detection.
        Function only called if an embed is planned to be sent
        """
        description=f"Motion has been detected near the bomb."
        if self.MotionsSinceLastSent > 0:
            description += f"\n\nThere have been `{self.MotionsSinceLastSent:,}` detections since you were last notified."

        embed = discord.Embed(
            title="Motion detected",
            description = description,
            colour = discord.Color.dark_red()
        )
        return embed
    def test_for_internet(self):
        """
        A check if the bomb is connected to the internet. If not, the red light
        will start flashing
        """
        URL = "https://www.google.com/"
        TIMEOUT = 5
        try:
            request = requests.get(URL, timeout=TIMEOUT)
            logging.info("Connected to the internet")
        except (requests.ConnectionError, requests.Timeout) as exception:
            logging.critical("No internet connection")
            self.RedLED.blink(on_time=1,off_time=1,n=50)
            exit()
    def run(self):
        self.test_for_internet()
        logging.info("Bomb ready for use")
        while True:
            self.Button.when_activated = self.button_pressed
            self.MotionSensor.when_activated = self.motion_detected
            self.ArmingSwitch.when_activated = self.arm_switch_on
            self.ArmingSwitch.when_deactivated = self.arm_switch_off
            