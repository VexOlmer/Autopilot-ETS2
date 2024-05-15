"""

Script to capture and display part of the screen

"""


import time
import os
import sys
from PIL import Image
import cv2 as cv
import numpy

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(dir_path, '..'))

from autopilot.screen import stream_local_game_screen, Box
from scripts.to_numpy import to_numpy

front_coord = (289, 167, 851, 508)    # Лобовое стекло
box = Box(0, 40, 1024, 768)

streamer = stream_local_game_screen(box=box, default_fps=30)

loop_time = time.time()
while True:
    
    image_data = next(streamer)
    img = Image.fromarray(image_data).convert('RGB')
    #img_front = img.crop(front_coord)
    img = to_numpy(img)

    cv.imshow("Image", img)
    
    print((type(image_data)), image_data.shape)
    print('FPS {}'.format(1 / (time.time() - loop_time)))
    
    loop_time = time.time()
    
    if cv.waitKey(1) == ord('q'):
        cv.destroyAllWindows()
        break