from typing import List

from snn.lif_neuron.lif_neuron import LeakyIntegrateFireNeuron
from snn.Constants import Constants


class LogNeuron1(LeakyIntegrateFireNeuron):
    def __init__(self, filename):
        # if filename == None:
        #     pass
        # else:
        super(LogNeuron1, self).__init__(filename, -60.0)
        self.refractory_period = 1

    def alter_current(self, input_current):
        return input_current * 5.0


class LogNeuron2(LeakyIntegrateFireNeuron):
    def __init__(self, filename, nrn):
        # if filename == None and nrn == None:
        #     pass
        # else:
        super(LogNeuron2, self).__init__(filename, -60.0)
        self.nrn1 = nrn
        self.refractory_period = 1

    def alter_current(self, input_current):
        size = len(self.nrn1.voltages)
        out1 = 0
        if size > 0:
            out1 = self.nrn1.voltages[-1]

        size = len(self.voltages)
        out = 0
        if size > 0:
            out = self.voltages[-1]

        return input_current * 10.0 * (-0.5) + self.to_current(out1) * 2.0 + self.to_current(out)


class LogNeuron3(LeakyIntegrateFireNeuron):
    def __init__(self, filename, nrn1, nrn2):
        # if filename == None and nrn1 == None and nrn2 == None:
        #     pass
        # else:
        super(LogNeuron3, self).__init__(filename, -60.0)
        self.nrn1 = nrn1
        self.nrn2 = nrn2
        self.refractory_period = 1

    def alter_current(self, input_current):
        size = len(self.nrn1.voltages)
        out1 = self.nrn1.voltages[-1] if size > 0 else 0

        size = len(self.nrn2.voltages)
        out2 = self.nrn2.voltages[-1] if size > 0 else 0

        size = len(self.voltages)
        out = self.voltages[-1] if size > 0 else 0

        return input_current * 15.0 * (1.0 / 3.0) + self.to_current(out1) * 3.0 + self.to_current(out2) * 2.0 + self.to_current(out)

class LogNeuron4(LeakyIntegrateFireNeuron):
    def __init__(self, filename, nrn1, nrn2, nrn3):
        # if filename == None and nrn1 == None and nrn2 == None and nrn3 == None:
        #     pass
        # else:
        super(LogNeuron4, self).__init__(filename, -60.0)
        self.nrn1 = nrn1
        self.nrn2 = nrn2
        self.nrn3 = nrn3
        self.refractory_period = 1
    
    def alter_current(self, input_current):
        size = len(self.nrn1.voltages)
        out1 = 0
        if size > 0:
            out1 = self.nrn1.voltages[-1]
        
        size = len(self.nrn2.voltages)
        out2 = 0
        if size > 0:
            out2 = self.nrn2.voltages[-1]
        
        size = len(self.nrn3.voltages)
        out3 = 0
        if size > 0:
            out3 = self.nrn3.voltages[-1]
        
        size = len(self.voltages)
        out = 0
        if size > 0:
            out = self.voltages[-1]
        
        return input_current * 20.0 * (-1.0/4.0) + \
            self.to_current(out1) * 4.0 + \
            self.to_current(out2) * 3.0 + \
            self.to_current(out3) * 2.0 + \
            self.to_current(out)
        

class LogNeuron5(LeakyIntegrateFireNeuron):
    def __init__(self, filename, nrn1, nrn2, nrn3, nrn4):
        # if filename == None and nrn1 == None and nrn2 == None and nrn3 == None and nrn4 == None:
        #     pass
        # else:
        super(LogNeuron5, self).__init__(filename, -60.0)
        self.nrn1 = nrn1
        self.nrn2 = nrn2
        self.nrn3 = nrn3
        self.nrn4 = nrn4
        self.refractory_period = 1
    
    def alter_current(self, input_current):
        size = len(self.nrn1.voltages)
        out1 = 0
        if size > 0:
            out1 = self.nrn1.voltages[-1]
        
        size = len(self.nrn2.voltages)
        out2 = 0
        if size > 0:
            out2 = self.nrn2.voltages[-1]
        
        size = len(self.nrn3.voltages)
        out3 = 0
        if size > 0:
            out3 = self.nrn3.voltages[-1]
        
        size = len(self.nrn4.voltages)
        out4 = 0
        if size > 0:
            out4 = self.nrn4.voltages[-1]
        
        size = len(self.voltages)
        out = 0
        if size > 0:
            out = self.voltages[-1]
        
        return input_current * 25.0 * (1.0/5.0) + \
            self.to_current(out1) * 5.0 + \
            self.to_current(out2) * 4.0 + \
            self.to_current(out3) * 3.0 + \
            self.to_current(out4) * 2.0 + \
            self.to_current(out)