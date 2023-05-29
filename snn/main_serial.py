import os
import sys
import cv2
import json
import time
import numpy as np
from pathlib import Path
from threading import Thread
from Constants import Constants
from midbrain.new_brain import NewBrain
from debug.debug import Debug

# Initialize appropriate debug level
debug_level = Debug.DEBUG_VERBOSE

# Global variables
left_cam = 1
right_cam = 2

arbotix_device = "/dev/ttyUSB0"
configFile = None
rootDir = None

# Config params
auto_detect_devices = True

def getexepath():
    return os.path.abspath(sys.argv[0])

def auto_detect():
    global arbotix_device, left_cam, right_cam
    arbotix_device = "/dev/" + list_udev("tty")
    leftRightCamDevNums = list_udev("video4linux")
    camNums = leftRightCamDevNums.split(',')
    if len(camNums) < 2:
        print("Error not enough eyes in the robot")
        sys.exit(-1)
    left_cam = int(camNums[1])
    right_cam = int(camNums[2])

def init():
    global configFile, rootDir, auto_detect_devices, left_cam, right_cam, arbotix_device, debug_level
    exepath = getexepath()
    rootDir = str(Path(exepath).parent)

    Constants.instance().rootDir = rootDir
    Constants.instance().outputDir = rootDir + "/tmp/"

    configFile = rootDir + "/" + "config.json"
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
        auto_detect()


def read_frames(filename): 
    cap = cv2.VideoCapture(filename)

    if not cap.isOpened():
        print('Error opening video file')
        exit()

    # Read the first frame
    ret, frame = cap.read()

    if not ret:
        print('Error reading frame')
        exit()

    height, width, _ = frame.shape
    frames = []

    for i in range(100):

        ret, frame = cap.read()
        if not ret:
            break
        
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # frame = np.array(frame, dtype=np.uint8)
        # Add the frame to the matrix
        frames.append(frame)

    # Release the video file
    cap.release()
    print("Loaded:", filename, len(frames))

    # Convert the list of frames to a numpy array
    return frames

def main():
    init()

    print("Begin run")

    # Init
    #control = ArbotixControl(arbotix_device)
    #control.move([512, 512], [512, 512], [512, 512])

    #llbn_in_l = WorkQueue()
    #llbn_in_r = WorkQueue()
    #opn_in = WorkQueue()

# Print the shape of the frames matrix
    frameQueue_Left = read_frames(os.path.join(rootDir, "tmp", "left_cam.avi"))
    frameQueue_Right = read_frames(os.path.join(rootDir, "tmp", "right_cam.avi"))

    #motor_output = WorkQueue()

    #cameraThread_Left = CameraThread(frameQueue_Left, left_cam, rootDir + "/tmp/left_cam.avi")
    #cameraThread_Right = CameraThread(frameQueue_Right, right_cam, rootDir + "/tmp/right_cam.avi")

    #cameraThread_Left.start()
    #cameraThread_Right.start()
    #print("Camera thread active")


    brain = NewBrain(frameQueue_Left, frameQueue_Right)
    #brain.setControl(control)
    brain.run()  # Has infinite loop inside

if __name__ == "__main__":
    main()