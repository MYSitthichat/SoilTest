from PySide6.QtCore import QThread, Signal,QObject
import serial as ser

class ControllerLVDT(QThread,QObject):
    displace_xy_data = Signal(list)
    connect_serial_arduino_signal = Signal()

    def __init__(self):    
        super(ControllerLVDT, self).__init__()
        self.running = True
        self.ar_data = ""
        self.ar_x = ""
        self.ar_y = ""


    def run(self):
        while self.running:
            try:
                self.ar_data = (self.LVDT_serial.readline().decode('utf-8')).strip()
                if self.ar_data != "" :
                    if len(self.ar_data.split(",")) == 2: 
                        self.ar_data = self.ar_data.split(",")
                        self.ar_x = self.ar_data[1]
                        self.ar_y = self.ar_data[0]
                        self.disxy_data = [self.ar_x,self.ar_y]
                        self.displace_xy_data.emit(self.disxy_data)
                    else:
                        self.ar_data = ""
                else:
                    self.ar_data = ""
            except Exception as e:
                pass
            self.msleep(100)  

    def stop(self):
        self.running = False
        self.LVDT_serial.close()
        self.wait()
        
    
    def get_comport(self,LVDT_comport):
        self.LVDT_serial = ser.Serial(port=LVDT_comport, baudrate=9600, timeout=1)
        if self.LVDT_serial.is_open:
            self.connect_serial_arduino_signal.emit()
        else:
            print("Serial Arduino not connected")

