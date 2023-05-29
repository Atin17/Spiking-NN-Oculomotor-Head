#ifndef ROBOT_CONTROL_LLBN_NEURON_H
#define ROBOT_CONTROL_LLBN_NEURON_H

#include "../izhikevich_neuron/izhikevich.h"

using namespace std;

class LLBN : public IzhikevichNeuron {
protected:
	double delta_v(double input_current) override {
		double I = alter_current(input_current);
		if(I < 0)
			I = 0;
		return params.tau * (0.04 * pow(v, 2) + 4.1 * v + 108 - u + I);
	}

	ofstream ifn_weights;
public:
	LLBN(string filename, IzhikevichNeuron *ifn_i) : IzhikevichNeuron(filename) {
		// Initialize parameters here
		/*
		params.a = 0.1;
		params.b = 0.5;
		params.c = -60;
		params.d = 0.05;
		params.v_rest = -60;
		params.tau = 0.5;
		v = params.v_rest;
		u = params.b * v;
		*/

		// Integrator params
		params.a=0.1;
		params.b=-0.075;
		params.c=-55;
		params.d= 6; //6
		params.v_rest=-60;
		params.tau = 1.0;
		v = params.v_rest;
		u = params.b*v;

		add_ifn_link(ifn_i);

		ifn_weights.open(Constants::instance()->outputDir + filename + "_ifn", ios::out);
	}

	// input_current = from sc (weighted)
	double alter_current(double input_current) override {
		double feedback_current = to_current(v);
		//IFN
		IzhikevichNeuron *ifn_i = inhibitory[0];
		int size = ifn_i->voltages.size();
		double ifn_i_v = 0;
		if(size > 1) {
			ifn_i_v = ifn_i->voltages[size - 2];
			if(learning) {
				inhibitory_pre_v[0].push_back(ifn_i_v == 25);
				if(inhibitory_pre_v[0].size() > Constants::instance()->learning_window)
					inhibitory_pre_v[0].pop_front();
			}
		}

		if(!learning)
			inhibitory_weights[0] = 100.0 * params.tau / 8;

		// ifn_i_w = 100.0 * params.tau / 8
		return input_current * 125.0 / 8// * 125.0 * params.tau / 8
			- to_current(ifn_i_v) * inhibitory_weights[0];
	}

	void add_ifn_link(IzhikevichNeuron *ifn_i) {
		this->inhibitory_synapse(ifn_i);
	}

	void update_weights(double reward_in) override {
		double h_ji = hebbian(inhibitory_pre_v[0], post_v, 10.0, inhibitory_weights[0]);
		// update etrace
		inhibitory_etrace[0] += delta_etrace(inhibitory_etrace[0], h_ji);
		inhibitory_weights[0] += h_ji * inhibitory_etrace[0] * (1 - reward_in) * Constants::instance()->learning_rate;
		// save weights to file
		ifn_weights << inhibitory_weights[0] << endl;
	}
};

#endif //ROBOT_CONTROL_LLBN_NEURON_H