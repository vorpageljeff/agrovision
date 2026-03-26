# services/detector.py
from ultralytics import YOLO
from collections import Counter

model = YOLO("yolo11n.pt")

def detect_image(image_path: str):
    results = model.predict(image_path)
    result = results[0]

    names = result.names
    classes = result.boxes.cls.tolist() if result.boxes else []
    confs = result.boxes.conf.tolist() if result.boxes else []

    objects = []
    labels = []

    for cls_id, conf in zip(classes, confs):
        label = names[int(cls_id)]
        labels.append(label)
        objects.append({
            "class": label,
            "confidence": round(float(conf), 2)
        })

    counter = Counter(labels)

    if counter:
        partes = [f"{qtd} {classe}" for classe, qtd in counter.items()]
        summary = "Foram detectados: " + ", ".join(partes) + "."
    else:
        summary = "Nenhum objeto relevante foi detectado."

    return {
        "objects": objects,
        "summary": summary
    }