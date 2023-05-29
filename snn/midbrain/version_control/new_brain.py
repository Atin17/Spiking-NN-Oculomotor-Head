import time
import cv2
import json
import numpy as np
from collections import deque
from typing import List
# Import the custom classes from their respective files
# For example:
from workqueue.workqueue import WorkQueue
from learning.rules import moving_average
from arbotix_pc_serial.position import Position
from debug.debug import Debug
from eye import receptive_field
from .colliculus_neuron import ColliculusNeuron
from .log_neuron_1 import LogNeuron1, LogNeuron2, LogNeuron3, LogNeuron4, LogNeuron5
from izhikevich_neuron.izhikevich import ExcitableIzhikevichNeuron
from lif_neuron.lif_neuron import LeakyIntegrateFireNeuron
from pons.reward_neuron import RewardNeuron
from pons.llbn import LLBN
from pons.ebn import EBN
from pons.ibn import IBN
from pons.ifn import IFN
from pons.opn import OPN
from pons.tonic_neuron import TonicNeuron
from pons.motor_neuron import MotorNeuron
from pons.selective_neuron import SelectiveNeuron
from thresh_neuron.thresh_neuron import ThreshNeuron
from sum_neuron.sum_neuron import SumNeuron

#from arbotix_pc_serial import arbotix_control

from Constants import Constants

threshold_value = 220
#Equivalent of say - Superior colliculus

