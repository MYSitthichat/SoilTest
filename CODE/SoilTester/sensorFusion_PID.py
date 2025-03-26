import time
from threading import Thread
from simple_pid import PID  
from Controller.lvdtReader import lvdtReader
from Controller.loadcellReader import loadcellReader
import mysql.connector
from Controller.motorController import motorController


class sensorFusion():
    def __init__(self, lvdtReaderObj, loadcellReaderObj_Y, loadcellReaderObj_X, motory, motorx, computationInterval, K_target):
        
        self.K_target = K_target
        self.computationInterval = computationInterval
        
        self.lvdtReader = lvdtReaderObj
        self.loadcellReader1 = loadcellReaderObj_Y
        self.loadcellReader2 = loadcellReaderObj_X
        
        self.motorY = motory
        self.motorX = motorx
        
        self.Dx = 0
        self.Dy = 0
        self.previous_Dy = 0
        self.Fx = 0
        self.Fy = 0
        self.previous_Fy = 0
        
        self.Fy_target = 0
        self.Kn = 0

        self.lock_data_referanec = False
        self.referance_Dy = 0.0
        self.referance_Dx = 0.0
        
        # ตั้งค่า PID (ค่าที่ต้องปรับจูน)
        self.pid = PID(Kp=4.0, Ki=0.5, Kd=0.1, setpoint=0)
        self.pid.output_limits = (-1000, 1000)  # จำกัดค่าความเร็วระหว่าง -90 ถึง 90

        # Start the threads
        self.sensorThread = Thread(target=self.collect_data, args=())
        self.sensorThread.start()
        
    def connect_to_sensor(self,lvdt_port,loadcell_port,loadcell_portx,motor_portx,motor_porty):
        print(f"lvdt_port: {lvdt_port}, loadcell_port: {loadcell_port}, loadcell_portx: {loadcell_portx}, motor_portx: {motor_portx}, motor_porty: {motor_porty}")

    
    def collect_data(self):
        while True:
            try:
                self.Dy, self.Dx = self.lvdtReader.get_data()
                self.Fx = self.loadcellReader2.get_data()
                self.Fy = self.loadcellReader1.get_data()
                self.Dy = float(self.Dy)
                self.Dy = round(self.Dy, 4)
                self.Dx = float(self.Dx)
                self.Dx = round(self.Dx, 4)
                
                
                if not self.lock_data_referanec and self.Dx != 0 and self.Dy != 0:
                    self.referance_Dy = self.Dy
                    self.referance_Dx = self.Dx
                    self.lock_data_referanec = True

                self.Dy -= self.referance_Dy
                self.Dy = round(self.Dy, 4)
                self.Dx -= self.referance_Dx
                self.Dx = round(self.Dx, 4)

                self.Fy = round(float(self.Fy) * 0.0098 / 0.0036, 4)
                self.Fx = round(float(self.Fx) * 0.0098 / 0.0036, 4)

                self.Kn = round((self.Fy - self.previous_Fy) / (self.Dy - self.previous_Dy), 4) if (self.Dy - self.previous_Dy) != 0 else 0
                self.Fy_target = round((self.Dy - self.previous_Dy) * self.K_target + self.previous_Fy, 4)

            except ZeroDivisionError:
                pass
            
            self.previous_Dy = self.Dy
            self.previous_Fy = self.Fy
            
            time.sleep(self.computationInterval)
            
    def get_data(self):
        return self.Dx, self.Dy, self.Fx, self.Fy, self.Kn, self.Fy_target
    
    def control_motor_Y(self):
        error = self.Fy_target - self.Fy
        speed_adjustment = self.pid(error)
        speed_adjustment = round(speed_adjustment, 4)

        if speed_adjustment > 0:
            self.motorY.set_direction(1)  # หมุนขึ้น
        else:
            self.motorY.set_direction(0)  # หมุนลง

        speed = max(200, min(abs(speed_adjustment), 900))  # จำกัดช่วงความเร็ว
        speed = round(speed, 4)
        print(f'speed: {speed} speed_adjustment: {speed_adjustment}')
        self.motorY.set_speed(speed)

        if speed > 20:
            self.motorY.start_motor()
        else:
            self.motorY.stop_motor()

class database():
    def __init__(self):
        self.connection = self.connect_to_database()
        
    def connect_to_database(self):
        try:
            connection = mysql.connector.connect(
                host='localhost',
                user='soiltester',
                password='111777000',
                database='soil_tester'
            )
            if connection.is_connected():
                print("Successfully connected to the database")
                return connection
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return None

    def close_connection(self):
        if self.connection.is_connected():
            self.connection.close()
            print("Database connection closed")
            
    def insert_data(self, Dx, Dy, Fx, Fy, Kn, Fy_target):
        cursor = self.connection.cursor()
        query = "INSERT INTO results (Dx, Dy, Fx, Fy, Kn,Fy_target ) VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.execute(query, (Dx, Dy, Fx, Fy, Kn, Fy_target))
        self.connection.commit()
        cursor.close()
        
    def get_data(self):
        cursor = self.connection.cursor()
        query = "SELECT * FROM results"
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
        return data
    
    def update_data(self, Dx, Dy, Fx, Fy, Kn, Fy_target):
        cursor = self.connection.cursor()
        query = "UPDATE results SET Dx = %s, Dy = %s, Fx = %s, Fy = %s, Kn = %s, Fy_target = %s"
        cursor.execute(query, (Dx, Dy, Fx, Fy, Kn, Fy_target))
        self.connection.commit()
        cursor.close()
        
    def delete_data(self):
        cursor = self.connection.cursor()
        query = "DELETE FROM results"
        cursor.execute(query)
        self.connection.commit()
        cursor.close()
        
    def __del__(self):
        self.close_connection()
        


if __name__ == '__main__':
    lvdtReaderObj = lvdtReader('COM10', 115200)
    loadcellReaderObj_Y = loadcellReader('COM17', 115200)
    loadcellReaderObj_X = loadcellReader('COM15', 115200)
    motorControllerX = motorController('COM12', 115200)
    motorControllerY = motorController('COM16', 115200)
    con_to_bass = database()
    
    sensorFusion = sensorFusion(lvdtReaderObj, loadcellReaderObj_Y, loadcellReaderObj_X, motorControllerY, motorControllerX, computationInterval=1, K_target=2500)
    
    motorControllerX.connect()
    time.sleep(0.1)
    motorControllerY.connect()
    time.sleep(3)
    motorControllerX.set_direction(1)
    time.sleep(0.1)
    motorControllerX.set_speed(90)
    time.sleep(0.1)
    motorControllerX.start_motor()

    for i in range(500):
        sensorFusion.control_motor_Y()

        Dx, Dy, Fx, Fy, Kn, Fy_target = sensorFusion.get_data()
        con_to_bass.insert_data(Dx, Dy, Fx, Fy, Kn, Fy_target)

        time.sleep(1)
        print(f'Dx: {Dx}, Dy: {Dy}, Fx: {Fx}, Fy: {Fy}, Kn: {Kn}, Fy_target: {Fy_target}')

    motorControllerY.stop_motor()
    time.sleep(0.1)
    motorControllerX.stop_motor()
    time.sleep(0.1)
    motorControllerY.disconnect()
    time.sleep(0.1)
    motorControllerX.disconnect()
