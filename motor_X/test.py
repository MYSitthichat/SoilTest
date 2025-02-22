import serial
import time

rounds = 0

# Configure the serial port
ser = serial.Serial('COM13', 115200, timeout=1) #x
ser2 = serial.Serial('COM16', 115200, timeout=1) #y

time.sleep(2)
print(f"ser x{ser.is_open} ===== ser y{ser2.is_open}")
time.sleep(1)
ser.write(b'r,1\n')
time.sleep(0.5)
ser2.write(b'r,1\n')

speed_list = [60,70,80]

for speed in speed_list:
    ser.write(b's,'+str(speed).encode()+b'\n')
    ser2.write(b's,'+str(speed).encode()+b'\n')
    for i in range(60):
        # forward
        ser.write(b'd,1\n')
        time.sleep(0.5)
        ser2.write(b'd,1\n')
        time.sleep(5)
        # reward
        ser.write(b'd,0\n')
        time.sleep(0.5)
        ser2.write(b'd,0\n')
        time.sleep(5)
        rounds += 1
        print(f"Round {rounds} = {rounds*10} seconds")

ser.write(b'r,0\n')
ser2.write(b'r,0\n')
time.sleep(3)
ser.close()
ser2.close()
