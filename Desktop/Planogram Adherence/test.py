import sys
import cv2
import torch
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QFileDialog, QMessageBox
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
from ultralytics import YOLO

class LocalImageDetectionApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Local Image Detection")
        self.setGeometry(100, 100, 500, 500)

        self.label = QLabel("Select an image:")
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)

        self.browse_button = QPushButton("Browse Image")
        self.detect_button = QPushButton("Run Detection")
        self.detect_button.setEnabled(False)  # Disable until an image is selected

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.image_label)
        layout.addWidget(self.browse_button)
        layout.addWidget(self.detect_button)
        self.setLayout(layout)

        self.browse_button.clicked.connect(self.browse_image)
        self.detect_button.clicked.connect(self.run_detection)

        self.model = YOLO("C:\\Users\\tednj\\runs\\detect\\train4\\weights\\best.pt")

        self.image_path = None

    def browse_image(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.jpg *.jpeg)")
        
        if file_path:
            self.image_path = file_path
            pixmap = QPixmap(file_path)
            self.image_label.setPixmap(pixmap.scaled(400, 400, Qt.KeepAspectRatio))
            self.detect_button.setEnabled(True)  # Enable detection button

    def run_detection(self):
        if self.image_path:
            output_path, detected_objects = self.detect_objects(self.image_path)

            if detected_objects:
                QMessageBox.information(self, "Detections", f"Detected Objects:\n{', '.join(detected_objects)}")
                self.display_detected_image(output_path)
            else:
                QMessageBox.information(self, "Detections", "No objects detected.")
        else:
            QMessageBox.warning(self, "Warning", "Please select an image first.")

    def detect_objects(self, image_path):
        detected_objects = set()
        image = cv2.imread(image_path)
        results = self.model(image)

        for result in results:
            for box in result.boxes.data:
                x1, y1, x2, y2, _, class_id = box.tolist()
                class_id = int(class_id)
                label = self.model.names[class_id]
                detected_objects.add(label)

                # Draw bounding box
                cv2.rectangle(image, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                cv2.putText(image, label, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Save the processed image
        output_path = "detected_image.jpg"
        cv2.imwrite(output_path, image)

        return output_path, list(detected_objects)

    def display_detected_image(self, image_path):
        pixmap = QPixmap(image_path)
        self.image_label.setPixmap(pixmap.scaled(400, 400, Qt.KeepAspectRatio))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LocalImageDetectionApp()
    window.show()
    sys.exit(app.exec_())
