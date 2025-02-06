from PySide6.QtCore import QThread, Signal,QObject
import serial as ser
import time

class ControllerMotor(QThread,QObject):
    displace_xy_data = Signal(list)
    connect_serial_motor_signal = Signal()

    def __init__(self):    
        super(ControllerMotor, self).__init__()
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
            self.connect_serial_motor_signal.emit()
            print(self.motor_serial.is_open)
        else:
            print("Serial Arduino not connected")
            
    # ====================== SET SPEED MOTOR ======================
    
    def get_setting_speed(self,speedx,speedy):
        speedx = int(speedx)
        speedy = int(speedy)
        try:
            if speedx > 100:
                speedx = 100
                speedx = str(speedx)
            if speedy > 100:
                speedy = 100
                speedy = str(speedy)
            speedx = str(speedx)
            speedy = str(speedy)
            self.set_speed_motor_x = (b'p1'+speedx.encode()+b'\n')
            self.set_speed_motor_y = (b'p2'+speedy.encode()+b'\n')
            # print(self.set_speed_motor_x)
            # print(self.set_speed_motor_y)
            self.motor_serial.write(self.set_speed_motor_x)
            time.sleep(0.5)
            self.motor_serial.write(self.set_speed_motor_y)
            time.sleep(0.5)
            self.stop_all_motors()
        except Exception as e:
            print(e)
            
    # ====================== Y ======================
    def up_motors_y(self):
        self.motor_serial.write(self.m_up_my)
        
    def down_motors_y(self):
        self.motor_serial.write(self.m_down_my)
    
    def stop_motors_y(self):
        self.motor_serial.write(self.stop_my)
    # ====================== X ======================
    def in_motors_x(self):
        self.motor_serial.write(self.m_in_mx)
    
    def out_motors_x(self):
        self.motor_serial.write(self.m_out_mx)
    
    def stop_motors_x(self):
        self.motor_serial.write(self.stop_mx)
    # ====================== SA ======================
    def stop_all_motors(self):
        self.motor_serial.write(self.stop_all_m)
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