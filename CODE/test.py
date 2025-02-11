from PySide6.QtWidgets import QApplication, QMessageBox, QPushButton, QWidget, QVBoxLayout
from PySide6.QtCore import QThread, Signal
import sys
import time

class Worker(QThread):
    show_message = Signal(str)  # สร้าง Signal สำหรับส่งข้อความไปยังเธรดหลัก

    def run(self):
        time.sleep(2)  # จำลองการทำงานหนัก
        self.show_message.emit("งานเสร็จแล้ว!")  # ส่งสัญญาณไปที่เมธอดในเธรดหลัก

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Thread Message Box Example (PySide6)")
        self.setGeometry(100, 100, 300, 200)

        self.button = QPushButton("เริ่มงาน", self)
        self.button.clicked.connect(self.start_thread)

        layout = QVBoxLayout()
        layout.addWidget(self.button)
        self.setLayout(layout)

        self.worker = Worker()
        self.worker.show_message.connect(self.show_message_box)  # เชื่อมสัญญาณไปที่ฟังก์ชัน

    def start_thread(self):
        self.worker.start()

    def show_message_box(self, message):
        QMessageBox.information(self, "แจ้งเตือน", message)  # แสดง MessageBox อย่างปลอดภัยในเธรดหลัก

app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())
