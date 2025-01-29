from ultralytics import YOLO

def load_yolo_model():
    return YOLO("yolov8n.pt")

def detect_objects(model, image):
    results = model(image)
    detected_objects = []
    if hasattr(results[0], "boxes") and results[0].boxes is not None:
        for box in results[0].boxes:
            if hasattr(box, "cls"):
                class_id = int(box.cls)
                class_name = model.names[class_id]
                detected_objects.append(class_name)
    return detected_objects
