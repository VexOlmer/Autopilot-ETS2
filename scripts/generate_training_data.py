import os
import sys
import threading
import keyboard

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(dir_path, '..'))

from autopilot.screen import Box
from autopilot.train import generate_training_data, Config

class MyConfig(Config):
    
    BOX = Box(0, 30, 1600, 930)
    DEFAULT_FPS = 10
    
    # DATA_PATH = os.path.join('C:\Projects\data_autopilot', 'csv')
    # IMG_PATH = os.path.join('C:\Projects\data_autopilot', 'img', 'raw')


generate_training_data(config = MyConfig)