from PySide6.QtCore import QThread, Signal,QObject
import serial as ser
import time

class Readloadcell(QThread,QObject):
    load_cell_data = Signal(list)
    connect_serial_XY_signal = Signal()
        
    def __init__(self):    
        super(Readloadcell, self).__init__()
        self.running = True
        self.y_data = ""
        self.x_data = ""

        
    def run(self):
        while self.running:
            self.y_data = self.loadcell_Y_serial.readline().decode('utf-8').strip()
            self.x_data = self.loadcell_X_serial.readline().decode('utf-8').strip()            
            load_cell_value = [self.y_data,self.x_data]
            self.load_cell_data.emit(load_cell_value)
            self.msleep(70)  
            

    def stop(self):
        self.running = False
        self.loadcell_Y_serial.close()
        self.loadcell_X_serial.close()
        self.wait()
        
    
    def get_comport(self,LY_comport,LX_comport):
        print(LY_comport,LX_comport)
        self.loadcell_Y_serial = ser.Serial(port=LY_comport,stopbits=1, bytesize=8, baudrate=9600, timeout=1)
        self.loadcell_X_serial = ser.Serial(port=LX_comport,stopbits=1, bytesize=8, baudrate=9600, timeout=1)
        if self.loadcell_Y_serial.is_open and self.loadcell_X_serial.is_open:
            self.connect_serial_XY_signal.emit()
        else:
            print("Serial not connected")
        

    

