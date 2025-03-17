from PyQt5.QtWidgets import (QMainWindow, QApplication, QPushButton, QWidget, 
                           QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                           QComboBox, QTabWidget, QSlider, QGroupBox, QSpinBox,
                           QDoubleSpinBox)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
import sys
import random
import paho.mqtt.client as mqtt
import qdarkgraystyle

class MQTTTestUI(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("MQTT Test Interface")
        self.setMinimumSize(600, 700)
        
        # Create main widget and layout
        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout(self.main_widget)
        
        # Create connection section
        self.create_connection_section()
        
        # Create tabs for different types of testing
        self.tabs = QTabWidget()
        self.main_layout.addWidget(self.tabs)
        
        # Create different tabs
        self.create_manual_publish_tab()
        self.create_sensor_simulation_tab()
        self.create_classification_simulation_tab()
        self.create_state_simulation_tab()
        
        # Set the central widget
        self.setCentralWidget(self.main_widget)
        
        # MQTT client
        self.mqtt_client = None
        self.connected = False
        
        # Set up logs section
        self.create_logs_section()
        
    def create_connection_section(self):
        connection_group = QGroupBox("MQTT Connection")
        connection_layout = QVBoxLayout()
        
        # Connection inputs
        server_layout = QHBoxLayout()
        server_layout.addWidget(QLabel("Server:"))
        self.server_input = QLineEdit("172.20.10.6")
        server_layout.addWidget(self.server_input)
        server_layout.addWidget(QLabel("Port:"))
        self.port_input = QLineEdit("1883")
        server_layout.addWidget(self.port_input)
        connection_layout.addLayout(server_layout)
        
        # Connect button
        button_layout = QHBoxLayout()
        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.toggle_connection)
        button_layout.addWidget(self.connect_button)
        connection_layout.addLayout(button_layout)
        
        connection_group.setLayout(connection_layout)
        self.main_layout.addWidget(connection_group)
        
    def create_manual_publish_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Topic selection
        topic_layout = QHBoxLayout()
        topic_layout.addWidget(QLabel("Topic:"))
        self.topic_combo = QComboBox()
        self.topic_combo.addItems(["sensor", "class_output", "state", "training_prompt"])
        self.topic_combo.setEditable(True)
        topic_layout.addWidget(self.topic_combo)
        layout.addLayout(topic_layout)
        
        # Message input
        message_layout = QHBoxLayout()
        message_layout.addWidget(QLabel("Message:"))
        self.message_input = QLineEdit()
        message_layout.addWidget(self.message_input)
        layout.addLayout(message_layout)
        
        # Publish button
        self.publish_button = QPushButton("Publish")
        self.publish_button.clicked.connect(self.publish_manual_message)
        layout.addWidget(self.publish_button)
        
        # Add to tabs
        self.tabs.addTab(tab, "Manual Publish")
        
    def create_sensor_simulation_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Slider for sensor value
        slider_group = QGroupBox("Manual Sensor Value")
        slider_layout = QVBoxLayout()
        
        self.sensor_slider = QSlider(Qt.Horizontal)
        self.sensor_slider.setMinimum(0)
        self.sensor_slider.setMaximum(1000)
        self.sensor_slider.setValue(500)
        self.sensor_slider.setTickPosition(QSlider.TicksBelow)
        self.sensor_slider.setTickInterval(100)
        
        self.sensor_value_label = QLabel("Value: 0.5")
        slider_layout.addWidget(self.sensor_value_label)
        slider_layout.addWidget(self.sensor_slider)
        
        self.sensor_slider.valueChanged.connect(self.update_sensor_value_label)
        
        # Send sensor value button
        self.send_sensor_button = QPushButton("Send Sensor Value")
        self.send_sensor_button.clicked.connect(self.send_sensor_value)
        slider_layout.addWidget(self.send_sensor_button)
        
        slider_group.setLayout(slider_layout)
        layout.addWidget(slider_group)
        
        # Automatic sensor simulation
        auto_group = QGroupBox("Automatic Sensor Simulation")
        auto_layout = QVBoxLayout()
        
        # Controls for automatic simulation
        control_layout = QHBoxLayout()
        
        control_layout.addWidget(QLabel("Min:"))
        self.min_value = QDoubleSpinBox()
        self.min_value.setRange(0, 10)
        self.min_value.setValue(0)
        self.min_value.setSingleStep(0.1)
        control_layout.addWidget(self.min_value)
        
        control_layout.addWidget(QLabel("Max:"))
        self.max_value = QDoubleSpinBox()
        self.max_value.setRange(0, 10)
        self.max_value.setValue(1)
        self.max_value.setSingleStep(0.1)
        control_layout.addWidget(self.max_value)
        
        control_layout.addWidget(QLabel("Interval (ms):"))
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(50, 5000)
        self.interval_spin.setValue(100)
        self.interval_spin.setSingleStep(50)
        control_layout.addWidget(self.interval_spin)
        
        auto_layout.addLayout(control_layout)
        
        # Start/stop buttons
        button_layout = QHBoxLayout()
        self.start_auto_button = QPushButton("Start Auto Sensor")
        self.start_auto_button.clicked.connect(self.start_auto_sensor)
        button_layout.addWidget(self.start_auto_button)
        
        self.stop_auto_button = QPushButton("Stop Auto Sensor")
        self.stop_auto_button.clicked.connect(self.stop_auto_sensor)
        self.stop_auto_button.setEnabled(False)
        button_layout.addWidget(self.stop_auto_button)
        
        auto_layout.addLayout(button_layout)
        
        auto_group.setLayout(auto_layout)
        layout.addWidget(auto_group)
        
        # Add to tabs
        self.tabs.addTab(tab, "Sensor Simulation")
        
        # Timer for auto simulation
        self.sensor_timer = QTimer()
        self.sensor_timer.timeout.connect(self.send_random_sensor)

    def create_classification_simulation_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Classification buttons
        class_group = QGroupBox("Classification Output")
        class_layout = QVBoxLayout()
        
        self.rest_button = QPushButton("Send 'rest' Classification")
        self.rest_button.clicked.connect(lambda: self.send_classification("rest"))
        class_layout.addWidget(self.rest_button)
        
        self.power_sphere_button = QPushButton("Send 'power sphere' Classification")
        self.power_sphere_button.clicked.connect(lambda: self.send_classification("power sphere"))
        class_layout.addWidget(self.power_sphere_button)
        
        self.large_diameter_button = QPushButton("Send 'large diameter' Classification")
        self.large_diameter_button.clicked.connect(lambda: self.send_classification("large diameter"))
        class_layout.addWidget(self.large_diameter_button)
        
        # Add numeric classification options
        self.class_0_button = QPushButton("Send '0' Classification (rest)")
        self.class_0_button.clicked.connect(lambda: self.send_classification("0"))
        class_layout.addWidget(self.class_0_button)
        
        self.class_1_button = QPushButton("Send '1' Classification (power sphere)")
        self.class_1_button.clicked.connect(lambda: self.send_classification("1"))
        class_layout.addWidget(self.class_1_button)
        
        self.class_2_button = QPushButton("Send '2' Classification (large diameter)")
        self.class_2_button.clicked.connect(lambda: self.send_classification("2"))
        class_layout.addWidget(self.class_2_button)
        
        # Random classification simulation
        rand_layout = QHBoxLayout()
        
        self.start_random_class = QPushButton("Start Random Classification")
        self.start_random_class.clicked.connect(self.start_random_classification)
        rand_layout.addWidget(self.start_random_class)
        
        self.stop_random_class = QPushButton("Stop Random Classification")
        self.stop_random_class.clicked.connect(self.stop_random_classification)
        self.stop_random_class.setEnabled(False)
        rand_layout.addWidget(self.stop_random_class)
        
        class_layout.addLayout(rand_layout)
        
        # Interval for random classification
        interval_layout = QHBoxLayout()
        interval_layout.addWidget(QLabel("Random Interval (ms):"))
        self.class_interval = QSpinBox()
        self.class_interval.setRange(500, 10000)
        self.class_interval.setValue(2000)
        self.class_interval.setSingleStep(500)
        interval_layout.addWidget(self.class_interval)
        
        class_layout.addLayout(interval_layout)
        
        class_group.setLayout(class_layout)
        layout.addWidget(class_group)
                
        # Add to tabs
        self.tabs.addTab(tab, "Classification Simulation")
        
        # Timer for random classification
        self.class_timer = QTimer()
        self.class_timer.timeout.connect(self.send_random_classification)
        
    def create_state_simulation_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # States section
        state_group = QGroupBox("State Control")
        state_layout = QVBoxLayout()
        
        states = [
            "calibration start", "calibration end",
            "evaluation start", "evaluation end",
            "evaluating", "evaluation_complete"
        ]
        
        for state in states:
            btn = QPushButton(f"Send '{state}' State")
            btn.clicked.connect(lambda checked, s=state: self.send_state(s))
            state_layout.addWidget(btn)
        
        state_group.setLayout(state_layout)
        layout.addWidget(state_group)
        
        # Training prompt section
        prompt_group = QGroupBox("Training Prompt Control")
        prompt_layout = QVBoxLayout()
        
        prompts = ["rest", "power sphere", "large diameter", "cancel"]
        
        for prompt in prompts:
            btn = QPushButton(f"Send '{prompt}' Training Prompt")
            btn.clicked.connect(lambda checked, p=prompt: self.send_training_prompt(p))
            prompt_layout.addWidget(btn)
        
        prompt_group.setLayout(prompt_layout)
        layout.addWidget(prompt_group)
        
        # Add to tabs
        self.tabs.addTab(tab, "State & Prompt Simulation")
        
    def create_logs_section(self):
        log_group = QGroupBox("Logs")
        log_layout = QVBoxLayout()
        
        self.log_label = QLabel("Not connected")
        self.log_label.setAlignment(Qt.AlignTop)
        self.log_label.setWordWrap(True)
        log_layout.addWidget(self.log_label)
        
        log_group.setLayout(log_layout)
        self.main_layout.addWidget(log_group)
        
    def toggle_connection(self):
        if not self.connected:
            try:
                server = self.server_input.text()
                port = int(self.port_input.text())
                
                # Create a new MQTT client
                self.mqtt_client = mqtt.Client(client_id="test_ui")
                self.mqtt_client.on_connect = self.on_connect
                self.mqtt_client.connect(server, port)
                self.mqtt_client.loop_start()
                
                self.log("Connecting to MQTT broker...")
            except Exception as e:
                self.log(f"Connection error: {str(e)}")
        else:
            if self.mqtt_client:
                self.mqtt_client.loop_stop()
                self.mqtt_client.disconnect()
                self.mqtt_client = None
                
            self.connected = False
            self.connect_button.setText("Connect")
            self.log("Disconnected from MQTT broker")
    
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.connected = True
            self.connect_button.setText("Disconnect")
            self.log("Connected to MQTT broker")
        else:
            self.log(f"Connection failed with code {rc}")
    
    def publish_manual_message(self):
        if not self.connected or not self.mqtt_client:
            self.log("Not connected to MQTT broker")
            return
            
        topic = self.topic_combo.currentText()
        message = self.message_input.text()
        
        try:
            self.mqtt_client.publish(topic, message)
            self.log(f"Published to {topic}: {message}")
        except Exception as e:
            self.log(f"Publish error: {str(e)}")
    
    def update_sensor_value_label(self):
        value = self.sensor_slider.value() / 1000.0
        self.sensor_value_label.setText(f"Value: {value:.3f}")
    
    def send_sensor_value(self):
        if not self.connected or not self.mqtt_client:
            self.log("Not connected to MQTT broker")
            return
            
        value = self.sensor_slider.value() / 1000.0
        
        try:
            self.mqtt_client.publish("sensor", str(value))
            self.log(f"Published sensor value: {value:.3f}")
        except Exception as e:
            self.log(f"Publish error: {str(e)}")
    
    def start_auto_sensor(self):
        if not self.connected or not self.mqtt_client:
            self.log("Not connected to MQTT broker")
            return
            
        interval = self.interval_spin.value()
        self.sensor_timer.start(interval)
        
        self.start_auto_button.setEnabled(False)
        self.stop_auto_button.setEnabled(True)
        
    def stop_auto_sensor(self):
        self.sensor_timer.stop()
        
        self.start_auto_button.setEnabled(True)
        self.stop_auto_button.setEnabled(False)
        
    def send_random_sensor(self):
        min_val = self.min_value.value()
        max_val = self.max_value.value()
        
        value = random.uniform(min_val, max_val)
        
        try:
            self.mqtt_client.publish("sensor", str(value))
            self.log(f"Published random sensor value: {value:.3f}")
        except Exception as e:
            self.log(f"Publish error: {str(e)}")
    
    def send_classification(self, classification):
        if not self.connected or not self.mqtt_client:
            self.log("Not connected to MQTT broker")
            return
            
        try:
            self.mqtt_client.publish("class_output", classification)
            self.log(f"Published classification: {classification}")
        except Exception as e:
            self.log(f"Publish error: {str(e)}")
    
    def start_random_classification(self):
        if not self.connected or not self.mqtt_client:
            self.log("Not connected to MQTT broker")
            return
            
        interval = self.class_interval.value()
        self.class_timer.start(interval)
        
        self.start_random_class.setEnabled(False)
        self.stop_random_class.setEnabled(True)
        
    def stop_random_classification(self):
        self.class_timer.stop()
        
        self.start_random_class.setEnabled(True)
        self.stop_random_class.setEnabled(False)
        
    def send_random_classification(self):
        classifications = ["rest", "power sphere", "large diameter"]
        classification = random.choice(classifications)
        
        try:
            self.mqtt_client.publish("class_output", classification)
            self.log(f"Published random classification: {classification}")
        except Exception as e:
            self.log(f"Publish error: {str(e)}")
    
    def send_state(self, state):
        if not self.connected or not self.mqtt_client:
            self.log("Not connected to MQTT broker")
            return
            
        try:
            self.mqtt_client.publish("state", state)
            self.log(f"Published state: {state}")
        except Exception as e:
            self.log(f"Publish error: {str(e)}")
    
    def send_training_prompt(self, prompt):
        if not self.connected or not self.mqtt_client:
            self.log("Not connected to MQTT broker")
            return
            
        try:
            self.mqtt_client.publish("training_prompt", prompt)
            self.log(f"Published training prompt: {prompt}")
        except Exception as e:
            self.log(f"Publish error: {str(e)}")
    
    def log(self, message):
        self.log_label.setText(message)
        

app = QApplication(sys.argv)
app.setStyleSheet(qdarkgraystyle.load_stylesheet())
window = MQTTTestUI()
window.show()
sys.exit(app.exec_())

