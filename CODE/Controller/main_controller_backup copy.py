from PySide6.QtCore import QObject , Slot , Signal
from view.view_main_frame import MainFrame
from Controller.databass_controller import DatabassController
from Controller.check_comport_controller import SerialPortChecker
import serial as ser
from PySide6.QtWidgets import QMessageBox ,QFileDialog
from Controller.read_loadcell import Readloadcell
from Controller.controller_LVDT import ControllerLVDT
from Controller.controller_motor_X import ControllerMotorX
from Controller.controller_motor_Y import ControllerMotorY
import  time
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
        self.databass_controller = DatabassController()
        self.loadcell_data = Readloadcell()
        self.CT_LVDT = ControllerLVDT()
        self.CT_motor_X = ControllerMotorX()
        
        self.CT_motor_Y = ControllerMotorY()
        
        self.check_port_controller.start()
        self.loadcell_data.connect_serial_XY_signal.connect(self.connect_serial_XY)
        self.CT_LVDT.connect_serial_arduino_signal.connect(self.connect_serial_arduino)
        self.CT_motor_X.connect_serial_motor_x_signal.connect(self.connect_serial_motor_x)
        self.CT_motor_Y.connect_serial_motor_y_signal.connect(self.connect_serial_motor_y)
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
        self.main_frame.test_clear_pushButton.clicked.connect(self.test_clear_button_pressed)
        self.main_frame.test_save_pushButton.clicked.connect(self.test_save_button_pressed)
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
        self.main_frame.dis_x_set_zero_pushButton.clicked.connect(self.set_zero_displace_x)
        self.main_frame.dis_y_set_zero_pushButton.clicked.connect(self.set_zero_displace_y)
        self.main_frame.test_k_set_pushButton.clicked.connect(self.set_k_parameter_pressed)
        self.show_message_info.connect(self.show_massege_box_info)
        self.clear_output_data_frame.connect(self.clear_data_frame)
        self.calculate_k_every_time.connect(self.calculate_k_parameter)
        self.runing_mono_test.connect(self.run_k_mono_test)
        self.serial_consuc =False
        self.serial_ar_con = False
        self.mono_test = False
        self.serial_motor_x_con = False
        self.serial_motor_y_con = False
        self.monotonic_state = 0
        self.loadcell_X = 0.0
        self.loadcell_Y = 0.0
        self.dis_x = 0.0
        self.dis_y = 0.0
        self.zero_x_reference = 0.0
        self.set_zero_x_data = False
        self.test_set_zero_x = False
        
        self.set_y_reference = 0.0
        self.set_zero_y_data = False
        self.test_set_zero_y = False
        
        self.set_k_param_success = False
        self.start_monotonic_calculate_k = False
        self.start_monotonic_load_y_input = False
        self.start_monotonic_k_control = False
        self.new_sigma_mono = 0.0
        self.lock_export_data = False
        
        self.round_data_monotonic = 0
        
        self.start_program()
        self.show_parameter()
        
    @Slot()
    @Slot(str)
    
    
    def set_k_parameter_pressed(self):
        self.set_k_param_success = True
    
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
        self.loadcell_Y_comport = self.main_frame.LY_Port_comboBox.currentText()
        self.loadcell_X_comport = self.main_frame.LX_Port_comboBox.currentText()
        self.LVDT_comport = self.main_frame.LDVT_Port_comboBox.currentText()
        self.motor_comport_x = self.main_frame.motor_Port_x_comboBox.currentText()
        self.motor_comport_y = self.main_frame.motor_Port_y_comboBox.currentText()
        
        self.speed_MX = self.main_frame.st_pwm_x_lineEdit.text()
        self.speed_MY = self.main_frame.st_pwm_y_lineEdit.text()
        
        self.loadcell_data.get_comport(self.loadcell_Y_comport,self.loadcell_X_comport)
        self.LVDT_comport = self.CT_LVDT.get_comport(self.LVDT_comport)
        self.motor_comport_x = self.CT_motor_X.get_comport(self.motor_comport_x)
        self.motor_comport_y = self.CT_motor_Y.get_comport(self.motor_comport_y)
        
        self.loadcell_data.running = True
        self.loadcell_data.start()
        self.CT_LVDT.running = True
        self.CT_LVDT.start()
        self.CT_motor_X.running = True
        self.CT_motor_X.start()
        
        try:
            if self.serial_consuc == True & self.serial_ar_con == True & self.serial_motor_x_con == True & self.serial_motor_y_con == True:
                msg_box = QMessageBox()
                msg_box.setIcon(QMessageBox.Information)
                msg_box.setWindowTitle("COMPORT CON")
                msg_box.setText(f"CONNECTED \n L1 to{self.loadcell_Y_comport} \n L2 to{self.loadcell_X_comport} \nLVDT to{self.LVDT_comport} \nMotor X to{self.motor_comport_x} \nMotor Y to{self.motor_comport_y}")
                msg_box.exec()
                self.enable_m_controll()
                self.main_frame.LY_Port_comboBox.setEnabled(False)
                self.main_frame.LY_Port_comboBox.setStyleSheet(u"background:gray")
                self.main_frame.LX_Port_comboBox.setEnabled(False)
                self.main_frame.LX_Port_comboBox.setStyleSheet(u"background:gray")
                self.main_frame.LDVT_Port_comboBox.setEnabled(False)
                self.main_frame.LDVT_Port_comboBox.setStyleSheet(u"background:gray")
                self.main_frame.motor_Port_x_comboBox.setEnabled(False)
                self.main_frame.motor_Port_x_comboBox.setStyleSheet(u"background:gray")
                self.main_frame.motor_Port_y_comboBox.setEnabled(False)
                self.main_frame.motor_Port_y_comboBox.setStyleSheet(u"background:gray")
                self.main_frame.con_port_pushButton.setEnabled(False)
                self.main_frame.con_port_pushButton.setStyleSheet(u"background:gray")
                self.main_frame.dis_port_pushButton.setEnabled(True)
                self.main_frame.dis_port_pushButton.setStyleSheet(u"background:rgb(252, 65, 54)")
                self.main_frame.test_dis_x_lineEdit.setEnabled(False)
                self.main_frame.test_dis_y_lineEdit.setEnabled(False)
                self.main_frame.dis_set_zero_x_lineEdit.setEnabled(False)
                self.main_frame.dis_set_zero_y_lineEdit.setEnabled(False)
                self.speed_MX = self.main_frame.st_pwm_x_lineEdit.text()
                self.speed_MY = self.main_frame.st_pwm_y_lineEdit.text()
                self.CT_motor_X.get_setting_speed(self.speed_MY)
                self.delay(1)
                self.CT_motor_Y.get_setting_speed(self.speed_MX)
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
        msg_box.setText(f"DIS CONNECTED \n L1 to{self.loadcell_Y_comport} \n L2 to{self.loadcell_X_comport} \nLVDT to{self.LVDT_comport} \nMotor to{self.motor_comport_x} \nMotor to{self.motor_comport_y}")
        msg_box.exec()
        self.main_frame.LY_Port_comboBox.setEnabled(True)
        self.main_frame.LY_Port_comboBox.setStyleSheet(u"background:white")
        self.main_frame.LX_Port_comboBox.setEnabled(True)
        self.main_frame.LX_Port_comboBox.setStyleSheet(u"background:white")
        self.main_frame.LDVT_Port_comboBox.setEnabled(True)
        self.main_frame.LDVT_Port_comboBox.setStyleSheet(u"background:white")
        self.main_frame.motor_Port_x_comboBox.setEnabled(True)
        self.main_frame.motor_Port_x_comboBox.setStyleSheet(u"background:white")
        self.main_frame.motor_Port_y_comboBox.setEnabled(True)
        self.main_frame.motor_Port_y_comboBox.setStyleSheet(u"background:white")
        
        self.serial_consuc = False
        self.serial_ar_con = False
        self.serial_motor_x_con = False
        self.serial_motor_y_con = False
        self.loadcell_data.stop()
        self.CT_LVDT.stop()
        self.CT_motor_X.stop()
        self.main_frame.con_port_pushButton.setEnabled(True)
        self.main_frame.con_port_pushButton.setStyleSheet(u"background:rgb(170, 255, 0)")
        self.clear_loadcell_data()
        self.clear_displace_data()
        self.main_frame.dis_port_pushButton.setEnabled(False)
        self.main_frame.dis_port_pushButton.setStyleSheet(u"background:gray")
        self.disable_ui_parameter()
    
    def update_loadcell_data(self,load_cell_value):
        self.loadcell_X = load_cell_value[1]
        self.loadcell_Y = load_cell_value[0]
        self.loadcell_X = float(self.loadcell_X)
        self.loadcell_Y = float(self.loadcell_Y)
        self.loadcell_X = round(self.loadcell_X * 0.0098, 3)
        self.loadcell_Y = round(self.loadcell_Y * 0.0098, 3)
        self.main_frame.test_weight_y_lineEdit.setText(str(self.loadcell_Y))
        self.main_frame.test_weight_x_lineEdit.setText(str(self.loadcell_X))
        self.main_frame.r_weight_x_lineEdit.setText(str(self.loadcell_X))
        self.main_frame.r_weight_y_lineEdit.setText(str(self.loadcell_Y))
    
    def update_displace_data(self,disxy_data):
        self.dis_x = disxy_data[0]
        self.dis_y = disxy_data[1]
        # ==================== set zero displace ====================
        if self.set_zero_x_data:
            self.zero_x_reference = float(self.dis_x) 
            self.set_zero_x_data = False
        self.dis_x = float(self.dis_x) - self.zero_x_reference
        self.dis_x = round(float(self.dis_x),3)
        self.dis_x = str(self.dis_x)
        self.main_frame.test_dis_x_lineEdit.setText(self.dis_x)
        self.main_frame.dis_set_zero_x_lineEdit.setText(self.dis_x)
        if self.set_zero_y_data:
            self.set_y_reference = float(self.dis_y)
            self.set_zero_y_data = False
        self.dis_y = float(self.dis_y) - self.set_y_reference
        self.dis_y = round(float(self.dis_y),3)
        self.dis_y = str(self.dis_y)
        self.main_frame.test_dis_y_lineEdit.setText(self.dis_y)
        self.main_frame.dis_set_zero_y_lineEdit.setText(self.dis_y)
        # ==================== set zero displace ====================
        
    def set_zero_displace_x(self):
        self.set_zero_x_data = True
        self.test_set_zero_x = True

    def set_zero_displace_y(self):
        self.set_zero_y_data = True  
        self.test_set_zero_y = True
    
    def monotonic_selected(self):
        self.monotonic_UI()
        self.monotonic_test = True
        self.cyclic_test = False
        
    def cyclic_selected(self):
        self.cyclic_UI()
        self.cyclic_test = True
        self.monotonic_test = False
    
    def m_up_pressed(self):
        self.CT_motor_Y.up_motors_y()
        
    def m_down_pressed(self):
        self.CT_motor_Y.down_motors_y()
    
    def m_in_pressed(self):
        self.CT_motor_X.in_motors_x()
        
    def m_out_pressed(self):
        self.CT_motor_X.out_motors_x()
        
    def stop_all_motors(self):
        self.CT_motor_Y.stop_motors_y()
        self.delay(0.5)
        self.CT_motor_X.stop_motors_x()
        
    def connect_serial_XY(self):
        self.serial_consuc = True
    
    def connect_serial_arduino(self):
        self.serial_ar_con = True
        
    def connect_serial_motor_x(self):
        self.serial_motor_x_con = True
        
    def connect_serial_motor_y(self):
        self.serial_motor_y_con = True
        
        
    def set_zero_button_pressed(self):
        print("Set Zero Clicked")
        
    def calibrate_button_pressed(self):
        print("Calibrate Clicked")

    def monotonic_UI(self):
        self.main_frame.st_cyclic_lineEdit.setEnabled(False)
        self.main_frame.st_weight_x_lineEdit.setEnabled(False)
        self.main_frame.st_weight_y_lineEdit.setEnabled(True)
        self.main_frame.st_K_lineEdit.setEnabled(True)
        self.main_frame.st_cyclic_lineEdit.clear()
        self.main_frame.st_weight_x_lineEdit.clear()
        self.main_frame.st_weight_y_lineEdit.clear()
        self.main_frame.st_K_lineEdit.clear()
        self.main_frame.st_cyclic_lineEdit.setStyleSheet(u"background:gray")
        self.main_frame.st_weight_x_lineEdit.setStyleSheet(u"background:gray")
        self.main_frame.st_weight_y_lineEdit.setStyleSheet(u"background:white")
        self.main_frame.st_K_lineEdit.setStyleSheet(u"background:white")
        self.main_frame.st_cyclic_lineEdit.setPlaceholderText("None")
        self.main_frame.st_weight_x_lineEdit.setPlaceholderText("None")
        
    def cyclic_UI(self):
        self.main_frame.st_cyclic_lineEdit.setEnabled(True)
        self.main_frame.st_weight_x_lineEdit.setEnabled(True)
        self.main_frame.st_weight_y_lineEdit.setEnabled(True)
        self.main_frame.st_K_lineEdit.setEnabled(True)
        self.main_frame.st_cyclic_lineEdit.clear()
        self.main_frame.st_weight_x_lineEdit.clear()
        self.main_frame.st_weight_y_lineEdit.clear()
        self.main_frame.st_K_lineEdit.clear()
        self.main_frame.st_cyclic_lineEdit.setStyleSheet(u"background:white")
        self.main_frame.st_weight_x_lineEdit.setStyleSheet(u"background:white")
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
        self.main_frame.test_k_set_pushButton.setEnabled(False)
        self.main_frame.dis_port_pushButton.setStyleSheet(u"background:gray")
        self.main_frame.test_k_set_pushButton.setStyleSheet(u"background:gray")
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
        read_area = self.main_frame.st_Area_lineEdit.text() 
        self.databass_controller.set_parameter_to_setting(read_pwmx,read_pwmy,read_limit_wx,read_limit_wy,read_limit_dx,read_limit_dy,read_area)
        
        self.show_massege_box_info("SAVE","save parameter success")
        self.disable_ui_parameter()
        self.CT_motor_X.get_setting_speed(read_pwmy)
        self.delay(1)
        self.CT_motor_Y.get_setting_speed(read_pwmx)
    
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
        
    def enable_ui_parameter(self):
        self.main_frame.st_config_pushButton.setEnabled(False)
        self.main_frame.st_save_pushButton.setEnabled(True)
        self.main_frame.st_pwm_x_lineEdit.setEnabled(True)
        self.main_frame.st_pwm_y_lineEdit.setEnabled(True)
        self.main_frame.st_limit_weight_x_lineEdit.setEnabled(True)
        self.main_frame.st_limit_weight_y_lineEdit.setEnabled(True)
        self.main_frame.st_limit_distance_x_lineEdit.setEnabled(True)
        self.main_frame.st_limit_distance_y_lineEdit.setEnabled(True)
        self.main_frame.st_Area_lineEdit.setEnabled(True)
        self.main_frame.st_config_pushButton.setStyleSheet(u"background:gray")
        self.main_frame.st_save_pushButton.setStyleSheet(u"background:rgb(170, 255, 0)")
        self.main_frame.st_pwm_x_lineEdit.setStyleSheet(u"background:white")
        self.main_frame.st_pwm_y_lineEdit.setStyleSheet(u"background:white")
        self.main_frame.st_limit_weight_x_lineEdit.setStyleSheet(u"background:white")
        self.main_frame.st_limit_weight_y_lineEdit.setStyleSheet(u"background:white")
        self.main_frame.st_limit_distance_x_lineEdit.setStyleSheet(u"background:white")
        self.main_frame.st_limit_distance_y_lineEdit.setStyleSheet(u"background:white")
        self.main_frame.st_Area_lineEdit.setStyleSheet(u"background:white")
        
    def disable_ui_parameter(self):
        self.main_frame.st_config_pushButton.setEnabled(True)
        self.main_frame.st_save_pushButton.setEnabled(False)
        self.main_frame.st_pwm_x_lineEdit.setEnabled(False)
        self.main_frame.st_pwm_y_lineEdit.setEnabled(False)
        self.main_frame.st_limit_weight_x_lineEdit.setEnabled(False)
        self.main_frame.st_limit_weight_y_lineEdit.setEnabled(False)
        self.main_frame.st_limit_distance_x_lineEdit.setEnabled(False)
        self.main_frame.st_limit_distance_y_lineEdit.setEnabled(False)
        self.main_frame.st_Area_lineEdit.setEnabled(False)
        self.main_frame.st_config_pushButton.setStyleSheet(u"background:rgb(115, 174, 253)")
        self.main_frame.st_save_pushButton.setStyleSheet(u"background:gray")
        self.main_frame.st_pwm_x_lineEdit.setStyleSheet(u"background:gray")
        self.main_frame.st_pwm_y_lineEdit.setStyleSheet(u"background:gray")
        self.main_frame.st_limit_weight_x_lineEdit.setStyleSheet(u"background:gray")
        self.main_frame.st_limit_weight_y_lineEdit.setStyleSheet(u"background:gray")
        self.main_frame.st_limit_distance_x_lineEdit.setStyleSheet(u"background:gray")
        self.main_frame.st_limit_distance_y_lineEdit.setStyleSheet(u"background:gray")
        self.main_frame.st_Area_lineEdit.setStyleSheet(u"background:gray")
        
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
        self.grap_weight_y = 0.05
        self.monotonic_k_param = 0.0
        self.new_sigma_y = 0.0
        self.new_sigma_y_sum = 0.0
        self.set_k_param_success = False
        self.main_frame.test_k_set_pushButton.setEnabled(True)
        self.main_frame.test_k_set_pushButton.setStyleSheet(u"background:rgb(206, 223, 255)")
        self.main_frame.test_output_textEdit.append("START MONOTONIC TEST")
        self.area_test_monotonic = float(self.main_frame.st_Area_lineEdit.text())
        
        while self.mono_test:
            
            self.calculate_k_every_time.emit()
            self.delay(1)
            self.runing_mono_test.emit(self.new_sigma_y_sum)
            self.delay(1)
            if self.monotonic_state == 1: #กดให้ได้ค่าน้ำหนักที่ต้องการ Y
                self.main_frame.test_output_textEdit.append("move Y to weight seting")
                self.start_monotonic_load_y_input = True
                self.CT_motor_Y.down_motors_y()
                self.monotonic_state = 2                
                
            elif self.monotonic_state == 2: #กดให้ได้ค่าน้ำหนักที่ต้องการ X
                if self.load_cell_y_test >= self.weight_y_recommand +- self.grap_weight_y:
                    self.CT_motor_Y.stop_motors_y()
                    self.lock_export_data = True
                    self.monotonic_state = 3
                    
            elif self.monotonic_state == 3: 
                self.show_message_info.emit("SET PARAMETER","โปรด SET ZERO ตำแหน่ง X และ Y และ SET K PARAMETER")
                self.diff_dis_y = 0.0
                self.monotonic_state = 4
                
            elif self.monotonic_state == 4:
                self.start_monotonic_load_y_input = False
                if self.set_k_param_success == True:
                    self.lock_export_data = False
                    self.monotonic_k_param = float(self.main_frame.st_K_lineEdit.text())
                    self.main_frame.test_k_set_pushButton.setEnabled(False)
                    self.main_frame.test_k_set_pushButton.setStyleSheet(u"background:gray")
                    time.sleep(3)
                    self.show_test()
                    self.monotonic_state = 5
                else:
                    # print("wait")
                    pass
            
            elif self.monotonic_state == 5:
                self.main_frame.test_output_textEdit.append(f"start chearacteristic test K = {self.monotonic_k_param}")
                if self.round_data_monotonic < 5:
                    self.new_sigma_y = 0.0
                    self.diff_dis_y = 0.0
                    self.old_dis_y = 0.0
                self.delay(3)
                self.start_monotonic_calculate_k = True
                self.delay(1.5)
                self.start_monotonic_k_control = True
                self.m_in_pressed()
                self.monotonic_state = 6
            
            elif self.monotonic_state == 6:
                if self.dis_x_mono >= self.limit_distance_x:
                    self.CT_motor_X.stop_motors_x()
                    self.monotonic_state = 7    
            
            elif self.monotonic_state == 7:
                self.show_message_info.emit("END TEST","เสร็จสิ้นการทดลองกรุณาใช้ระบบแมนนวลเพื่อถอยแกน X กลับ")
                self.start_monotonic_k_control = False
                self.CT_motor_Y.stop_motors_y()
                self.monotonic_state = 8
            
            elif self.monotonic_state == 8:
                pass
            
            elif self.monotonic_state == 666:#is debug case 666  
                self.calculte_k_start = Thread(target=self.calculate_k_parameter)
                self.calculte_k_start.start()
            
            

                
                
    # def run_k_mono_test(self,new_sigma_mono):
    #     # print(new_sigma_mono)
        
    #     if self.start_monotonic_k_control == True:
    #         if new_sigma_mono >= self.sigma_y :
    #             self.CT_motor_Y.down_motors_y()
                
    #         if new_sigma_mono <= self.sigma_y :
    #             self.CT_motor_Y.up_motors_y()
                
    #         if new_sigma_mono == self.sigma_y:
    #             self.CT_motor_Y.stop_motors_y()
            
            
    def pid_control(self, setpoint, pv, kp, ki, kd, dt):
        error = setpoint - pv
        self.integral = getattr(self, 'integral', 0) + error * dt
        derivative = (error - getattr(self, 'previous_error', 0)) / dt
        output = kp * error + ki * self.integral + kd * derivative
        self.previous_error = error
        return output

    def run_k_mono_test(self, new_sigma_mono):
        if self.start_monotonic_k_control:
            dt = 0.1  # time step
            kp = 1.0  # proportional gain
            ki = 0.1  # integral gain
            kd = 0.05  # derivative gain
            control_signal = self.pid_control(self.sigma_y, new_sigma_mono, kp, ki, kd, dt)
            
            if control_signal > 0:
                self.CT_motor_Y.down_motors_y()
            elif control_signal < 0:
                self.CT_motor_Y.up_motors_y()
            else:
                self.CT_motor_Y.stop_motors_y()
    
    def calculate_k_parameter(self):
        if self.lock_export_data == False:
            self.limit_weight_y = float(self.main_frame.st_limit_weight_y_lineEdit.text())
            self.limit_weight_x = float(self.main_frame.st_limit_weight_x_lineEdit.text())
            self.limit_distance_x = float(self.main_frame.st_limit_distance_x_lineEdit.text())
            self.limit_distance_y = float(self.main_frame.st_limit_distance_y_lineEdit.text())
            self.weight_y_recommand = float(self.main_frame.st_weight_y_lineEdit.text())
            self.load_cell_y_test = float(self.main_frame.test_weight_y_lineEdit.text())
            self.dis_x_mono = round(float(self.main_frame.test_dis_x_lineEdit.text()),3)
            
            self.sigma_y = round(self.load_cell_y_test/self.area_test_monotonic,3) ## คำนวณค่าแรงต่อพื้นที่
            
            print(self.monotonic_k_param,self.sigma_y,self.new_sigma_y)
            
            if self.start_monotonic_calculate_k == True:
                self.old_dis_y = getattr(self, 'old_dis_y', 0.0)
                self.diff_dis_y = round(float(self.dis_y) - (self.old_dis_y),3)

                self.new_sigma_y = round( (self.diff_dis_y) * ( self.monotonic_k_param + self.sigma_y ) ,3)
                
                self.new_sigma_y_sum = round((self.sigma_y)+(self.new_sigma_y),3) 
                
                # print(f"new sigma {self.new_sigma_y}, old sigma {self.sigma_y}, new sigma sum {self.new_sigma_y_sum} , diff {self.diff_dis_y}")
                
                self.round_data_monotonic += 1
                self.timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                self.main_frame.test_output_textEdit.append(f"{self.timestamp} , {self.dis_y} , {self.old_dis_y} , {self.diff_dis_y} , {self.dis_x}  , {self.loadcell_Y} , {self.loadcell_X} , {self.sigma_y} , {self.new_sigma_y_sum} ,{self.round_data_monotonic}")
                self.old_dis_y = float(self.dis_y)
                
            if self.start_monotonic_load_y_input == True:
                self.round_data_monotonic += 1
                self.old_dis_y = getattr(self, 'old_dis_y', 0.0)
                self.diff_dis_y = round(float(self.dis_y) - self.old_dis_y,3)
                self.timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                self.main_frame.test_output_textEdit.append(f"{self.timestamp} , {self.dis_y} , {self.old_dis_y} , {self.diff_dis_y} , {self.dis_x}   , {self.loadcell_Y} , {self.loadcell_X} , {self.sigma_y} , {self.new_sigma_y_sum},{self.round_data_monotonic}")
                self.old_dis_y = float(self.dis_y)
            else:
                pass
        else:
            self.limit_weight_y = 0.0
            self.limit_weight_x = 0.0
            self.limit_distance_x = 0.0
            self.limit_distance_y = 0.0
            self.weight_y_recommand = 0.0
            self.load_cell_y_test = 0.0
            self.dis_x_mono = 0.0
            self.sigma_y = 0.0
            self.new_sigma_y = 0.0
            self.new_sigma_y_sum = 0.0
            self.diff_dis_y = 0.0
            self.old_dis_y = 0.0


    def start_monotonic_test(self):
        self.mono_test = True
        self.lock_export_data = False
        self.monotonic_state = 1 #useing 1
        self.round_data_monotonic = 0
        # self.monotonic_state = 666 #Debug 666
        # self.start_monotonic_calculate_k = True
        # self.monotonic_k_param = float(self.main_frame.st_K_lineEdit.text())#deboger
        self.monotonic_thread = Thread(target=self.run_monotonic_test)
        self.monotonic_thread.start()

    def stop_monotonic_test(self):
        self.mono_test = False
        self.start_monotonic_calculate_k = False
        self.start_monotonic_k_control = False
        self.monotonic_state = 0
        self.stop_all_motors()
        self.monotonic_thread.join()
        
