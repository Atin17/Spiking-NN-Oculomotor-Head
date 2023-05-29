from typing import Optional
from snn.izhikevich_neuron.izhikevich import IzhikevichNeuron
from snn.pons.motor_neuron import MotorNeuron
from snn.pons.tonic_neuron import TonicNeuron


class SelectiveNeuron(MotorNeuron):
    def __init__(self, filename, ibn, tn_i, w_i  = 0, tn_c = None, w_c = None, tn_cc = None, w_cc = 0):
        super(SelectiveNeuron, self).__init__(filename)
        self.add_ibn_link(ibn)
        self.add_tn_link(tn_i)
        self.w_tn_v = w_i
        self.w_tn_vv = w_c
        self.w_tn_cv = w_cc
        self.add_tn_link(tn_c)
        if tn_cc is not None:
            self.add_tn_link(tn_cc)