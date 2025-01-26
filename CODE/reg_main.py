import sys
from PySide6.QtWidgets import QApplication
from Controller.main_controller import MainController


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_app = MainController()
    main_app.Show_main()
    app.exec()
    
