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

class PlanogramUploaderGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Planogram Uploader")
        self.setGeometry(100, 100, 400, 150)

        self.label = QLabel("Planogram Path:")
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

        self.browse_button.clicked.connect(self.browse_planogram)
        self.upload_button.clicked.connect(self.upload_planogram)

        self.selected_file = None

    def browse_planogram(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Planogram", "", "All Files (*)", options=options)
        
        if file_path:
            self.selected_file = file_path
            self.text_field.setText(file_path)

    def upload_planogram(self):
        if self.selected_file:
            conn = get_database_connection()
            if conn:
                try:
                    cursor = conn.cursor()
                    query = "INSERT INTO planogram (file_name, file_path, uploaded_at) VALUES (%s, %s, NOW())"
                    values = (os.path.basename(self.selected_file), self.selected_file)
                    cursor.execute(query, values)
                    conn.commit()
                    QMessageBox.information(self, "Success", f"Planogram uploaded successfully: {os.path.basename(self.selected_file)}")
                except mysql.connector.Error as err:
                    QMessageBox.critical(self, "Error", f"Database error: {err}")
                finally:
                    conn.close()
        else:
            QMessageBox.warning(self, "Warning", "Please select a planogram first.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PlanogramUploaderGUI()
    window.show()
    sys.exit(app.exec_())
