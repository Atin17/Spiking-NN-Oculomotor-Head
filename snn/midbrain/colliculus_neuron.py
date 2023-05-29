import cv2
import numpy as np
from snn.debug.debug import Debug
from snn.Constants import Constants

class ColliculusNeuron:
    def __init__(self, x, y, eye):
        self.x = x
        self.y = y

        self.field = []
        

        self.folder_name = Constants.instance().outputDir
        self.out_filename = "sc_{}_{}_{}".format(eye, x, y)

        self.Rm = 100
        self.Cm = 10
        self.tau = self.Rm * self.Cm
        self.dt = 30
        self.spike_voltage = 15.0
        self.resting_potential = -70
        self.voltages = [self.resting_potential]

        self.v_th = 10
        self.v_max = 25

    def set_field(self, defined_field):
        self.field.extend(defined_field)

    def process(self, input_val):
        v = self.voltages[-1]
        dV = ((input_val * 100.0 * self.Rm) - v) * (self.dt / self.tau)
        v += dV

        if v > self.v_th:
            v += self.spike_voltage

        if v > self.v_max:
            v = self.v_max

        if v < self.resting_potential:
            v = self.resting_potential

        self.voltages.append(v)

        return v

    def reset(self):
        self.voltages.append(self.resting_potential)
                             

    def process_frame(self, frame):
        input_val = 0

        for xy in self.field:
            x_v, y_v = map(int, xy.split(","))
            val = frame[y_v, x_v]

            if val > 240:  # TODO: Convert this into inhibitory synaptic behavior for thresholding
                if Debug.debug_level <= Debug.DEBUG_VERBOSE:
                    print("X: {}, Y: {}, val: {}".format(self.x, self.y, val))
                input_val += 1

        return self.process(input_val)

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def get_last_output(self):
        return self.voltages[-1]