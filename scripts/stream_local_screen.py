import time
import os
import sys
from PIL import Image
import cv2 as cv
from ultralytics import YOLO
import torch

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(dir_path, '..'))

from scripts.to_numpy import to_numpy
from autopilot.screen import stream_local_game_screen, Box
from scripts.lane_lines import LaneLines, process

# TODO remove fixed screens, get dimensions through window info when creating

front_coord = (289,167, 851, 508)
#x1, y1 = (68, 54)
box = Box(0, 40, 1024, 768)

model = YOLO("yolov8m.pt")
device = 'cuda' if torch.cuda.is_available() else 'cpu'
model.to(device)
classes = [0, 2, 7, 9]

streamer = stream_local_game_screen(box=box, default_fps=30)

loop_time = time.time()
while True:
    
    image_data = next(streamer)
    img = Image.fromarray(image_data)
    #img_front = img.crop(front_coord)  # Остается только лобовое стекло грузовика
    img_front = to_numpy(img)
    
    img_front = cv.cvtColor(img_front, cv.COLOR_RGB2BGR)

    #model.predict(process(img_front), classes=classes, conf=0.5, save=False, show=True)
    model.predict(img_front, classes=classes, conf=0.5, save=False, show=True)
    
    #cv.imshow('Computer Vision', img_front)
    
    print('FPS {}'.format(1 / (time.time() - loop_time)))
    loop_time = time.time()
    
    if cv.waitKey(1) == ord('q'):
        cv.destroyAllWindows()
        break
    
    
    # arr = image.img_to_array(img)
    # arr = normalize(arr)
    # arr = np.reshape(arr, (1,) + arr.shape)