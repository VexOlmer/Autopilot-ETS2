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
classes = [2, 7, 9]  # 2 - car, 7 - truck, 9 - traffic light

streamer = stream_local_game_screen(box=box, default_fps=30)

loop_time = time.time()
while True:
    print(device)
    
    image_data = next(streamer)
    img = Image.fromarray(image_data)
    #img_front = img.crop(front_coord)  # Остается только лобовое стекло грузовика
    img_front = to_numpy(img)
    
    img_front = cv.cvtColor(img_front, cv.COLOR_RGB2BGR)
    img_traffic = img_front

    result = model.predict(img_front, classes=classes, conf=0.5, save=False, show=False)
    result = result[0]
    output = []

    for box in result.boxes:
        colors_dict = {'Green':0, 'Yellow':0, 'Red':0} # Unknow color ?
        traffic_color = ""
        color = (0, 255, 255) # yellow in BGR

        x1, y1, x2, y2 = [
          round(x) for x in box.xyxy[0].tolist()
        ] 
        class_id = box.cls[0].item()
        class_names = result.names[class_id]
        prob = round(box.conf[0].item(), 2)

        output.append([
          x1, y1, x2, y2, class_names, prob
        ])      

        if class_names == 'traffic light':
            pic = img_front[y1:y2, x1:x2]
            
            hsv = cv.cvtColor(pic, cv.COLOR_BGR2HSV)
            
            colors_dict['green'] = cv.inRange(hsv, (60,0,235), (80,255,255)).sum()
            colors_dict['yellow'] = cv.inRange(hsv, (91,0,233), (95,255,255)).sum()
            colors_dict['red'] = cv.inRange(hsv, (106,0,245), (120,255,255)).sum()
            
            traffic_color = max(colors_dict, key=colors_dict.get)
            color = (0, 0, 255)  # red in BGR
    
        cv.rectangle(img_traffic, (x1, y1), (x2, y2), color, 2)
        text = traffic_color + " " + class_names + " " + str(prob)
        cv.putText(img_traffic, text, (x1, y1 - 5), cv.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    print(output)

    cv.imshow("Image", img_traffic)
    
    print('FPS {}'.format(1 / (time.time() - loop_time)))
    loop_time = time.time()
    
    if cv.waitKey(1) == ord('q'):
        cv.destroyAllWindows()
        break