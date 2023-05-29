import os
from typing import Optional, List
from collections import deque
from snn.izhikevich_neuron.izhikevich import IzhikevichNeuron
from snn.Constants import Constants
from snn.learning import rules
import numpy as np


class EBN(IzhikevichNeuron):
    def __call__(
        self,
        filename,
        llbn,
        opn = None,
        ibn = None,
    ):
        
        # if filename == None and llbn == None and opn == None and ibn == None:
        #      pass
        # else: 
        super(EBN, self).__call__(filename)
        self.bias_current = 10

        self.opn_weights = None
        self.ibn_weights = None

        # Initialize parameters here
        self.params.a = 0.02
        self.params.b = 0.2
        self.params.c = -65.0
        self.params.d = 2.0
        self.params.v_rest = -70.0
        self.params.tau = 0.25
        self.v = self.params.v_rest
        self.u = self.params.b * self.v

        self.add_llbn_link(llbn)
        # self.llbn_weights = open(os.path.join(Constants.instance().outputDir, "{}_llbn".format(filename)), "w")

        if opn is not None:
            self.add_opn_link(opn)
            # self.opn_weights = open(
            #     os.path.join(Constants.instance().outputDir, "{}_opn".format(filename)), "w"
            # )

        if ibn is not None:
            self.add_ibn_link(ibn)
            # self.ibn_weights = open(
            #     os.path.join(Constants.instance().outputDir, "{}_ibn".format(filename)), "w"
            # )

    def alter_current(self, input_current):
        # LLBN
        llbn_v = self.excitatory[0].voltages[-1]

        # OPN - IBN_c - only for LL / RR , not LR/RL
        opn_v, ibn_c_v = 0, 0
        if self.inhibitory:
            # OPN
            opn = self.inhibitory[0]
            size = len(opn.voltages)
            if size > 1:
                opn_v = opn.voltages[-2]

            # IBN_c
            ibn_c = self.inhibitory[1]
            size = len(ibn_c.voltages)
            if size > 1:
                ibn_c_v = ibn_c.voltages[-2]
        else:
            self.inhibitory_weights.append(10.4 * 130.0)
            self.inhibitory_weights.append(0.5 * 130.0)

        # Learning
        if self.learning:
            if self.inhibitory:
                self.inhibitory_pre_v[0].append(float(opn_v == 25))
                #print(self.inhibitory_pre_v)
                if len(self.inhibitory_pre_v[0]) > Constants.instance().learning_window:
                    self.inhibitory_pre_v[0].popleft()
                self.inhibitory_pre_v[1].append(float(ibn_c_v == 25))
                if len(self.inhibitory_pre_v[1]) > Constants.instance().learning_window:
                    self.inhibitory_pre_v[1].popleft()
            self.excitatory_pre_v[0].append(float(llbn_v == 25))
            if len(self.excitatory_pre_v[0]) > Constants.instance().learning_window:
                self.excitatory_pre_v[0].popleft()


        return input_current \
        + self.bias_current \
        + self.to_current(llbn_v) * self.excitatory_weights[0] \
        - self.to_current(ibn_c_v) * self.inhibitory_weights[1] \
        - self.to_current(opn_v) * self.inhibitory_weights[0]
    

    def add_opn_link(self, opn):
        IzhikevichNeuron.inhibitory_synapse(self, opn)

    def add_ibn_link(self, ibn):
        IzhikevichNeuron.inhibitory_synapse(self, ibn)

    def add_llbn_link(self, llbn):
        IzhikevichNeuron.excitatory_synapse(self, llbn)