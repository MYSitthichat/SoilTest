from PySide6.QtCore import QObject , Slot , Signal
from view.view_main_frame import MainFrame
from Controller.check_comport_controller import SerialPortChecker
from Controller.lvdtReader import lvdtReader
from Controller.loadcellReader import loadcellReader
from Controller.motorController import motorController
from Controller.databass_controller import DatabassController
from PySide6.QtWidgets import QMessageBox,QFileDialog
import time
from simple_pid import PID
from threading import Thread
import csv




class MainController(QObject):
    show_message_info = Signal(str,str)
    show_message_error = Signal(str,str)
    calculate_k_every_time = Signal()
    runing_mono_test = Signal(float)
    clear_output_data_frame = Signal()
    
    def __init__(self):
        super(MainController, self).__init__()
        self.main_frame = MainFrame()
        self.check_port_controller = SerialPortChecker()
        self.loadcell_con_Y = loadcellReader()
        self.loadcell_con_X = loadcellReader()
        self.lvdt_con = lvdtReader()
        self.motor_con_x = motorController()
        self.motor_con_y = motorController()
        self.databass_controller = DatabassController()
        self.databass_controller.create_databass()
        self.databass_controller.check_record_setting()
        self.databass_controller.check_record_offset()
        self.show_parameter()
        self.main_frame.disable_manual_control()
        self.check_port_controller.start()
        self.main_frame.test_manual_control_checkBox.stateChanged.connect(self.check_manual_control)
        self.main_frame.set_offset_pushButton.clicked.connect(self.set_offset_pressed)
        self.main_frame.save_offset_pushButton.clicked.connect(self.save_offset_pressed)
        self.main_frame.set_zero_dx_pushButton.clicked.connect(self.set_zero_Dx_pressed)
        self.main_frame.set_zero_dy_pushButton.clicked.connect(self.set_zero_Dy_pressed)
        self.check_port_controller.ports_updated.connect(self.port_updated)
        self.main_frame.con_port_pushButton.clicked.connect(self.con_port_pressed)
        self.main_frame.test_pushButton.clicked.connect(self.show_test)
        self.main_frame.setting_pushButton.clicked.connect(self.show_setting)
        self.main_frame.calibrate_pushButton.clicked.connect(self.show_calibate)
        self.main_frame.home_pushButton.clicked.connect(self.Show_main)
        self.main_frame.dis_port_pushButton.clicked.connect(self.disconnect_port)
        self.show_message_info.connect(self.show_massege_box_info)
        self.main_frame.st_config_pushButton.clicked.connect(self.config_button_pressed)
        self.main_frame.st_save_pushButton.clicked.connect(self.save_button_pressed)
        self.main_frame.test_start_pushButton.clicked.connect(self.start_test)
        self.main_frame.test_stop_pushButton.clicked.connect(self.stop_test)
        self.main_frame.test_clear_pushButton.clicked.connect(self.clear_test)
        self.main_frame.test_save_pushButton.clicked.connect(self.save_test)
        self.main_frame.test_k_set_pushButton.clicked.connect(self.k_button_pressed)
        self.main_frame.m_in_pushButton.clicked.connect(self.motor_x_out)
        self.main_frame.m_out_pushButton.clicked.connect(self.motor_x_in)
        self.main_frame.m_up_pushButton.clicked.connect(self.motor_y_up)
        self.main_frame.m_down_pushButton.clicked.connect(self.motor_y_down)
        self.main_frame.m_stop_all_pushButton.clicked.connect(self.stop_motor_all)
        
        
        self.computationInterval = 1 # ความถี่ในการคำนวณ
        self.start_collect_data = False
        self.Dx = 0
        self.offset_dx = 0.0
        self.set_zero_dx_get_data = 0.0
        self.Dy = 0
        self.offset_dy = 0.0
        self.set_zero_dy_get_data = 0.0
        self.previous_Dy = 0
        self.Fx = 0
        self.Fy = 0
        self.previous_Fy = 0
        self.Fy_target = 0
        self.Kn = 0
        self.K_target = 0
        
        self.lock_data_referanec = False
        self.referance_Dy = 0.0
        self.referance_Dx = 0.0
        
        # ตั้งค่า PID (ค่าที่ต้องปรับจูน)
        self.pid = PID(Kp=4.0, Ki=0.5, Kd=0.1, setpoint=0)
        self.pid.output_limits = (-1000, 1000)  # จำกัดค่าความเร็วระหว่าง -90 ถึง 90
        
        # k button pressed =================================================================================================
        self.status_k_button = False
        # k button pressed =================================================================================================
        
        # monotonic test =================================================================================================
        self.start_loop_mono_test = False
        self.loop_mono_state = 0
        self.lock_export_data = True
        # monotonic test =================================================================================================
        self.start_up_programe()

    @Slot()
    @Slot(str)
    
    def set_zero_Dy_pressed(self):
        self.set_zero_dx_get_data = float(self.main_frame.test_dis_x_lineEdit.text())
        # self.set_zero_dy_get_data = float(self.Dy)
        # print(self.set_zero_dy_get_data)
    
    def set_zero_Dx_pressed(self):
        self.set_zero_dy_get_data = float(self.main_frame.test_dis_y_lineEdit.text())
        # self.set_zero_dx_get_data = float(self.Dx)
        # print(self.set_zero_dx_get_data)
    
    def set_offset_pressed(self):
        self.main_frame.dis_set_offset_x_lineEdit.setEnabled(True)
        self.main_frame.dis_set_offset_y_lineEdit.setEnabled(True)
        self.main_frame.save_offset_pushButton.setEnabled(True)
        self.main_frame.set_offset_pushButton.setEnabled(False)
        self.main_frame.save_offset_pushButton.setStyleSheet("background:rgb(255, 128, 130)")
        self.main_frame.set_offset_pushButton.setStyleSheet("background:gray")
        self.show_massege_box_info("SET OFFSET","You want to set offset ??")
        
    def save_offset_pressed(self):
        self.offset_dx_get = self.main_frame.dis_set_offset_x_lineEdit.text()
        self.offset_dy_get = self.main_frame.dis_set_offset_y_lineEdit.text()
        self.databass_controller.insert_offset_to_databass(self.offset_dx_get,self.offset_dy_get)
        self.main_frame.dis_set_offset_x_lineEdit.setEnabled(False)
        self.main_frame.dis_set_offset_y_lineEdit.setEnabled(False)
        self.main_frame.save_offset_pushButton.setEnabled(False)
        self.main_frame.set_offset_pushButton.setEnabled(True)
        self.main_frame.save_offset_pushButton.setStyleSheet("background:gray")
        self.main_frame.set_offset_pushButton.setStyleSheet("background:rgb(187, 255, 144)")
        self.show_massege_box_info("SAVE OFFSET","You want to save offset ??")
    
    def check_manual_control(self):
        try:
            if self.main_frame.test_manual_control_checkBox.isChecked():
                self.motor_con_x.set_speed(1000)
                self.motor_con_y.set_speed(1000)
                self.main_frame.enable_manual_control()
            else:
                self.motor_con_x.set_speed(200)
                self.motor_con_y.set_speed(200)
                self.main_frame.disable_manual_control()
        except Exception as e:
            print(e)
    
    def motor_x_in(self):
        self.motor_con_x.in_and_up()
        
    def motor_x_out(self):
        self.motor_con_x.out_and_down()
    
    def motor_y_up(self):
        self.motor_con_y.in_and_up()
        
    def motor_y_down(self):
        self.motor_con_y.out_and_down()
    
    def stop_motor_all(self):
        self.motor_con_y.stop_motor()
        self.motor_con_x.stop_motor()
    
    def start_test(self):
        self.start_thread_mono = Thread(target=self.run_mono_test, args=())
        self.start_thread_mono.start()
        self.start_loop_mono_test = True
        self.loop_mono_state = 1
    
    def stop_test(self):
        self.start_loop_mono_test = False
        self.status_k_button = False
        self.lock_export_data = True
        self.start_thread_mono.join()
        self.loop_mono_state = 0
        self.main_frame.test_k_set_pushButton.setEnabled(True)
        self.main_frame.test_k_set_pushButton.setStyleSheet("background:rgb(206, 223, 255)")
    
    def clear_test(self):
        self.main_frame.test_output_textEdit.clear()
    
    def save_test(self):
        # Get the data from the text edit
        data = self.main_frame.test_output_textEdit.toPlainText()
        
        # Ask user for file name
        file_name, _ = QFileDialog.getSaveFileName(self.main_frame, "Save File", "", "CSV Files (*.csv);;Text Files (*.txt)")
        if file_name.endswith('.csv'):
            with open(file_name, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["time", "Dis X(Dx)","Dis Y(Dv)","loadcell X (kPa)", "loadcell Y (kPa)", "K (kPa)", "Fy target (kPa)"])
                for line in data.split('\n'):
                    writer.writerow(line.split(','))
        elif file_name.endswith('.txt'):
            with open(file_name, 'w', encoding='utf-8') as txtfile:
                txtfile.write(data)
            self.show_message_info.emit("SAVE", f"Data saved to {file_name}")
        else:
            self.show_message_info.emit("SAVE", "Save operation cancelled")
    
    def k_button_pressed(self):
        self.status_k_button = True
        self.K_target = float(self.main_frame.st_K_lineEdit.text())
        self.main_frame.test_k_set_pushButton.setEnabled(False)
        self.main_frame.test_k_set_pushButton.setStyleSheet("background-color:gray;")
    
    def run_mono_test(self):
        self.recommand_Dx = float(self.main_frame.st_limit_distance_x_lineEdit.text())
        while self.start_loop_mono_test:
            if (self.loop_mono_state == 0):
                pass
            
            elif (self.loop_mono_state == 1):
                self.show_message_info.emit("Mono Test","Start Mono Test")
                self.recommand_weigh_Fy = float(self.main_frame.st_weight_y_lineEdit.text())
                self.motor_con_y.set_speed(200)
                self.delay(0.1)
                self.motor_con_y.set_direction(0)
                self.delay(0.1)
                self.motor_con_y.start_motor()
                self.delay(0.1)
                self.lock_export_data = False
                self.loop_mono_state = 2
                
            elif (self.loop_mono_state == 2):
                if (self.Fy >= self.recommand_weigh_Fy):
                    self.lock_export_data = True
                    self.motor_con_y.stop_motor()
                    self.show_message_info.emit("Mono Test","Fy set success")
                    self.delay(2)
                    self.show_setting()
                    self.loop_mono_state = 3

            elif (self.loop_mono_state == 3):
                if self.status_k_button == True:
                    self.show_message_info.emit("Mono Test","K set success")
                    self.delay(1.5)
                    self.show_test()
                    self.lock_export_data = False
                    self.loop_mono_state = 4
            
            elif (self.loop_mono_state == 4):
                # print("start slide test")
                self.motor_con_x.set_speed(90)
                self.delay(0.1)
                self.motor_con_x.set_direction(1)
                self.delay(0.1)
                self.motor_con_x.start_motor()
                self.delay(0.1)
                self.main_frame.test_output_textEdit.append("start slide test")
                self.loop_mono_state = 5
                
            elif (self.loop_mono_state == 5):
                self.control_motor_Y()
                # print("move x to recommand")
                if (self.Dx >= self.recommand_Dx):
                    self.motor_con_x.stop_motor()
                    self.delay(1)
                    self.show_message_info.emit("Mono Test","Dx move to recommand success")
                    self.loop_mono_state = 6

            elif (self.loop_mono_state == 6):
                self.control_motor_Y()
                # print("wait for stop and revest motor x")
                
            self.export_data_to_dash_bord()
            time.sleep(1)

    def export_data_to_dash_bord(self):
        Dx, Dy, Fx, Fy, Kn, Fy_target = self.get_data()
        E_Dx = Dx;E_Dy = Dy;E_Fx = Fx;E_Fy = Fy;E_Kn = Kn;E_Fy_target = Fy_target
        if self.lock_export_data == True:
            pass
        else:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            self.main_frame.test_output_textEdit.append(f"{timestamp},{E_Dx},{E_Dy},{E_Fx},{E_Fy},{E_Kn},{E_Fy_target}")

    def port_updated(self, ports):
        if len(ports) == 0:
            print("No port found")
            self.main_frame.LY_Port_comboBox.setEnabled(False)
            self.main_frame.LY_Port_comboBox.clear()
            self.main_frame.LY_Port_comboBox.addItem("None")
            self.main_frame.LX_Port_comboBox.setEnabled(False)
            self.main_frame.LX_Port_comboBox.clear()
            self.main_frame.LX_Port_comboBox.addItem("None")
            self.main_frame.LDVT_Port_comboBox.setEnabled(False)
            self.main_frame.LDVT_Port_comboBox.clear()
            self.main_frame.LDVT_Port_comboBox.addItem("None")
            self.main_frame.motor_Port_x_comboBox.setEnabled(False)
            self.main_frame.motor_Port_x_comboBox.clear()
            self.main_frame.motor_Port_x_comboBox.addItem("None")
            self.main_frame.motor_Port_y_comboBox.setEnabled(False)
            self.main_frame.motor_Port_y_comboBox.clear()
            self.main_frame.motor_Port_y_comboBox.addItem("None")
        else:
            self.main_frame.LY_Port_comboBox.clear()
            self.main_frame.LY_Port_comboBox.setEnabled(True)
            self.main_frame.LX_Port_comboBox.clear()
            self.main_frame.LX_Port_comboBox.setEnabled(True)
            self.main_frame.LDVT_Port_comboBox.clear()
            self.main_frame.LDVT_Port_comboBox.setEnabled(True)
            self.main_frame.motor_Port_x_comboBox.clear()
            self.main_frame.motor_Port_x_comboBox.setEnabled(True)
            self.main_frame.motor_Port_y_comboBox.clear()
            self.main_frame.motor_Port_y_comboBox.setEnabled(True)
            for port in ports:
                self.main_frame.LY_Port_comboBox.addItem(port.device)
                self.main_frame.LX_Port_comboBox.addItem(port.device)
                self.main_frame.LDVT_Port_comboBox.addItem(port.device)
                self.main_frame.motor_Port_x_comboBox.addItem(port.device)
                self.main_frame.motor_Port_y_comboBox.addItem(port.device)

    def con_port_pressed(self):
        self.ly_port = self.main_frame.LY_Port_comboBox.currentText()
        self.lx_port = self.main_frame.LX_Port_comboBox.currentText()
        self.LVDT_port = self.main_frame.LDVT_Port_comboBox.currentText()
        self.mx_port = self.main_frame.motor_Port_x_comboBox.currentText()
        self.my_port = self.main_frame.motor_Port_y_comboBox.currentText()
        
        self.baudrate = 115200
        self.loadcell_con_Y.connect(self.ly_port, self.baudrate)
        self.loadcell_con_X.connect(self.lx_port, self.baudrate)
        self.lvdt_con.connect(self.LVDT_port, self.baudrate)
        self.motor_con_x.connect(self.mx_port, self.baudrate)
        self.motor_con_y.connect(self.my_port, self.baudrate)
        
        if (self.loadcell_con_Y.check_connection() & self.loadcell_con_X.check_connection() & self.lvdt_con.check_connection() & self.motor_con_x.check_connection() & self.motor_con_y.check_connection()) == True:
            self.show_message_info.emit("Connection","Connected to all devices")
            self.main_frame.con_to_port()
            self.motor_con_x.set_speed(200)
            self.motor_con_y.set_speed(200)
            self.start_collect_data = True
            self.sensorThread = Thread(target=self.collect_data, args=())
            self.sensorThread.start()
            
        self.main_frame.test_weight_y_lineEdit.setEnabled(False)
        self.main_frame.test_weight_x_lineEdit.setEnabled(False)
        self.main_frame.test_dis_y_lineEdit.setEnabled(False)
        self.main_frame.test_dis_x_lineEdit.setEnabled(False)
        self.speed_MX = self.main_frame.st_pwm_x_lineEdit.text()
        self.speed_MY = self.main_frame.st_pwm_y_lineEdit.text()

    def disconnect_port(self):
        self.loadcell_con_Y.disconnect()
        self.loadcell_con_X.disconnect()
        self.lvdt_con.disconnect()
        self.motor_con_x.disconnect()
        self.motor_con_y.disconnect()
        self.start_collect_data = False
        self.K_target = 0
        self.main_frame.dis_con_to_port()
        if self.sensorThread.is_alive():
            self.sensorThread.join()
        self.show_message_info.emit("Connection","Disconnected to all devices")

    def collect_data(self):
        while self.start_collect_data == True:
            try:
                self.offset_dx_test = float(self.main_frame.dis_set_offset_x_lineEdit.text())
                self.offset_dy_test = float(self.main_frame.dis_set_offset_y_lineEdit.text())
                area = float(self.main_frame.st_Area_lineEdit.text())
                self.Dy, self.Dx = self.lvdt_con.get_data()
                self.Fx = self.loadcell_con_X.get_data()
                self.Fy = self.loadcell_con_Y.get_data()
                self.Dy = float((self.Dy-self.offset_dy_test))
                self.Dy = float(self.Dy-self.set_zero_dy_get_data)
                self.Dy = round(self.Dy, 4)
                self.Dx = float((self.Dx-self.offset_dx_test))
                self.Dx = float(self.Dx-self.set_zero_dx_get_data)
                self.Dx = round(self.Dx, 4)

                if not self.lock_data_referanec and self.Dx != 0 and self.Dy != 0:
                    self.referance_Dy = self.Dy
                    self.referance_Dx = self.Dx
                    self.lock_data_referanec = True

                self.Dy -= self.referance_Dy
                self.Dy = round(self.Dy, 4)
                self.Dx -= self.referance_Dx
                self.Dx = round(self.Dx, 4)

                self.Fy = round(float(self.Fy) * 0.0098 / area, 4)
                self.Fx = round(float(self.Fx) * 0.0098 / area, 4)
                
                self.inseart_data_to_ui(self.Dx,self.Dy,self.Fx,self.Fy)

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
            self.motor_con_y.set_direction(1)  # หมุนขึ้น
            print("up")
        else:
            self.motor_con_y.set_direction(0)  # หมุนลง
            print("down")

        speed = max(200, min(abs(speed_adjustment), 900))  # จำกัดช่วงความเร็ว
        speed = round(speed, 4)
        # print(f'speed: {speed} speed_adjustment: {speed_adjustment}')
        self.motor_con_y.set_speed(speed)

        if speed > 20:
            self.motor_con_y.start_motor()
        else:
            self.motor_con_y.stop_motor()
    # setup page ========================================================================================================
    def start_up_programe(self):
        self.main_frame.setup_programe_ui()
    # setup page ========================================================================================================
    # show page ========================================================================================================
    def show_setting(self):
        self.main_frame.show_setting_page()
        self.main_frame.show()  
    def show_test(self):
        self.main_frame.show_test_page()
        self.main_frame.show()
    def show_calibate(self):
        self.main_frame.show_calibate_page()
        self.main_frame.show()
    def Show_main(self):
        self.main_frame.show_home_page()
        self.main_frame.show()
    # show page ========================================================================================================
    # show message box  ========================================================================================
    def show_massege_box_question(self,title,text):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle(title)
        msg_box.setText(text)
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    def show_massege_box_info(self,title,text):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle(title)
        msg_box.setText(text)
        msg_box.exec()
    def show_massege_box_error(self,title,text):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle(title)
        msg_box.setText(text)
        msg_box.exec()
    def show_massege_box_warning(self,title,text):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle(title)
        msg_box.setText(text)
        msg_box.exec()
    # show message box  =============================================================================================
    # show parameter to ui ==========================================================================================
    def show_parameter(self):
        self.data_st = str(self.databass_controller.read_parameter_to_setting()).strip("[]").strip("()").split(",")
        self.ID_P = str(self.data_st[0])
        self.p_pwmx = str(self.data_st[1])
        self.p_pwmy = str(self.data_st[2])
        self.limit_wx = str(self.data_st[3])
        self.limit_wy = str(self.data_st[4])
        self.limit_dx = str(self.data_st[5])
        self.limit_dy = str(self.data_st[6])
        self.area_test = str(self.data_st[7])
        self.set_parameter_to_ui(self.p_pwmx,self.p_pwmy,self.limit_wx,self.limit_wy,self.limit_dx,self.limit_dy,self.area_test)
        self.offset_data = str(self.databass_controller.read_offset_to_ui()).strip("[]").strip("()").split(",")
        
        self.offset_dis_x = float(self.offset_data[1])
        self.offset_dx = round(self.offset_dis_x, 4)
        # print(self.offset_dx)
        self.offset_dis_x = str(self.offset_dis_x)
        
        self.offset_dis_y = float(self.offset_data[2])
        self.offset_dy = round(self.offset_dis_y, 4)
        # print(self.offset_dy)
        self.offset_dis_y = str(self.offset_dis_y)
        
        self.set_parameter_offset_to_ui(self.offset_dis_x,self.offset_dis_y)
        
    def set_parameter_offset_to_ui(self,off_dis_x,off_dis_y):
        self.main_frame.dis_set_offset_x_lineEdit.setText(off_dis_x)
        self.main_frame.dis_set_offset_y_lineEdit.setText(off_dis_y)
        self.main_frame.dis_set_offset_x_lineEdit.setEnabled(False)
        self.main_frame.dis_set_offset_y_lineEdit.setEnabled(False)
        
    def set_parameter_to_ui(self,ppx,ppy,lwx,lwy,ldx,ldy,area):
        self.main_frame.st_pwm_x_lineEdit.setText(ppx)
        self.main_frame.st_pwm_y_lineEdit.setText(ppy)
        self.main_frame.st_limit_weight_x_lineEdit.setText(lwx)
        self.main_frame.st_limit_weight_y_lineEdit.setText(lwy)
        self.main_frame.st_limit_distance_x_lineEdit.setText(ldx)
        self.main_frame.st_limit_distance_y_lineEdit.setText(ldy)
        self.main_frame.st_Area_lineEdit.setText(area)
        self.main_frame.st_pwm_x_lineEdit.setEnabled(False)
        self.main_frame.st_pwm_y_lineEdit.setEnabled(False)
        self.main_frame.st_limit_weight_x_lineEdit.setEnabled(False)
        self.main_frame.st_limit_weight_y_lineEdit.setEnabled(False)
        self.main_frame.st_limit_distance_x_lineEdit.setEnabled(False)
        self.main_frame.st_limit_distance_y_lineEdit.setEnabled(False)
        self.main_frame.st_Area_lineEdit.setEnabled(False)
    # set parameter to ui ==========================================================================================
    # set parameter to ui frame ==========================================================================================
    def config_button_pressed(self):
        self.show_message_info.emit("CONFIG","You want to change the parameter ??")
        self.main_frame.config_parameter()

    def save_button_pressed(self):
        read_pwmx = self.main_frame.st_pwm_x_lineEdit.text()
        read_pwmy = self.main_frame.st_pwm_y_lineEdit.text()
        read_limit_wx = self.main_frame.st_limit_weight_x_lineEdit.text()
        read_limit_wy = self.main_frame.st_limit_weight_y_lineEdit.text()
        read_limit_dx = self.main_frame.st_limit_distance_x_lineEdit.text()
        read_limit_dy = self.main_frame.st_limit_distance_y_lineEdit.text()
        read_area = self.main_frame.st_Area_lineEdit.text() 
        self.databass_controller.set_parameter_to_setting(read_pwmx,read_pwmy,read_limit_wx,read_limit_wy,read_limit_dx,read_limit_dy,read_area)
        self.show_message_info.emit("SAVE","save parameter success")
        self.main_frame.save_parameter()
    # set parameter to ui frame ==========================================================================================
    # insert data to UI ==========================================================================================
    def inseart_data_to_ui(self,dx,dy,fx,fy):
        self.main_frame.test_weight_y_lineEdit.setText(str(fy))
        self.main_frame.r_weight_y_lineEdit.setText(str(fy))
        self.main_frame.test_weight_x_lineEdit.setText(str(fx))
        self.main_frame.r_weight_x_lineEdit.setText(str(fx))
        self.main_frame.test_dis_y_lineEdit.setText(str(dy))
        self.main_frame.test_dis_x_lineEdit.setText(str(dx))
    def delay(self,seconds):
        start_time = time.perf_counter()
        while time.perf_counter() - start_time < seconds:
            pass  # ทำงานอื่นต่อไปได้
    def __del__(self):
        self.loadcell_con_Y.disconnect()
        self.loadcell_con_X.disconnect()
        self.lvdt_con.disconnect()
        self.motor_con_x.disconnect()
        self.motor_con_y.disconnect()
        if self.sensorThread.is_alive():
            self.sensorThread.join()