"""

Script to capture and display part of the screen

"""


import time
import os
import sys
from PIL import Image
import cv2 as cv
import numpy
import datetime
import hashlib
import re
from pynput.keyboard import Key, Controller

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(dir_path, '..'))

from autopilot.screen import stream_local_game_screen, Box
from scripts.to_numpy import to_numpy

from ets2_telemetry.truck_values import TruckValues
from ets2_telemetry import TelemetryReader

front_coord = (289, 167, 851, 508)    # Лобовое стекло
box = Box(0, 40, 1024, 768)

streamer = stream_local_game_screen(box=box, default_fps=30)

d = str(datetime.datetime.now()).encode('utf8')
_train_uid = hashlib.md5(d).hexdigest()[:8]
_img_ext = 'jpg'
_img_path = "D:\Projects\data_autopilot"

telemetry_reader = TelemetryReader()
truck_info = TruckValues()

loop_time = time.time()
while True:
    
    image_data = next(streamer)
    #img_front = img.crop(front_coord)

    filename = _train_uid + '_' + re.sub(
    '[-:.]', '_', datetime.datetime.now().isoformat('_')[:-4]) + \
    '.' + _img_ext

    image = Image.fromarray(image_data, 'RGB')
    #image.save(os.path.join(_img_path, filename))

    image = to_numpy(image)

    #cv.imshow("Image", image)
    
    print((type(image_data)), image_data.shape)
    print('FPS {}'.format(1 / (time.time() - loop_time)))
    
    loop_time = time.time()
    
    if cv.waitKey(1) == ord('q'):
        cv.destroyAllWindows()
        break
    
    break