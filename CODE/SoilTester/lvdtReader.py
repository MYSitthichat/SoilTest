import serial
from threading import Thread
import time
import statistics

class lvdtReader():
    def __init__(self, port, baudrate, read_interval=0.8):  # read_interval: time interval between
        self.port = port
        self.baudrate = baudrate
        # set up serial connection
        self.ser = serial.Serial()
        self.ser.port = self.port
        self.ser.baudrate = self.baudrate
        
        self.readInterval = read_interval
        
        self.xData_buffer = []
        self.yData_buffer = []
        self.connect()
    
    def connect(self):
        try:
            self.ser.open()
            self.ser.flushInput()
            self.ser.flushOutput()
            self.ser.flush()
            # print('Connected to load cell reader')
            
            # start timer
            self.read_timer = Thread(target=self.read_data, args=())
            self.read_timer.start()
            
            return True
        except Exception as e:
            print('Error connecting to load cell reader123')
            print(e)
            return False
        
    def check_connection(self):
        return self.ser.is_open

    def read_data(self):
        while True:
            time.sleep(self.readInterval)
            try:
                data = self.ser.readline().decode('utf-8').strip()
                # if , in data, split data by comma
                if ',' in data:
                    data = data.split(',')
                    
                    # convert data to float
                    data[0] = float(data[0])
                    data[1] = float(data[1])
                    self.xData_buffer.append(data[0])
                    self.yData_buffer.append(data[1])
                    
                    # check list length
                    if len(self.xData_buffer) > 3:
                        self.xData_buffer.pop(0)

                    if len(self.yData_buffer) > 3:
                        self.yData_buffer.pop(0)
            except Exception as e:
                print(e)
                

    def get_data(self):
        if len(self.xData_buffer) >= 1:
            xAvg = sum([float(i) for i in self.xData_buffer]) / len(self.xData_buffer)
            xAvg = round(xAvg, 3)
        else:
            xAvg = 0
            
        if len(self.yData_buffer) >= 1:
            yAvg = sum([float(i) for i in self.yData_buffer]) / len(self.yData_buffer)
            yAvg = round(yAvg, 3)
        else:
            yAvg = 0
        return xAvg, yAvg
        
if __name__ == '__main__':
    reader = lvdtReader('COM10', 115200, 0.8)
    reader.connect()
    while True:
        print(reader.get_data())
        time.sleep(0.5)