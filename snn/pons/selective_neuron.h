#ifndef ROBOT_CONTROL_SELECTIVE_NEURON_H_
#define ROBOT_CONTROL_SELECTIVE_NEURON_H_

#include "../pons/motor_neuron.h"
#include "../pons/tonic_neuron.h"
#include "../izhikevich_neuron/izhikevich.h"
#include <string>

using namespace std;

class SelectiveNeuron : public MotorNeuron {
public:
	SelectiveNeuron(string filename, IzhikevichNeuron *ibn, TonicNeuron *tn_i, double w_i, TonicNeuron *tn_c, double w_c, TonicNeuron *tn_cc = NULL, double w_cc = 0) : MotorNeuron(filename) {
		add_ibn_link(ibn);
		add_tn_link(tn_i);
		w_tn_v = w_i;
		w_tn_vv = w_c;
		w_tn_cv = w_cc;
		add_tn_link(tn_c);
		if(tn_cc != NULL)
			add_tn_link(tn_cc);
	}
};


#endif //ROBOT_CONTROL_SELECTIVE_NEURON_H_