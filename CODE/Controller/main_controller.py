from PySide6.QtCore import QObject , Signal , Slot
from view.view_main_frame import MainFrame
from Controller.databass_controller import DatabassController
from Controller.check_comport_controller import SerialPortChecker
import serial as ser
from PySide6.QtWidgets import QMessageBox
from Controller.read_loadcell import Readloadcell

class MainController(QObject):
    
    def __init__(self):
        super(MainController, self).__init__()
        self.main_frame = MainFrame()
        self.check_port_controller = SerialPortChecker()
        self.databass_controller = DatabassController()
        self.loadcell_data = Readloadcell()
        self.check_port_controller.start()
        self.loadcell_data.connect_serial_XY_signal.connect(self.connect_serial_XY)
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
        self.databass_controller.create_databass()
        self.databass_controller.check_record_setting()
        self.databass_controller.list_for_parameter.connect(self.show_parameter)
        self.loadcell_data.load_cell_data.connect(self.update_loadcell_data)
        self.serial_consuc =False
        self.start_program()
        
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
            self.main_frame.Arduino_Port_comboBox.setEnabled(False)
            self.main_frame.Arduino_Port_comboBox.clear()
            self.main_frame.Arduino_Port_comboBox.addItem("None")
        else:
            self.main_frame.LY_Port_comboBox.clear()
            self.main_frame.LY_Port_comboBox.setEnabled(True)
            self.main_frame.LX_Port_comboBox.clear()
            self.main_frame.LX_Port_comboBox.setEnabled(True)
            self.main_frame.Arduino_Port_comboBox.clear()
            self.main_frame.Arduino_Port_comboBox.setEnabled(True)
            for port in ports:
                self.main_frame.LY_Port_comboBox.addItem(port.device)
                self.main_frame.LX_Port_comboBox.addItem(port.device)
                self.main_frame.Arduino_Port_comboBox.addItem(port.device)

    def start_button_pressed(self):
        print("Start Clicked")
        
    def stop_button_pressed(self):
        print("Stop Clicked")
        
    def clear_button_pressed(self):
        print("Clear Clicked")
        
    def save_button_pressed(self):
        print("Save Clicked")
    
    def show_parameter(self):
        # self.databass_controller.set_parameter_to_setting()
        print("Show Parameter")

    def con_port_pressed(self):
        self.loadcell_Y_comport = self.main_frame.LY_Port_comboBox.currentText()
        self.loadcell_X_comport = self.main_frame.LX_Port_comboBox.currentText()
        self.arduino_comport = self.main_frame.Arduino_Port_comboBox.currentText()
        self.loadcell_data.get_comport(self.loadcell_Y_comport,self.loadcell_X_comport)
        self.loadcell_data.running = True
        self.loadcell_data.start()
        try:
            self.arduino_serial = ser.Serial(port=self.arduino_comport, baudrate=9600, timeout=1)
            if self.serial_consuc == True & self.arduino_serial.is_open:
                msg_box = QMessageBox()
                msg_box.setIcon(QMessageBox.Information)
                msg_box.setWindowTitle("COMPORT CON")
                msg_box.setText(f"CONNECTED \n L1 to{self.loadcell_Y_comport} \n L2 to{self.loadcell_X_comport} \nArduino to{self.arduino_comport}")
                msg_box.exec()
                self.main_frame.LY_Port_comboBox.setEnabled(False)
                self.main_frame.LY_Port_comboBox.setStyleSheet(u"background:gray")
                self.main_frame.LX_Port_comboBox.setEnabled(False)
                self.main_frame.LX_Port_comboBox.setStyleSheet(u"background:gray")
                self.main_frame.Arduino_Port_comboBox.setEnabled(False)
                self.main_frame.Arduino_Port_comboBox.setStyleSheet(u"background:gray")
                self.main_frame.con_port_pushButton.setEnabled(False)
                self.main_frame.con_port_pushButton.setStyleSheet(u"background:gray")
                self.main_frame.dis_port_pushButton.setEnabled(True)
                self.main_frame.dis_port_pushButton.setStyleSheet(u"background:rgb(252, 65, 54)")
        except ser.SerialException as e:
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Critical)
            msg_box.setWindowTitle("COMPORT CON ERROR")
            msg_box.setText(f"Failed to connect to {e} \n please check the comport")
            msg_box.exec()
            
    def discon_port_pressed(self):
        self.arduino_serial.close()
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle("Dis Connected")
        msg_box.setText(f"DIS CONNECTED \n L1 to{self.loadcell_Y_comport} \n L2 to{self.loadcell_X_comport} \nArduino to{self.arduino_comport}")
        msg_box.exec()
        self.main_frame.LY_Port_comboBox.setEnabled(True)
        self.main_frame.LY_Port_comboBox.setStyleSheet(u"background:white")
        self.main_frame.LX_Port_comboBox.setEnabled(True)
        self.main_frame.LX_Port_comboBox.setStyleSheet(u"background:white")
        self.main_frame.Arduino_Port_comboBox.setEnabled(True)
        self.main_frame.Arduino_Port_comboBox.setStyleSheet(u"background:white")
        self.serial_consuc = False
        self.loadcell_data.stop()
        self.main_frame.con_port_pushButton.setEnabled(True)
        self.main_frame.con_port_pushButton.setStyleSheet(u"background:rgb(170, 255, 0)")
        self.clear_loadcell_data()
    
    def update_loadcell_data(self,load_cell_value):
        loadcell_Y = load_cell_value[0]
        loadcell_X = load_cell_value[1]
        self.main_frame.test_weight_y_lineEdit.setText(loadcell_Y)
        self.main_frame.test_weight_x_lineEdit.setText(loadcell_X)
        self.main_frame.r_weight_x_lineEdit.setText(loadcell_X)
        self.main_frame.r_weight_y_lineEdit.setText(loadcell_Y)
        
    
    def connect_serial_XY(self):
        self.serial_consuc = True
    
    def config_button_pressed(self):
        print("Config Clicked")
        
    def save_button_pressed(self):
        print("Save Clicked")
    
    def set_zero_button_pressed(self):
        print("Set Zero Clicked")
        
    def calibrate_button_pressed(self):
        print("Calibrate Clicked")


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

    def start_program(self):
        self.main_frame.test_weight_x_lineEdit.setEnabled(False)
        self.main_frame.test_weight_y_lineEdit.setEnabled(False)
        self.main_frame.r_weight_x_lineEdit.setEnabled(False)
        self.main_frame.r_weight_y_lineEdit.setEnabled(False)
        self.main_frame.dis_port_pushButton.setEnabled(True)
        self.main_frame.dis_port_pushButton.setStyleSheet(u"background:gray")
        
    def clear_loadcell_data(self):
        self.main_frame.test_weight_x_lineEdit.clear()
        self.main_frame.test_weight_y_lineEdit.clear()
        self.main_frame.r_weight_x_lineEdit.clear()
        self.main_frame.r_weight_y_lineEdit.clear()