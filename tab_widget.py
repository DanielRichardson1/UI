from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QWidget, QAction, QTabWidget, QVBoxLayout, QLabel
import sys
from graph_widget import GraphWidget
import paho.mqtt.client as mqtt

class TabWidget(QWidget):
    def __init__(self, parent, mqtt_client):
        super(QWidget, self).__init__(parent)
        self.layout = QVBoxLayout(self)
        
        self.mqtt_client = mqtt_client  # Store the MQTT client reference
  
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
        self.calibrate_button = QPushButton("Calibrate")
        self.calibrate_button.clicked.connect(self.publish_calibrate)
        self.tab2.layout.addWidget(self.calibrate_button)
        self.tab2.setLayout(self.tab2.layout)

        # Evaluate Model tab
        self.tab3.layout = QVBoxLayout(self)
        self.evaluate_button = QPushButton("Evaluate")
        self.evaluate_button.clicked.connect(self.publish_evaluate)
        self.tab3.layout.addWidget(self.evaluate_button)
        self.tab3.setLayout(self.tab3.layout)
        
        # Add tabs to widget
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)
        
    def publish_calibrate(self):
        self.mqtt_client.publish("state", "calibrate")
        
    def publish_evaluate(self):
        self.mqtt_client.publish("state", "evaluate")
