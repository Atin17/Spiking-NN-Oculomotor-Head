from typing import List
from collections import deque
from snn.learning import rules
from snn.izhikevich_neuron.izhikevich import IzhikevichNeuron
from snn.Constants import Constants
#import tonic_neuron


class MotorNeuron(object):
    def __init__(self, filename, tn = None):
            # Neuron parameters
        self.Rm = 100.0 # Membrane resistance (kOhm)
        self.Cm = 10.0 # Membrane capacitance (uF)
        self.tau_m = self.Rm * self.Cm # Time constant (ms)
        self.dt = 1.0 # Time difference - with 30 fps
        self.spike_voltage = 15.0 # Spike potential (mV)
        self.resting_potential = None # Resting membrane potential (mV)
        self.refractory_period = 1.0 # Neuron refractory period (ms)
        self.resting_time = 0.0 # Neuron rest period after spike (ms)
        self.v_th = 10.0 # Threshold membrane potential for spike (mV)
        self.v_max = 25.0 # Max membrane potential (mV)

        self.folderName = Constants.instance().outputDir
        self.out_filename = filename
        self.memb_out = None
        self.inputs = None

        self.inhibitory = []
        self.excitatory = []

        self.inhibitory_weights = []
        self.excitatory_weights = []

        self.post_v = deque()
        self.inhibitory_pre_v = []
        self.excitatory_pre_v = []
        self.inhibitory_etrace = []
        self.excitatory_etrace = []

        self.voltages = []
        self.w_tn_v = 1.0
        self.w_tn_vv = 1.0
        self.w_tn_cv = 1.0
        self.tnv_weights = None
        self.tnvv_weights = None
        self.tncv_weights = None
        self.ibn_weights = None
        self.learning = False
        self.window_position = 0

        self.voltages.append(-50)
        self.resting_potential = -50.0
        self.learning = Constants.instance().learning

        # if not self.memb_out or not self.memb_out.is_open():
        #     self.memb_out = open((self.folderName + self.out_filename), "w")
        # if not self.inputs or not self.inputs.is_open():
        #     self.inputs = open((self.folderName + "inp_" + self.out_filename), "w")
        self.w_tn_v = 1.0
        self.w_tn_vv = 1.0
        self.w_tn_cv = 1.0

        if tn:
            self.add_tn_link(tn)

        # if self.learning:
        #     self.tnv_weights = open(self.folderName + self.out_filename + "_tnv", "w")
        #     self.tnvv_weights = open(self.folderName + self.out_filename + "_tnvv", "w")
        #     self.tncv_weights = open(self.folderName + self.out_filename + "_tncv", "w")
        #     self.ibn_weights = open(self.folderName + self.out_filename + "_ibn", "w")

    def to_current(self, membrane_potential):
        if membrane_potential == 25:  # Action potential
            return 1
        return 0

    def add_tn_link(self, tn):
        self.excitatory.append(tn)
        self.excitatory_weights.append(1.0)
        self.excitatory_pre_v.append(deque())
        self.excitatory_etrace.append(0.0)

    def process(self, input_current): #, reward_in=0):
        new_membrane_potential = self.resting_potential

        if self.resting_time > 0:
            self.resting_time -= 1
            new_membrane_potential = self.resting_potential
            self.voltages.append(new_membrane_potential)
            return new_membrane_potential

        membrane_potential = self.voltages[-1]
        I = self.alter_current(input_current)
        if I < 0:
            I = 0

        # self.inputs.write(str(I) + '\n')

        voltage_delta = ((I * self.Rm) - membrane_potential) * (self.dt/self.tau_m)

        new_membrane_potential = membrane_potential + voltage_delta

        if new_membrane_potential > self.v_th:
            new_membrane_potential += self.spike_voltage
            self.resting_time = self.refractory_period

        if new_membrane_potential > self.v_max:
            new_membrane_potential = self.v_max

        if new_membrane_potential < self.resting_potential:
            new_membrane_potential = self.resting_potential

        self.voltages.append(new_membrane_potential)

        if self.learning:
            self.post_v.append(float(new_membrane_potential == 25))
            if len(self.post_v) > Constants.instance().learning_window:
                self.post_v.popleft()
            self.window_position += 1
            if self.window_position % Constants.instance().learning_window == 0:
                self.window_position = 0
                # self.update_weights(reward_in)

        # self.memb_out.write(str(new_membrane_potential) + '\n')
        return new_membrane_potential

    def alter_current(self, input_current):
        ibn_v = 0
        size = 0
        
        if len(self.inhibitory) > 0:
            ibn = self.inhibitory[0]
            size = len(ibn.voltages)
            if size > 1:
                ibn_v = ibn.voltages[-1]

        else:
            self.inhibitory_weights.append(4.0 * self.tau_m * 180.0 / 1000.0)

        tn = self.excitatory[0]
        size = len(tn.voltages)
        tn_v = 0
        if size > 0:
            tn_v = tn.voltages[-1]

        tn_vv = 0
        if len(self.excitatory) >= 2:
            tn = self.excitatory[1]
            size = len(tn.voltages)
            if size > 0:
                tn_vv = tn.voltages[-1]

        else:
            self.excitatory_weights.append(8.0 * self.tau_m * 175.0 / 1000.0)

        tn_cv = 0
        if len(self.excitatory) == 3:
            tn = self.excitatory[2]
            size = len(tn.voltages)
            if size > 0:
                tn_cv = tn.voltages[-1]

        else:
            self.excitatory_weights.append(8.0 * self.tau_m * 175.0 / 1000.0)

        if self.learning:
            if len(self.inhibitory) > 0:
                self.inhibitory_pre_v[0].append(float(ibn_v == 25))
                if len(self.inhibitory_pre_v[0]) > Constants.instance().learning_window:
                    self.inhibitory_pre_v[0].popleft()

            self.excitatory_pre_v[0].append(float(tn_v == 25))
            if len(self.excitatory_pre_v[0]) > Constants.instance().learning_window:
                self.excitatory_pre_v[0].popleft()

            if len(self.excitatory) >= 2:
                self.excitatory_pre_v[1].append(float(tn_vv == 25))
                if len(self.excitatory_pre_v[1]) > Constants.instance().learning_window:
                    self.excitatory_pre_v[1].popleft()

            if len(self.excitatory) == 3:
                self.excitatory_pre_v[2].append(float(tn_cv == 25))
                if len(self.excitatory_pre_v[2]) > Constants.instance().learning_window:
                    self.excitatory_pre_v[2].popleft()

        # else:
        #     self.excitatory_weights[0] = 8.0 * self.tau_m * 175.0 / 1000.0
        #     self.excitatory_weights[1] = 8.0 * self.tau_m * 175.0 / 1000.0
        #     self.excitatory_weights[2] = 8.0 * self.tau_m * 175.0 / 1000.0
        #     self.inhibitory_weights[0] = 4.0 * self.tau_m * 180.0 / 1000.0

        return input_current \
            + self.to_current(tn_v) * self.w_tn_v * self.excitatory_weights[0] \
            + self.to_current(tn_vv) * self.w_tn_vv * self.excitatory_weights[1] \
            + self.to_current(tn_cv) * self.w_tn_cv * self.excitatory_weights[2] \
            - self.to_current(ibn_v) * self.inhibitory_weights[0]

        
    def update_weights(self, reward_in):
        if len(self.inhibitory) > 0:
            # print(self.post_v)
            h_ji = rules.hebbian(self.inhibitory_pre_v[0], self.post_v, 10.0, self.inhibitory_weights[0])
            # update etrace
            self.inhibitory_etrace[0] += self.delta_etrace(self.inhibitory_etrace[0], h_ji)
            self.inhibitory_weights[0] += h_ji * self.inhibitory_etrace[0] * (1 - reward_in) * Constants.instance().learning_rate
            # save weights to file
            self.ibn_weights.write(str(self.inhibitory_weights[0]) + "\n")
            self.ibn_weights.flush()

        h_ji = rules.hebbian(self.excitatory_pre_v[0], self.post_v, 10.0,self. excitatory_weights[0])
        # update etrace
        self.excitatory_etrace[0] += self.delta_etrace(self.excitatory_etrace[0], h_ji)
        self.excitatory_weights[0] += h_ji * self.excitatory_etrace[0] * (1 - reward_in) * Constants.instance().learning_rate

        if len(self.excitatory) >= 2:
            h_ji = rules.hebbian(self.excitatory_pre_v[1], self.post_v, 10.0, self.excitatory_weights[1])
            # update etrace
            self.excitatory_etrace[1] += self.delta_etrace(self.excitatory_etrace[1], h_ji)
            self.excitatory_weights[1] += h_ji * self.excitatory_etrace[1] * (1 - reward_in) * Constants.instance().learning_rate

        if len(self.excitatory) == 3:
            h_ji = rules.hebbian(self.excitatory_pre_v[2], self.post_v, 10.0, self.excitatory_weights[2])
            # update etrace
            self.excitatory_etrace[2] += self.delta_etrace(self.excitatory_etrace[2], h_ji)
            self.excitatory_weights[2] += h_ji * self.excitatory_etrace[2] * (1 - reward_in) * Constants.instance().learning_rate
        # save weights to file
        self.tnv_weights.write(str(self.excitatory_weights[0]) + "\n")
        self.tnvv_weights.write(str(self.excitatory_weights[1]) + "\n")
        self.tncv_weights.write(str(self.excitatory_weights[2]) + "\n")
        self.tnv_weights.flush()
        self.tnvv_weights.flush()
        self.tncv_weights.flush()


    def reset(self):
        self.voltages.append(self.resting_potential)


    def add_tn_link(self, tn):
        self.excitatory.append(tn)
        self.excitatory_weights.append(100)
        self.excitatory_pre_v.append(deque())
        self.excitatory_etrace.append(0)


    def add_ibn_link(self, ibn):
        self.inhibitory.append(ibn)
        self.inhibitory_weights.append(100)
        self.inhibitory_pre_v.append(deque())
        self.inhibitory_etrace.append(0)


    def delta_etrace(self, curr_value, h_ji):
        return (h_ji - curr_value) / (Constants.instance().learning_window * 3.0)
