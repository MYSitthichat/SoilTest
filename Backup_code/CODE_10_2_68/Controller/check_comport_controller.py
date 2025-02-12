import serial.tools.list_ports
from PySide6.QtCore import QThread, Signal,QObject


class SerialPortChecker(QThread,QObject):
    ports_updated = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.running = True
        
    def run(self):
        previous_ports = []
        while self.running:
            current_ports = serial.tools.list_ports.comports()
            if current_ports != previous_ports:
                self.ports_updated.emit(current_ports)
                previous_ports = current_ports
            self.msleep(500)  

    def stop(self):
        self.running = False
        self.wait()
    

