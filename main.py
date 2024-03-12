import cv2 as cv
import numpy as np
import os
from time import time
from windowcapture import WindowCapture
from ultralytics import YOLO
import torch
from scripts.lane_lines import LaneLines, process

model = YOLO("yolov8m.pt")
device = 'cuda' if torch.cuda.is_available() else 'cpu'
model.to(device)
classes = [0, 2, 7, 9]

wincap = WindowCapture('Euro Truck Simulator 2') # not work
#wincap = WindowCapture('INSIDE') # work
#wincap = WindowCapture('Zup!') # work
#wincap = WindowCapture('HALF-LIFE 2 - Direct3D 9') # work
#wincap = WindowCapture('Steam') # error!!!

loop_time = time()
while(True):

    screenshot = wincap.get_screenshot()
    
    #result = model.predict(screenshot, classes=classes, conf=0.4, save=True)
    #lane_lines = LaneLines(screenshot)

    #cv.imshow('Computer Vision', lane_lines.find_lane_lines())
    #cv.imshow('Computer Vision', process(screenshot))
    cv.imshow('Computer Vision', screenshot)

    print('FPS {}'.format(1 / (time() - loop_time)))
    loop_time = time()

    if cv.waitKey(1) == ord('q'):
        cv.destroyAllWindows()
        break


# Игра не будет работать, если ее просто свернуть
#      или она будет в полноэкранному режиме 