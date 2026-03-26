from ultralytics import YOLO

# carregar modelo base
model = YOLO("yolov8n.pt")

# treinar modelo
model.train(
    data="dataset_agro/dataset.yaml",
    epochs=50,
    imgsz=640,
    batch=8,
    name="agrovision_gado"
)