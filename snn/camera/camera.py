import cv2
import numpy as np

class Camera:
    width = 720
    height = 720

    def __init__(self, device=0, video_stream_filename=''):
        self.cam = cv2.VideoCapture(device)
        self.out_file = video_stream_filename
        fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        # Uncomment the following line if you want to save the video.
        # self.out = cv2.VideoWriter(video_stream_filename, fourcc, 30, (Camera.width, Camera.height), True)

    def get_next_frame(self):
        if not self.cam.isOpened():
            raise Exception('Camera not opened')

        ret, frame = self.cam.read()

        # hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # # Define the lower and upper bounds for the red color in HSV color space
        # # lower_red = np.array([0, 100, 100])
        # # upper_red = np.array([10, 255, 255])

        # lower_red = np.array([160, 100, 100])
        # upper_red = np.array([179, 255, 255])
        # # Create a mask for the red color
        # mask = cv2.inRange(hsv, lower_red, upper_red)

        # # Perform a bitwise AND operation to extract only the red color from the image
        # red_only = cv2.bitwise_and(frame, frame, mask=mask)

        # # Convert the red-only image to grayscale
        # frame = cv2.cvtColor(red_only, cv2.COLOR_BGR2GRAY)

        # if not ret:
        #     raise Exception('Error reading frame from camera')

        

        bgr = cv2.split(frame)
        resized_gray = cv2.resize(bgr[2], (Camera.width, Camera.height))

        # Uncomment the following lines if you want to save the video.
        # resized_frame = cv2.resize(frame, (Camera.width, Camera.height))
        # self.out.write(resized_frame)

        return resized_gray

    def release(self):
        self.cam.release()
