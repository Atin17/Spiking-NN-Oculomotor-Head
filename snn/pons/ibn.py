import os
from typing import List
from collections import deque
from snn.learning import rules
from snn.izhikevich_neuron.izhikevich import IzhikevichNeuron

from snn.Constants import Constants

class IBN(IzhikevichNeuron):
    def __call__(self, filename = None, ebn = None, opn = None, ibn_c = None):
        # if filename  == None and ebn == None and opn == None and ibn_c == None:
        #     pass
        # else:
        super(IBN, self).__call__(filename)
        self.bias_current = 10.0
        # self.ebn_weights = open(os.path.join(Constants.instance().outputDir, "{}_ebn".format(filename)), "w")
        # self.opn_weights = open(os.path.join(Constants.instance().outputDir, "{}_opn".format(filename)), "w")
        # self.ibn_weights = open(os.path.join(Constants.instance().outputDir, "{}_ibn".format(filename)), "w")
        self.params.a = 0.02
        self.params.b = 0.2
        self.params.c = -65.0
        self.params.d = 2.0
        self.params.v_rest = -70.0
        self.params.tau = 0.25
        self.v = self.params.v_rest
        self.u = self.params.b * self.v
        self.add_ebn_link(ebn)
        self.add_opn_link(opn)
        self.add_ibn_link(ibn_c)
        self.inhibitory_pre_v = []
        self.excitatory_pre_v = []
        self.inhibitory_etrace = [0.0, 0.0]
        self.excitatory_etrace = [0.0]
        self.inhibitory_weights = [0.0, 0.0]
        self.excitatory_weights = [0.10 * 125.0]
        self.learning = False

    def alter_current(self, input_current):
        # EBN
        ebn_v = self.excitatory[0].voltages[-1]
        # OPN
        opn = self.inhibitory[0]
        opn_v = 0
        if len(opn.voltages) > 1:
            opn_v = opn.voltages[-2]
        # IBN_c
        ibn_c = self.inhibitory[1]
        ibn_c_v = 0
        if len(ibn_c.voltages) > 1:
            ibn_c_v = ibn_c.voltages[-2]

        if self.learning:
            self.inhibitory_pre_v[0].append(float(opn_v == 25))
            if len(self.inhibitory_pre_v[0]) > Constants.instance().learning_window:
                self.inhibitory_pre_v[0].popleft()
            self.inhibitory_pre_v[1].append(float(ibn_c_v == 25))
            if len(self.inhibitory_pre_v[1]) > Constants.instance().learning_window:
                self.inhibitory_pre_v[1].popleft()
            self.excitatory_pre_v[0].append(float(ebn_v == 25))
            if len(self.excitatory_pre_v[0]) > Constants.instance().learning_window:
                self.excitatory_pre_v[0].popleft()
        # else:
        #     self.excitatory_weights[0] = 0.10 * 125.0
        #     self.inhibitory_weights[0] = 6.4 * 125.0
        #     self.inhibitory_weights[1] = 0.15 * 125.0

        return (input_current + self.bias_current + self.to_current(ebn_v) * self.excitatory_weights[0] - self.to_current(ibn_c_v) * self.inhibitory_weights[1] - self.to_current(opn_v) * self.inhibitory_weights[0]) # * 6.4 * 125;
    
    def update_weights(self, reward_in):
        h_ji = rules.hebbian(self.inhibitory_pre_v[0], self.post_v, 10.0, self.inhibitory_weights[0])
        # update etrace
        self.inhibitory_etrace[0] += IzhikevichNeuron.delta_etrace(self.inhibitory_etrace[0], h_ji)
        self.inhibitory_weights[0] += h_ji * self.inhibitory_etrace[0] * (1 - reward_in) * Constants.instance().learning_rate

        h_ji = rules.hebbian(self.inhibitory_pre_v[1], self.post_v, 10.0, self.inhibitory_weights[1])
        # update etrace
        self.inhibitory_etrace[1] += IzhikevichNeuron.delta_etrace(self.inhibitory_etrace[1], h_ji)
        self.inhibitory_weights[1] += h_ji * self.inhibitory_etrace[1] * (1 - reward_in) * Constants.instance().learning_rate
        # save weights to file
        self.opn_weights.write(str(self.inhibitory_weights[0]) + "\n")
        self.ibn_weights.write(str(self.inhibitory_weights[1]) + "\n")

        h_ji = rules.hebbian(self.excitatory_pre_v[0], self.post_v, 10.0, self.excitatory_weights[0])
        # update etrace
        self.excitatory_etrace[0] += IzhikevichNeuron.delta_etrace(self.excitatory_etrace[0], h_ji)
        self.excitatory_weights[0] += h_ji * self.excitatory_etrace[0] * (1 - reward_in) * Constants.instance().learning_rate
        # save weights to file
        self.ebn_weights.write(str(self.excitatory_weights[0]) + "\n")

    def add_ibn_link(self, ibn_c):
        IzhikevichNeuron.inhibitory_synapse(self, ibn_c)

    def add_opn_link(self, opn):
        IzhikevichNeuron.inhibitory_synapse(self, opn)

    def add_ebn_link(self, ebn):
        IzhikevichNeuron.excitatory_synapse(self, ebn)