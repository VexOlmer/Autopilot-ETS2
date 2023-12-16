import torch
from super_gradients.training import models

yolo_nas_l = models.get("yolo_nas_s", pretrained_weights="coco")

model = yolo_nas_l.to("cuda" if torch.cuda.is_available() else "cpu")

model.eval()

model.predict_webcam()