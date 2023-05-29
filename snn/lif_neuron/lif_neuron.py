from typing import List
import os
from snn.Constants import Constants



class LeakyIntegrateFireNeuron(object):
    def __init__(self, filename, rest_potential = -70.0):
        self.Rm = 100.0                 # Membrane resistance (kOhm)
        self.Cm = 10.0                  # Membrane capacitance (uF)
        self.tau_m = self.Rm * self.Cm  # Time constant (ms)
        self.spike_voltage = 15.0       # Spike potential (mV)
        self.resting_potential = rest_potential  # Resting membrane potential (mV)
        self.refractory_period = 0      # Neuron refractory period (ms)
        self.resting_time = 0           # Neuron rest period after spike (ms)
        self.v_th = 10.0                # Threshold membrane potential for spike (mV)
        self.v_max = 25.0               # Max membrane potential (mV)
        self.dt = 60.0                  # Time difference - with 30 fps
        self.voltages = [rest_potential] # type: List[float]
        self.folderName = Constants.instance().outputDir
        self.out_filename = filename
        self.memb_out = None
        if not os.path.exists(self.folderName):
            os.makedirs(self.folderName)
        self.memb_out = open(os.path.join(self.folderName, self.out_filename), 'w')

    def alter_current(self, input_current):
        return input_current

    def process(self, input_current) :

        new_membrane_potential = self.resting_potential

        if self.resting_time > 0:
            self.resting_time -= 1
            new_membrane_potential = self.resting_potential
            self.voltages.append(new_membrane_potential)
            return new_membrane_potential

        input_current = self.alter_current(input_current)

        if input_current < 0:
            input_current = 0

        membrane_potential = self.voltages[-1]
        voltage_delta = ((input_current * self.Rm) - membrane_potential) * (self.dt/self.tau_m)

        new_membrane_potential = membrane_potential + voltage_delta

        if new_membrane_potential > self.v_th:
            new_membrane_potential += self.spike_voltage
            self.resting_time = self.refractory_period

        if new_membrane_potential > self.v_max:
            new_membrane_potential = self.v_max

        if new_membrane_potential < self.resting_potential:
            new_membrane_potential = self.resting_potential

        self.voltages.append(new_membrane_potential)
        return new_membrane_potential

    def getSize(self):
        print("{}:{}".format(len(self.voltages), self.voltages.__len__()))
        return len(self.voltages)

    def reset(self):
        self.voltages.append(self.resting_potential)

    def to_current(self, voltage):
        return voltage == 25.0