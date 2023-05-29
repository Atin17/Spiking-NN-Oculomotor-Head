import math
import os
from collections import deque
from typing import List

from .izhikevich_params import IzhikevichParams
from snn.Constants import Constants



class IzhikevichNeuron(object):
    def __call__(self, filename):
        # if filename == None:
        #     pass
        # else:
        self.params = IzhikevichParams()
        self.u_values = []
        self.u = 0.0
        self.v = 0.0
        self.inhibitory = []
        self.excitatory = []
        self.inhibitory_weights = []
        self.excitatory_weights = []
        self.post_v = deque()
        self.inhibitory_pre_v = []
        self.excitatory_pre_v = []
        self.inhibitory_etrace = []
        self.excitatory_etrace = []
        self.folder_name = Constants.instance().outputDir
        self.out_filename = filename
        self.memb_out = None
        self.learning = Constants.instance().learning
        self.window_position = 0
        self.voltages = []
        self.v_max = 25.0
        self.voltages = []
        self.u_values = []
        self.v = self.params.v_rest
        self.u = self.params.b * self.v
        
        # if not self.memb_out:
        #     self.memb_out = open(os.path.join(self.folder_name, self.out_filename), 'w')

    def to_current(self, membrane_potential):
        return membrane_potential == 25.0  # Action potential

    def delta_v(self, input_current):
        I = self.alter_current(input_current)
        if I < 0:
            I = 0
        
        return self.params.tau * (0.04 * math.pow(self.v, 2) + 5 * self.v + 140 - self.u + I)

    def process(self, input_current): #, reward_in = 0.0):
        if input_current < 0:
            input_current = 0
        self.v += self.delta_v(input_current)
        self.u += self.params.tau * self.params.a * (self.params.b * self.v - self.u)
        if self.v > self.v_max:
            self.voltages.append(self.v_max)
            self.v = self.params.c
            self.u += self.params.d
        else:
            self.voltages.append(self.v)
        self.u_values.append(self.u)
        v_out = self.voltages[-1]
        if self.learning:
            self.post_v.append(float(v_out == 25))
            if len(self.post_v) > Constants.instance().learning_window:
                self.post_v.popleft()
            self.window_position += 1
            if self.window_position % Constants.instance().learning_window == 0:
                self.window_position = 0
                # self.update_weights(reward_in)
        # self.memb_out.write(str(v_out) + '\n')
        return v_out

    def reset(self):
            self.v = self.params.v_rest
            self.u = self.params.b * self.v

    def inhibitory_synapse(self, nrn):
        self.inhibitory.append(nrn)
        self.inhibitory_weights.append(100)  # learning - initialize to random value?
        self.inhibitory_pre_v.append(deque())
        self.inhibitory_etrace.append(0)

    def excitatory_synapse(self, nrn):
        self.excitatory.append(nrn)
        self.excitatory_weights.append(100)  # learning - initialize to random value?
        self.excitatory_pre_v.append(deque())
        self.excitatory_etrace.append(0)

    @classmethod
    def delta_etrace(cls, curr_value, h_ji):
        return (h_ji - curr_value) / (Constants.instance().learning_window * 3.0)

    def update_weights(self, reward_in):
        pass

    def alter_current(self, input_current):
        pass

class ExcitableIzhikevichNeuron(IzhikevichNeuron):
    def __init__(self, filename):
        if filename == None:
            pass
        else:
            super(ExcitableIzhikevichNeuron, self).__call__(filename)
            # Initialize parameters here
            self.params.a = 0.1
            self.params.b = -0.1
            self.params.c = -55
            self.params.d = 6.0
            self.params.v_rest = -60
            self.params.tau = 0.5
            self.v = self.params.v_rest
            self.u = self.params.b * self.v
    
    def delta_v(self, input_current):
        I = input_current
        if I < 0:
            I = 0
        return self.params.tau * (0.04 * pow(self.v, 2) + 4.1 * self.v + 108 - self.u + I)
