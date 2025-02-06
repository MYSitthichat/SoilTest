from PySide6.QtCore import QObject , Slot
from view.view_main_frame import MainFrame
from Controller.databass_controller import DatabassController
from Controller.check_comport_controller import SerialPortChecker
import serial as ser
from PySide6.QtWidgets import QMessageBox
from Controller.read_loadcell import Readloadcell
from Controller.controller_LVDT import ControllerLVDT
from Controller.controller_motor import ControllerMotor
import  time
from threading import Thread

class MainController(QObject):
    def __init__(self):
        super(MainController, self).__init__()
        self.main_frame = MainFrame()
        self.check_port_controller = SerialPortChecker()
        self.databass_controller = DatabassController()
        self.loadcell_data = Readloadcell()
        self.CT_LVDT = ControllerLVDT()
        self.CT_motor = ControllerMotor()
        self.check_port_controller.start()
        self.loadcell_data.connect_serial_XY_signal.connect(self.connect_serial_XY)
        self.CT_LVDT.connect_serial_arduino_signal.connect(self.connect_serial_arduino)
        self.CT_motor.connect_serial_motor_signal.connect(self.connect_serial_motor)
        self.check_port_controller.ports_updated.connect(self.port_updated)
        self.main_frame.home_pushButton.clicked.connect(self.Show_main)
        self.main_frame.calibrate_pushButton.clicked.connect(self.show_calibate)
        self.main_frame.test_pushButton.clicked.connect(self.show_test)
        self.main_frame.setting_pushButton.clicked.connect(self.show_setting)
        self.main_frame.con_port_pushButton.clicked.connect(self.con_port_pressed)
        self.main_frame.dis_port_pushButton.clicked.connect(self.discon_port_pressed)
        self.main_frame.st_config_pushButton.clicked.connect(self.config_button_pressed)
        self.main_frame.st_save_pushButton.clicked.connect(self.save_button_pressed)
        self.main_frame.cl_set_zero_pushButton.clicked.connect(self.set_zero_button_pressed)
        self.main_frame.cl_calibrate_pushButton.clicked.connect(self.calibrate_button_pressed)
        self.main_frame.test_start_pushButton.clicked.connect(self.start_button_pressed)
        self.main_frame.test_stop_pushButton.clicked.connect(self.stop_button_pressed)
        self.main_frame.test_clear_pushButton.clicked.connect(self.clear_button_pressed)
        self.main_frame.test_save_pushButton.clicked.connect(self.save_button_pressed)
        self.main_frame.test_monotonic_radioButton.clicked.connect(self.monotonic_selected)
        self.main_frame.test_cyclic_radioButton.clicked.connect(self.cyclic_selected)
        self.databass_controller.create_databass()
        self.databass_controller.check_record_setting()
        self.loadcell_data.load_cell_data.connect(self.update_loadcell_data)
        self.CT_LVDT.displace_xy_data.connect(self.update_displace_data)
        self.main_frame.m_up_pushButton.clicked.connect(self.m_up_pressed)
        self.main_frame.m_down_pushButton.clicked.connect(self.m_down_pressed)
        self.main_frame.m_in_pushButton.clicked.connect(self.m_out_pressed)
        self.main_frame.m_out_pushButton.clicked.connect(self.m_in_pressed)
        self.main_frame.m_stop_all_pushButton.clicked.connect(self.stop_all_motors)
        self.serial_consuc =False
        self.serial_ar_con = False
        self.mono_test = False
        self.serial_motor_con = False
        self.monotonic_state = 0
        self.start_program()
        self.show_parameter()
        
    @Slot()
    @Slot(str)
    
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
            self.main_frame.motor_Port_comboBox.setEnabled(False)
            self.main_frame.motor_Port_comboBox.clear()
            self.main_frame.motor_Port_comboBox.addItem("None")
        else:
            self.main_frame.LY_Port_comboBox.clear()
            self.main_frame.LY_Port_comboBox.setEnabled(True)
            self.main_frame.LX_Port_comboBox.clear()
            self.main_frame.LX_Port_comboBox.setEnabled(True)
            self.main_frame.LDVT_Port_comboBox.clear()
            self.main_frame.LDVT_Port_comboBox.setEnabled(True)
            self.main_frame.motor_Port_comboBox.clear()
            self.main_frame.motor_Port_comboBox.setEnabled(True)
            for port in ports:
                self.main_frame.LY_Port_comboBox.addItem(port.device)
                self.main_frame.LX_Port_comboBox.addItem(port.device)
                self.main_frame.LDVT_Port_comboBox.addItem(port.device)
                self.main_frame.motor_Port_comboBox.addItem(port.device)

    def clear_button_pressed(self):
        print("Clear Clicked")
        
    def save_button_pressed(self):
        print("Save Clicked")

    def con_port_pressed(self):
        self.loadcell_Y_comport = self.main_frame.LY_Port_comboBox.currentText()
        self.loadcell_X_comport = self.main_frame.LX_Port_comboBox.currentText()
        self.LVDT_comport = self.main_frame.LDVT_Port_comboBox.currentText()
        self.motor_comport = self.main_frame.motor_Port_comboBox.currentText()
        self.speed_MX = self.main_frame.st_pwm_x_lineEdit.text()
        self.speed_MY = self.main_frame.st_pwm_y_lineEdit.text()
        self.loadcell_data.get_comport(self.loadcell_Y_comport,self.loadcell_X_comport)
        self.LVDT_comport = self.CT_LVDT.get_comport(self.LVDT_comport)
        self.motor_comport = self.CT_motor.get_comport(self.motor_comport)
        self.loadcell_data.running = True
        self.loadcell_data.start()
        self.CT_LVDT.running = True
        self.CT_LVDT.start()
        self.CT_motor.running = True
        self.CT_motor.start()
        
        try:
            if self.serial_consuc == True & self.serial_ar_con == True & self.serial_motor_con == True:
                msg_box = QMessageBox()
                msg_box.setIcon(QMessageBox.Information)
                msg_box.setWindowTitle("COMPORT CON")
                msg_box.setText(f"CONNECTED \n L1 to{self.loadcell_Y_comport} \n L2 to{self.loadcell_X_comport} \nLVDT to{self.LVDT_comport} \nMotor to{self.motor_comport}")
                msg_box.exec()
                self.enable_m_controll()
                self.main_frame.LY_Port_comboBox.setEnabled(False)
                self.main_frame.LY_Port_comboBox.setStyleSheet(u"background:gray")
                self.main_frame.LX_Port_comboBox.setEnabled(False)
                self.main_frame.LX_Port_comboBox.setStyleSheet(u"background:gray")
                self.main_frame.LDVT_Port_comboBox.setEnabled(False)
                self.main_frame.LDVT_Port_comboBox.setStyleSheet(u"background:gray")
                self.main_frame.motor_Port_comboBox.setEnabled(False)
                self.main_frame.motor_Port_comboBox.setStyleSheet(u"background:gray")
                self.main_frame.con_port_pushButton.setEnabled(False)
                self.main_frame.con_port_pushButton.setStyleSheet(u"background:gray")
                self.main_frame.dis_port_pushButton.setEnabled(True)
                self.main_frame.dis_port_pushButton.setStyleSheet(u"background:rgb(252, 65, 54)")
                self.speed_MX = self.main_frame.st_pwm_x_lineEdit.text()
                self.speed_MY = self.main_frame.st_pwm_y_lineEdit.text()
                self.CT_motor.get_setting_speed(self.speed_MX,self.speed_MY)
        except ser.SerialException as e:
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Critical)
            msg_box.setWindowTitle("COMPORT CON ERROR")
            msg_box.setText(f"Failed to connect to {e} \n please check the comport")
            msg_box.exec()
        
    def discon_port_pressed(self):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle("Dis Connected")
        msg_box.setText(f"DIS CONNECTED \n L1 to{self.loadcell_Y_comport} \n L2 to{self.loadcell_X_comport} \nLVDT to{self.LVDT_comport} \nMotor to{self.motor_comport}")
        msg_box.exec()
        self.main_frame.LY_Port_comboBox.setEnabled(True)
        self.main_frame.LY_Port_comboBox.setStyleSheet(u"background:white")
        self.main_frame.LX_Port_comboBox.setEnabled(True)
        self.main_frame.LX_Port_comboBox.setStyleSheet(u"background:white")
        self.main_frame.LDVT_Port_comboBox.setEnabled(True)
        self.main_frame.LDVT_Port_comboBox.setStyleSheet(u"background:white")
        self.main_frame.motor_Port_comboBox.setEnabled(True)
        self.main_frame.motor_Port_comboBox.setStyleSheet(u"background:white")
        
        self.serial_consuc = False
        self.serial_ar_con = False
        self.serial_motor_con = False
        self.loadcell_data.stop()
        self.CT_LVDT.stop()
        self.CT_motor.stop()
        self.main_frame.con_port_pushButton.setEnabled(True)
        self.main_frame.con_port_pushButton.setStyleSheet(u"background:rgb(170, 255, 0)")
        self.clear_loadcell_data()
        self.clear_displace_data()
        self.main_frame.dis_port_pushButton.setEnabled(False)
        self.main_frame.dis_port_pushButton.setStyleSheet(u"background:gray")
        self.disable_ui_parameter()
    
    def update_loadcell_data(self,load_cell_value):
        self.loadcell_Y = load_cell_value[0]
        self.loadcell_X = load_cell_value[1]
        self.main_frame.test_weight_y_lineEdit.setText(self.loadcell_Y)
        self.main_frame.test_weight_x_lineEdit.setText(self.loadcell_X)
        self.main_frame.r_weight_x_lineEdit.setText(self.loadcell_X)
        self.main_frame.r_weight_y_lineEdit.setText(self.loadcell_Y)
    
    def update_displace_data(self,disxy_data):
        self.dis_x = disxy_data[0]
        self.dis_y = disxy_data[1]
        self.main_frame.test_dis_x_lineEdit.setEnabled(False)
        self.main_frame.test_dis_y_lineEdit.setEnabled(False)
        self.main_frame.test_dis_x_lineEdit.setText(self.dis_x)
        self.main_frame.test_dis_y_lineEdit.setText(self.dis_y)
        
    def monotonic_selected(self):
        self.monotonic_UI()
        self.monotonic_test = True
        self.cyclic_test = False
        
    def cyclic_selected(self):
        self.cyclic_UI()
        self.cyclic_test = True
        self.monotonic_test = False
    
    def m_up_pressed(self):
        # print("M UP")
        self.CT_motor.up_motors_y()
        
    def m_down_pressed(self):
        # print("M DOWN")
        self.CT_motor.down_motors_y()
    
    def m_in_pressed(self):
        # print("M IN")
        self.CT_motor.in_motors_x()
        
    def m_out_pressed(self):
        # print("M OUT")
        self.CT_motor.out_motors_x()
        
    def stop_all_motors(self):
        # print("STOP ALL")
        self.CT_motor.stop_all_motors()
        
    def connect_serial_XY(self):
        self.serial_consuc = True
    
    def connect_serial_arduino(self):
        self.serial_ar_con = True
        
    def connect_serial_motor(self):
        self.serial_motor_con = True
        
    def set_zero_button_pressed(self):
        print("Set Zero Clicked")
        
    def calibrate_button_pressed(self):
        print("Calibrate Clicked")

    def monotonic_UI(self):
        self.main_frame.st_cyclic_lineEdit.setEnabled(False)
        self.main_frame.st_weight_x_lineEdit.setEnabled(False)
        self.main_frame.st_Area_lineEdit.setEnabled(True)
        self.main_frame.st_weight_y_lineEdit.setEnabled(True)
        self.main_frame.st_K_lineEdit.setEnabled(True)
        
        self.main_frame.st_cyclic_lineEdit.clear()
        self.main_frame.st_weight_x_lineEdit.clear()
        self.main_frame.st_Area_lineEdit.clear()
        self.main_frame.st_weight_y_lineEdit.clear()
        self.main_frame.st_K_lineEdit.clear()
        
        self.main_frame.st_cyclic_lineEdit.setStyleSheet(u"background:gray")
        self.main_frame.st_weight_x_lineEdit.setStyleSheet(u"background:gray")
        self.main_frame.st_Area_lineEdit.setStyleSheet(u"background:white")
        self.main_frame.st_weight_y_lineEdit.setStyleSheet(u"background:white")
        self.main_frame.st_K_lineEdit.setStyleSheet(u"background:white")
        
        self.main_frame.st_cyclic_lineEdit.setPlaceholderText("None")
        self.main_frame.st_weight_x_lineEdit.setPlaceholderText("None")
        
    def cyclic_UI(self):
        self.main_frame.st_cyclic_lineEdit.setEnabled(True)
        self.main_frame.st_weight_x_lineEdit.setEnabled(True)
        self.main_frame.st_Area_lineEdit.setEnabled(True)
        self.main_frame.st_weight_y_lineEdit.setEnabled(True)
        self.main_frame.st_K_lineEdit.setEnabled(True)
        
        self.main_frame.st_cyclic_lineEdit.clear()
        self.main_frame.st_weight_x_lineEdit.clear()
        self.main_frame.st_Area_lineEdit.clear()
        self.main_frame.st_weight_y_lineEdit.clear()
        self.main_frame.st_K_lineEdit.clear()
        
        self.main_frame.st_cyclic_lineEdit.setStyleSheet(u"background:white")
        self.main_frame.st_weight_x_lineEdit.setStyleSheet(u"background:white")
        self.main_frame.st_Area_lineEdit.setStyleSheet(u"background:white")
        self.main_frame.st_weight_y_lineEdit.setStyleSheet(u"background:white")
        self.main_frame.st_K_lineEdit.setStyleSheet(u"background:white")
        
        self.main_frame.st_cyclic_lineEdit.setPlaceholderText("")
        self.main_frame.st_weight_x_lineEdit.setPlaceholderText("")
    
    # show page
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
    # show page
    
    def start_program(self):
        self.main_frame.test_weight_x_lineEdit.setEnabled(False)
        self.main_frame.test_weight_y_lineEdit.setEnabled(False)
        self.main_frame.r_weight_x_lineEdit.setEnabled(False)
        self.main_frame.r_weight_y_lineEdit.setEnabled(False)
        self.main_frame.dis_port_pushButton.setEnabled(False)
        self.main_frame.st_save_pushButton.setEnabled(False)
        self.main_frame.dis_port_pushButton.setStyleSheet(u"background:gray")
        self.disable_ui_parameter()
        
    def clear_loadcell_data(self):
        self.main_frame.test_weight_x_lineEdit.clear()
        self.main_frame.test_weight_y_lineEdit.clear()
        self.main_frame.r_weight_x_lineEdit.clear()
        self.main_frame.r_weight_y_lineEdit.clear()
        
    def clear_displace_data(self):
        self.main_frame.test_dis_x_lineEdit.clear()
        self.main_frame.test_dis_y_lineEdit.clear()
        
    
    # set parameter to ui frame
    def config_button_pressed(self):
        self.show_massege_box_info("CONFIG","You want to change the parameter ??")
        self.enable_ui_parameter()

        
    def save_button_pressed(self):
        read_pwmx = self.main_frame.st_pwm_x_lineEdit.text()
        read_pwmy = self.main_frame.st_pwm_y_lineEdit.text()
        read_limit_wx = self.main_frame.st_limit_weight_x_lineEdit.text()
        read_limit_wy = self.main_frame.st_limit_weight_y_lineEdit.text()
        read_limit_dx = self.main_frame.st_limit_distance_x_lineEdit.text()
        read_limit_dy = self.main_frame.st_limit_distance_y_lineEdit.text()
        self.databass_controller.set_parameter_to_setting(read_pwmx,read_pwmy,read_limit_wx,read_limit_wy,read_limit_dx,read_limit_dy)
        
        self.show_massege_box_info("SAVE","save parameter success")
        self.disable_ui_parameter()
        
        self.CT_motor.get_setting_speed(read_pwmx,read_pwmy)
    
    def show_parameter(self):
        self.data_st = str(self.databass_controller.read_parameter_to_setting()).strip("[]").strip("()").split(",")
        self.ID_P = str(self.data_st[0])
        self.p_pwmx = str(self.data_st[1])
        self.p_pwmy = str(self.data_st[2])
        self.limit_wx = str(self.data_st[3])
        self.limit_wy = str(self.data_st[4])
        self.limit_dx = str(self.data_st[5])
        self.limit_dy = str(self.data_st[6])
        self.set_parameter_to_ui(self.p_pwmx,self.p_pwmy,self.limit_wx,self.limit_wy,self.limit_dx,self.limit_dy)
        
    def set_parameter_to_ui(self,ppx,ppy,lwx,lwy,ldx,ldy):
        self.main_frame.st_pwm_x_lineEdit.setText(ppx)
        self.main_frame.st_pwm_y_lineEdit.setText(ppy)
        self.main_frame.st_limit_weight_x_lineEdit.setText(lwx)
        self.main_frame.st_limit_weight_y_lineEdit.setText(lwy)
        self.main_frame.st_limit_distance_x_lineEdit.setText(ldx)
        self.main_frame.st_limit_distance_y_lineEdit.setText(ldy)
        self.main_frame.st_pwm_x_lineEdit.setEnabled(False)
        self.main_frame.st_pwm_y_lineEdit.setEnabled(False)
        self.main_frame.st_limit_weight_x_lineEdit.setEnabled(False)
        self.main_frame.st_limit_weight_y_lineEdit.setEnabled(False)
        self.main_frame.st_limit_distance_x_lineEdit.setEnabled(False)
        self.main_frame.st_limit_distance_y_lineEdit.setEnabled(False)
        
    def enable_ui_parameter(self):
        self.main_frame.st_config_pushButton.setEnabled(False)
        self.main_frame.st_save_pushButton.setEnabled(True)
        self.main_frame.st_pwm_x_lineEdit.setEnabled(True)
        self.main_frame.st_pwm_y_lineEdit.setEnabled(True)
        self.main_frame.st_limit_weight_x_lineEdit.setEnabled(True)
        self.main_frame.st_limit_weight_y_lineEdit.setEnabled(True)
        self.main_frame.st_limit_distance_x_lineEdit.setEnabled(True)
        self.main_frame.st_limit_distance_y_lineEdit.setEnabled(True)
        self.main_frame.st_config_pushButton.setStyleSheet(u"background:gray")
        self.main_frame.st_save_pushButton.setStyleSheet(u"background:rgb(170, 255, 0)")
        self.main_frame.st_pwm_x_lineEdit.setStyleSheet(u"background:white")
        self.main_frame.st_pwm_y_lineEdit.setStyleSheet(u"background:white")
        self.main_frame.st_limit_weight_x_lineEdit.setStyleSheet(u"background:white")
        self.main_frame.st_limit_weight_y_lineEdit.setStyleSheet(u"background:white")
        self.main_frame.st_limit_distance_x_lineEdit.setStyleSheet(u"background:white")
        self.main_frame.st_limit_distance_y_lineEdit.setStyleSheet(u"background:white")
        
    def disable_ui_parameter(self):
        self.main_frame.st_config_pushButton.setEnabled(True)
        self.main_frame.st_save_pushButton.setEnabled(False)
        self.main_frame.st_pwm_x_lineEdit.setEnabled(False)
        self.main_frame.st_pwm_y_lineEdit.setEnabled(False)
        self.main_frame.st_limit_weight_x_lineEdit.setEnabled(False)
        self.main_frame.st_limit_weight_y_lineEdit.setEnabled(False)
        self.main_frame.st_limit_distance_x_lineEdit.setEnabled(False)
        self.main_frame.st_limit_distance_y_lineEdit.setEnabled(False)
        self.main_frame.st_config_pushButton.setStyleSheet(u"background:rgb(115, 174, 253)")
        self.main_frame.st_save_pushButton.setStyleSheet(u"background:gray")
        self.main_frame.st_pwm_x_lineEdit.setStyleSheet(u"background:gray")
        self.main_frame.st_pwm_y_lineEdit.setStyleSheet(u"background:gray")
        self.main_frame.st_limit_weight_x_lineEdit.setStyleSheet(u"background:gray")
        self.main_frame.st_limit_weight_y_lineEdit.setStyleSheet(u"background:gray")
        self.main_frame.st_limit_distance_x_lineEdit.setStyleSheet(u"background:gray")
        self.main_frame.st_limit_distance_y_lineEdit.setStyleSheet(u"background:gray")
        
    def enable_m_controll(self):
        self.main_frame.m_up_pushButton.setEnabled(True)
        self.main_frame.m_down_pushButton.setEnabled(True)
        self.main_frame.m_in_pushButton.setEnabled(True)
        self.main_frame.m_out_pushButton.setEnabled(True)
        self.main_frame.m_stop_all_pushButton.setEnabled(True)
        self.main_frame.test_start_pushButton.setEnabled(True)
        self.main_frame.test_stop_pushButton.setEnabled(True)
        self.main_frame.test_clear_pushButton.setEnabled(True)
        self.main_frame.test_save_pushButton.setEnabled(True)
        self.main_frame.m_up_pushButton.setStyleSheet(u"background:rgb(85, 255, 0)")
        self.main_frame.m_down_pushButton.setStyleSheet(u"background:rgb(85, 255, 0)")
        self.main_frame.m_in_pushButton.setStyleSheet(u"background:rgb(85, 170, 255)")
        self.main_frame.m_out_pushButton.setStyleSheet(u"background:rgb(85, 170, 255)")
        self.main_frame.m_stop_all_pushButton.setStyleSheet(u"background:rgb(255, 145, 137)")
        self.main_frame.test_start_pushButton.setStyleSheet(u"background:rgb(155, 221, 163)")
        self.main_frame.test_stop_pushButton.setStyleSheet(u"background:rgb(255, 61, 2)")
        self.main_frame.test_clear_pushButton.setStyleSheet(u"background:rgb(0, 170, 255)")
        self.main_frame.test_save_pushButton.setStyleSheet(u"background:rgb(170, 255, 255)")

        
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
    
    # ========= START BUTTON =========
    def start_button_pressed(self):
        try:
            if self.monotonic_test:
                self.start_monotonic_test()
                
            elif self.cyclic_test:
                pass
            
        except Exception as e:
            self.show_massege_box_error("ERROR",f"Not Selected Test Type")
                
    def stop_button_pressed(self):
        try:
            if self.monotonic_test:
                self.stop_monotonic_test()
            elif self.cyclic_test:
                pass
        except Exception as e:
            self.show_massege_box_error("ERROR",f"Not Selected Test Type")
    
    # ============== test monotonic ====================
    
    def run_monotonic_test(self):
        # print(self.loadcell_Y,self.loadcell_X,self.dis_x,self.dis_y)
        monotonic_grap_wiegth_y = 5.0
        
        monotonic_reverse_success_disX = 0.5
        monotonic_reverse_success_wiegthY = 3.0
        monotonic_stopmy = 0.0
        monotonic_success_wiegthY = False
        monotonic_success_disX = False
        
        self.strat_export_data = False
        while self.mono_test:
            self.limit_weight_y = float(self.main_frame.st_limit_weight_y_lineEdit.text())
            self.limit_weight_x = float(self.main_frame.st_limit_weight_x_lineEdit.text())
            self.limit_distance_x = float(self.main_frame.st_limit_distance_x_lineEdit.text())
            self.limit_distance_y = float(self.main_frame.st_limit_distance_y_lineEdit.text())
            self.weight_y_recommand = float(self.main_frame.st_weight_y_lineEdit.text())
            self.load_cell_y_data = float(self.loadcell_Y) 
            self.dis_mono_x = float(self.dis_x)
            if self.monotonic_state == 0:
                self.CT_motor.stop_all_motors()
            
            elif self.monotonic_state == 1:
                self.CT_motor.down_motors_y()
                time.sleep(0.5)
                self.monotonic_state = 2
            
            elif self.monotonic_state == 2:
                if self.load_cell_y_data >= self.weight_y_recommand +- monotonic_grap_wiegth_y:
                    self.CT_motor.stop_motors_y()
                    self.strat_export_data = True
                    self.monotonic_state = 3
                else:
                    pass
            elif self.monotonic_state == 3:
                self.CT_motor.in_motors_x()
                self.monotonic_state = 4
                time.sleep(0.5)
                
            elif self.monotonic_state == 4:
                if self.load_cell_y_data > self.weight_y_recommand +- monotonic_grap_wiegth_y:
                    self.CT_motor.up_motors_y()
                    
                if self.load_cell_y_data < self.weight_y_recommand:
                    self.CT_motor.down_motors_y()
                    
                if self.load_cell_y_data == self.weight_y_recommand:
                    self.CT_motor.stop_motors_y()
                
                if self.dis_mono_x >= self.limit_distance_x:
                    self.CT_motor.stop_motors_x()
                    self.CT_motor.stop_motors_y()
                    self.monotonic_state = 5
                self.CT_motor.in_motors_x()
                    
            elif self.monotonic_state == 5:
                self.CT_motor.stop_all_motors()
                self.monotonic_state = 6
                self.strat_export_data = False
                
            elif self.monotonic_state == 6:
                self.CT_motor.up_motors_y()
                self.CT_motor.out_motors_x()
                self.monotonic_state = 7
                
            # elif self.monotonic_state == 7:
            #     print((self.load_cell_y_data),(self.dis_mono_x))
            #     if self.load_cell_y_data <= monotonic_stopmy +- 5.0:
            #         self.CT_motor.stop_motors_y()
            #         print("stop y")
                #     monotonic_success_wiegthY = True
                # if self.dis_mono_x == 0 +- monotonic_reverse_success_disX:
                #     self.CT_motor.stop_motors_x()
                #     print("stop x")
                #     monotonic_success_disX = True
                # if monotonic_success_wiegthY & monotonic_success_disX:
                #     self.CT_motor.stop_all_motors()
                #     print("stop all")
                #     self.monotonic_state = 8
                    
            # elif self.monotonic_state == 8:
            #     self.show_massege_box_info("MONOTONIC TEST","Test Success")
            #     self.main_frame.test_output_textEdit.clear()
            #     self.monotonic_state = 0
            
            # if self.strat_export_data:
            #     timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            #     self.main_frame.test_output_textEdit.append(f"{timestamp}:{self.load_cell_y_data}:{self.loadcell_X}:{self.dis_x}:{self.dis_y}")
            time.sleep(0.1)

    def start_monotonic_test(self):
        self.mono_test = True
        self.monotonic_state = 1
        self.monotonic_thread = Thread(target=self.run_monotonic_test)
        self.monotonic_thread.start()

    def stop_monotonic_test(self):
        self.mono_test = False
        self.monotonic_state = 0
        self.CT_motor.stop_all_motors()
        self.monotonic_thread.join()
        
    # ============== test monotonic ====================
