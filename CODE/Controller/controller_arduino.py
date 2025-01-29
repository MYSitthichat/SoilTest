from PySide6.QtCore import QThread, Signal,QObject
import serial as ser

class ControllerArduino(QThread,QObject):
    displace_xy_data = Signal(list)
    connect_serial_arduino_signal = Signal()
        
    def __init__(self):    
        super(ControllerArduino, self).__init__()
        self.running = True
        self.ar_data = ""
        self.ar_x = ""
        self.ar_y = ""
        self.start_my = (b'm1')
        self.stop_my = (b'm1s')
        self.start_mx = (b'm2')
        self.stop_mx = (b'm2s')

        
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
        
    def start_motors_y(self):
        print(self.start_my)
        self.arduino_serial.write(self.start_my)
        print("Motor 1 started")
        
    def start_motors_x(self):
        self.arduino_serial.write(b'm2')
    
    def stop_motors_y(self):
        self.arduino_serial.write(b'm1s')
        print("Motor 1 stopped")
    
    def stop_motors_x(self):
        self.arduino_serial.write(b'm2s')
        
    def stop_all_motors(self):
        self.arduino_serial.write(b'STOP_ALL')
        
    

# help          - Display this help message
# m1            - Start Motor 1 clockwise
# m1r           - Start Motor 1 counterclockwise
# m1s           - Stop Motor 1
# m2            - Start Motor 2 clockwise
# m2r           - Start Motor 2 counterclockwise
# m2s           - Stop Motor 2
# m1vX          - Set Motor 1 speed (X = 0-5)
# m2vX          - Set Motor 2 speed (X = 0-5)
#   m1m2  : Start Motor 1 and Motor 2 clockwise
#   m1m2r : Start Motor 1 and Motor 2 counterclockwise
#   m1m2s : Stop Motor 1 and Motor 2
# STOP_ALL      - Stop all motors
# STOP_READING  - Stop distance measurement
# START_READING - Start distance measurement
# d1            - Send 'd1' to Slave and wait for response. Send 'idl' if response is received.