import os
import sys

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(dir_path, '..'))

from autopilot.screen import Box
from autopilot.train import generate_training_data, Config

class MyConfig(Config):
    
    BOX = Box(0, 0, 500, 500)
    DEFAULT_FPS = 5

generate_training_data(config=MyConfig)