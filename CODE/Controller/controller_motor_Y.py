from PySide6.QtCore import QThread, Signal,QObject
import serial as ser
import time

class ControllerMotorY(QThread,QObject):
    connect_serial_motor_y_signal = Signal()

    def __init__(self):    
        super(ControllerMotorY, self).__init__()
        self.running = True
        self.ar_data = ""
        self.ar_x = ""
        self.ar_y = ""
        self.m_up_my = (b'm1\n')
        self.m_down_my = (b'm1r\n')
        self.stop_my = (b'm1s\n')


    def run(self):
        while self.running:
            try:
                pass
            except Exception as e:
                pass
            self.msleep(1000)  

    def stop(self):
        self.running = False
        self.motor_serial.close()
        self.wait()
        
    
    def get_comport(self,motor_comport):
        self.motor_serial = ser.Serial(port=motor_comport, baudrate=9600, timeout=1)
        if self.motor_serial.is_open:
            self.connect_serial_motor_y_signal.emit()
        else:
            print("Serial Arduino not connected")
            
    # ====================== SET SPEED MOTOR ======================
    
    def get_setting_speed(self,speedy):
        speedy = int(speedy)
        try:
            if speedy > 100:
                speedy = 100
                speedy = str(speedy)
            speedy = str(speedy)
            self.set_speed_motor_y = (b'p1'+speedy.encode()+b'\n')
            self.motor_serial.write(self.set_speed_motor_y)
            self.delay(1)
            self.stop_motors_y()
        except Exception as e:
            print(e)
        
        
    def delay(self,seconds):
        start_time = time.perf_counter()
        while time.perf_counter() - start_time < seconds:
            pass  # ทำงานอื่นต่อไปได้
            
    # ====================== Y ======================
    def up_motors_y(self):
        self.motor_serial.write(self.m_up_my)
        
    def down_motors_y(self):
        self.motor_serial.write(self.m_down_my)
    
    def stop_motors_y(self):
        self.motor_serial.write(self.stop_my)
    # ====================== X ======================
    


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