from typing import List
from collections import deque
from snn.learning import rules
from snn.izhikevich_neuron.izhikevich import IzhikevichNeuron


from snn.Constants import Constants


class TonicNeuron:
    def __init__(self, filename, ebn, ibn = None):  
        self.Rm = 100.0                      # Membrane resistance (kOhm)
        self.Cm = 10.0                         # Membrane capacitance (uF)
        self.tau_m = self.Rm * self.Cm      # Time constant (ms)
        self.dt = 1.0                        # Time difference - with 30 fps
        self.spike_voltage = 15.0           # Spike potential (mV)
        self.resting_potential = -60.0        # Resting membrane potential (mV)
        self.refractory_period = 1.0          # Neuron refractory period (ms)
        self.resting_time = 0               # Neuron rest period after spike (ms)

        self.v_th = 10.0                      # Threshold membrane potential for spike (mV)
        self.v_max = 25.0                     # Max membrane potential (mV)

        self.folderName = Constants.instance().outputDir
        self.out_filename = filename
        self.memb_out = None

        self.inhibitory = []
        self.excitatory = []
        self.inhibitory_weights = []
        self.excitatory_weights = []

        self.post_v = deque()
        self.inhibitory_pre_v = []
        self.excitatory_pre_v = []
        self.inhibitory_etrace = []
        self.excitatory_etrace = []

        self.voltages = [-60]
        self.learning = Constants.instance().learning

        # if self.memb_out is None:
        #     self.memb_out = open((self.folderName + self.out_filename), 'w')

        self.add_ebn_link(ebn)
        if ibn is not None:
            self.add_ibn_link(ibn)

        # if self.learning:
        #     self.ebn_weights = open(self.folderName + filename + '_ebn', 'w')
        #     if ibn is not None:
        #         self.ibn_weights = open(self.folderName + filename + '_ibn', 'w')

        self.window_position = 0

    def add_ebn_link(self, ebn):
        self.excitatory.append(ebn)
        self.excitatory_pre_v.append(deque())
        self.excitatory_etrace.append(0)
        self.excitatory_weights.append(1)

    def add_ibn_link(self, ibn):
        self.inhibitory.append(ibn)
        self.inhibitory_pre_v.append(deque())
        self.inhibitory_etrace.append(0)
        self.inhibitory_weights.append(1)

    def to_current(self, membrane_potential) :
        if membrane_potential == 25:  # Action potential
            return 1
        return 0

    def process(self, input_current): #, reward_in = 0.0):
        new_membrane_potential = self.resting_potential

        if self.resting_time > 0:
            self.resting_time -= 1
            new_membrane_potential = self.resting_potential
            self.voltages.append(new_membrane_potential)
            return new_membrane_potential

        membrane_potential = self.voltages[-1]
        I = self.alter_current(input_current)
        if I < 0:
            I = 0
        voltage_delta = ((I * self.Rm) - membrane_potential) * (self.dt / self.tau_m)

        new_membrane_potential = membrane_potential + voltage_delta

        if new_membrane_potential > self.v_th:
            new_membrane_potential += self.spike_voltage
            self.resting_time = self.refractory_period

        if new_membrane_potential > self.v_max:
            new_membrane_potential = self.v_max

        if new_membrane_potential < self.resting_potential:
            new_membrane_potential = self.resting_potential

        self.voltages.append(new_membrane_potential)

        if self.learning:
            self.post_v.append(float(new_membrane_potential == 25))
            if len(self.post_v) > Constants.instance().learning_window:
                self.post_v.popleft()
            self.window_position += 1
            if self.window_position % Constants.instance().learning_window == 0:
                self.window_position = 0
                # self.update_weights(reward_in)

        # self.memb_out.write(str(new_membrane_potential) + '\n')
        return new_membrane_potential


    def update_weights(self, reward_in):
        h_ji = None
        if len(self.inhibitory) > 0:
            h_ji = rules.hebbian(self.inhibitory_pre_v[0], self.post_v, 10.0, self.inhibitory_weights[0])
            # update etrace
            self.inhibitory_etrace[0] += self.delta_etrace(self.inhibitory_etrace[0], h_ji)
            self.inhibitory_weights[0] += h_ji * self.inhibitory_etrace[0] * (1 - reward_in) * Constants.instance().learning_rate
            # save weights to file
            self.ibn_weights.write(str(self.inhibitory_weights[0]) + "\n")
            self.ibn_weights.flush()

        h_ji = rules.hebbian(self.excitatory_pre_v[0], self.post_v, 10.0, self.excitatory_weights[0])
        # update etrace
        self.excitatory_etrace[0] += self.delta_etrace(self.excitatory_etrace[0], h_ji)
        self.excitatory_weights[0] += h_ji * self.excitatory_etrace[0] * (1 - reward_in) * Constants.instance().learning_rate
        # save weights to file
        self.ebn_weights.write(str(self.excitatory_weights[0]) + "\n")
        self.ebn_weights.flush()

    def alter_current(self, input_current):
        feedback_current = self.to_current(self.voltages[-1])
        ibn_c_v = 0
        size = None
        #IBN_c - only LL/RR not LR/RL
        if len(self.inhibitory) > 0:
            #IBN
            ibn_c = self.inhibitory[0]
            size = len(ibn_c.voltages)
            if size > 1:
                ibn_c_v = ibn_c.voltages[-2]
        else:
            self.inhibitory_weights.append(3.8 * self.tau_m * 40)

        #EBN
        ebn_i = self.excitatory[0]
        size = len(ebn_i.voltages)
        ebn_i_v = 0
        if size > 1:
            ebn_i_v = ebn_i.voltages[-2]

        if self.learning:
            if len(self.inhibitory) > 0:
                self.inhibitory_pre_v[0].append(float(ibn_c_v == 25))
                if len(self.inhibitory_pre_v[0]) > Constants.instance().learning_window:
                    self.inhibitory_pre_v[0].popleft()
            self.excitatory_pre_v[0].append(float(ebn_i_v == 25))
            if len(self.excitatory_pre_v[0]) > Constants.instance().learning_window:
                self.excitatory_pre_v[0].popleft()
        # else:
        #     self.excitatory_weights[0] = 3.8 * self.tau_m * 30
        #     self.inhibitory_weights[0] = 3.8 * self.tau_m * 40

        return (feedback_current +
                self.to_current(ebn_i_v) * self.excitatory_weights[0] 
                - self.to_current(ibn_c_v) * self.inhibitory_weights[0])

    def reset(self):
        self.voltages.append(self.resting_potential)

    def inhibitory_synapse(self, nrn):
        self.inhibitory.append(nrn)
        self.inhibitory_weights.append(100)
        self.inhibitory_pre_v.append(deque())
        self.inhibitory_etrace.append(0)

    def excitatory_synapse(self, nrn):
        self.excitatory.append(nrn)
        self.excitatory_weights.append(100)
        self.excitatory_pre_v.append(deque())
        self.excitatory_etrace.append(0)

    def add_ibn_link(self, ibn_c):
        self.inhibitory_synapse(ibn_c)

    def add_ebn_link(self, ebn_i):
        self.excitatory_synapse(ebn_i)

    def delta_etrace(self, curr_value, h_ji):
        return (h_ji - curr_value) / (Constants.instance().learning_window * 3.0)
