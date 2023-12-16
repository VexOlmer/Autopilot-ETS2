import torch
import gc
import os
from super_gradients.training import models

device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
list_models = ["yolo_nas_l", "yolo_nas_m", "yolo_nas_s"]

list_models = ["yolo_nas_s"]

for chosen_net in list_models:
  net = models.get(chosen_net, pretrained_weights="coco")
  net.to(device)

  print("\nchosen_net:", chosen_net, "\n")

  for video_name in os.listdir("./videos"):

    if video_name == "Greece.mp4":
        in_video_path = os.path.join("./videos", video_name)
        out_video_path = os.path.join("./predictions", video_name.replace(".mp4", f"_{chosen_net}.mp4"))

        print("in_video_path:", in_video_path)

        net.predict(in_video_path).save(out_video_path)

  print()

  del net
  gc.collect()
  torch.cuda.empty_cache()