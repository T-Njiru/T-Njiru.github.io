import mysql.connector
import cv2
import torch
from PyQt5.QtWidgets import QApplication, QLabel, QPushButton, QVBoxLayout, QComboBox, QWidget, QMessageBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from ultralytics import YOLO

# Database connection function
def get_database_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="Planogram_Adherence"
        )
        return conn
    except mysql.connector.Error as err:
        print("Error connecting to database:", err)
        return None

# Load YOLO model
model = YOLO("C:\\Users\\tednj\\runs\\detect\\train3\\weights\\best.pt")

def compare_images(planogram_path, shelf_path):
    """Compares two images and returns an adherence score."""
    planogram_objects = detect_objects(planogram_path)
    shelf_objects = detect_objects(shelf_path)

    total_expected = sum(planogram_objects.values())
    matches = sum(min(planogram_objects.get(obj, 0), shelf_objects.get(obj, 0)) for obj in planogram_objects)

    return (matches / total_expected) * 100 if total_expected > 0 else 0

def detect_objects(image_path):
    """Detects objects in an image using YOLO model."""
    detected_objects = {}
    results = model(image_path)

    for result in results:
        for box in result.boxes.data:
            class_id = int(box[-1].item())
            label = model.names[class_id]
            detected_objects[label] = detected_objects.get(label, 0) + 1

    return detected_objects

class PlanogramComparatorGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Planogram Comparator")
        self.setGeometry(100, 100, 600, 400)

        self.planogram_combo = QComboBox()
        self.image_combo = QComboBox()
        self.compare_btn = QPushButton("Compare")
        self.planogram_label = QLabel()
        self.image_label = QLabel()

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Select Planogram:"))
        layout.addWidget(self.planogram_combo)
        layout.addWidget(QLabel("Select Image:"))
        layout.addWidget(self.image_combo)
        layout.addWidget(self.compare_btn)
        layout.addWidget(self.planogram_label)
        layout.addWidget(self.image_label)
        self.setLayout(layout)

        self.load_image_paths()
        self.load_planogram_paths()

        self.planogram_combo.currentIndexChanged.connect(lambda: self.display_image(self.planogram_combo, self.planogram_label))
        self.image_combo.currentIndexChanged.connect(lambda: self.display_image(self.image_combo, self.image_label))
        self.compare_btn.clicked.connect(self.compare_action)

    def load_planogram_paths(self):
        self.planogram_paths = self.load_paths_from_db("SELECT file_path FROM planogram")
        self.planogram_combo.addItems(self.planogram_paths)

    def load_image_paths(self):
        self.image_paths = self.load_paths_from_db("SELECT filepath FROM images")
        self.image_combo.addItems(self.image_paths)

    def load_paths_from_db(self, query):
        paths = []
        conn = get_database_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(query)
                paths = [row[0] for row in cursor.fetchall()]
            except mysql.connector.Error as e:
                print("Database error:", e)
            finally:
                conn.close()
        return paths

    def display_image(self, combo, label):
        image_path = combo.currentText()
        if image_path:
            pixmap = QPixmap(image_path)
            label.setPixmap(pixmap.scaled(250, 250, Qt.KeepAspectRatio))

    def compare_action(self):
        planogram_path = self.planogram_combo.currentText()
        image_path = self.image_combo.currentText()
        if planogram_path and image_path:
            score = compare_images(planogram_path, image_path)
            QMessageBox.information(self, "Adherence Score", f"Adherence Score: {score:.2f}%")

if __name__ == "__main__":
    app = QApplication([])
    window = PlanogramComparatorGUI()
    window.show()
    app.exec_()
