import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QMessageBox
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import mariadb
import matplotlib.dates as mdates
import matplotlib.ticker as ticker

ticker.Locator.MAXTICKS = 2000  # Increase the limit

# Database Configuration
DB_CONFIG = {
    "user": "soiltester",
    "password": "111777000",
    "host": "localhost",
    "database": "soil_tester"
}

# Connect to MariaDB
def connect_database():
    try:
        conn = mariadb.connect(**DB_CONFIG)
        return conn
    except mariadb.Error as e:
        QMessageBox.critical(None, "Database Error", f"Error connecting to database: {e}")
        sys.exit(1)

# Fetch the last record for each sensor type
def fetch_data():
    conn = connect_database()
    cursor = conn.cursor()
    
    # Fx,Fy,Dx,Dy,Kn

    sql_cmd = "SELECT dTime, Fx,Fy,Dx,Dy,Kn FROM results ORDER BY dTime DESC LIMIT 1"
    cursor.execute(sql_cmd)
    data = cursor.fetchall()
    conn.close()
    
    dTime = data[0][0]
    # find everage of the data
    Fx = sum([x[1] for x in data]) / len(data)
    Fy = sum([x[2] for x in data]) / len(data)
    Dx = sum([x[3] for x in data]) / len(data)
    Dy = sum([x[4] for x in data]) / len(data)
    Kn = sum([x[5] for x in data]) / len(data)
    
    return dTime, Fx, Fy, Dx, Dy, Kn

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Temperature and Humidity Plotter")
        # Data initialization
        self.dTime = []
        self.Fx = []
        self.Fy = []
        self.Dx = []
        self.Dy = []
        self.Kn = []


        # Create Matplotlib figures and canvases
        self.fig_force = Figure()
        self.canvas_force = FigureCanvas(self.fig_force)
        self.ax_force = self.fig_force.add_subplot(111)
        
        self.fig_displacement = Figure()
        self.canvas_displacement = FigureCanvas(self.fig_displacement)
        self.ax_dis = self.fig_displacement.add_subplot(111)

        self.fig_Kn = Figure()
        self.canvas_Kn = FigureCanvas(self.fig_Kn)
        self.ax_Kn = self.fig_Kn.add_subplot(111)


        # Layout
        v_layout = QVBoxLayout()

        force_layout = QVBoxLayout()
        force_layout.addWidget(self.canvas_force)

        displacement_layout = QVBoxLayout()
        displacement_layout.addWidget(self.canvas_displacement)
        
        Kn_layout = QVBoxLayout()
        Kn_layout.addWidget(self.canvas_Kn)

        v_layout.addLayout(force_layout)
        v_layout.addLayout(displacement_layout)
        v_layout.addLayout(Kn_layout)

        self.setLayout(v_layout)

        # Initialize plots
        self.line_force_x, = self.ax_force.plot([], [], label='Fx')
        self.line_force_y, = self.ax_force.plot([], [], label='Fy')
        
        self.line_dis_x, = self.ax_dis.plot([], [], label='Dx')
        self.line_dis_y, = self.ax_dis.plot([], [], label='Dy')
        
        self.line_Kn, = self.ax_Kn.plot([], [], label='Kn')



        # self.ax_temp.set_xlabel("Time")
        self.ax_force.set_ylabel("Force")
        self.ax_force.legend()
        self.ax_force.legend(loc='upper right')

        # self.ax_humidity.set_xlabel("Time")
        self.ax_dis.set_ylabel("Diplacement")
        self.ax_dis.legend()
        # set legend on top of the plot
        self.ax_dis.legend(loc='upper right')
        
        self.ax_Kn.set_ylabel("Kn")
        self.ax_Kn.legend()
        self.ax_Kn.legend(loc='upper right')
        

        self.timer = self.startTimer(100)  # Update every 10 seconds

        # Adjust plot margins
        self.fig_force.subplots_adjust(left=0.05, right=0.95, bottom=0.1, top=0.9)
        self.fig_displacement.subplots_adjust(left=0.05, right=0.95, bottom=0.1, top=0.9)
        self.fig_Kn.subplots_adjust(left=0.05, right=0.95, bottom=0.1, top=0.9)

        self.generate_data()
        self.update_plots()

        self.resize(1800, 900)
        self.show()

    def timerEvent(self, event):
        self.generate_data()
        self.update_plots()
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.canvas_force.draw_idle()
        self.canvas_displacement.draw_idle()
        self.canvas_Kn.draw_idle()

    def generate_data(self):
        # get data from the database
        dTime,Fx,Fy,Dx,Dy,Kn = fetch_data()
        
        # append the data to the lists for plotting
        self.dTime.append(dTime)
        self.Fx.append(Fx)
        self.Fy.append(Fy)
        self.Dx.append(Dx)
        self.Dy.append(Dy)
        self.Kn.append(Kn)

        # Limit data points to 20
        
        self.dTime = self.dTime[-10:]
        self.Fx = self.Fx[-10:]
        self.Fy = self.Fy[-10:]
        self.Dx = self.Dx[-10:]
        self.Dy = self.Dy[-10:]
        self.Kn = self.Kn[-10:]

    def update_plots(self):
        formatter = mdates.DateFormatter('%H:%M')  # Specify the HH:MM:SS format
        # Update force plot
        self.line_force_x.set_data(self.dTime, self.Fx)
        self.line_force_y.set_data(self.dTime, self.Fy)
        self.ax_force.xaxis.set_major_formatter(formatter)
        self.ax_force.xaxis.set_major_locator(mdates.MinuteLocator(interval=1))
        
        self.ax_force.relim()
        self.ax_force.autoscale_view()

        # Update displacement plot
        self.line_dis_x.set_data(self.dTime, self.Dx)
        self.line_dis_y.set_data(self.dTime, self.Dy)
        self.ax_dis.xaxis.set_major_formatter(formatter)
        self.ax_dis.xaxis.set_major_locator(mdates.MinuteLocator(interval=1))
        
        self.ax_dis.relim()
        self.ax_dis.autoscale_view()

        # update Kn plot
        self.line_Kn.set_data(self.dTime, self.Kn)
        self.ax_Kn.xaxis.set_major_formatter(formatter)
        self.ax_Kn.xaxis.set_major_locator(mdates.MinuteLocator(interval=1))
        
        self.ax_Kn.relim()
        self.ax_Kn.autoscale_view()
        
        self.canvas_force.draw()
        self.canvas_displacement.draw()
        self.canvas_Kn.draw()




if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())
