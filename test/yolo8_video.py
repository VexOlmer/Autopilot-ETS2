from ultralytics import YOLO
import cv2
import torch
from PIL import ImageGrab, Image
import numpy as np
from mss import mss
from screeninfo import get_monitors


model = YOLO("yolov8m.pt")
device = 'cuda' if torch.cuda.is_available() else 'cpu'
model.to(device)
classes = [0, 2, 7, 9]
source = "screen"

# 0 - person
# 2 - car
# 7 - truck
# 9 - traffic light
# 11 - stop sign

#result = model.predict(source, classes=classes, conf=0.4, show=True, vid_stride=1, save=True)
#print(result)

for m in get_monitors():
    monitor = str(m).split(',')
    width = int(monitor[2].split('=')[1])
    height = int(monitor[3].split('=')[1])
    
bounding_box = {'top': 0, 'left': 0, 'width': width, 'height': height}

sct = mss()

while True:
    #sct_img = sct.grab(bounding_box)
    # cv2.imshow('screen', np.array(sct_img))
    
    result = model.predict(source, classes=classes, conf=0.4, vid_stride=1, save=True)

    if (cv2.waitKey(1) & 0xFF) == ord('q'):
        cv2.destroyAllWindows()
        break
