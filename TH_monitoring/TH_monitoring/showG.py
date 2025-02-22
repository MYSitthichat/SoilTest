import sys
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QGroupBox)
from PySide6.QtCharts import QChartView, QLineSeries, QChart, QDateTimeAxis, QValueAxis
from PySide6.QtCore import Qt, QDateTime, QTimer
from random import random  # For simulated data


class SensorDataVisualization(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Sensor Data Visualization")

        main_layout = QVBoxLayout()

        # Temperature Sensors Group
        temp_group = QGroupBox("Temperature Sensors")
        temp_layout = QVBoxLayout()

        self.temp_chart_view = QChartView()
        self.temp1_chart = QChart()
        self.temp2_chart = QChart()
        self.temp3_chart = QChart()
        self.temp_chart_view.setChart(self.temp1_chart)
        self.temp_chart_view.setChart(self.temp2_chart)
        self.temp_chart_view.setChart(self.temp3_chart)
        temp_layout.addWidget(self.temp_chart_view)
        temp_group.setLayout(temp_layout)
        main_layout.addWidget(temp_group)

        # Humidity Sensors Group
        humidity_group = QGroupBox("Humidity Sensors")
        humidity_layout = QVBoxLayout()

        self.humidity_chart_view = QChartView()
        self.humidity_chart = QChart()
        self.humidity_chart_view.setChart(self.humidity_chart)
        humidity_layout.addWidget(self.humidity_chart_view)
        humidity_group.setLayout(humidity_layout)
        main_layout.addWidget(humidity_group)

        self.setLayout(main_layout)

        self.setup_charts()

        # Timer for dynamic updates (optional - if you have live data)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_data)
        self.timer.start(1000)  # Update every 1000ms (1 second)

    def setup_charts(self):
        # Temperature Chart
        self.temp_series = QLineSeries()

        # Example data (replace with your actual data)
        temp_data = [
            (QDateTime.fromMSecsSinceEpoch(1678886400000 + i * 60000), 30.0 + random() * 2)  # Example: Milliseconds since epoch
            for i in range(7)
        ]
        for dt, value in temp_data:
            self.temp_series.append(dt.toMSecsSinceEpoch(), value)


        self.temp1_chart.addSeries(self.temp_series)
        self.temp1_chart.setTitle("Temperature (°C)")
        self.temp1_chart.legend().hide()

        temp_axis_x = QDateTimeAxis()
        temp_axis_x.setTickCount(7)  # Adjust as needed
        temp_axis_x.setFormat("hh:mm:ss")
        temp_axis_x.setTitleText("Timestamp")
        self.temp1_chart.addAxis(temp_axis_x, Qt.AlignBottom)
        self.temp_series.attachAxis(temp_axis_x)

        temp_axis_y = QValueAxis()  # Use QValueAxis for y-axis
        temp_axis_y.setTitleText("Temperature (°C)")
        self.temp1_chart.addAxis(temp_axis_y, Qt.AlignLeft)  # Add it to the chart
        self.temp_series.attachAxis(temp_axis_y)  # Attach the series to the axis


        # Humidity Chart (same pattern as temperature chart)
        self.humidity_series = QLineSeries()

        # Example data (replace with your actual data)
        humidity_data = [
            (QDateTime.fromMSecsSinceEpoch(1678886400000 + i * 60000), 31.0 + random() * 2)  # Example: Milliseconds since epoch
            for i in range(6)
        ]
        for dt, value in humidity_data:
            self.humidity_series.append(dt.toMSecsSinceEpoch(), value)

        self.humidity_chart.addSeries(self.humidity_series)
        self.humidity_chart.setTitle("Humidity (%)")
        self.humidity_chart.legend().hide()

        humidity_axis_x = QDateTimeAxis()
        humidity_axis_x.setTickCount(6)  # Adjust as needed
        humidity_axis_x.setFormat("hh:mm:ss")
        humidity_axis_x.setTitleText("Timestamp")
        self.humidity_chart.addAxis(humidity_axis_x, Qt.AlignBottom)
        self.humidity_series.attachAxis(humidity_axis_x)

        humidity_axis_y = QValueAxis()  # Use QValueAxis for y-axis
        humidity_axis_y.setTitleText("Humidity (%)")
        self.humidity_chart.addAxis(humidity_axis_y, Qt.AlignLeft)  # Add it to the chart
        self.humidity_series.attachAxis(humidity_axis_y)  # Attach the series to the axis

    def update_data(self):
        new_temp_dt = QDateTime.currentMSecsSinceEpoch()
        new_temp_value = self.get_new_temperature_reading()
        self.temp_series.append(new_temp_dt.toMSecsSinceEpoch(), new_temp_value)

        new_humidity_dt = QDateTime.currentMSecsSinceEpoch()
        new_humidity_value = self.get_new_humidity_reading()
        self.humidity_series.append(new_humidity_dt.toMSecsSinceEpoch(), new_humidity_value)

        # Remove old data points if needed (example)
        if self.temp_series.count() > 10:
            self.temp_series.remove(0)
        if self.humidity_series.count() > 10:
            self.humidity_series.remove(0)

        # *** CORRECT AND EFFICIENT WAY TO UPDATE THE CHART VIEW ***
        self.temp_chart_view.update()       # Directly update the view
        self.humidity_chart_view.update()   # Directly update the view

    def get_new_temperature_reading(self):
        return 25.0 + (random() * 5)  # Simulate

    def get_new_humidity_reading(self):
        return 60.0 + (random() * 10)  # Simulate

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SensorDataVisualization()
    window.show()
    sys.exit(app.exec())