import torch
from super_gradients.training import models

yolo_nas_l = models.get("yolo_nas_s", pretrained_weights="coco")

device = "cuda" if torch.cuda.is_available() else "cpu"
device  = "cpu"

model = yolo_nas_l.to(device)

model.eval()

model.predict_webcam()