import pyqtgraph as pg
from PyQt5 import QtWidgets, QtCore
import numpy as np

from graph_widget import GraphWidget 
from tab_widget import TabWidget

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setWindowTitle("Prosthetic Hand Grasping Classification")
        self.tabWidget = TabWidget(self)
        self.setCentralWidget(self.tabWidget)



app = QtWidgets.QApplication([])
window = MainWindow()
window.show()
app.exec_()
