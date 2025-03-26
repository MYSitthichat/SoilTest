import serial
from threading import Thread
import time

class loadcellReader():
    def __init__(self,):  # read_interval: time interval between
        self.data_buffer = []
        self.data_buffer.append(0)
        # self.connect()
        self.start_func = False
    
    def connect(self, port, baudrate):
        self.port = port
        self.baudrate = baudrate
        self.ser = serial.Serial(port=self.port, baudrate=self.baudrate)
        if self.ser.is_open:
            self.ser.close()
        try:
            self.ser.open()
            self.ser.flushInput()
            self.ser.flushOutput()
            self.ser.flush()
            self.start_func = True
            # start timer
            self.read_timer = Thread(target=self.read_data, args=())
            self.read_timer.start()
            
            return True
        except Exception as e:
            print('Error connecting to load cell reader123')
            print(f"llll{e}")
            return False
        
    def disconnect(self):
        self.start_func = False
        try:
            if self.read_timer.is_alive():
                self.read_timer.join(timeout=1)
            self.ser.close()
        except Exception as e:
            print(f"loadcell{e}")

    def check_connection(self):
        return self.ser.is_open
    
    def read_data(self):
        time.sleep(0.8)
        while True:
            if self.start_func == True:
                data = self.ser.readline().decode('utf-8').strip()
                self.data_buffer.append(data)
                
                if len(self.data_buffer) > 10:
                    self.data_buffer.pop(0)
            else:
                break
                    
    def get_data(self):
        return self.data_buffer[-1]
        

if __name__ == '__main__':
    reader = loadcellReader()
    reader.connect('COM17', 115200)
    while True:
        print(reader.get_data())
        time.sleep(1)