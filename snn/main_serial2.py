import os
import cv2
import sys
import json
import glob

from Constants import Constants
from camera.camera_thread import CameraThread
from workqueue.workqueue import WorkQueue
from midbrain.new_brain import NewBrain
from arbotix_pc_serial.arbotix_control import ArbotixControl

# Set debug level
debug_level = 1

left_cam = 1
right_cam = 2

arbotix_device = "/dev/ttyUSB0"
configFile = None
rootDir = None

auto_detect_devices = True

threshold = 246

class Robothead:
    def get_exe_path(self):
        return os.path.dirname(os.path.abspath(sys.argv[0]))

    def auto_detect(self):
        global left_cam, right_cam, arbotix_device
        arbotix_device = glob.glob('/dev/ttyUSB*')[0]
        video_devices = glob.glob('/dev/video*')
        if len(video_devices) < 2:
            print("Error: not enough eyes in the robot")
            sys.exit(-1)
        left_cam = int(video_devices[1][-1])
        right_cam = int(video_devices[2][-1])

    def __init__(self):
        self.brain = None
        global left_cam, right_cam, arbotix_device, configFile, rootDir, auto_detect_devices
        exe_path = self.get_exe_path()
        rootDir = exe_path

        self.cameraThread_Left = None
        self.cameraThread_Right = None

        self.control = None
        Constants.instance().rootDir = rootDir
        Constants.instance().outputDir = rootDir + "/tmp/"

        configFile = os.path.join(rootDir, "config.json")
        with open(configFile, 'r') as configF:
            configJson = json.load(configF)

        auto_detect_devices = configJson["auto_detect_devices"]
        left_cam = configJson["left_camera_num"]
        right_cam = configJson["right_camera_num"]
        arbotix_device = configJson["arbotix_device"]
        debug_level = configJson["debug_level"]

        Constants.instance().saveVideo = configJson["capture_video"]
        Constants.instance().learning = configJson["learning"]
        Constants.instance().coordinated_run = configJson["coordinated_run"]

        if auto_detect_devices:
            self.auto_detect()

        self.initialize_brain()

    def update(self, threshold_value):
        self.brain.update_threshold(threshold_value)




    def initialize_brain(self):
        global threshold

        print("Begin run")

        # Initialize control
        self.control = ArbotixControl(arbotix_device)
        self.control.move([512, 512], [512, 512], [512, 512])

        # llbn_in_l = WorkQueue()
        # llbn_in_r = WorkQueue()
        # opn_in = WorkQueue()
        frameQueue_Left = WorkQueue()  # Specify the data type as cv2.Mat (numpy.ndarray)
        frameQueue_Right = WorkQueue()  # Specify the data type as cv2.Mat (numpy.ndarray)
        # motor_output = WorkQueue()

        self.cameraThread_Left = CameraThread(frameQueue_Left, left_cam)#, os.path.join(rootDir, "tmp", "left_cam.avi"))
        self.cameraThread_Right = CameraThread(frameQueue_Right, right_cam)#, os.path.join(rootDir, "tmp", "right_cam.avi"))

        self.cameraThread_Left.start()
        self.cameraThread_Right.start()
        print("Camera thread active")

        self.brain = NewBrain(frameQueue_Left, frameQueue_Right, threshold)
        self.brain.setControl(self.control)
        # self.brain.run()  # Has infinite loop inside

    def reset_robot(self):
        #for i in range(50):       
        self.control.move([512, 512], [512, 512], [512, 512])

