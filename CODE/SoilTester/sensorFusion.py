import time
from threading import Thread
from lvdtReader import lvdtReader
from loadcellReader import loadcellReader
import mysql.connector
import matplotlib.pyplot as plt
from motorController import motorController


class sensorFusion():
    def __init__(self, lvdtReaderObj, loadcellReaderObj_Y, loadcellReaderObj_X, motory, motorx,computationInterval, K_target):
        
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
        self.previous_Fy = 0
        
        self.Fy_target = 0
        
        self.Kn = 0
        
        self.lock_data_referanec = False
        self.referance_Dy = 0.0
        self.referance_Dx = 0.0
        
        # Start the threads
        self.sensorThread = Thread(target=self.collect_data, args=())
        self.sensorThread.start()
        
    def collect_data(self):
        while True:
            try:
                self.Dy,self.Dx = lvdtReaderObj.get_data()
                self.Fx = loadcellReaderObj_X.get_data()
                self.Fy = loadcellReaderObj_Y.get_data()
                self.Dy = float(self.Dy)
                self.Dx = float(self.Dx)
                # print('Dx:', self.Dx, 'Dy:', self.Dy)
                # =============================== set zero point ================================
                if(self.Dx != 0 and self.Dy != 0):
                    if self.lock_data_referanec == False:
                        self.referance_Dy = self.Dy
                        self.referance_Dx = self.Dx
                        self.lock_data_referanec = True
                self.Dy = self.Dy - self.referance_Dy
                self.Dx = self.Dx - self.referance_Dx
                self.Dy = round(self.Dy, 4)
                self.Dx = round(self.Dx, 4)
                
                # =============================== convert ================================
                self.Fy = float(self.Fy)
                self.Fy = float(self.Fy * 0.0098) # convert to Newton
                self.Fy = (self.Fy/0.0036) # convert to kPa
                self.Fy = round(self.Fy, 4)
                # =============================== convert ================================
                self.Fx = float(self.Fx)
                self.Fx = float(self.Fx * 0.0098)
                self.Fx = (self.Fx/0.0036) # convert to kPa
                self.Fx = round(self.Fx, 4)
                
                self.Kn = (float(self.Fy) - float(self.previous_Fy)) / (float(self.Dy) - float(self.previous_Dy))
                self.Kn = round(self.Kn, 4)
                
                self.Fy_target = (float(self.Dy) - float(self.previous_Dy)) * self.K_target + float(self.previous_Fy)
                self.Fy_target = round(self.Fy_target, 4)
                
            except ZeroDivisionError:
                pass
            
            self.previous_Dy = self.Dy
            self.previous_Fy = self.Fy
            
            time.sleep(self.computationInterval)
            
        
    def get_data(self):
        return self.Dx, self.Dy, self.Fx, self.Fy, self.Kn, self.Fy_target
    
    def update_data_to_database(self):
        pass 
# =============================== motor y ================================

    def check_connection_in_MY(self):
        self.motorY.check_connection()

    def connect_mY(self):
        self.motorY.connect()
    
    def disconnect_mY(self):
        self.motorY.disconnect()
    
    def move_motor_Y(self):
        self.motorY.start_motor()

    def stop_motor_Y(self):
        self.motorY.stop_motor()

    def set_motory_speed(self, speed):
        self.motorY.set_speed(speed)
    
    def up_motor_Y(self):
        self.motorY.set_direction(1)
        
    def down_motor_Y(self):
        self.motorY.set_direction(0)

# =============================== motor x =================================

    def check_connection_in_MX(self):
        self.motorX.check_connection()
        
    def connect_mX(self):
        self.motorX.connect()
        
    def disconnect_mX(self):
        self.motorX.disconnect()
        
    def move_motor_X(self):
        self.motorX.start_motor()
        
    def stop_motor_X(self):
        self.motorX.stop_motor()
    
    def set_motorx_speed(self, speed):
        self.motorX.set_speed(speed)
        
    def in_motor_X(self):
        self.motorX.set_direction(1)
        
    def out_motor_X(self):
        self.motorX.set_direction(0)


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
    
    sensorFusion = sensorFusion(lvdtReaderObj, loadcellReaderObj_Y, loadcellReaderObj_X, motorControllerY, motorControllerX,computationInterval=1, K_target=500)
    
    # while True:
    
    sensorFusion.connect_mY()
    time.sleep(0.1)
    sensorFusion.connect_mX()
    time.sleep(3)
    sensorFusion.set_motory_speed(50)
    time.sleep(0.1)
    sensorFusion.set_motorx_speed(100)
    time.sleep(0.1)
    sensorFusion.move_motor_Y()
    time.sleep(0.1)
    sensorFusion.move_motor_X()
    time.sleep(0.1)
    sensorFusion.in_motor_X()
    time.sleep(0.1)
    
    # Fy == 300 kPa
    
    for i in range(500):

        Dx, Dy, Fx, Fy, Kn, Fy_target = sensorFusion.get_data()
        Fy = float(Fy)
        Fy_target = float(Fy_target)
        

        if Fy < Fy_target:
            sensorFusion.down_motor_Y()
        if Fy > Fy_target:
            sensorFusion.up_motor_Y()
        else:
            pass
        
        con_to_bass.insert_data(Dx, Dy, Fx, Fy, Kn, Fy_target)
        time.sleep(1)
        print('Dx:', Dx, 'Dy:', Dy, 'Fx:', Fx, 'Fy:', Fy, 'Kn:', Kn, 'Fy_target:', Fy_target)
    
    print("success")
    sensorFusion.stop_motor_Y()
    time.sleep(0.1)
    sensorFusion.stop_motor_X()
    time.sleep(0.1)
    sensorFusion.disconnect_mY()
    time.sleep(0.1)
    sensorFusion.disconnect_mX()