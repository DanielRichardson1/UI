from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QWidget, QAction, QTabWidget, QVBoxLayout, QLabel, QDialog
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPixmap, QFont
import sys
from graph_widget import GraphWidget
import paho.mqtt.client as mqtt


class EvaluationWindow(QDialog):
    def __init__(self, parent=None):
        super(EvaluationWindow, self).__init__(parent)

        self.setWindowTitle("Evaluation")
        self.setMinimumSize(500, 400)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        
        # Title label
        self.title_label = QLabel("Waiting for classification...")
        self.title_label.setFont(QFont("Arial", 18, QFont.Bold))
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)
        
        # Image label
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.image_label)
        
        # Classification label
        self.classification_label = QLabel("Current Classification: None")
        self.classification_label.setFont(QFont("Arial", 16))
        self.classification_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.classification_label)
        
        # Instructions label
        self.instructions_label = QLabel("Perform different grasp types to see real-time classification")
        self.instructions_label.setFont(QFont("Arial", 12))
        self.instructions_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.instructions_label)
        
        # Status label
        self.status_label = QLabel("System Status: Ready")
        self.status_label.setFont(QFont("Arial", 10))
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        
        # Close button
        self.close_button = QPushButton("Close Evaluation")
        self.close_button.clicked.connect(self.close_evaluation)
        layout.addWidget(self.close_button)
        
        # Image paths dictionary
        self.image_paths = {
            "rest": "./images/rest.png",
            "power sphere": "./images/power_sphere.png",
            "large diameter": "./images/large_diameter.png"
        }
        
        # Get MQTT client from parent
        if parent and hasattr(parent, 'mqtt_client'):
            self.mqtt_client = parent.mqtt_client
            
            # Set up callback for receiving classifications
            self.original_on_message = self.mqtt_client.on_message
            self.mqtt_client.on_message = self.on_message
        else:
            # Fallback if no parent or no mqtt_client in parent
            self.mqtt_client = mqtt.Client(client_id="evaluation_window")
            self.mqtt_client.connect("localhost", 1883)
            self.mqtt_client.on_message = self.on_message
            self.mqtt_client.loop_start()
        
        # Subscribe to classification output
        self.mqtt_client.subscribe("class_output", qos=1)
        
        self.set_layout(layout)
        self.start_process()

    def set_layout(self, layout):
        self.setLayout(layout)
    
    def start_process(self):
        """Initialize the evaluation process"""
        self.status_label.setText("System Status: Evaluating...")
        self.mqtt_client.publish("state", "evaluating")
        # Set default image for starting state
        self.update_display("rest")
    
    def on_message(self, client, userdata, msg):
        """Handle incoming MQTT messages"""
        if msg.topic == "class_output":
            try:
                classification = msg.payload.decode().strip().lower()
                self.update_display(classification)
                print(f"Received classification: {classification}")
            except Exception as e:
                print(f"Error processing classification message: {e}")
        
        # Call original callback for other messages
        if hasattr(self, 'original_on_message') and self.original_on_message:
            self.original_on_message(client, userdata, msg)
    
    def update_display(self, classification):
        """Update the display based on the received classification"""
        # Normalize classification string
        if classification == "power_sphere" or classification == "power sphere" or "1":
            display_class = "power sphere"
        elif classification == "large_diameter" or classification == "large diameter" or "2":
            display_class = "large diameter"
        else:
            display_class = "rest"
        
        # Update the image
        if display_class in self.image_paths:
            pixmap = QPixmap(self.image_paths[display_class])
            self.image_label.setPixmap(pixmap)
            self.image_label.setScaledContents(False)
        
        # Update labels
        self.classification_label.setText(f"Current Classification: {display_class.title()}")
        
        # Set title based on classification
        if display_class == "rest":
            self.title_label.setText("Resting Position Detected")
        elif display_class == "power sphere":
            self.title_label.setText("Power Sphere Grasp Detected")
        elif display_class == "large diameter":
            self.title_label.setText("Large Diameter Grasp Detected")
    
    def close_evaluation(self):
        """Handle closing the evaluation window"""
        # Restore original MQTT callback if it exists
        if hasattr(self, 'original_on_message') and self.original_on_message:
            self.mqtt_client.on_message = self.original_on_message
        
        # Publish state change
        self.mqtt_client.publish("state", "evaluation_complete")
        self.close()
    
    def closeEvent(self, event):
        """Override closeEvent to ensure proper cleanup"""
        # Restore original MQTT callback if it exists
        if hasattr(self, 'original_on_message') and self.original_on_message:
            self.mqtt_client.on_message = self.original_on_message
        
        # Publish state change
        self.mqtt_client.publish("state", "evaluation end")
        event.accept()