class NewBrain:
    def __init__(self, frameQueue_Left: WorkQueue, frameQueue_Right: WorkQueue):

        self.coordinated_run = False
        self.frameQueue_Left = frameQueue_Left
        self.frameQueue_Right = frameQueue_Right


        # Assuming only horizontal movement to start with
        self.sc_neurons_Left = []
        self.sc_neurons_Right = []

        self.inverseJson = None

        self.frame_count = 0

        # status file
        self.stat_file = None
        self.at_start = True

        # position outputs
        self.pos_out_left = None
        self.pos_out_right = None
        self.pos_out_neck = None

        self.folderName = Constants.instance().outputDir

        self.opn = OPN()

        # Horizontal conjugate movements
        self.llbn_Left = LLBN()
        self.ebn_Left = EBN()
        self.ibn_Left = IBN()
        self.ifn_Left = IFN()

        self.llbn_Right = LLBN()
        self.ebn_Right = EBN()
        self.ibn_Right = IBN()
        self.ifn_Right = IFN()


        # Horizontal vergence movements
        self.llbn_LR = LLBN()
        self.ebn_LR = EBN()
        self.ifn_LR = IFN()

        self.llbn_RL = LLBN()
        self.ebn_RL = EBN()
        self.ifn_RL = IFN()

        # Vertical Movement
        self.llbn_U = LLBN()
        self.ebn_U = EBN()
        self.ifn_U = IFN()

        self.llbn_D = LLBN()
        self.ebn_D = EBN()
        self.ifn_D = IFN()

        # Horizontal motor neurons
        # Selection path based




        # Define neuron objects


        #self.control = ArbotixControl()
        self.leftEyeposition = Position()
        self.rightEyeposition = Position()
        self.neckposition = Position()

        self.neck_left_inputs = deque()
        self.neck_right_inputs = deque()

        # Horizontal
        # print("#1", self.ifn_Left)
        self.llbn_Left("llbn_l", self.ifn_Left)
        self.ifn_Left("ifn_l", self.ebn_Left, self.ibn_Right)
        # print("#2", self.ifn_Left)
        self.ebn_Left("ebn_l", self.llbn_Left, self.opn, self.ibn_Right)
        self.ibn_Left("ibn_l", self.ebn_Left, self.opn, self.ibn_Right)
        
        
        self.llbn_Right("llbn_r", self.ifn_Right)
        self.ebn_Right("ebn_r", self.llbn_Right, self.opn, self.ibn_Left)
        self.ibn_Right("ibn_r", self.ebn_Right, self.opn, self.ibn_Left)
        self.ifn_Right("ifn_r", self.ebn_Right, self.ibn_Left)
        self.opn("opn", self.ibn_Left, self.ibn_Right)
        self.tn_Left = TonicNeuron("tn_l", self.ebn_Left, self.ibn_Right)
        self.tn_Right = TonicNeuron("tn_r", self.ebn_Right, self.ibn_Left)

        # Vergence
        self.ifn_LR("ifn_lr", self.ebn_LR)
        self.ifn_RL("ifn_rl", self.ebn_RL)
        self.llbn_LR("llbn_lr", self.ifn_LR)
        self.llbn_RL("llbn_rl", self.ifn_RL)
        self.ebn_LR("ebn_lr", self.llbn_LR)
        self.ebn_RL("ebn_rl", self.llbn_RL)
        
        
        self.tn_LR = TonicNeuron("tn_lr", self.ebn_LR, self.ibn_Left)
        self.tn_RL = TonicNeuron("tn_rl", self.ebn_RL, self.ibn_Right)

        # Vertical
        self.llbn_U("llbn_u", self.ifn_U)
        self.llbn_D("llbn_d", self.ifn_D)
        self.ebn_U("ebn_u", self.llbn_U)
        self.ebn_D("ebn_d", self.llbn_D)
        self.ifn_U("ifn_u", self.ebn_U)
        self.ifn_D("ifn_d", self.ebn_D)
        self.tn_U = TonicNeuron("tn_u", self.ebn_U)
        self.tn_D = TonicNeuron("tn_d", self.ebn_D)
        self.mn_U = MotorNeuron("mn_u", self.tn_U)
        self.mn_D = MotorNeuron("mn_d", self.tn_D)

        # Neck - Horizontal
        self.mn_NL = LeakyIntegrateFireNeuron("mn_nl")
        self.mn_NR = LeakyIntegrateFireNeuron("mn_nr")
        self.mn_NU = LeakyIntegrateFireNeuron("mn_nu")
        self.mn_ND = LeakyIntegrateFireNeuron("mn_nd")

        # Selectivity Neurons - Eyes horizontal
        self.s1_r = ThreshNeuron("s1_r", 30, 3)
        self.s2_r = ThreshNeuron("s2_r", 30, 2)

        self.s3_r = ThreshNeuron("s3_r", 30, 1)
        self.s4_r = ThreshNeuron("s4_r", 30, 1)
        self.s1_l = ThreshNeuron("s1_l", 30, 3)
        self.s2_l = ThreshNeuron("s2_l", 30, 2)
        self.s3_l = ThreshNeuron("s3_l", 30, 1)
        self.s4_l = ThreshNeuron("s4_l", 30, 1)

        #Selectivity based motor neurons

        self.s1_r_mn_LR = SelectiveNeuron("s1_r_mn_lr", self.ibn_Left, self.tn_Right, 0, self.tn_LR, 0.8)
        self.s1_r_mn_RR = SelectiveNeuron("s1_r_mn_rr", self.ibn_Left, self.tn_Right, 0, self.tn_LR, 0)
        self.s2_r_mn_LR = SelectiveNeuron("s2_r_mn_lr", self.ibn_Left, self.tn_Right, 0, self.tn_LR, 1.3, self.tn_RL, 2.0)
        self.s2_r_mn_RR = SelectiveNeuron("s2_r_mn_rr", self.ibn_Left, self.tn_Right, 0, self.tn_LR, 0)
        self.s3_r_mn_LR = SelectiveNeuron("s3_r_mn_lr", self.ibn_Left, self.tn_Right, 0, self.tn_LR, 0.8)
        self.s3_r_mn_RR = SelectiveNeuron("s3_r_mn_rr", self.ibn_Left, self.tn_Right, 0, self.tn_LR, 3.0)
        self.s4_r_mn_LR = SelectiveNeuron("s4_r_mn_lr", self.ibn_Left, self.tn_Right, 1.5, self.tn_LR, 0)
        self.s4_r_mn_RR = SelectiveNeuron("s4_r_mn_rr", self.ibn_Left, self.tn_Right, 1.0, self.tn_LR, 0)
        self.r_mn_LR = SelectiveNeuron("r_mn_lr", self.ibn_Left, self.tn_Right, 0, self.tn_LR, 1.5)
        self.r_mn_RR = SelectiveNeuron("r_mn_rr", self.ibn_Left, self.tn_Right, 1.5, self.tn_LR, 0)
        self.s1_l_mn_RL = SelectiveNeuron("s1_l_mn_rl", self.ibn_Right, self.tn_Left, 0, self.tn_RL, 0.8)
        self.s1_l_mn_LL = SelectiveNeuron("s1_l_mn_ll", self.ibn_Right, self.tn_Left, 0, self.tn_RL, 0)
        self.s2_l_mn_RL = SelectiveNeuron("s2_l_mn_rl", self.ibn_Right, self.tn_Left, 0, self.tn_RL, 1.3, self.tn_LR, 2.0)
        self.s2_l_mn_LL = SelectiveNeuron("s2_l_mn_ll", self.ibn_Right, self.tn_Left, 0, self.tn_RL, 0)
        self.s3_l_mn_RL = SelectiveNeuron("s3_l_mn_rl", self.ibn_Right, self.tn_Left, 0, self.tn_RL, 0.8)
        self.s3_l_mn_LL = SelectiveNeuron("s3_l_mn_ll", self.ibn_Right, self.tn_Left, 0, self.tn_RL, 3.0)
        self.s4_l_mn_RL = SelectiveNeuron("s4_l_mn_rl", self.ibn_Right, self.tn_Left, 1.5, self.tn_RL, 0)
        self.s4_l_mn_LL = SelectiveNeuron("s4_l_mn_ll", self.ibn_Right, self.tn_Left, 1.0, self.tn_RL, 0)

        self.l_mn_RL = SelectiveNeuron("l_mn_rl", self.ibn_Right, self.tn_Left, 0, self.tn_RL, 1.5)
        self.l_mn_LL = SelectiveNeuron("l_mn_ll", self.ibn_Right, self.tn_Left, 1.5, self.tn_RL, 0)
        self.mn_LL = SumNeuron("mn_ll")
        self.mn_LR = SumNeuron("mn_lr")
        self.mn_RL = SumNeuron("mn_rl")
        self.mn_RR = SumNeuron("mn_rr")
        self.neck_mn_u = ExcitableIzhikevichNeuron("n_mn_u")
        self.neck_mn_d = ExcitableIzhikevichNeuron("neck_mn_d")
        self.neck_mn_l = ExcitableIzhikevichNeuron("neck_mn_l")
        self.neck_mn_r = ExcitableIzhikevichNeuron("neck_mn_r")

        # Learning/Reward Neurons
        self.rew_ll = RewardNeuron("rew_ll", self.llbn_Left, self.ebn_Left)
        self.rew_lr = RewardNeuron("rew_lr", self.llbn_LR, self.ebn_LR)
        self.rew_rl = RewardNeuron("rew_rl", self.llbn_RL, self.ebn_RL)
        self.rew_rr = RewardNeuron("rew_rr", self.llbn_Right, self.ebn_Right)

        # Speed Neurons
        self.sn1_ll = LogNeuron1("sn1_ll")
        self.sn2_ll = LogNeuron2("sn2_ll", self.sn1_ll)
        self.sn3_ll = LogNeuron3("sn3_ll", self.sn1_ll, self.sn2_ll)
        self.sn4_ll = LogNeuron4("sn4_ll", self.sn1_ll, self.sn2_ll, self.sn3_ll)
        self.sn5_ll = LogNeuron5("sn5_ll", self.sn1_ll, self.sn2_ll, self.sn3_ll, self.sn4_ll)
        
        self.sn1_lr = LogNeuron1("sn1_lr")
        self.sn2_lr = LogNeuron2("sn2_lr", self.sn1_lr)
        self.sn3_lr = LogNeuron3("sn3_lr", self.sn1_lr, self.sn2_lr)
        self.sn4_lr = LogNeuron4("sn4_lr", self.sn1_lr, self.sn2_lr, self.sn3_lr)
        self.sn5_lr = LogNeuron5("sn5_lr", self.sn1_lr, self.sn2_lr, self.sn3_lr, self.sn4_lr)

        self.sn1_rl = LogNeuron1("sn1_rl")
        self.sn2_rl = LogNeuron2("sn2_rl", self.sn1_rl)
        self.sn3_rl = LogNeuron3("sn3_rl", self.sn1_rl, self.sn2_rl)
        self.sn4_rl = LogNeuron4("sn4_rl", self.sn1_rl, self.sn2_rl, self.sn3_rl)
        self.sn5_rl = LogNeuron5("sn5_rl", self.sn1_rl, self.sn2_rl, self.sn3_rl, self.sn4_rl)
        
        self.sn1_rr = LogNeuron1("sn1_rr")
        self.sn2_rr = LogNeuron2("sn2_rr", self.sn1_rr)
        self.sn3_rr = LogNeuron3("sn3_rr", self.sn1_rr, self.sn2_rr)
        self.sn4_rr = LogNeuron4("sn4_rr", self.sn1_rr, self.sn2_rr, self.sn3_rr)
        self.sn5_rr = LogNeuron5("sn5_rr", self.sn1_rr, self.sn2_rr, self.sn3_rr, self.sn4_rr)
        
        self.sn1_u = LogNeuron1("sn1_u")
        self.sn2_u = LogNeuron2("sn2_u", self.sn1_u)
        self.sn3_u = LogNeuron3("sn3_u", self.sn1_u, self.sn2_u)
        self.sn4_u = LogNeuron4("sn4_u", self.sn1_u, self.sn2_u, self.sn3_u)
        self.sn5_u = LogNeuron5("sn5_u", self.sn1_u, self.sn2_u, self.sn3_u, self.sn4_rr)
        
        self.sn1_d = LogNeuron1("sn1_d")
        self.sn2_d = LogNeuron2("sn2_d", self.sn1_d)
        self.sn3_d = LogNeuron3("sn3_d", self.sn1_d, self.sn2_d)
        self.sn4_d = LogNeuron4("sn4_d", self.sn1_d, self.sn2_d, self.sn3_d)
        self.sn5_d = LogNeuron5("sn5_d", self.sn1_d, self.sn2_d, self.sn3_d, self.sn4_d)
        
        # Establishing neuron connections
        self.sc_neurons_Left = receptive_field.read_frontal_receptive_field(0)
        self.sc_neurons_Right = receptive_field.read_frontal_receptive_field(1)
        self.inverseJson = receptive_field.read_inverse_receptive_field()

        print("All neuron connections established")

        # Initializing eye and neck positions
        self.leftEyeposition = Position(1)
        self.rightEyeposition = Position(2)
        self.neckposition = Position(3)

        # Initializing output files
        self.pos_out_left = open(Constants.instance().outputDir + "pos_out_left", "w")
        self.pos_out_right = open(Constants.instance().outputDir + "pos_out_right", "w")
        self.pos_out_neck = open(Constants.instance().outputDir + "pos_out_neck", "w")

        # Initializing the status file
        self.stat_file = open("/tmp/robot_status", "a+")

        # Setting the coordinated run flag
        self.coordinated_run = Constants.instance().coordinated_run


    frame_num = 0  

    def computeColliculusInput(self, colliculusInput, x, y, eye):
        # eye = {0, 1} = {left, right}
        # Instead of having a center min weight based approach
        # Use min
        # Vertical Movement
        max_w = np.log(1 + 360.0/288.0)

        if x > 360: #Down
            w = np.log(1 + (x - 360.0)/288.0) / max_w
            colliculusInput[0] += w
        if x < 360: #Up
            w = np.log(1 + (360.0 - x)/288.0) / max_w
            colliculusInput[1] += w
        # Horizontal Movement
        if y < 360: #Left
            w = np.log(1 + (360.0 - y)/288.0) / max_w
            colliculusInput[2] += w
            if eye == 1:
                # right eye
                val = np.log(1 + (y)/288.0) / max_w
                colliculusInput[4] += val
        if y > 360: #Right
            w = np.log(1 + (y - 360.0)/288.0) / max_w
            colliculusInput[3] += w
            if eye == 0:
                # left eye
                val = np.log(1 + (720 - y)/288.0) / max_w
                colliculusInput[4] += val 

    def run(self):
        cv2.namedWindow("Left Eye")
        cv2.namedWindow("Right Eye")
        minPixelValue, maxPixelValue = None, None
        minPixelLocation, maxPixelLocation_Left, maxPixelLocation_Right = None, None, None
        maxLocation_Left, maxLocation_Right = "", ""
        neuronsWithFieldAtPixel_Left, neuronsWithFieldAtPixel_Right = [], []
        activeBipolars = None
        frame_count = 0
        frame_num = 0

        while True:
            leftQueueLength = len(self.frameQueue_Left)
            rightQueueLength = len(self.frameQueue_Right)

            if leftQueueLength == 0 or rightQueueLength == 0:
                continue

            frame_count += 1

            #Read frame from both eyes simultaneously
            frame_Left = self.frameQueue_Left.pop()
            frame_Right = self.frameQueue_Right.pop()

            #Invalid frame from one of the eyes
            if frame_Left.shape[0] == 0 or frame_Right.shape[0] == 0 or frame_Left.shape[1] == 0 or frame_Right.shape[1] == 0:
                raise Exception("-1")


            cv2.threshold(frame_Left, threshold_value, 255, cv2.THRESH_BINARY, dst=frame_Left)
            cv2.threshold(frame_Right, threshold_value, 255, cv2.THRESH_BINARY, dst=frame_Right)

            cv2.imshow("Left Eye", frame_Left)
            cv2.imshow("Right Eye", frame_Right)

            if cv2.waitKey(3) == 27:
                print("esc key is pressed by user")
                break

            frame_num += 1

            print("frame Number #", frame_num)

            if frame_count <= 30:
                self.process(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
                continue


            colliculusInput_Left = [0.0, 0.0, 0.0, 0.0, 0.0]
            colliculusInput_Right = [0.0, 0.0, 0.0, 0.0, 0.0]

            # Process frame
            locations_Left, locations_Right = np.empty([0,0]), np.empty([0,0])
            #frame_Left = np.array(frame_Left, dtype=np.uint8)
            #frame_Right = np.array(frame_Right, dtype=np.uint8)

            #print("frame num:{}, frame left{}, frame right {}".format(frame_num, frame_Left, frame_Right))
            
            locations_Left = cv2.findNonZero(frame_Left)
            locations_Right = cv2.findNonZero(frame_Right)

            input_Left, input_Right = {}, {}
            left_centers, right_centers = 0, 0

            left_x_center, left_y_center, right_x_center, right_y_center = 0, 0, 0, 0

            print("locations_Left:{}, locations_Right:{}".format(locations_Left, locations_Right))

            if locations_Left is None or locations_Right is None:
                continue

            for point in locations_Left:
                loc = f"{point[0][0]},{point[0][1]}"
                #print("loc:", loc)
                left_x_center += point[0][0]
                left_y_center += point[0][1]
                listOfNeurons = self.inverseJson[loc]
                for nrnIndex in listOfNeurons:
                    if nrnIndex not in input_Left:
                        input_Left[nrnIndex] = 1
                        left_centers += 1
                    else:
                        input_Left[nrnIndex] += 1

            for point in locations_Right:
                loc = f"{point[0][0]},{point[0][1]}"
                right_x_center += point[0][0]
                right_y_center += point[0][1]
                listOfNeurons = self.inverseJson[loc]
                for nrnIndex in listOfNeurons:
                    if nrnIndex not in input_Right:
                        input_Right[nrnIndex] = 1
                        right_centers += 1
                    else:
                        input_Right[nrnIndex] += 1

            if locations_Left.size > 0:
                left_x_center /= locations_Left.size
                left_y_center /= locations_Left.size
            if locations_Right.size > 0:
                right_x_center /= locations_Right.size
                right_y_center /= locations_Right.size

            # Send frame through all of the higher processing centers of the brain
            # to generate colliculus to LLBN/pons inputs
            in_l, in_r, left_c, right_c = 0, 0, 0, 0
            out_Left, out_Right, sc_in = 0, 0, 0

            # Left-right movement
            inp_llbn_Left_Left, inp_llbn_Left_Right = 0, 0
            inp_llbn_Right_Left, inp_llbn_Right_Right = 0, 0
            inp_from_right, inp_from_left = 0, 0

            # Up-down movement
            inp_llbn_Left_Up, inp_llbn_Left_Down = 0, 0
            inp_llbn_Right_Up, inp_llbn_Right_Down = 0, 0

            for cn_index in range(len(self.sc_neurons_Left)):
                self.sc_neurons_Left[cn_index].reset()
                self.sc_neurons_Right[cn_index].reset()

            for cn_index in range(len(self.sc_neurons_Left)):
                if cn_index not in input_Left:
                    in_l = 0
                else:
                    in_l = input_Left[cn_index]

                if cn_index not in input_Right:
                    in_r = 0
                else:
                    in_r = input_Right[cn_index]

                out_Left = self.sc_neurons_Left[cn_index].process(in_l)
                out_Right = self.sc_neurons_Right[cn_index].process(in_r)

                if out_Left == 25:
                    left_c += 1
                    self.computeColliculusInput(colliculusInput_Left, self.sc_neurons_Left[cn_index].get_y(), self.sc_neurons_Left[cn_index].get_x(), 0)
                    # Horizontal movement - left / right - for left eye
                    inp_llbn_Left_Left = colliculusInput_Left[2]
                    inp_llbn_Left_Right = colliculusInput_Left[3]
                    # Vertical movement - up / down - for left eye
                    inp_llbn_Left_Up = colliculusInput_Left[1]
                    inp_llbn_Left_Down = colliculusInput_Left[0]
                    # input for right eye from left
                    inp_from_left = colliculusInput_Left[4]

                if out_Right == 25:
                    right_c += 1
                    self.computeColliculusInput(colliculusInput_Right, self.sc_neurons_Right[cn_index].get_y(), self.sc_neurons_Right[cn_index].get_x(), 1)
                    # Horizontal movement - left / right - for right eye
                    inp_llbn_Right_Left = colliculusInput_Right[2]
                    inp_llbn_Right_Right = colliculusInput_Right[3]
                    # Vertical movement - up / down - for left eye
                    inp_llbn_Right_Up = colliculusInput_Right[1]
                    inp_llbn_Right_Down = colliculusInput_Right[0]
                    # input for left eye from right
                    inp_from_right = colliculusInput_Right[4]

            if left_c > 1:
                inp_llbn_Left_Left /= left_c
                inp_llbn_Left_Right /= left_c
                inp_from_left /= left_c
                inp_llbn_Left_Up /= left_c
                inp_llbn_Left_Down /= left_c

            if right_c > 1:
                inp_llbn_Right_Right /= right_c
                inp_llbn_Right_Left /= right_c
                inp_from_right /= right_c
                inp_llbn_Right_Down /= right_c
                inp_llbn_Right_Up /= right_c

            self.setReward(left_x_center, right_x_center, (right_y_center + left_y_center) / 2)

            # NOTE: Control transfer to midbrain
            ver_factor = 1.2
            opn_sc_input = (inp_llbn_Left_Left + inp_llbn_Right_Right) / 1.5
            self.process(
                inp_llbn_Left_Left,  # LL
                inp_llbn_Right_Right,  # RR
                opn_sc_input,  # OPN
                (inp_llbn_Left_Right),  # LR
                (inp_llbn_Right_Left),  # RL,
                inp_from_left,  # Fovea_in_Left
                inp_from_right,  # Fovea_in_right
                (inp_llbn_Left_Up + inp_llbn_Right_Up) / ver_factor,  # Up
                (inp_llbn_Left_Down + inp_llbn_Right_Down) / ver_factor,  # Down
                left_x_center, left_y_center,
                right_x_center, right_y_center
                )

    def setControl(arbotix_control):
        control = arbotix_control

    def setReward(self, left_x_center, right_x_center, vertical_center):
        if Constants.instance().learning:
            # Left-Left Reward
            new_reward = (-1.0 + (left_x_center <= 360) * 2.0) * (1 - (360 - left_x_center) / 360.0)
            Constants.instance().ll_reward = new_reward
            Constants.instance().ll_reward_avg = moving_average(Constants.instance().ll_reward_avg, new_reward)
            Constants.instance().ll_reward_signal = (Constants.instance().ll_reward - Constants.instance().ll_reward_avg)

            # Left-Right Reward
            new_reward = (-1.0 + (left_x_center >= 360) * 2.0) * (1 - (left_x_center - 360.0) / 360.0)
            Constants.instance().lr_reward = new_reward
            Constants.instance().lr_reward_avg = moving_average(Constants.instance().lr_reward_avg, new_reward)
            Constants.instance().lr_reward_signal = (Constants.instance().lr_reward - Constants.instance().lr_reward_avg)

            # Right-Left Reward
            new_reward = (-1.0 + (right_x_center <= 360) * 2.0) * (1 - (360 - right_x_center) / 360.0)
            Constants.instance().rl_reward = new_reward
            Constants.instance().rl_reward_avg = moving_average(Constants.instance().rl_reward_avg, new_reward)
            Constants.instance().rl_reward_signal = (Constants.instance().rl_reward - Constants.instance().rl_reward_avg)

            # Right-Right Reward
            new_reward = (-1.0 + (right_x_center >= 360) * 2.0) * (1 - (right_x_center - 360.0) / 360.0)
            Constants.instance().rr_reward = new_reward
            Constants.instance().rr_reward_avg = moving_average(Constants.instance().rr_reward_avg, new_reward)
            Constants.instance().rr_reward_signal = (Constants.instance().rr_reward - Constants.instance().rr_reward_avg)

            # Up Reward
            new_reward = (-1.0 + (vertical_center <= 360) * 2.0) * (1 - (360 - vertical_center) / 360.0)
            Constants.instance().u_reward = new_reward
            Constants.instance().u_reward_avg = moving_average(Constants.instance().u_reward_avg, new_reward)
            Constants.instance().u_reward_signal = (Constants.instance().u_reward - Constants.instance().u_reward_avg)

            # Down Reward
            new_reward = (-1.0 + (vertical_center >= 360) * 2.0) * (1 - (vertical_center - vertical_center) / 360.0)
            Constants.instance().d_reward = new_reward
            Constants.instance().d_reward_avg = moving_average(Constants.instance().d_reward_avg, new_reward)
            Constants.instance().d_reward_signal = (Constants.instance().d_reward - Constants.instance().d_reward_avg)

    def setReward_sc_input_based(self, ll_in, lr_in, rl_in, rr_in, u_in, d_in):
        if Constants.instance().learning:
            new_reward = ll_in - lr_in
            Constants.instance().ll_reward = new_reward
            Constants.instance().ll_reward_avg = moving_average(Constants.instance().ll_reward_avg, new_reward)
            Constants.instance().ll_reward_signal = Constants.instance().ll_reward - Constants.instance().ll_reward_avg

            new_reward = lr_in - ll_in
            Constants.instance().lr_reward = new_reward
            Constants.instance().lr_reward_avg = moving_average(Constants.instance().lr_reward_avg, new_reward)
            Constants.instance().lr_reward_signal = Constants.instance().lr_reward - Constants.instance().lr_reward_avg

            new_reward = rl_in - rr_in
            Constants.instance().rl_reward = new_reward
            Constants.instance().rl_reward_avg = moving_average(Constants.instance().rl_reward_avg, new_reward)
            Constants.instance().rl_reward_signal = Constants.instance().rl_reward - Constants.instance().rl_reward_avg

            new_reward = rr_in - rl_in
            Constants.instance().rr_reward = new_reward
            Constants.instance().rr_reward_avg = moving_average(Constants.instance().rr_reward_avg, new_reward)
            Constants.instance().rr_reward_signal = Constants.instance().rr_reward - Constants.instance().rr_reward_avg

            new_reward = u_in - d_in
            Constants.instance().u_reward = new_reward
            Constants.instance().u_reward_avg = moving_average(Constants.instance().u_reward_avg, new_reward)
            Constants.instance().u_reward_signal = Constants.instance().u_reward - Constants.instance().u_reward_avg

            new_reward = d_in - u_in
            Constants.instance().d_reward = new_reward
            Constants.instance().d_reward_avg = moving_average(Constants.instance().d_reward_avg, new_reward)
            Constants.instance().d_reward_signal = Constants.instance().d_reward - Constants.instance().d_reward_avg


    def process(self, sc_left_in, sc_right_in, sc_weak_in, sc_LR, sc_RL, fovea_in_l, fovea_in_r, sc_U, sc_D, left_x_center, left_y_center, right_x_center, right_y_center):
        out_mn_u = out_mn_d = out_mn_nl = out_mn_nr = 0.0
        out_tn_ll = out_tn_rl = out_tn_lr = out_tn_rr = 0.0
        left_LR = right_RL = left_LL = right_RR = max_left_LR = max_left_LL = max_right_RL = max_right_RR = out_mn_LR = out_mn_RL = out_mn_LL = out_mn_RR = 0
        up = down = neck_l = neck_r = neck_u = neck_d = 0
        mem_tn_ll = deque()
        mem_tn_lr = deque()
        mem_tn_rl = deque()
        mem_tn_rr = deque()
        sum_tn_ll = sum_tn_lr = sum_tn_rl = sum_tn_rr = 0.0
        out_s1_r = out_s2_r = out_s3_r = out_s4_r = 0.0
        out_s1_l = out_s2_l = out_s3_l = out_s4_l = 0.0
        s1_r_c = s2_r_c = s3_r_c = s4_r_c = s1_l_c = s2_l_c = s3_l_c = s4_l_c = 0
        count_tn_l = count_tn_r = count_tn_lr = count_tn_rl = 0
        sp_count_ll = sp_count_lr = sp_count_rl = sp_count_rr = sp_count_u = sp_count_d = 0

        self.mn_NU.reset()
        self.mn_ND.reset()
        self.mn_NL.reset()
        self.mn_NR.reset()

        # reset speed neurons
        self.sn1_ll.reset()
        self.sn2_ll.reset()
        self.sn3_ll.reset()
        self.sn4_ll.reset()
        self.sn5_ll.reset()

        self.sn1_lr.reset()
        self.sn2_lr.reset()
        self.sn3_lr.reset()
        self.sn4_lr.reset()
        self.sn5_lr.reset()

        self.sn1_rl.reset()
        self.sn2_rl.reset()
        self.sn3_rl.reset()
        self.sn4_rl.reset()
        self.sn5_rl.reset()

        self.sn1_rr.reset()
        self.sn2_rr.reset()
        self.sn3_rr.reset()
        self.sn4_rr.reset()
        self.sn5_rr.reset()

        self.sn1_u.reset()
        self.sn2_u.reset()
        self.sn3_u.reset()
        self.sn4_u.reset()
        self.sn5_u.reset()

        self.sn1_d.reset()
        self.sn2_d.reset()
        self.sn3_d.reset()
        self.sn4_d.reset()
        self.sn5_d.reset()

        for i in range(Constants.instance().window_size):
            # Horizontal
            self.llbn_Left.process(sc_left_in, Constants.instance().ll_reward_signal)
            self.llbn_Right.process(sc_right_in, Constants.instance().rr_reward_signal)
            self.llbn_LR.process(sc_LR, Constants.instance().lr_reward_signal)
            self.llbn_RL.process(sc_RL, Constants.instance().rl_reward_signal)

            self.ebn_Left.process(sc_left_in, Constants.instance().ll_reward_signal)
            self.ebn_Right.process(sc_right_in, Constants.instance().rr_reward_signal)
            self.ebn_LR.process(sc_LR, Constants.instance().lr_reward_signal)
            self.ebn_RL.process(sc_RL, Constants.instance().rl_reward_signal)

            self.rew_ll.process(sc_left_in)
            self.rew_lr.process(sc_LR)
            self.rew_rr.process(sc_right_in)

            self.ibn_Left.process(sc_left_in, Constants.instance().ll_reward_signal)
            self.ibn_Right.process(sc_right_in, Constants.instance().rr_reward_signal)

            self.ifn_Left.process(0, Constants.instance().ll_reward_signal)
            self.ifn_Right.process(0, Constants.instance().rr_reward_signal)
            self.ifn_LR.process(0, Constants.instance().lr_reward_signal)
            self.ifn_RL.process(0, Constants.instance().rl_reward_signal)

            self.opn.process(sc_weak_in, (
            Constants.instance().ll_reward_signal + Constants.instance().lr_reward_signal +
            Constants.instance().rl_reward_signal + Constants.instance().rr_reward_signal) / 4.0)

            out_tn_ll = self.tn_Left.process(0, Constants.instance().ll_reward_signal)
            mem_tn_ll.append(out_tn_ll == 25)
            sum_tn_ll += (out_tn_ll == 25)
            count_tn_l += (out_tn_ll == 25)

            if len(mem_tn_ll) > 10:
                sum_tn_ll -= mem_tn_ll[0]
                mem_tn_ll.popleft()

            out_tn_rr = self.tn_Right.process(0, Constants.instance().rr_reward_signal)
            mem_tn_rr.append(out_tn_rr == 25)
            sum_tn_rr += (out_tn_rr == 25)
            count_tn_r += (out_tn_rr == 25)

            if len(mem_tn_rr) > 10:
                sum_tn_rr -= mem_tn_rr[0]
                mem_tn_rr.popleft()

            out_tn_lr = self.tn_LR.process(0, Constants.instance().lr_reward_signal)
            mem_tn_lr.append(out_tn_lr == 25)
            sum_tn_lr += (out_tn_lr == 25)
            count_tn_lr += (out_tn_lr == 25)

            if len(mem_tn_lr) > 10:
                sum_tn_lr -= mem_tn_lr[0]
                mem_tn_lr.popleft()

            out_tn_rl = self.tn_RL.process(0, Constants.instance().rl_reward_signal)
            mem_tn_rl.append(out_tn_rl == 25)
            sum_tn_rl += (out_tn_rl == 25)
            count_tn_rl += (out_tn_rl == 25)

            if len(mem_tn_rl) > 10:
                sum_tn_rl -= mem_tn_rl[0]
                mem_tn_rl.popleft()

            #Eyes - right side - direction selection
            out_s1_r = self.s1_r.process((out_tn_lr == 25) - sum_tn_rr * 10 - self.s4_r.out_3 * 20)
            out_s1_r = (out_s1_r == 25)
            s1_r_c += out_s1_r
            out_s2_r = self.s2_r.process((out_tn_lr == 25) - sum_tn_rr * 10 - self.s1_r.out_3 * 10 - self.s4_r.out_3 * 20)
            out_s2_r = (out_s2_r == 25)
            s2_r_c += out_s2_r
            out_s3_r = self.s3_r.process((out_tn_lr == 25) - sum_tn_rr * 10 - self.s1_r.out_3 * 10 - self.s2_r.out_3 * 10 - self.s4_r.out_3 * 20)
            out_s3_r = (out_s3_r == 25)
            s3_r_c += out_s3_r
            out_s4_r = self.s4_r.process((out_tn_rr == 25) - sum_tn_lr * 10)
            out_s4_r = (out_s4_r == 25)
            s4_r_c += out_s4_r

            left_LR += self.s1_r_mn_LR.process((out_s2_r + out_s3_r + out_s4_r) * (-100.0), Constants.instance().lr_reward_signal) == 25
            right_RR += self.s1_r_mn_RR.process((out_s2_r + out_s3_r + out_s4_r) * (-100.0), Constants.instance().rr_reward_signal) == 25

            left_LR += self.s2_r_mn_LR.process((out_s1_r + out_s3_r + out_s4_r) * (-100.0), Constants.instance().lr_reward_signal) == 25
            right_RR += self.s2_r_mn_RR.process((out_s1_r + out_s3_r + out_s4_r) * (-100.0), Constants.instance().rr_reward_signal) == 25

            left_LR += self.s3_r_mn_LR.process((out_s2_r + out_s1_r + out_s4_r) * (-100.0), Constants.instance().lr_reward_signal) == 25
            right_RR += self.s3_r_mn_RR.process((out_s2_r + out_s1_r + out_s4_r) * (-100.0), Constants.instance().rr_reward_signal) == 25

            left_LR += self.s4_r_mn_LR.process((out_s2_r + out_s3_r + out_s1_r) * (-100.0), Constants.instance().lr_reward_signal) == 25
            right_RR += self.s4_r_mn_RR.process((out_s2_r + out_s3_r + out_s1_r) * (-100.0), Constants.instance().rr_reward_signal) == 25

            left_LR += self.r_mn_LR.process((out_s1_r + out_s2_r + out_s3_r + out_s4_r) * (-100.0), Constants.instance().lr_reward_signal) == 25
            right_RR += self.r_mn_RR.process((out_s1_r + out_s2_r + out_s3_r + out_s4_r) * (-100.0), Constants.instance().rr_reward_signal) == 25

            #Eyes - left side - direction selection
            out_s1_l = self.s1_l.process((out_tn_rl == 25) - sum_tn_ll * 10 - self.s4_l.out_3 * 20)
            out_s1_l = (out_s1_l == 25)
            s1_l_c += out_s1_l
            out_s2_l = self.s2_l.process((out_tn_rl == 25) - sum_tn_ll * 10 - self.s1_l.out_3 * 10 - self.s4_l.out_3 * 20)
            out_s2_l = (out_s2_l == 25)
            s2_l_c += out_s2_l
            out_s3_l = self.s3_l.process((out_tn_rl == 25) - sum_tn_ll * 10 - self.s1_l.out_3 * 10 - self.s2_l.out_3 * 10 - self.s4_l.out_3 * 20)
            out_s3_l = (out_s3_l == 25)
            s3_l_c += out_s3_l
            out_s4_l = self.s4_l.process((out_tn_ll == 25) - sum_tn_rl * 10)
            out_s4_l = (out_s4_l == 25)
            s4_l_c += out_s4_l

            right_RL += self.s1_l_mn_RL.process((out_s2_l + out_s3_l + out_s4_l) * (-100.0), Constants.instance().rl_reward_signal) == 25
            left_LL += self.s1_l_mn_LL.process((out_s2_l + out_s3_l + out_s4_l) * (-100.0), Constants.instance().ll_reward_signal) == 25

            right_RL += self.s2_l_mn_RL.process((out_s1_l + out_s3_l + out_s4_l) * (-100.0), Constants.instance().rl_reward_signal) == 25
            left_LL += self.s2_l_mn_LL.process((out_s1_l + out_s3_l + out_s4_l) * (-100.0), Constants.instance().ll_reward_signal) == 25

            right_RL += self.s3_l_mn_RL.process((out_s2_l + out_s1_l + out_s4_l) * (-100.0), Constants.instance().rl_reward_signal) == 25
            left_LL += self.s3_l_mn_LL.process((out_s2_l + out_s1_l + out_s4_l) * (-100.0), Constants.instance().ll_reward_signal) == 25

            right_RL += self.s4_l_mn_RL.process((out_s2_l + out_s3_l + out_s1_l) * (-100.0), Constants.instance().rl_reward_signal) == 25
            left_LL += self.s4_l_mn_LL.process((out_s2_l + out_s3_l + out_s1_l) * (-100.0), Constants.instance().ll_reward_signal) == 25

            right_RL += self.l_mn_RL.process((out_s1_l + out_s2_l + out_s3_l + out_s4_l) * (-100.0), Constants.instance().rl_reward_signal) == 25
            left_LL += self.l_mn_LL.process((out_s1_l + out_s2_l + out_s3_l + out_s4_l) * (-100.0), Constants.instance().ll_reward_signal) == 25

            out_mn_LL += self.mn_LL.process(left_LL - left_LR) == 25
            out_mn_RR += self.mn_RR.process(right_RR - right_RL) == 25
            out_mn_LR += self.mn_LR.process(left_LR - left_LL) == 25
            out_mn_RL += self.mn_RL.process(right_RL - right_RR) == 25

            # Vertical
            self.llbn_U.process(sc_U, Constants.instance().u_reward_signal)
            self.llbn_D.process(sc_D, Constants.instance().d_reward_signal)

            self.ebn_U.process(sc_U, Constants.instance().u_reward_signal)
            self.ebn_D.process(sc_D, Constants.instance().d_reward_signal)

            self.ifn_U.process(0, Constants.instance().u_reward_signal)
            self.ifn_D.process(0, Constants.instance().d_reward_signal)

            self.tn_U.process(0, Constants.instance().u_reward_signal)
            self.tn_D.process(0, Constants.instance().d_reward_signal)

            out_mn_u = self.mn_U.process(0, Constants.instance().u_reward_signal) == 25
            out_mn_d = self.mn_D.process(0, Constants.instance().d_reward_signal) == 25

            up += out_mn_u
            down += out_mn_d

            # Horizontal - Neck
            nl_in = 0
            nr_in = 0
            nl_in = (sc_left_in * 10.0 + sc_RL * 1.5) * 10.0
            nr_in = (sc_right_in * 10.0 + sc_LR * 1.5) * 10.0

            # Vertical - Neck
            nu_in = 0
            nd_in = 0
            nu_in = (sc_U) * 5.0 + out_mn_u * 5.0
            nd_in = (sc_D) * 5.0 + out_mn_d * 5.0

            # Write positions to output
            ms = int(round(time.time() * 1000))
            self.pos_out_left.write(f"{ms} {self.leftEyeposition.pan} {self.leftEyeposition.tilt}\n")
            self.pos_out_right.write(f"{ms} {self.rightEyeposition.pan} {self.rightEyeposition.tilt}\n")
            self.pos_out_neck.write(f"{ms} {self.neckposition.pan} {self.neckposition.tilt}\n")

            if self.coordinated_run:
                if at_start:
                    print("At start")
                    self.stat_file.write("START\n")
                    self.stat_file.flush()
                    at_start = False
                else:
                    status = self.stat_file.readline().strip()
                    self.stat_file.seek(0, 0)  # Go to beginning
                    if status != "START":
                        print("End?: ", status)
                        exit(0)

            out_mn_nl = self.mn_NL.process(nl_in)
            out_mn_nr = self.mn_NR.process(nr_in)

            out_mn_nu = self.mn_NU.process(nu_in)
            out_mn_nd = self.mn_ND.process(nd_in)

            neck_l += self.neck_mn_l.process((out_mn_nl == 25) * 20.0) == 25
            neck_r += self.neck_mn_r.process((out_mn_nr == 25) * 20.0) == 25
            neck_u += self.neck_mn_u.process((out_mn_nu == 25) * 25.0) == 25
            neck_d += self.neck_mn_d.process((out_mn_nd == 25) * 25.0) == 25

            # speed control
            # sc_left_in, sc_right_in, sc_LR, sc_RL
            self.sn1_ll.process(sc_left_in)
            self.sn2_ll.process(sc_left_in)
            self.sn3_ll.process(sc_left_in)
            self.sn4_ll.process(sc_left_in)
            sp_count_ll += self.sn5_ll.process(sc_left_in) == 25

            self.sn1_lr.process(sc_LR)
            self.sn2_lr.process(sc_LR)
            self.sn3_lr.process(sc_LR)
            self.sn4_lr.process(sc_LR)
            sp_count_lr += self.sn5_lr.process(sc_LR) == 25

            self.sn1_rl.process(sc_RL)
            self.sn2_rl.process(sc_RL)
            self.sn3_rl.process(sc_RL)
            self.sn4_rl.process(sc_RL)
            sp_count_rl += self.sn5_rl.process(sc_RL) == 25

            self.sn1_rr.process(sc_right_in)
            self.sn2_rr.process(sc_right_in)
            self.sn3_rr.process(sc_right_in)
            self.sn4_rr.process(sc_right_in)
            sp_count_rr += self.sn5_rr.process(sc_right_in) == 25

            self.sn1_u.process(sc_U)
            self.sn2_u.process(sc_U)
            self.sn3_u.process(sc_U)
            self.sn4_u.process(sc_U)
            sp_count_u += self.sn5_u.process(sc_U) == 25

            self.sn1_d.process(sc_D)
            self.sn2_d.process(sc_D)
            self.sn3_d.process(sc_D)
            self.sn4_d.process(sc_D)
            sp_count_d += self.sn5_d.process(sc_D) == 25

            if not(sc_left_in == 0 and sc_right_in == 0 and sc_LR == 0 and sc_RL == 0 and sc_U == 0 and sc_D == 0):
                self.executeMotorCommand(out_mn_LL, out_mn_RR, out_mn_LR, out_mn_RL, up, down, neck_l, neck_r, neck_u, neck_d, sp_count_ll, sp_count_lr, sp_count_rl, sp_count_rr, sp_count_u, sp_count_d)

    def executeMotorCommand(self, left_LR, right_LR, left_MR, right_MR, up, down, neck_left, neck_right, neck_up, neck_down, speed_ll, speed_lr, speed_rl, speed_rr, speed_u, speed_d):
        leftEyeSpikes = [down, up, left_LR, left_MR] # Down-Up-Left-Right
        rightEyeSpikes = [down, up, right_MR, right_LR]
        neckSpikes = [neck_down, neck_up, neck_left, neck_right]

        self.convertSpikesToposition(leftEyeSpikes, self.leftEyeposition, speed_ll, speed_lr, speed_u, speed_d)
        self.convertSpikesToposition(rightEyeSpikes, self.rightEyeposition, speed_rl, speed_rr, speed_u, speed_d)
        self.convertSpikesToNeckposition(neckSpikes, self.neckposition)

        #if(Constants.instance()::instance()->learning) {
        #    neckposition->pan = 512;
        #    neckposition->tilt = 512;
        #    neckposition->changed = false;
        #}
        #put back in to disable neck movement, because it currently seems that the neck cannot learn

        if(self.leftEyeposition.changed or self.rightEyeposition.changed or self.neckposition.changed):
            #self.control.move([self.neckposition.pan, self.neckposition.tilt, self.leftEyeposition.pan, self.leftEyeposition.tilt, self.rightEyeposition.pan, self.rightEyeposition.tilt])
            print([self.neckposition.pan, self.neckposition.tilt, self.leftEyeposition.pan, self.leftEyeposition.tilt, self.rightEyeposition.pan, self.rightEyeposition.tilt])

    def convertSpikesToNeckposition(self, oculoMotorSpikes, pos):
        horizontalRange = 20.0
        verticalRange = 20.0
        ignore = 1  # No. of spikes to ignore as no input
        pos.changed = False
        maxSpikes_Hor = 25.0
        maxSpikes_Ver = 20.0

        if oculoMotorSpikes[1] > oculoMotorSpikes[0]:
            # Move the tilt motor up
            position = verticalRange * np.log(1.0 + (oculoMotorSpikes[1] - ignore) / maxSpikes_Ver) / 0.6690496289808848
            pos.tilt += position
            if position > 0:
                pos.changed = True
        elif oculoMotorSpikes[0] > oculoMotorSpikes[1]:
            # Move tilt motor down
            position = verticalRange * np.log(1.0 + (oculoMotorSpikes[0] - ignore) / maxSpikes_Ver) / 0.6690496289808848
            pos.tilt -= position
            if position > 0:
                pos.changed = True

        if oculoMotorSpikes[2] > oculoMotorSpikes[3]:
            # Move pan motor left
            position = horizontalRange * np.log(1.0 + (oculoMotorSpikes[2] - ignore) / maxSpikes_Hor) / 0.6690496289808848
            pos.pan += position
            if position > 0:
                pos.changed = True
        elif oculoMotorSpikes[3] > oculoMotorSpikes[2]:
            # move pan motor right
            position = horizontalRange * np.log(1.0 + (oculoMotorSpikes[3] - ignore) / maxSpikes_Hor) / 0.6690496289808848
            pos.pan -= position
            if position > 0:
                pos.changed = True

        # Max pan / tilt positions of eye determine when the neck should move
        if pos.pan > 512 + 110:
            pos.pan = 622
        if pos.pan < 512 - 110:
            pos.pan = 402
        if pos.tilt > 512 + 100:
            pos.tilt = 612
        if pos.tilt < 512 - 100:
            pos.tilt = 412

    def convertSpikesToposition(self, oculoMotorSpikes, pos, speed_left, speed_right, speed_up, speed_down):
        horizontalRange = 2.0
        verticalRange = 5.0
        ignore = 1 #No. of spikes to ignore as no input
        pos.changed = False
        maxSpikes_Hor = 20.0
        maxSpikes_Ver = 20.0

        if oculoMotorSpikes[1] > oculoMotorSpikes[0]:
            #Move the tilt motor up
            position = verticalRange * speed_up * np.log(1.0 + (oculoMotorSpikes[1] - ignore) / maxSpikes_Ver) / 0.6690496289808848
            pos.tilt -= position
            if position > 0:
                pos.changed = True
        elif oculoMotorSpikes[0] > oculoMotorSpikes[1]:
            #Move tilt motor down
            position = verticalRange * speed_down * np.log(1.0 + (oculoMotorSpikes[0] - ignore) / maxSpikes_Ver) / 0.6690496289808848
            pos.tilt += position
            if position > 0:
                pos.changed = True
        if oculoMotorSpikes[2] > oculoMotorSpikes[3]:
            #Move pan motor left
            position = horizontalRange * speed_left * np.log(1.0 + (oculoMotorSpikes[2] - ignore) / maxSpikes_Hor) / 0.6690496289808848
            pos.pan += position
            if position > 0:
                pos.changed = True
        elif oculoMotorSpikes[3] > oculoMotorSpikes[2]:
            #move pan motor right
            position = horizontalRange * speed_right * np.log(1.0 + (oculoMotorSpikes[3] - ignore) / maxSpikes_Hor) / 0.6690496289808848
            pos.pan -= position
            if position > 0:
                pos.changed = True

        #Max pan / tilt positions of eye determine when the neck should move
        if pos._type == 1:
            if pos.pan > 512 + pos.lateral_range:
                pos.pan = (512 + pos.lateral_range)
            if pos.pan < 512 - pos.medial_range:
                pos.pan = (512 - pos.medial_range)
        else:
            if pos.pan > 512 + pos.medial_range:
                pos.pan = (512 + pos.medial_range)
            if pos.pan < 512 - pos.lateral_range:
                pos.pan = (512 - pos.lateral_range)

        if pos.tilt > 512 + 60:
            pos.tilt = 512 + 60
        if pos.tilt < 512 - 60:
            pos.tilt = 512 - 60

