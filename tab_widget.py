from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QWidget, QAction, QTabWidget, QVBoxLayout, QLabel 
import sys

from graph_widget import GraphWidget


class TabWidget(QWidget): 
    def __init__(self, parent): 
        super(QWidget, self).__init__(parent) 
        self.layout = QVBoxLayout(self) 
  
        # Initialize tab screen 
        self.tabs = QTabWidget() 
        self.tab1 = QWidget() 
        self.tab2 = QWidget() 
        self.tab3 = QWidget() 
        self.tabs.resize(300, 200) 
  
        # Add tabs 
        self.tabs.addTab(self.tab1, "Graphs") 
        self.tabs.addTab(self.tab2, "Calibrate Model") 
        self.tabs.addTab(self.tab3, "Evaluate Model") 
  
        # Graphs tab 
        self.tab1.layout = QVBoxLayout(self)
        self.graph1 = GraphWidget()
        self.graph2 = GraphWidget()
        self.tab1.layout.addWidget(self.graph1)
        self.tab1.layout.addWidget(self.graph2)
        self.tab1.setLayout(self.tab1.layout)

        # Calibrate Model tab
        self.tab2.layout = QVBoxLayout(self) 
        self.tab2.layout.addWidget(QLabel("This is the second tab")) 
        self.tab2.setLayout(self.tab2.layout) 

        # Evaluate Model tab
        self.tab3.layout = QVBoxLayout(self) 
        self.tab3.layout.addWidget(QLabel("This is the third tab")) 
        self.tab3.setLayout(self.tab3.layout) 
        
        # Add tabs to widget 
        self.layout.addWidget(self.tabs) 
        self.setLayout(self.layout)