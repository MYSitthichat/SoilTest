import serial
from threading import Thread
import time

class loadcellReader():
    def __init__(self, port, baudrate, read_interval=0.1):  # read_interval: time interval between
        self.port = port
        self.baudrate = baudrate
        self.ser = serial.Serial()
        self.ser.port = self.port
        self.ser.baudrate = self.baudrate
        self.data_buffer = []
        self.connect()
    
    def connect(self):
        try:
            self.ser.open()
            # print(self.ser.is_open)
            self.ser.flushInput()
            self.ser.flushOutput()
            self.ser.flush()
            # print('Connected to load cell reader')
            
            # start timer
            self.read_timer = Thread(target=self.read_data, args=())
            self.read_timer.start()
            
            return True
        except Exception as e:
            print('Error connecting to load cell reader')
            print(e)
            return False
        
    def read_data(self):
        while True:
            data = self.ser.readline().decode('utf-8').strip()
            self.data_buffer.append(data)
            
            if len(self.data_buffer) > 10:
                self.data_buffer.pop(0)
                
                
    def get_data(self):
        avg = 100
        if len(self.data_buffer) >= 10:
            # find average of last 10 readings
            avg = sum([float(i) for i in self.data_buffer]) / len(self.data_buffer)
            avg = round(avg, 4)
        else:
            avg = 0
        return avg
        
        
# if __name__ == '__main__':
#     reader = loadcellReader('COM17', 9600, 1)
#     reader.connect()
#     while True:
#         print(reader.get_data())
#         time.sleep(1)