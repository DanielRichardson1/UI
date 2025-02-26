from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QWidget, QAction, QTabWidget, QVBoxLayout, QLabel, QDialog
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPixmap
import sys
from graph_widget import GraphWidget
import paho.mqtt.client as mqtt


class CalibrationWindow(QDialog):
    def __init__(self, parent=None):
        super(CalibrationWindow, self).__init__(parent)

        self.setWindowTitle("Calibration")
        
        layout = QVBoxLayout(self)
        
        self.label = QLabel("")
        layout.addWidget(self.label)
        
        self.image_label = QLabel(self)
        layout.addWidget(self.image_label)
        
        self.timer_label = QLabel("")
        layout.addWidget(self.timer_label)
        
        self.rep_label = QLabel("")  # New label for rep count
        layout.addWidget(self.rep_label)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        
        self.time_left = 0
        self.rep_count = 0
        self.state = "rest"
        
        self.steps = [
            ("Rest for 20 seconds", "./images/rest.png", 20), # 0
            ("Prepare for Power Sphere Grasp", "./images/rest.png", 2), # 1
            ("Power Sphere Grasp", "./images/power_sphere.png", 2), # 2
            ("Relax your hand", "./images/rest.png", 2), # 3
            ("Prepare for Large Diameter Grasp", "./images/rest.png", 2), # 4
            ("Large Diameter Grasp", "./images/large_diameter.png", 2), # 5
            ("Relax your hand", "./images/rest.png", 2), # 6
        ]
        
        self.current_step = 0
        
        self.set_layout(layout)
        self.start_process()

    def set_layout(self, layout):
        self.setLayout(layout)
    
    def start_process(self):
        self.current_step = 0
        self.time_left = self.steps[self.current_step][2]
        self.update_step()

    def update_step(self):
        step = self.steps[self.current_step]
        self.label.setText(step[0])
        self.image_label.setPixmap(QPixmap(step[1]))
        self.timer_label.setText(f"Time Remaining: {self.time_left}")
        self.timer.start(1000)
        
        if self.current_step != 0:
            self.rep_label.setText(f"Repetition: {self.rep_count}/10")

    def update_timer(self):
        self.time_left -= 1
        if self.time_left >= 0:
            self.timer_label.setText(f"Time Remaining: {self.time_left}")
        else:
            self.timer.stop()

            if self.current_step == 0:
                self.rep_count = 1
                self.label.setText(f"{self.steps[self.current_step][0]}: {self.rep_count}/10")
                self.current_step += 1
                self.time_left = self.steps[self.current_step][2]

            elif self.current_step == 1 or self.current_step == 4:
                self.current_step += 1

            elif self.current_step == 2 or self.current_step == 5:
                if self.rep_count < 10:
                    self.rep_count += 1
                    self.label.setText(f"{self.steps[self.current_step][0]}: {self.rep_count}/10")  # Show rep count
                    self.current_step += 1
                else:
                    self.rep_count = 1  # Reset the rep count after completing 10 reps
                    self.current_step += 2

            elif (self.current_step == 3 or self.current_step == 6) and self.rep_count <= 10:
                self.current_step -= 1  # Go back to grasp after relaxing
            else:
                self.current_step += 1

            if self.current_step < len(self.steps):
                self.time_left = self.steps[self.current_step][2]
                self.update_step()
            else:
                self.close()
                self.mqtt_client.publish("state", "calibration_complete")
