import serial
import time

class motorController():
    def __init__(self):
        print("motor controller")
        
    def connect(self, comport, baudrate):
        self.ser = serial.Serial(port=comport, baudrate=baudrate)
        if self.ser.is_open:
            self.ser.close()
        try:
            self.ser.open()
            self.ser.flushInput()
            self.ser.flushOutput()
            self.ser.flush()
            return True
        except Exception as e:
            print('Error connecting to motor controller123')
            print(f"mmmm{e}")
            return False
        
    def disconnect(self):
        self.ser.close()
        
    def check_connection(self):
        return self.ser.is_open
        
    def start_motor(self):
        message = 'r,1\n'
        # print(message)
        self.ser.write(message.encode())
    
    def stop_motor(self):
        message = 'r,0\n'
        # print(message)
        self.ser.write(message.encode())
        
    def in_and_up(self):
        message = 'IU\n'
        # print(message)
        self.ser.write(message.encode())
        
    def out_and_down(self):
        message = 'OD\n'
        # print(message)
        self.ser.write(message.encode())
    
    def set_speed(self, speed):
        message = f's,{speed}\n'
        # print(message)
        self.ser.write(message.encode())
    
    def set_direction(self, direction):
        message = f'd,{direction}\n'
        # print(message)
        self.ser.write(message.encode())
        
if __name__ == '__main__':
    motorControllerObj = motorController('COM16', 115200)
    motorControllerObj.connect()
    time.sleep(5)
    
    if motorControllerObj.check_connection():
        print('Connected to motor controller')
        motorControllerObj.stop_motor()
        time.sleep(0.1)
        motorControllerObj.set_speed(100)
        time.sleep(0.1)
    else:
        print('Error connecting to motor controller')
    
    print('Starting motor')
    motorControllerObj.start_motor()
    time.sleep(0.1)
    for i in range(10):
        print(f'Loop {i}')
        motorControllerObj.set_direction(0)
        time.sleep(3)
        motorControllerObj.set_direction(1)
        time.sleep(3)
    
    motorControllerObj.stop_motor()
    