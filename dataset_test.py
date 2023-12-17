from roboflow import Roboflow

rf = Roboflow(api_key="nMScVGsC4WS19GoKrMtf")
project = rf.workspace("trafficlightdetect").project("traffic-light-ke5b5")
dataset = project.version(10).download("yolov8")