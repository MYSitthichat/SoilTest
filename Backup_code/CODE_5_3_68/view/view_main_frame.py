from PySide6.QtWidgets import QMainWindow
from view.main_frame import Ui_MAIN

class MainFrame(QMainWindow,Ui_MAIN):
    def __init__(self, parent=None):
        super(MainFrame, self).__init__(parent)
        self.setupUi(self)

    def show_home_page(self):
        self.stackedWidget.setCurrentIndex(0)
        self.show()

    def show_calibate_page(self):
        self.stackedWidget.setCurrentIndex(1)
        self.show()

    def show_test_page(self):
        self.stackedWidget.setCurrentIndex(2)
        self.show()

    def show_setting_page(self):
        self.stackedWidget.setCurrentIndex(3)
        self.show()
