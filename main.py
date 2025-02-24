import pyqtgraph as pg
from PyQt5 import QtWidgets, QtCore
import numpy as np
import paho.mqtt.client as mqtt
import threading

from graph_widget import GraphWidget 
from tab_widget import TabWidget

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, mqtt_client, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setWindowTitle("Prosthetic Hand Grasping Classification")
        self.tabWidget = TabWidget(self, mqtt_client)
        self.graphWidget = self.tabWidget.graph1  # Reference to the first graph
        self.setCentralWidget(self.tabWidget)

def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))

def on_message(client, userdata, msg):
    if msg.topic == "sensor":
        try:
            value = float(msg.payload.decode())
            userdata.add_data(value)
            print("Received message: " + str(value))
        except ValueError:
            pass  # case where the payload is not float


#
# MAIN
#

# GUI
app = QtWidgets.QApplication([])

# Create the MainWindow instance first
window = MainWindow(None)  # Temporarily pass None for the mqtt_client
window.show()

# SERVER CLIENT
client = mqtt.Client(client_id="gui", userdata=window.graphWidget)
client.on_subscribe = on_subscribe
client.on_message = on_message  
# Pi: my hotspot: 172.20.10.6
# Computer: 192.168.56.1
client.connect("192.168.56.1", 1883)
client.subscribe("sensor", qos=1)
client.subscribe("class_output", qos=1)

# Now update the MainWindow with the actual mqtt_client
window.tabWidget.mqtt_client = client

# Start the MQTT client in a separate thread
mqtt_thread = threading.Thread(target=client.loop_forever)
mqtt_thread.start()

# Start the GUI in a separate thread
app.exec_()