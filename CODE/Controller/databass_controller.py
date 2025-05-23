import os
import sqlite3
from PySide6.QtCore import Signal,QObject

directory = "DATABASS"
db_path = r'DATABASS/CT.db'

class DatabassController(QObject):
    list_for_parameter = Signal(list)
    def __init__(self):    
        super(DatabassController, self).__init__()
        

    def create_databass(self):
        try:
            if not os.path.exists(directory):
                    os.makedirs(directory)
                    conn = sqlite3.connect(r'DATABASS/CT.db')
            if os.path.isfile(db_path):
                self.check_all_table()
            else:
                    conn = sqlite3.connect(r'DATABASS/CT.db')
        except OSError:
            print("Error Create Folder")
    
    def check_all_table(self):
        self.check_table_setting()
        self.check_table_offset()
        
# ======================================= tabel offset =======================================
        
    def check_table_offset(self):
        print("check table offset")
        conn = sqlite3.connect(r'DATABASS/CT.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='OFFSET';")
        table_exists = cursor.fetchone()
        if table_exists:
            pass
        else:
            self.create_table_offset()
        conn.close()
    
    def create_table_offset(self):
        conn = sqlite3.connect(r'DATABASS/CT.db')
        conn.execute('''CREATE TABLE OFFSET
            (ID INT PRIMARY KEY     NOT NULL,
            OFFSET_X                INT    NOT NULL,
            OFFSET_Y                INT    NOT NULL);''')
        conn.close()
    
    def check_record_offset(self):
        conn = sqlite3.connect(r'DATABASS/CT.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM OFFSET")
        record_exists = cursor.fetchone()
        if record_exists:
            print("record offset exists")
        else:
            self.insert_defualt_record_offset()
            print("insert record offset to default")
        conn.close()
    
    def insert_defualt_record_offset(self):
        conn = sqlite3.connect(r'DATABASS/CT.db')
        conn.execute("INSERT INTO OFFSET (ID,OFFSET_X,OFFSET_Y) VALUES (1,0,0);")
        conn.commit()
        conn.close()
    
    def read_offset_to_ui(self):
        conn = sqlite3.connect(r'DATABASS/CT.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM OFFSET WHERE ID = (SELECT MAX(ID) FROM OFFSET);")
        offset_record = cursor.fetchone()
        return offset_record
    
    def insert_offset_to_databass(self,offset_x,offset_y):
        conn = sqlite3.connect(r'DATABASS/CT.db')
        conn.execute("INSERT INTO OFFSET (ID, OFFSET_X, OFFSET_Y) VALUES ((SELECT IFNULL(MAX(ID), 0) + 1 FROM OFFSET), ?, ?);", (offset_x, offset_y))
        conn.commit()
        conn.close()
    
    # ======================================= tabel setting =======================================
    def check_table_setting(self):
        conn = sqlite3.connect(r'DATABASS/CT.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='SETTING';")
        table_exists = cursor.fetchone()
        if table_exists:
            pass
        else:
            self.create_table_setting()
        conn.close()
    
    def create_table_setting(self):
        conn = sqlite3.connect(r'DATABASS/CT.db')
        conn.execute('''CREATE TABLE SETTING
            (ID INT PRIMARY KEY     NOT NULL,
            PWM_X                INT    NOT NULL,
            PWM_Y                INT    NOT NULL,
            LIMIT_WEIGHT_X       INT    NOT NULL,
            LIMIT_WEIGHT_Y       INT    NOT NULL,
            LIMIT_DISTANCE_X     INT    NOT NULL,
            LIMIT_DISTANCE_Y     INT    NOT NULL,
            AREA_TEST            INT    NOT NULL);''')
        conn.close() 
        
    def check_record_setting(self):
        conn = sqlite3.connect(r'DATABASS/CT.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM SETTING")
        record_exists = cursor.fetchone()
        if record_exists:
            self.read_parameter_to_setting()
        else:
            self.insert_defualt_record_setting()
            print("insert record setting to default")
        conn.close()
    
    def insert_defualt_record_setting(self):
        conn = sqlite3.connect(r'DATABASS/CT.db')
        conn.execute("INSERT INTO SETTING (ID,PWM_X,PWM_Y,LIMIT_WEIGHT_X,LIMIT_WEIGHT_Y,LIMIT_DISTANCE_X,LIMIT_DISTANCE_Y,AREA_TEST) VALUES (1,0,0,0,0,0,0,0);")
        conn.commit()
        conn.close()
    
    def set_parameter_to_setting(self,pwmx,pwmy,limit_weight_x,limit_weight_y,limit_distance_x,limit_distance_y,area_test):
        conn = sqlite3.connect(r'DATABASS/CT.db')
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(ID) FROM SETTING;")
        highest_id = cursor.fetchone()[0]
        if highest_id:
            ids = str(highest_id+1)
            cursor.execute("INSERT INTO SETTING (ID,PWM_X,PWM_Y,LIMIT_WEIGHT_X,LIMIT_WEIGHT_Y,LIMIT_DISTANCE_X,LIMIT_DISTANCE_Y,AREA_TEST) VALUES (?,?,?,?,?,?,?,?);",(ids,pwmx,pwmy,limit_weight_x,limit_weight_y,limit_distance_x,limit_distance_y,area_test))
            conn.commit()
            conn.close()
        else:
            print("No New setting")
            conn.close()
    
    def read_parameter_to_setting(self):
        conn = sqlite3.connect(r'DATABASS/CT.db')
        cursor = conn.cursor()
        cursor.execute("SELECT ID FROM SETTING WHERE ID > 1;")
        ids = cursor.fetchall()
        if ids:
            cursor.execute("SELECT * FROM SETTING WHERE ID = (SELECT MAX(ID) FROM SETTING);")
            self.setting_record = cursor.fetchall()
            # print(f"Record:{setting_record}")
            # self.list_for_parameter.emit(setting_record)
        else:
            cursor.execute("SELECT * FROM SETTING WHERE ID = 1;")
            self.setting_record = cursor.fetchone()
            # print(f"Default record:{setting_record}")
            # self.list_for_parameter.emit(setting_record)
        return self.setting_record
            

    

