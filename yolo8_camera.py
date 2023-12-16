from ultralytics import YOLO
import cv2

model = YOLO("yolov8m.pt")
model.to('cuda')

#print(model.names)

# camera
#results = model.predict(source="0", show=True, stream=True)

#source = "C:/Users/dan4i/Videos/Euro Truck Simulator 2/medium quality/ets city best.mp4"
# medium quality
# ets city best.mp4
# ets city medium.mp4
# ets city small object.mp4

source = "C:/Users/dan4i/Videos/Euro Truck Simulator 2/high quality/ets cabin clear road.mp4"
# high quality
# ets cabin clear road.mp4
# ets city big.mp4
# ets city small.mp4
model.predict(source, conf=0.5, show=True, vid_stride=3)