import cv2
import numpy as np
import time
import threading
from camera import Camera

class CameraThread(threading.Thread):
    def __init__(self, queue, device=0, video_out=''):
        super().__init__()
        self.queue = queue
        self.cam = Camera(device, video_out)
        self.tmp = 0
        self.device_num = device
        self.pause = 0.005 # 0.03
        self.prev_frame = None
        self._suspended = False

    def run(self):
        while True:
            frame = self.cam.get_next_frame()
            if frame.shape[0] == 0 or frame.shape[1] == 0:
                print("Error: No frame to read")


            if not self._suspended:
                self.queue.add(frame)
                self.prev_frame = frame
                self.tmp += 1

            time.sleep(self.pause)

    def __del__(self):
        self.cam.release()

    def get_frame(self):
        return self.prev_frame

    def suspend(self):
        self._suspended = True

    def resume(self):
        self._suspended = False
