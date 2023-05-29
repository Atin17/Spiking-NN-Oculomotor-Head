from typing import Optional
from snn.learning import rules
from collections import deque
from snn.izhikevich_neuron.izhikevich import IzhikevichNeuron
from snn.Constants import Constants
import math

class IFN(IzhikevichNeuron):
    def __call__(self, filename, ebn, ibn_c = None):
        # if filename == None and ebn == None and ibn_c == None:
        #     pass
        # else:
        super(IFN, self).__call__(filename)
        
        self.params.a = 0.02
        self.params.b = 0.2
        self.params.c = -65.0
        self.params.d = 2.0
        self.params.v_rest = -70.0
        self.params.tau = 0.25
        self.v = self.params.v_rest
        self.u = self.params.b * self.v
        
        self.add_ebn_link(ebn)
        # self.ebn_weights = open(Constants.instance().outputDir + filename + "_ebn", "w")
        
        if ibn_c:
            self.add_ibn_link(ibn_c)
            # self.ibn_weights = open(Constants.instance().outputDir + filename + "_ibn", "w")
    
    def alter_current(self, input_current):
        # EBN
        ebn_v = self.excitatory[0].voltages[-1]
        
        # IBN_c
        ibn_c_v = 0
        if self.inhibitory:
            # IBN_c - only for LL and RR, not for LR / RL
            ibn_c = self.inhibitory[0]
            size = len(ibn_c.voltages)
            if size > 1:
                ibn_c_v = ibn_c.voltages[-2]
        else:
            self.inhibitory_weights.append(0)
        
        if self.learning:
            if self.inhibitory:
                self.inhibitory_pre_v[0].append(float(ibn_c_v == 25))

                if len(self.inhibitory_pre_v[0]) > Constants.instance().learning_window:
                    self.inhibitory_pre_v[0].popleft()
            
            self.excitatory_pre_v[0].append(float(ebn_v == 25))
            if len(self.excitatory_pre_v[0]) > Constants.instance().learning_window:
                self.excitatory_pre_v[0].popleft()
        # else:
        #     self.excitatory_weights[0] = 125.0
        #     self.inhibitory_weights[0] = 125.0


        return (input_current 
                + self.to_current(ebn_v) * self.excitatory_weights[0]
                - self.to_current(ibn_c_v) * self.inhibitory_weights[0])
        
    def update_weights(self, reward_in):
        h_ji = 0.0
        if len(self.inhibitory) > 0:
            h_ji = rules.hebbian(self.inhibitory_pre_v[0], self.post_v, 10.0, self.inhibitory_weights[0])
            # update etrace
            self.inhibitory_etrace[0] += IzhikevichNeuron.delta_etrace(self.inhibitory_etrace[0], h_ji)
            self.inhibitory_weights[0] += h_ji * self.inhibitory_etrace[0] * (1 - reward_in) * Constants.instance().learning_rate

            # save weights to file
            self.ibn_weights.write(str(self.inhibitory_weights[0]) + "\n")
        
        h_ji = rules.hebbian(self.excitatory_pre_v[0], self.post_v, 10.0, self.excitatory_weights[0])
        # update etrace
        self.excitatory_etrace[0] += IzhikevichNeuron.delta_etrace(self.excitatory_etrace[0], h_ji)
        self.excitatory_weights[0] += h_ji * self.excitatory_etrace[0] * (1 - reward_in) * Constants.instance().learning_rate
        # save weights to file
        self.ebn_weights.write(str(self.excitatory_weights[0]) + "\n")

    def add_ebn_link(self, ebn):
        IzhikevichNeuron.excitatory_synapse(self, ebn)

    def add_ibn_link(self, ibn_c):
        IzhikevichNeuron.inhibitory_synapse(self, ibn_c)