#include <iostream>
#include "lif_neuron.h"

using namespace std;

int main() {
	double input = 0.3;
	int spike_count = 0;
	LeakyIntegrateFireNeuron neuron;
	int iter = 1;
	for(int i = 0; i < 30 * iter; i++) {
		if(neuron.process(input) == 25) {
			spike_count++;
		}
	}
	cout << "Input - " << input << " - Spike count - " << double(spike_count / iter) << endl;
	return 0;
}