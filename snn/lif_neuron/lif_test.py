from lif_neuron import LeakyIntegrateFireNeuron

input_val = 0.3
spike_count = 0
neuron = LeakyIntegrateFireNeuron()
iter_count = 1

for i in range(30 * iter_count):
    if neuron.process(input_val) == 25:
        spike_count += 1

print("Input - ", input_val, " - Spike count - ", spike_count / iter_count)