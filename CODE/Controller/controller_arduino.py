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
        self.m_up_my = (b'm1\n')
        self.m_down_my = (b'm1r\n')
        self.stop_my = (b'm1s\n')
        self.m_in_mx = (b'm2\n')
        self.m_out_mx = (b'm2r\n')
        self.stop_mx = (b'm2s\n')
        self.stop_all_m = (b'm1s\n'+b'm2s\n')


    def run(self):
        while self.running:
            try:
                self.ar_data = (self.arduino_serial.readline().decode('utf-8')).strip()
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
        self.arduino_serial.close()
        self.wait()
        
    
    def get_comport(self,Arduino_comport):
        self.arduino_serial = ser.Serial(port=Arduino_comport, baudrate=9600, timeout=1)
        if self.arduino_serial.is_open:
            self.connect_serial_arduino_signal.emit()
        else:
            print("Serial Arduino not connected")
    # ====================== Y ======================
    def up_motors_y(self):
        self.arduino_serial.write(self.m_up_my)
        
    def down_motors_y(self):
        self.arduino_serial.write(self.m_down_my)
    
    def stop_motors_y(self):
        self.arduino_serial.write(self.stop_my)
    # ====================== X ======================
    def in_motors_x(self):
        self.arduino_serial.write(self.m_in_mx)
    
    def out_motors_x(self):
        self.arduino_serial.write(self.m_out_mx)
    
    def stop_motors_x(self):
        self.arduino_serial.write(self.stop_mx)
    # ====================== SA ======================
    def stop_all_motors(self):
        self.arduino_serial.write(self.stop_all_m)
    # ==============================================
        
    

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