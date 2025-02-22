import time
from threading import Thread
from lvdtReader import lvdtReader
from loadcellReader import loadcellReader
import mysql.connector
import matplotlib.pyplot as plt


class sensorFusion():
    def __init__(self, lvdtReaderObj, loadcellReaderObj_Y, loadcellReaderObj_X,computationInterval):
        
        self.computationInterval = computationInterval
        
        self.lvdtReader = lvdtReaderObj
        self.loadcellReader1 = loadcellReaderObj_Y
        self.loadcellReader2 = loadcellReaderObj_X
        
        self.Dx = 0
        self.Dy = 0
        self.Fx = 0
        self.Fy = 0
        old_Fy = 0
        
        self.Kn = 0
        
        # Start the threads
        self.sensorThread = Thread(target=self.collect_data, args=())
        self.sensorThread.start()
        
        # Start the computation thread
        self.computationThread = Thread(target=self.compute_Kn, args=())
        self.computationThread.start()
        
    def collect_data(self):
        while True:
            self.Dy,self.Dx = lvdtReaderObj.get_data()
            
            if type(self.Dy) != float or type(self.Dx) != float:
                print(self.Dx, self.Dy)
                
            self.Fx = loadcellReaderObj_X.get_data()
            self.Fy = loadcellReaderObj_Y.get_data()
            time.sleep(0.1)
            
    def compute_Kn(self):
        while True:
            old_dis_y = getattr(self, 'old_dis_y', 0.0)
            old_fy = getattr(self, 'old_fy', 0.0)
            new_Fy = self.Fy
            new_Dy = self.Dy
            try:
                self.Kn = (new_Fy - old_fy) / (new_Dy - old_dis_y)
                self.Kn = round(self.Kn, 4)
            except ZeroDivisionError:
                pass
            self.old_dis_y = new_Dy
            self.old_fy = new_Fy

            time.sleep(self.computationInterval)

        
    def get_data(self):
        return self.Dx, self.Dy, self.Fx, self.Fy, self.Kn
    
    def update_data_to_database(self):
        pass 
    
    
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
            
    def insert_data(self, Dx, Dy, Fx, Fy, Kn):
        cursor = self.connection.cursor()
        query = "INSERT INTO results (Dx, Dy, Fx, Fy, Kn) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(query, (Dx, Dy, Fx, Fy, Kn))
        self.connection.commit()
        cursor.close()
        
    def get_data(self):
        cursor = self.connection.cursor()
        query = "SELECT * FROM results"
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
        return data
    
    def update_data(self, Dx, Dy, Fx, Fy, Kn):
        cursor = self.connection.cursor()
        query = "UPDATE results SET Dx = %s, Dy = %s, Fx = %s, Fy = %s, Kn = %s"
        cursor.execute(query, (Dx, Dy, Fx, Fy, Kn))
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
    loadcellReaderObj_Y = loadcellReader('COM17', 9600)
    loadcellReaderObj_X = loadcellReader('COM15', 9600)
    con_to_bass = database()
    
    sensorFusion = sensorFusion(lvdtReaderObj, loadcellReaderObj_Y, loadcellReaderObj_X,computationInterval=1)
    for i in range(100):
        Dx, Dy, Fx, Fy, Kn = sensorFusion.get_data()
        con_to_bass.insert_data(Dx, Dy, Fx, Fy, Kn)
        # print('Dx:', Dx, 'Dy:', Dy, 'Fx:', Fx, 'Fy:', Fy, 'Kn:', Kn)
        time.sleep(1)