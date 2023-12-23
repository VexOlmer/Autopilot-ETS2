import time
import os
import sys
from PIL import Image
import cv2 as cv

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(dir_path, '..'))

from scripts.to_numpy import to_numpy
from autopilot.screen import stream_local_game_screen, Box

box = Box(0, 0, 1280, 720)
streamer = stream_local_game_screen(box=box, default_fps=30)

loop_time = time.time()
while True:
    
    image_data = next(streamer)
    img = Image.fromarray(image_data)
    img = to_numpy(img)
    
    img = cv.cvtColor(img, cv.COLOR_RGB2BGR)
    
    cv.imshow('Computer Vision', img)
    
    print('FPS {}'.format(1 / (time.time() - loop_time)))
    loop_time = time.time()
    
    if cv.waitKey(1) == ord('q'):
        cv.destroyAllWindows()
        break
    
    # img_front = im.crop(front_coord)  # Остается только лобовое стекло грузовика
    
    # arr = image.img_to_array(img)
    # arr = normalize(arr)
    # arr = np.reshape(arr, (1,) + arr.shape)