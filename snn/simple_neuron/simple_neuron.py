class SimpleNeuron:
    white_value = 255
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.field = []
        self.voltages = []
        
    def set_field(self, defined_field):
        self.field = defined_field
        
    def process(self, frame, inhibiting_neuron_outputs):
        out = 0
        for val in inhibiting_neuron_outputs:
            if val == 1:
                self.voltages.append(out) # NOTE: out = 0
                return out
        
        for xy in self.field:
            x_v, y_v = map(int, xy.split(','))
            val = int(frame[y_v, x_v])
            
            if val > 240: # TODO: Convert this into inhibitory synaptic behavior for thresholding
                print("X: {}, Y: {}, val: {}".format(self.x, self.y, val))
                out = 1
                break
                
            
        self.voltages.append(out)
        return out
        
    def get_x(self):
        return self.x
        
    def get_y(self):
        return self.y
        
    def get_last_output(self):
        return self.voltages[-1]
