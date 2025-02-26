from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QWidget, QAction, QTabWidget, QVBoxLayout, QLabel, QDialog
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPixmap, QFont
import sys
from graph_widget import GraphWidget
import paho.mqtt.client as mqtt

from CalibrationWindow import CalibrationWindow
from EvaluationWindow import EvaluationWindow


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

        #
        # Graphs tab ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        #
        
        self.tab1.layout = QVBoxLayout(self)
        self.graph1 = GraphWidget()
        self.graph2 = GraphWidget()
        self.tab1.layout.addWidget(self.graph1)
        self.tab1.layout.addWidget(self.graph2)
        self.tab1.setLayout(self.tab1.layout)

        #
        # Calibrate Model tab ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        #
        
        self.tab2.layout = QVBoxLayout(self)

        # Add a title label with a big font
        self.calibrate_title = QLabel("Calibration Process")
        self.calibrate_title.setFont(QFont("Arial", 18, QFont.Bold))  # Big bold font
        self.calibrate_title.setAlignment(Qt.AlignCenter)  # Center align
        self.tab2.layout.addWidget(self.calibrate_title)

        # Add a description label
        self.calibrate_description = QLabel(
            "Press 'Calibrate' to start the calibration process.\n\n"
            "You will perform:\n"
            "- 20 seconds of rest\n"
            "- 10 cycles of: 2 seconds rest, 2 seconds grasping\n\n"
            "This will be done for two grasp types:\n"
            "1. Power Sphere\n"
            "2. Large Diameter\n\n"
            "Follow the instructions carefully when prompted."
        )
        self.calibrate_description.setFont(QFont("Arial", 12))  # Slightly larger readable font
        self.calibrate_description.setWordWrap(True)  # Enable word wrapping for readability
        self.tab2.layout.addWidget(self.calibrate_description)

        # Add the calibrate button
        self.calibrate_button = QPushButton("Calibrate")
        self.calibrate_button.setFont(QFont("Arial", 14, QFont.Bold))  # Make button text bigger
        self.calibrate_button.clicked.connect(self.publish_calibrate)
        self.tab2.layout.addWidget(self.calibrate_button)
        
        # Apply layout
        self.tab2.setLayout(self.tab2.layout)

                #
        # Evaluate Model tab ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        #
        
        self.tab3.layout = QVBoxLayout(self)

        # Add a title label with a big font
        self.evaluate_title = QLabel("Evaluate Model")
        self.evaluate_title.setFont(QFont("Arial", 18, QFont.Bold))  # Big bold font
        self.evaluate_title.setAlignment(Qt.AlignCenter)  # Center align
        self.tab3.layout.addWidget(self.evaluate_title)

        # Add a description label
        self.evaluate_description = QLabel(
            "Before evaluating, ensure that you have completed the calibration process.\n\n"
            "During evaluation, you can perform grasping motions at your own pace.\n\n"
            "The machine learning model will classify your grasp type in real time"
            " and results will be displayed based on the system's classification."
        )
        self.evaluate_description.setFont(QFont("Arial", 12))  # Readable font size
        self.evaluate_description.setWordWrap(True)  # Enable word wrapping for readability
        self.tab3.layout.addWidget(self.evaluate_description)

        # Add the evaluate button
        self.evaluate_button = QPushButton("Evaluate")
        self.evaluate_button.setFont(QFont("Arial", 14, QFont.Bold))  # Bigger button text
        self.evaluate_button.clicked.connect(self.publish_evaluate)
        self.tab3.layout.addWidget(self.evaluate_button)

        # Apply layout
        self.tab3.setLayout(self.tab3.layout)

        # Add tabs to widget
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)
        
    def publish_calibrate(self):
        self.mqtt_client.publish("state", "start calibrate")
        
        self.calibration_window = CalibrationWindow(self)
        self.calibration_window.exec_()  # Show the calibration window as a modal dialog

    def publish_evaluate(self):
        self.mqtt_client.publish("state", "start evaluate")
        
        self.evaluation_window = EvaluationWindow(self)
        self.evaluation_window.exec_()
