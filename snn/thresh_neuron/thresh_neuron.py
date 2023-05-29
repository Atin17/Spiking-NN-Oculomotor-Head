from collections import deque
import os

from snn.Constants import Constants


class ThreshNeuron:
    def __init__(self, filename, window=20, thresh=10):
        # Neuron parameters
        self.window_size = window
        self.threshold = thresh
        self.v_max = 25
        self.resting_potential = -70

        self.folder_name = Constants.instance().outputDir
        self.out_filename = filename
        # self.memb_out = open(os.path.join(self.folder_name, self.out_filename), "w")

        self.inputs = deque()
        self.effective_input = 0
        self.outs = deque()
        self.voltages = [self.resting_potential]
        self.out_3 = 0

    def process(self, input_current):
        new_membrane_potential = self.resting_potential
        negative = False

        if input_current < 0:
            input_current = 0
            negative = True

        self.effective_input += input_current

        self.inputs.append(input_current)
        if len(self.inputs) > self.window_size:
            self.effective_input -= self.inputs.popleft()

        if self.effective_input > self.threshold and not negative:
            new_membrane_potential = self.v_max

        self.voltages.append(new_membrane_potential)

        self.outs.append(1 if new_membrane_potential == 25 else 0)
        self.out_3 += 1 if new_membrane_potential == 25 else 0
        if len(self.outs) > 3:
            self.out_3 -= self.outs.popleft()

        # self.memb_out.write(str(new_membrane_potential) + "\n")

        return new_membrane_potential

    def reset(self):
        self.inputs.clear()
        self.voltages = [self.resting_potential]
        self.outs.clear()
        self.out_3 = 0
