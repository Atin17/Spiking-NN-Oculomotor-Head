from snn.learning import rules
from snn.izhikevich_neuron.izhikevich import IzhikevichNeuron

from snn.Constants import Constants
from collections import deque
import math

class LLBN(IzhikevichNeuron):
    def __call__(self, filename = None, ifn_i = None):
        # if filename == None and ifn_i == None:
        #     pass
        # else:
        super(LLBN, self).__call__(filename)
        # Initialize parameters here
        '''
        params.a = 0.1;
        params.b = 0.5;
        params.c = -60;
        params.d = 0.05;
        params.v_rest = -60;
        params.tau = 0.5;
        v = params.v_rest;
        u = params.b * v;
        '''
        # Integrator params
        self.params.a = 0.1
        self.params.b = -0.075
        self.params.c = -55.0
        self.params.d = 6.0 # 6
        self.params.v_rest = -60.0
        self.params.tau = 1.0
        self.v = self.params.v_rest
        self.u = self.params.b * self.v

        self.add_ifn_link(ifn_i)

        # self.ifn_weights = open(Constants.instance().outputDir + filename + "_ifn", "w")

    def delta_v(self, input_current):
        I = self.alter_current(input_current)
        if I < 0:
            I = 0
        return self.params.tau * (0.04 * math.pow(self.v, 2) + 4.1 * self.v + 108 - self.u + I)

    # input_current = from sc (weighted)
    def alter_current(self, input_current):
        feedback_current = self.to_current(self.v)
        # IFN
        ifn_i = self.inhibitory[0]
        size = len(ifn_i.voltages)
        ifn_i_v = 0
        if size > 1:
            ifn_i_v = ifn_i.voltages[-2]
            if self.learning:
                self.inhibitory_pre_v[0].append(float(ifn_i_v == 25))
                if len(self.inhibitory_pre_v[0]) > Constants.instance().learning_window:
                    self.inhibitory_pre_v[0].popleft()

        # if not self.learning:
        #     self.inhibitory_weights[0] = 100.0 * self.params.tau / 8.0

        # ifn_i_w = 100.0 * params.tau / 8
        return input_current * 125.0 / 8 - self.to_current(ifn_i_v) * self.inhibitory_weights[0]

    def add_ifn_link(self, ifn_i):
        IzhikevichNeuron.inhibitory_synapse(self, ifn_i)

    def update_weights(self, reward_in):
        h_ji = rules.hebbian(self.inhibitory_pre_v[0], self.post_v, 10.0, self.inhibitory_weights[0])
        # update etrace
        self.inhibitory_etrace[0] += IzhikevichNeuron.delta_etrace(self.inhibitory_etrace[0], h_ji)
        self.inhibitory_weights[0] += h_ji * self.inhibitory_etrace[0] * (1 - reward_in) * Constants.instance().learning_rate
        # save weights to file
        self.ifn_weights.write(str(self.inhibitory_weights[0]) + "\n")