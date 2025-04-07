import mysql.connector
from ultralytics import YOLO

model = YOLO("C:\\Users\\tednj\\runs\\detect\\train4\\weights\\best.pt")

def get_database_connection():
    conn = mysql.connector.connect(
        host="localhost", user="root", password="", database="Planogram_Adherence"
    )
    return conn

def get_image_path(image_id):
    conn = get_database_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT filepath FROM images WHERE image_id = %s", (image_id,))
    result = cursor.fetchone()
    conn.close()
    return result["filepath"] if result else None

def detect_objects(image_path):
    detected_objects = {}
    results = model(image_path)

    for result in results:
        for box in result.boxes.data:
            class_id = int(box[-1].item())
            label = model.names[class_id]
            detected_objects[label] = detected_objects.get(label, 0) + 1

    return detected_objects

def compare_images(planogram_path, shelf_path):
    planogram_objects = detect_objects(planogram_path)
    shelf_objects = detect_objects(shelf_path)

    total_expected = sum(planogram_objects.values())
    matches = sum(min(planogram_objects.get(obj, 0), shelf_objects.get(obj, 0)) for obj in planogram_objects)

    return (matches / total_expected) * 100 if total_expected > 0 else 0
