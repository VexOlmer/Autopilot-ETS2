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
    DEFAULT_FPS = 5
    
    # DATA_PATH = os.path.join('C:\Projects\data_autopilot', 'csv')
    # IMG_PATH = os.path.join('C:\Projects\data_autopilot', 'img', 'raw')

# NOTE увеличить число машин, их слишком мало!!!
# NOTE посмотреть бывает ли отрицательное ускорение или торможение
# NOTE убрать возможность добавление данных с нулевым углом маршрута
# NOTE проверить правильно ли сохраняются зеркальные изображения (на -1 умножение идет или нет)
# NOTE проверить по примерам нахождение угла поворота маршрута, будто ошибки какие-то там

generate_training_data(config = MyConfig)