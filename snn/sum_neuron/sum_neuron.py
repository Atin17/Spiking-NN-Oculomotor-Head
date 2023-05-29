import numpy as np
import os
from snn.Constants import Constants

class SumNeuron:
    def __init__(self, filename):
    # Neuron parameters
        self.v_max = 25
        self.resting_potential = -70
        
        self.folderName = Constants.instance().outputDir
        self.out_filename = filename
        self.voltages = [self.resting_potential]
        self.out_3 = 0

        # if not os.path.isfile(self.folderName + self.out_filename):
        #     self.memb_out = open(self.folderName + self.out_filename, "w")
        # else:
        #     self.memb_out = open(self.folderName + self.out_filename, "a")
        
    def process(self, input_current):          
        new_membrane_potential = self.resting_potential
        
        if input_current > 0:
            new_membrane_potential = self.v_max
            
        self.voltages.append(new_membrane_potential)
        # self.memb_out.write(str(new_membrane_potential) + "\n")
        
        return new_membrane_potential
    
    def reset(self):
        self.voltages.append(self.resting_potential)