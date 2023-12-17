import cv2 as cv
import numpy as np
import os
from time import time
from windowcapture import WindowCapture
from ultralytics import YOLO
import torch
from lane_lines import LaneLines, process

# Change the working directory to the folder this script is in.
# Doing this because I'll be putting the files from each video in their own folder on GitHub
os.chdir(os.path.dirname(os.path.abspath(__file__)))

model = YOLO("yolov8m.pt")
device = 'cuda' if torch.cuda.is_available() else 'cpu'
model.to(device)
classes = [0, 2, 7, 9]

wincap = WindowCapture('Zup!')

loop_time = time()
while(True):

    # get an updated image of the game
    screenshot = wincap.get_screenshot()
    #result = model.predict(screenshot, classes=classes, conf=0.4, save=True)
    
    lane_lines = LaneLines(screenshot)

    #cv.imshow('Computer Vision', lane_lines.find_lane_lines())
    cv.imshow('Computer Vision', process(screenshot))

    # debug the loop rate
    print('FPS {}'.format(1 / (time() - loop_time)))
    loop_time = time()

    if cv.waitKey(1) == ord('q'):
        cv.destroyAllWindows()
        break