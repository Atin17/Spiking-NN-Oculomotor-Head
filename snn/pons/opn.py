from typing import List
import os
from snn.Constants import Constants
from snn.learning import rules
from snn.izhikevich_neuron.izhikevich import IzhikevichNeuron


class OPN(IzhikevichNeuron):
    bias_current = 40

    def __call__(self, filename = None, ibn_i = None, ibn_c = None):
        # if filename == None and ibn_i == None and ibn_c == None:
        #    pass
        # else:
        super(OPN, self).__call__(filename)
        self.params.a = 0.02
        self.params.b = 0.2
        self.params.c = -65.0
        self.params.d = 2.0
        self.params.v_rest = -70.0
        self.params.tau = 0.25
        self.v = self.params.v_rest
        self.u = self.params.b * self.v
        
        self.inhibitory = []
        self.add_ibn_link(ibn_i)
        self.add_ibn_link(ibn_c)
        
        # if self.learning:
        #     output_dir = Constants.instance().outputDir

        #     # self.ibn_i_weights = open(os.path.join(output_dir, filename + "_ibn_i"), 'w')
        #     # self.ibn_c_weights = open(os.path.join(output_dir, filename + "_ibn_c"), 'w')
    
    def alter_current(self, input_current):
        ibn_l = self.inhibitory[0]
        size = len(ibn_l.voltages)
        ibn_l_v = 0
        if size > 1:
            ibn_l_v = ibn_l.voltages[size - 2]
        
        ibn_r = self.inhibitory[1]
        size = len(ibn_r.voltages)
        ibn_r_v = 0
        if size > 1:
            ibn_r_v = ibn_r.voltages[size - 2]
        
        if self.learning:
            self.inhibitory_pre_v[0].append(float(ibn_l_v == 25))
            if len(self.inhibitory_pre_v[0]) > Constants.instance().learning_window:
                self.inhibitory_pre_v[0].popleft()
            
            self.inhibitory_pre_v[1].append(float(ibn_r_v == 25))
            if len(self.inhibitory_pre_v[1]) > Constants.instance().learning_window:
                self.inhibitory_pre_v[1].popleft()
        # else:
        #     self.inhibitory_weights[0] = 0.18 * 100.0
        #     self.inhibitory_weights[1] = 0.18 * 100.0
        
        return self.bias_current - input_current * 250.0 * 0.075 - self.to_current(ibn_l_v) * self.inhibitory_weights[0] - self.to_current(ibn_r_v) * self.inhibitory_weights[1]
    
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
        self.ibn_i_weights.write(str(self.inhibitory_weights[0]) + '\n')
        self.ibn_c_weights.write(str(self.inhibitory_weights[1]) + '\n')


    def add_ibn_link(self, ibn):
        IzhikevichNeuron.inhibitory_synapse(self, ibn)