# ============== SAVE CLEAR ====================
    def test_save_button_pressed(self):
        # Get the data from the text edit
        data = self.main_frame.test_output_textEdit.toPlainText()
        
        # Ask user for file name
        file_name, _ = QFileDialog.getSaveFileName(self.main_frame, "Save File", "", "CSV Files (*.csv);;Text Files (*.txt)")
        if file_name.endswith('.csv'):
            with open(file_name, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["time", "Dis Y(Dv)","Dis Y Old(Dv)" , "difference Dis Y" ,"Dis X(Dh)", "loadcell Y (KN)", "loadcell X (KN)", "sigma Y (KN/M^2)", "newsigma Y (KN/M^2)","round data"])
                for line in data.split('\n'):
                    writer.writerow(line.split(','))
        elif file_name.endswith('.txt'):
            with open(file_name, 'w', encoding='utf-8') as txtfile:
                txtfile.write(data)
            self.show_message_info.emit("SAVE", f"Data saved to {file_name}")
        else:
            self.show_message_info.emit("SAVE", "Save operation cancelled")
        
    def test_clear_button_pressed(self):
        self.clear_data_frame()
# ============== test monotonic ====================
    def delay(self,seconds):
        start_time = time.perf_counter()
        while time.perf_counter() - start_time < seconds:
            pass  # ทำงานอื่นต่อไปได้

    def clear_data_frame(self):
        self.main_frame.test_output_textEdit.clear()
