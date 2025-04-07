import sys
import os
import mysql.connector
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QLineEdit, QFileDialog, QMessageBox

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
        print("Database connection error:", err)
        return None

class ImageUploaderGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Uploader")
        self.setGeometry(100, 100, 400, 150)

        self.label = QLabel("Image Path:")
        self.text_field = QLineEdit(self)
        self.text_field.setReadOnly(True)

        self.browse_button = QPushButton("Browse")
        self.upload_button = QPushButton("Upload")

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.text_field)
        layout.addWidget(self.browse_button)
        layout.addWidget(self.upload_button)
        self.setLayout(layout)

        self.browse_button.clicked.connect(self.browse_image)
        self.upload_button.clicked.connect(self.upload_image)

        self.selected_file = None

    def browse_image(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.jpg *.jpeg *.bmp *.gif);;All Files (*)", options=options)
        
        if file_path:
            self.selected_file = file_path
            self.text_field.setText(file_path)

    def upload_image(self):
        if self.selected_file:
            conn = get_database_connection()
            if conn:
                try:
                    cursor = conn.cursor()
                    query = "INSERT INTO images (filename, filepath, uploaded_at) VALUES (%s, %s, NOW())"
                    values = (os.path.basename(self.selected_file), self.selected_file)
                    cursor.execute(query, values)
                    conn.commit()
                    QMessageBox.information(self, "Success", f"Image uploaded successfully: {os.path.basename(self.selected_file)}")
                except mysql.connector.Error as err:
                    QMessageBox.critical(self, "Error", f"Database error: {err}")
                finally:
                    conn.close()
        else:
            QMessageBox.warning(self, "Warning", "Please select an image first.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageUploaderGUI()
    window.show()
    sys.exit(app.exec_())
