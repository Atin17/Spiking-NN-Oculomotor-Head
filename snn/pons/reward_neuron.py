import os
from snn.izhikevich_neuron.izhikevich import IzhikevichNeuron
from snn.Constants import Constants
from collections import deque


class RewardNeuron(IzhikevichNeuron):
    def __init__(self, filename, llbn, ebn):
        super(RewardNeuron, self).__call__(filename)
        self.params.a = 0.1
        self.params.b = -0.075
        self.params.c = -55.0
        self.params.d = 6.0
        self.params.v_rest = -60.0
        self.params.tau = 1.0
        self.v = self.params.v_rest
        self.u = self.params.b * self.v

        self.add_llbn_link(llbn)
        self.add_ebn_link(ebn)

        self.learning = Constants.instance().learning
        self.window_size = 21
        self.window_position = 0
        self.window_count = 0
        self.prev_input = -1.0
        self.v_pre = deque()
        self.v_post = deque()

    def delta_v(self, input_current):
        I = self.alter_current(input_current)
        if I < 0:
            I = 0
        return self.params.tau * (0.04 * pow(self.v, 2) + 4.1 * self.v + 108 - self.u + I)

    def alter_current(self, input_current):
        curr = 0
        if self.learning:
            llbn_v = self.excitatory[0].voltages[-1]
            ebn_v = self.excitatory[1].voltages[-1]

            if self.prev_input == -1:
                self.prev_input = input_current

            self.v_pre.append(llbn_v == 25)
            self.v_post.append(ebn_v == 25)

            if len(self.v_pre) > self.window_size:
                self.v_pre.popleft()

            if len(self.v_post) > self.window_size:
                self.v_post.popleft()

            self.window_position += 1
            if self.window_position % self.window_size == 0:
                err = input_current + (float(self.prev_input) - float(input_current)) / 2.0
                curr = err * 10.0 + (sum(self.v_pre) - sum(self.v_post))
                self.prev_input = input_current
                self.window_position = 0
                self.window_count += 1
        return curr

    def add_ebn_link(self, ebn):
        IzhikevichNeuron.excitatory_synapse(self, ebn)

    def add_llbn_link(self, llbn):
        IzhikevichNeuron.excitatory_synapse(self, llbn)