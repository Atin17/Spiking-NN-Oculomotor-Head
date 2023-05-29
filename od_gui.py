import sys
from PyQt4.QtGui import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QSlider, QFont
from PyQt4.QtCore import Qt, QThread, SIGNAL
from head_control import HeadRosControl

class Worker(QThread):
    def __init__(self, func):
        super(Worker, self).__init__()
        self.func = func
        self.flag = False

    def run(self):
        self.func()

    def stop(self):
        self.flag = True

class RobotInterface(QMainWindow):
    def __init__(self):
        super(RobotInterface, self).__init__()
        self.setWindowTitle("Robot Controller")
        self.setGeometry(0, 0, 1920, 1080)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.label = QLabel("Neuro Robot Controller", self)
        self.label.setFont(QFont('Roboto', 20))
        layout.addWidget(self.label)

        self.start_button = QPushButton('Start', self)
        self.start_button.setFont(QFont('Roboto', 20))
        self.start_button.clicked.connect(self.start_snn)
        layout.addWidget(self.start_button)

        self.reset_button = QPushButton('Reset', self)
        self.reset_button.setFont(QFont('Roboto', 20))
        self.reset_button.clicked.connect(self.reset_robot)
        layout.addWidget(self.reset_button)

        self.exit_button = QPushButton('Exit', self)
        self.exit_button.setFont(QFont('Roboto', 20))
        self.exit_button.clicked.connect(self.close)
        layout.addWidget(self.exit_button)

        self.threshold_slider = QSlider(Qt.Horizontal, self)
        self.threshold_slider.setRange(0, 255)
        self.threshold_slider.setValue(240)
        layout.addWidget(self.threshold_slider)

        self.apply_threshold_button = QPushButton('Apply Threshold', self)
        self.apply_threshold_button.setFont(QFont('Roboto', 20))
        self.apply_threshold_button.clicked.connect(self.apply_threshold)
        layout.addWidget(self.apply_threshold_button)

        self.reset_threshold_button = QPushButton('Reset Threshold', self)
        self.reset_threshold_button.setFont(QFont('Roboto', 20))
        self.reset_threshold_button.clicked.connect(self.reset_threshold)
        layout.addWidget(self.reset_threshold_button)

        self.worker = None

    def start_snn(self):
        if not self.worker or not self.worker.isRunning():
            print("Started SNN")
            self.worker = Worker(control_node.run_node)
            self.worker.start()

    def reset_robot(self):
        control_node.reset_robot()

    def apply_threshold(self):
        threshold_value = self.threshold_slider.value()
        control_node.update(threshold_value)

    def reset_threshold(self):
        default_threshold = 230
        self.threshold_slider.setValue(default_threshold)
        control_node.update(default_threshold)
        


if __name__ == '__main__':
    from params import cfg

    eye_pan_inc = cfg['head']['eye_pan_inc']
    eye_pan_lim = cfg['head']['eye_pan_lim']
    eye_tilt_inc = cfg['head']['eye_tilt_inc']
    eye_tilt_lim = cfg['head']['eye_tilt_lim']
    neck_pan_inc = cfg['head']['neck_pan_inc']
    neck_pan_lim = cfg['head']['neck_pan_lim']
    neck_tilt_inc = cfg['head']['neck_tilt_inc']
    neck_tilt_lim = cfg['head']['neck_tilt_lim']
    move_spd = cfg['head']['servo_move_spd']
    in_amp = cfg['head']['input_amp']
    rate = cfg['head']['ros_rate']

    threshold = 230
    control_node = HeadRosControl(eye_pan_inc, eye_pan_lim, eye_tilt_inc, eye_tilt_lim,
                                  neck_pan_inc, neck_pan_lim, neck_tilt_inc, neck_tilt_lim,
                                  in_amp, move_spd, rate, threshold)
    
    max_ita = rate * cfg['head']['run_time']

    

    explanation = """click 'Start' to run"""

    app = QApplication([])
    window = RobotInterface()
    window.show()
    sys.exit(app.exec_())