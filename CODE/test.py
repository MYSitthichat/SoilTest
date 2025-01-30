import serial as ser
import time

arduino_serial = ser.Serial(port="COM10", baudrate=115200, timeout=1 ,bytesize = 8,parity = "N",stopbits = 1,)
time.sleep(2)
print(arduino_serial.is_open)
arduino_serial.flush()

print("Serial Arduino connected")
arduino_serial.write(b'm1\n')
print("Motor 1 started")
time.sleep(5)
arduino_serial.write(b'm1s\n')
print("Motor 1 stopped")
arduino_serial.close()
