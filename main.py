"""
Motion sensor program

I said it would work, i never said it would work well


Developed by BSpoones -> May 2022
"""
import logging
import threading
from motion_detector import MotionDetector
from bot import Bot, bot
__version__ = "1.0"
__author__ = "BSpoones"

logging.basicConfig(
    format="%(asctime)s - %(levelname)s: %(message)s",
    encoding='utf-8', 
    level=logging.INFO,
    handlers=[
        logging.FileHandler("motiondetectorlogs.log"),
        logging.StreamHandler()
    ]
    )

logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
rootLogger = logging.getLogger()

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
rootLogger.addHandler(consoleHandler)

if __name__ == "__main__":
    Bomb = MotionDetector()
    bomb_main_thread = threading.Thread(target=Bomb.run)
    bomb_main_thread.start()
    bomb_bot_thread = threading.Thread(target=bot.run())
    bomb_bot_thread.start()
    
    bomb_main_thread.join()
    bomb_bot_thread.join()