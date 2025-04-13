import pyqtgraph as pg
from PyQt5 import QtWidgets, QtCore
import numpy as np

class GraphWidget(QtWidgets.QWidget):
    def __init__(self, color=(255, 0, 0), width=2, *args, **kwargs):
        super(GraphWidget, self).__init__(*args, **kwargs)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.graphWidget = pg.PlotWidget()
        self.layout.addWidget(self.graphWidget)
        
        self.x = list(range(100))  # 100 time points
        self.y = [0] * 100      # 100 data points
        self.graphWidget.setBackground('w')

        pen = pg.mkPen(color=color, width=width)
        self.data_line = self.graphWidget.plot(self.x, self.y, pen=pen)

        self.timer = QtCore.QTimer()
        self.timer.setInterval(50)  # Refresh rate in ms
        self.timer.timeout.connect(self.update_plot_data)
        self.timer.start()

    def update_plot_data(self):
        self.data_line.setData(self.x, self.y)  # Update the plot.
    
    def add_data(self, value):
        self.y = self.y[1:]  # Remove the first
        self.y.append(value)  # Add new value