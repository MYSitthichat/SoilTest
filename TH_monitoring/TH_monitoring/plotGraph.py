import sys
import mariadb
import numpy as np
import pyqtgraph as pg
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QMessageBox
from PySide6.QtCore import Qt, QTimer
import numpy as np
import datetime

# Database Configuration
DB_CONFIG = {
    "user": "username",             # Replace with your own username and password
    "password": "password",
    "host": "localhost",
    "database": "sensor_databases"
}


# Connect to MariaDB
def connect_database():
    try:
        conn = mariadb.connect(**DB_CONFIG)
        return conn
    except mariadb.Error as e:
        QMessageBox.critical(None, "Database Error", f"Error connecting to database: {e}")
        sys.exit(1)

# Fetch the last 10 records for each sensor type
def fetch_data():
    conn = connect_database()
    cursor = conn.cursor()

    # Fetch last 10 humidity readings
    cursor.execute("SELECT dTime, node, humidity FROM humidity ORDER BY dTime DESC LIMIT 10")
    humidity_data = cursor.fetchall()

    # Fetch last 10 temperature readings
    cursor.execute("SELECT dTime, node, temperature FROM temperature ORDER BY dTime DESC LIMIT 10")
    temperature_data = cursor.fetchall()

    conn.close()
    
    return humidity_data, temperature_data

class SensorPlotter(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Sensor Data Visualization")
        self.setGeometry(100, 100, 800, 600)

        # Create main widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Create plots
        self.temp_plot = pg.PlotWidget(title="Temperature Sensors")
        self.humidity_plot = pg.PlotWidget(title="Humidity Sensors")

        layout.addWidget(self.temp_plot)
        layout.addWidget(self.humidity_plot)

        # Setup plots
        self.setup_plots()

        # Timer to refresh data every 5 seconds
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_plots)
        self.timer.start(5000)  # Refresh every 5 seconds

        # Initial plot
        self.update_plots()

    def setup_plots(self):
        """Setup graph properties"""
        self.temp_plot.setLabel('left', 'Temperature (°C)')
        self.temp_plot.setLabel('bottom', 'Timestamp')
        self.temp_plot.addLegend()
        self.temp_plot.showGrid(x=True, y=True)

        self.humidity_plot.setLabel('left', 'Humidity (%)')
        self.humidity_plot.setLabel('bottom', 'Timestamp')
        self.humidity_plot.addLegend()
        self.humidity_plot.showGrid(x=True, y=True)

    def update_plots(self):
        """Fetch data and update the plots"""
        humidity_data, temperature_data = fetch_data()

        # Sort by timestamp (oldest first)
        humidity_data = sorted(humidity_data, key=lambda x: x[0])
        temperature_data = sorted(temperature_data, key=lambda x: x[0])

        # Convert data for plotting
        temp_timestamps, temp_sensors = self.process_data(temperature_data)
        hum_timestamps, hum_sensors = self.process_data(humidity_data)

        # Clear previous plots
        self.temp_plot.clear()
        self.humidity_plot.clear()

        # Plot temperature sensors
        colors = ['r', 'g', 'b']  # Colors for different sensors
        for i, node in enumerate(temp_sensors.keys()):
            self.temp_plot.plot(temp_timestamps, temp_sensors[node], pen=colors[i], name=f"Temp Sensor {node}")

        # Plot humidity sensors
        for i, node in enumerate(hum_sensors.keys()):
            self.humidity_plot.plot(hum_timestamps, hum_sensors[node], pen=colors[i], name=f"Hum Sensor {node}")

    def process_data(self, data):
        """Process fetched data into aligned timestamps and sensor values"""
        timestamps = sorted(set(dTime for dTime, _, _ in data))  # Unique, sorted timestamps
        sensor_data = {}

        # Convert timestamps to datetime only if they are strings
        if isinstance(timestamps[0], str):  
            timestamps_dt = [datetime.datetime.strptime(t, "%Y-%m-%d %H:%M:%S") for t in timestamps]
        else:
            timestamps_dt = timestamps  # Already in datetime format

        # Convert to float (Unix timestamps)
        timestamps_numeric = np.array([t.timestamp() for t in timestamps_dt], dtype=np.float64)

        # Initialize sensor_data with NaN values
        for _, node, _ in data:
            if node not in sensor_data:
                sensor_data[node] = np.full(len(timestamps), np.nan, dtype=np.float64)

        # Fill actual values
        for dTime, node, value in data:
            index = timestamps.index(dTime)  # Find correct timestamp index
            sensor_data[node][index] = np.float64(value)  # Ensure numerical values

        return timestamps_numeric, sensor_data  # X-axis in float format, Y-axis as dict of NumPy arrays

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SensorPlotter()
    window.show()
    sys.exit(app.exec())
