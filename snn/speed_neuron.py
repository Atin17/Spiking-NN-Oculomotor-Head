'''
'''
import matplotlib.pyplot as plt
import math

class LIF(object):
    type = "Leaky Integrate and Fire"

    def __init__(self):
        super(LIF, self).__init__()
        # LIF Neuron Parameters #
        self.Rm = 100                # resistance (kOhm)
        self.Cm = 10               # capacitance (uF)
        self.tau_m = self.Rm * self.Cm       # time constant (ms)
        self.dt = 60  # time difference (ms) - considering 30fps frame rate
        self.spike_voltage = 15    # spike potential (mV)
        self.resting_potential = -60
        self.refractory_period = 1  # (ms)
        self.V_th = 10                # (mv)
        self.V_max = 25               # (mV)
        self.resting_time = 0
        self.voltages = [self.resting_potential]      

    def process(self, current):
        ''' '''
        if current < 0:
            current = 0

        new_membrane_potential = self.resting_potential

        if(self.resting_time > 0):
            self.resting_time -= 1
            self.voltages.append(new_membrane_potential)
            return new_membrane_potential

        membrane_potential = self.voltages[len(self.voltages) - 1]
        d_v = (1.0 / self.tau_m) * (-membrane_potential + current * self.Rm) * self.dt
        new_membrane_potential = membrane_potential + d_v

        if new_membrane_potential > self.V_th:
            new_membrane_potential += self.spike_voltage
            self.resting_time = self.refractory_period

        if new_membrane_potential > self.V_max:
            new_membrane_potential = self.V_max

        if new_membrane_potential < self.resting_potential:
            new_membrane_potential = self.resting_potential

        self.voltages.append(new_membrane_potential)

        return new_membrane_potential

    def reset(self):
        self.voltages.append(self.resting_potential)

def to_current(out):
    if out == 25:
        return 1
    return 0

if __name__ == '__main__':
    nrn1 = LIF()
    nrn2 = LIF()
    nrn3 = LIF()
    nrn4 = LIF()
    nrn5 = LIF()

    def run(inp):
        nrn1.reset()
        nrn2.reset()
        nrn3.reset()
        nrn4.reset()
        nrn5.reset()
        count = 0
        out1, out2, out3, out4, out5 = [0, 0, 0, 0, 0]
        for i in range(int(100000/45)):
            out1 = nrn1.process(inp * 5)
            out2 = nrn2.process(inp * 10 * (-0.5) + to_current(out2) + to_current(out1) * 2)
            out3 = nrn3.process(inp * 15 * (1/3) + to_current(out3) + to_current(out2) * 2 + to_current(out1) * 3)
            out4 = nrn4.process(inp * 20 * (-0.25) + to_current(out4) + to_current(out3) * 2 + to_current(out2) * 3 + to_current(out1) * 4)
            out5 = nrn5.process(inp * 25 * (1/5) + to_current(out5) + to_current(out4) * 2 + to_current(out3) * 3 + to_current(out2) * 4 + to_current(out1) * 5)
            count += to_current(out5)
        return count

    for x in range(360, 720, 30):
        max_w = math.log(1 + 360.0/288.0);
        y = math.log(1 + (x - 360.0)/288.0) / max_w;
        approx = y - (y**2)/2 + (y**3) / 3 - (y**4)/4 + (y**5)/5
        for it in range(niter):
            count = run(y, expected)
        print('Input: %s, Actual: %d, Approx: %d, From SNN: %d' % (y, math.log(1 + y) * 10, approx * 10, count))
