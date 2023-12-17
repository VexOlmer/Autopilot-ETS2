from ultralytics import YOLO
 
model = YOLO('yolov8s.pt')

if __name__ == '__main__' :
    results = model.train(
    data="./Traffic-light-10/data.yaml",
    imgsz=640,
    epochs=30,
    batch=8,
    name='yolov8s_b8_30e',
    plots=True,
    device="cuda"
    )