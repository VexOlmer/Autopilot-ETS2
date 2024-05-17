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
import keyboard

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(dir_path, '..'))

from autopilot.screen import stream_local_game_screen, Box
from scripts.to_numpy import to_numpy

from ets2_telemetry.truck_values import TruckValues
from ets2_telemetry import TelemetryReader

running = True
def on_key_press(event):
    global running
    if event.name == 'q':
        running = False

keyboard.on_press_key('q', on_key_press)

front_coord = (530, 290, 955, 610)              # Лобовое стекло
minimax_coord = (1356, 645, 1450, 720)          # Путь на миникарте
box = Box(0, 30, 1600, 930)

streamer = stream_local_game_screen(box=box, default_fps=30)

d = str(datetime.datetime.now()).encode('utf8')
_train_uid = hashlib.md5(d).hexdigest()[:8]
_img_ext = 'jpg'
_img_path = "D:\Projects\data_autopilot"

telemetry_reader = TelemetryReader()
truck_info = TruckValues()

default_fps = 2
time_per_frame = 1.0 / default_fps
while True:
    start_time = time.time()
    
    image_data = next(streamer)

    # filename = _train_uid + '_' + re.sub(
    # '[-:.]', '_', datetime.datetime.now().isoformat('_')[:-4]) + \
    # '.' + _img_ext

    image = Image.fromarray(image_data, 'RGB')
    image = image.crop(minimax_coord)
    #image.save(os.path.join(_img_path, filename))

    image = to_numpy(image)

    cv.imshow("Image", image)

    # if (running):
    #     telemetry_reader.update_telemetry(truck_info)
    #     print(f'Steer (поворот руля) {truck_info.steer}', type(truck_info.steer))
    #     print(f'Throttle (ускорение) {truck_info.throttle}', type(truck_info.throttle))
    #     print(f'Brake (тормоз) {truck_info.brake}', type(truck_info.brake))
    #     # print(f'Clutch {truck_info.clutch}')
    #     # print(f'WheelPositionZ  {truck_info.wheelPositionZ }')
    #     print("------------------------------------------------\n")
    
    execution_time = time.time() - start_time
    print('FPS {}'.format(1 / (time.time() - start_time)))

    if execution_time > time_per_frame:
        # Too high fps. No need to sleep.
        pass
    else:
        time.sleep(time_per_frame - execution_time)
    
    if cv.waitKey(1) == ord('q'):
        cv.destroyAllWindows()
        break