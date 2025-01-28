from PySide6.QtCore import QThread, Signal,QObject
import serial as ser
import time

class ControllerArduino(QThread,QObject):
    displace_xy_data = Signal(list)
    connect_serial_arduino_signal = Signal()
        
    def __init__(self):    
        super(ControllerArduino, self).__init__()
        self.running = True
        self.ar_data = ""
        self.ar_x = ""
        self.ar_y = ""

        
    def run(self):
        while self.running:
            self.ar_data = self.arduino_serial.readline().decode('utf-8').strip()
            if self.ar_data != "":
                if len(self.ar_data.split(",")) == 2: 
                    self.ar_data = self.ar_data.split(",")
                    self.ar_x = self.ar_data[0]
                    self.ar_y = self.ar_data[1]
                    self.disxy_data = [self.ar_x,self.ar_y]
                    self.displace_xy_data.emit(self.disxy_data)
                else:
                    pass
            else:
                pass
            self.msleep(100)  
            

    def stop(self):
        self.running = False
        self.arduino_serial.close()
        self.wait()
        
    
    def get_comport(self,Arduino_comport):
        self.arduino_serial = ser.Serial(port=Arduino_comport, baudrate=9600, timeout=1)
        if self.arduino_serial.is_open:
            self.connect_serial_arduino_signal.emit()
        else:
            print("Serial Arduino not connected")
        

    

