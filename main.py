import pyqtgraph as pg
from PyQt5 import QtWidgets
from PyQt5.QtGui import QIcon
import numpy as np
import paho.mqtt.client as mqtt
import threading
import sys
import qdarkgraystyle

from graph_widget import GraphWidget 
from tab_widget import TabWidget

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, mqtt_client, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setWindowTitle("Prosthetic Hand Grasping Classification")
        self.tabWidget = TabWidget(self, mqtt_client)
        self.graphWidget1 = self.tabWidget.graph1  # Reference to the first graph
        self.graphWidget2 = self.tabWidget.graph2  # Reference to the second graph
        self.mqtt_client = mqtt_client  # Store reference to MQTT client
        self.setCentralWidget(self.tabWidget)

    def closeEvent(self, event):
        """Handles window closing, ensuring the script exits cleanly."""
        if self.mqtt_client:
            self.mqtt_client.loop_stop()  # Stop MQTT loop
            self.mqtt_client.disconnect()  # Disconnect MQTT client
        print("Application closing...")
        event.accept()
        sys.exit(0)  # Ensure script fully exits


def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))


def on_message(client, userdata, msg):
    if msg.topic == "sensor":
        try:
            payload = msg.payload.decode()
            # Check if the payload matches the new format with comma-separated values
            if ',' in payload:
                values = payload.split(',')
                if len(values) >= 2:
                    value1 = float(values[0])
                    value2 = float(values[1])
                    # Update each graph with its respective value
                    userdata["graph1"].add_data(value1)
                    userdata["graph2"].add_data(value2)
                    print(f"Received sensor: {value1}, {value2}")
            else:
                # Fallback for old format (single value)
                value = float(payload)
                userdata["graph1"].add_data(value)
                userdata["graph2"].add_data(value)
                print("Received sensor: " + str(value))
        except ValueError as e:
            print(f"Error processing sensor data: {e}")
            
    if msg.topic == "class_output":
        try:
            classification = msg.payload.decode().strip()
            print(f"Received classification: {classification}")
        except Exception as e:
            print(f"Error processing classification message: {e}")


#
# MAIN
#

# GUI
app = QtWidgets.QApplication([sys.argv])

# Load and apply stylesheet
# with open("styles.qss", "r") as stylesheet:
#     app.setStyleSheet(stylesheet.read()) 

# Create the MQTT client first
client = mqtt.Client(client_id="gui")
client.on_subscribe = on_subscribe
client.on_message = on_message  
client.connect("172.20.10.6", 1883) 
client.subscribe("sensor", qos=1)
client.subscribe("class_output", qos=1)

# Create the MainWindow instance with the actual MQTT client
window = MainWindow(client)

# Create a dictionary to hold references to both graphs for passing to the MQTT client
graph_references = {
    "graph1": window.graphWidget1,
    "graph2": window.graphWidget2
}

# Update the userdata with the graph references
client.user_data_set(graph_references)

# setup stylesheet
app.setStyleSheet(qdarkgraystyle.load_stylesheet())
icon = QIcon('./images/mechanical-arm.png')
app.setWindowIcon(icon)
window.show()

# Start the MQTT client in a separate thread
mqtt_thread = threading.Thread(target=client.loop_forever, daemon=True)
mqtt_thread.start()

# Start the GUI
QtWidgets.QApplication.instance().setWindowIcon(icon) 
app.exec_()

# Ensure cleanup after GUI closes
client.loop_stop()
client.disconnect()
sys.exit(0)