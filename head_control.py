import rospy
from arbotix_msgs.srv import SetSpeed
from std_msgs.msg import Float64, Float32MultiArray
import numpy as np
import math
import copy
import time
import os
import sys
import json

from snn.midbrain.new_brain import NewBrain
from snn.Constants import Constants

class HeadRosControl:
    """ Control Head using ROS and SNN on Loihi """

    def __init__(self, eye_pan_increase, eye_pan_limit, eye_tilt_increase, eye_tile_limit,
                 neck_pan_increase, neck_pan_limit, neck_tilt_increase, neck_tilt_limit,
                 input_amp, move_speed, ros_rate, threshold):
        """

        Args:
            eye_pan_increase (float): eye pan increase rate
            eye_pan_limit (float): eye pan position limit
            eye_tilt_increase (float): eye tilt increase rate
            eye_tile_limit (float): eye tilt position limit
            neck_pan_increase (float): neck pan increase rate
            neck_pan_limit (float): neck pan position limit
            neck_tilt_increase (float): neck tilt increase rate
            neck_tilt_limit (float): neck tilt position limit
            move_speed (float): move speed for servo between positions
            input_amp (float): input amplifier for control output
            ros_rate (int): ros node update rate
        """

        exe_path = self.get_exe_path()
        rootDir = exe_path

        self.cameraThread_Left = None
        self.cameraThread_Right = None
        self.running = True
        self.control = None
        print(rootDir)
        Constants.instance().rootDir = rootDir
        Constants.instance().outputDir = rootDir + "/tmp/"

        configFile = os.path.join(rootDir, "config.json")
        with open(configFile, 'r') as configF:
            configJson = json.load(configF)


        Constants.instance().saveVideo = configJson["capture_video"]
        Constants.instance().learning = configJson["learning"]
        Constants.instance().coordinated_run = configJson["coordinated_run"]




        self.brain = NewBrain(threshold)

        rospy.init_node("head_ros_control")

        self.eye_pan_increase = eye_pan_increase
        self.eye_pan_limit = eye_pan_limit
        self.eye_tilt_increase = eye_tilt_increase
        self.eye_tilt_limit = eye_tile_limit
        self.neck_pan_increase = neck_pan_increase
        self.neck_pan_limit = neck_pan_limit
        self.neck_tilt_increase = neck_tilt_increase
        self.neck_tilt_limit = neck_tilt_limit
        self.input_amp = input_amp
        self.move_speed = move_speed
        self.ros_rate = rospy.Rate(ros_rate)

        # Create eye output control subscriber
        self.left_eye_output = None
        self.right_eye_output = None
        self.left_eye_sub = rospy.Subscriber('/left_cam/control_output', Float32MultiArray,
                                             self.left_eye_cb, queue_size=1)
        self.right_eye_sub = rospy.Subscriber('/right_cam/control_output', Float32MultiArray,
                                              self.right_eye_cb, queue_size=1)
        rospy.loginfo("Wait Left and Right Eye Init ...")
        while self.left_eye_output is None and self.right_eye_output is None and not rospy.is_shutdown():
            continue
        rospy.loginfo("Left and Right Eye Init finished ...")

        # Create Service and Publisher for head control
        self.joint_position = np.zeros(7)
        self.joint_name_list = ['neck_pan', 'neck_tilt1', 'neck_tilt2',
                                'left_eye_pan', 'left_eye_tilt',
                                'right_eye_pan', 'right_eye_tilt']
        self.speed_srv_list = []
        self.pos_pub_list = []
        for name in self.joint_name_list:
            speed_srv_name = '/full_head/' + name + '/set_speed'
            self.speed_srv_list.append(rospy.ServiceProxy(speed_srv_name, SetSpeed))
            pos_pub_name = '/full_head/' + name + '/command'
            self.pos_pub_list.append(rospy.Publisher(pos_pub_name, Float64, queue_size=5))

        # Set all servo with moving speed
        for speed_srv in self.speed_srv_list[:3]:
            try:
                speed_srv(move_speed / 4.)
            except rospy.ServiceException as e:
                print("Setting move speed Failed: %s" % e)
        for speed_srv in self.speed_srv_list[3:]:
            try:
                speed_srv(move_speed)
            except rospy.ServiceException as e:
                print("Setting move speed Failed: %s" % e)

    def left_eye_cb(self, msg):
        """
        Callback function for left eye

        Args:
            msg (Message): Message

        """
        self.left_eye_output = msg.data

    def right_eye_cb(self, msg):
        """
        Callback function for right eye

        Args:
            msg (Message): Message

        """
        self.right_eye_output = msg.data

    def run_node(self, max_ros_ita):
        """
        Run ROS node for the head

        Args:
            max_ros_ita (int): max ros iteration
            encoder_channel (Loihi Channel): Encoder input channel
            decoder_channel (Loihi Channel): Decoder input channel

        """
        ros_ita = 0
        
        while not rospy.is_shutdown() and self.running:
            
            left_eye_current = copy.deepcopy(self.left_eye_output)
            right_eye_current = copy.deepcopy(self.right_eye_output)

            print("Left raw current: ", left_eye_current, " Right raw current: ", right_eye_current)

            if left_eye_current[4] != 1 or right_eye_current[4] != 1:    
                self.joint_position = [0, 0, 0, 0, 0, 0, 0]
                for dd, pos_pub in enumerate(self.pos_pub_list, 0):
                    pos_msg = Float64()
                    pos_msg.data = self.joint_position[dd]
                    pos_pub.publish(pos_msg)

                continue


            # if left_eye_current[4] == -1 or right_eye_current[4] == -1:
            #     self.joint_position = [0, 0, 0, 0, 0, 0, 0]
            #     for dd, pos_pub in enumerate(self.pos_pub_list, 0):
            #         pos_msg = Float64()
            #         pos_msg.data = self.joint_position[dd]
            #         pos_pub.publish(pos_msg)

            #     continue

            neuron_spikes = self.brain.run(left_eye_current, right_eye_current)
            if neuron_spikes is None:
                continue

            delta_motor_spikes = neuron_spikes[0]
            motor_speed = neuron_spikes[1]
            print("JOINT", delta_motor_spikes, motor_speed)


            # Update neck positions
            self.joint_position[0] += self.neck_pan_increase * (delta_motor_spikes[8] - delta_motor_spikes[9])
            self.joint_position[1] += self.neck_tilt_increase * (delta_motor_spikes[6] - delta_motor_spikes[7])
            self.joint_position[2] = self.joint_position[1]
            if abs(self.joint_position[0]) > self.neck_pan_limit:
                self.joint_position[0] = math.copysign(1.0, self.joint_position[0]) * self.neck_pan_limit
            if abs(self.joint_position[1]) > self.neck_tilt_limit:
                self.joint_position[1] = math.copysign(1.0, self.joint_position[1]) * self.neck_tilt_limit
                self.joint_position[2] = self.joint_position[1]

            # Update left eye positions
            left_eye_move = (delta_motor_spikes[2] - delta_motor_spikes[3])
            right_eye_move = (delta_motor_spikes[4] - delta_motor_spikes[5])

            if delta_motor_spikes[2] > delta_motor_spikes[3]:
                self.joint_position[3] += self.eye_pan_increase * (0.7 * left_eye_move + 0.3 * right_eye_move)  * motor_speed[0] 
            elif delta_motor_spikes[2] < delta_motor_spikes[3]:
                self.joint_position[3] += self.eye_pan_increase * (0.7 * left_eye_move + 0.3 * right_eye_move) * motor_speed[1] 

            if delta_motor_spikes[0] > delta_motor_spikes[1]:
                self.joint_position[4] += self.eye_tilt_increase * delta_motor_spikes[0] * motor_speed[4] 
            elif delta_motor_spikes[0] < delta_motor_spikes[1]:
                self.joint_position[4] -= self.eye_tilt_increase * delta_motor_spikes[1] * motor_speed[5] 

            if abs(self.joint_position[3]) > self.eye_pan_limit:
                self.joint_position[3] = math.copysign(1.0, self.joint_position[3]) * self.eye_pan_limit
            if abs(self.joint_position[4]) > self.eye_tilt_limit:
                self.joint_position[4] = math.copysign(1.0, self.joint_position[4]) * self.eye_tilt_limit

            # Update right eye positions
            if delta_motor_spikes[4] > delta_motor_spikes[5]:
                self.joint_position[5] += self.eye_pan_increase * (0.3 * left_eye_move + 0.7 * right_eye_move) * motor_speed[2] 
            elif delta_motor_spikes[4] < delta_motor_spikes[5]:
                self.joint_position[5] += self.eye_pan_increase * (0.3 * left_eye_move + 0.7 * right_eye_move) * motor_speed[3] 

            if delta_motor_spikes[0] > delta_motor_spikes[1]:
                self.joint_position[6] += self.eye_tilt_increase * delta_motor_spikes[0] * motor_speed[4] 
            elif delta_motor_spikes[0] < delta_motor_spikes[1]:
                self.joint_position[6] -= self.eye_tilt_increase * delta_motor_spikes[1] * motor_speed[5] 

            if abs(self.joint_position[5]) > self.eye_pan_limit:
                self.joint_position[5] = math.copysign(1.0, self.joint_position[5]) * self.eye_pan_limit
            if abs(self.joint_position[6]) > self.eye_tilt_limit:
                self.joint_position[6] = math.copysign(1.0, self.joint_position[6]) * self.eye_tilt_limit

            # #Update left eye positions
            # self.joint_position[3] += self.eye_pan_increase * (delta_motor_spikes[2] - delta_motor_spikes[3])
            # self.joint_position[4] += self.eye_tilt_increase * (delta_motor_spikes[0] - delta_motor_spikes[1])
            # if abs(self.joint_position[3]) > self.eye_pan_limit:
            #     self.joint_position[3] = math.copysign(1.0, self.joint_position[3]) * self.eye_pan_limit
            # if abs(self.joint_position[4]) > self.eye_tilt_limit:
            #     self.joint_position[4] = math.copysign(1.0, self.joint_position[4]) * self.eye_tilt_limit

            # # Update right eye positions
            # self.joint_position[5] += self.eye_pan_increase * (delta_motor_spikes[4] - delta_motor_spikes[5])
            # self.joint_position[6] += self.eye_tilt_increase * (delta_motor_spikes[0] - delta_motor_spikes[1])
            # if abs(self.joint_position[5]) > self.eye_pan_limit:
            #     self.joint_position[5] = math.copysign(1.0, self.joint_position[5]) * self.eye_pan_limit
            # if abs(self.joint_position[6]) > self.eye_tilt_limit:
            #     self.joint_position[6] = math.copysign(1.0, self.joint_position[6]) * self.eye_tilt_limit


            # Control servos
            for dd, pos_pub in enumerate(self.pos_pub_list, 0):
                pos_msg = Float64()
                pos_msg.data = self.joint_position[dd]
                pos_pub.publish(pos_msg)

            #self.ros_rate.sleep()

    def stop_brain(self):
            self.running = False

    def reset_robot(self):
        ros_sleep = 500
        
        self.joint_position = [0, 0, 0, 0, 0, 0, 0]

        for dd, pos_pub in enumerate(self.pos_pub_list, 0):
            pos_msg = Float64()
            pos_msg.data = self.joint_position[dd]
            pos_pub.publish(pos_msg)

        rospy.Rate(ros_sleep).sleep()
        # rospy.Rate(sefl.ros)
        

    def get_exe_path(self):
        return os.path.dirname(os.path.abspath(sys.argv[0]))
    
    def update(self, threshold_value):
        self.brain.update_threshold(threshold_value)







