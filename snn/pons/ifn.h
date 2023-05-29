#ifndef ROBOT_CONTROL_IFN_NEURON_H
#define ROBOT_CONTROL_IFN_NEURON_H

#include "../izhikevich_neuron/izhikevich.h"

using namespace std;

class IFN : public IzhikevichNeuron {
private:
	ofstream ebn_weights, ibn_weights;
public:
	IFN(string filename, IzhikevichNeuron *ebn, IzhikevichNeuron *ibn_c = NULL) : IzhikevichNeuron(filename) {
		// Initialize parameters here
		params.a = 0.02;
		params.b = 0.2;
		params.c = -65;
		params.d = 2;
		params.v_rest = -70;
		params.tau = 0.25;
		v = params.v_rest;
		u = params.b * v;

		add_ebn_link(ebn);
		ebn_weights.open(Constants::instance()->outputDir + filename + "_ebn", ios::out);
		if(ibn_c != NULL) {
			add_ibn_link(ibn_c);
			ibn_weights.open(Constants::instance()->outputDir + filename + "_ibn", ios::out);
		}
	}

	// input_current = 0
	// Excitatory: EBN
	// Inhibitory: IBN_c
	double alter_current(double input_current) override {
		//EBN
		double ebn_v = excitatory[0]->voltages.back();
		//IBN_c
		double ibn_c_v = 0;
		if(inhibitory.size() > 0) {
			//IBN_c - only for LL and RR, not for LR / RL
			IzhikevichNeuron *ibn_c = inhibitory[0];
			int size = ibn_c->voltages.size();
			if(size > 1) {
				ibn_c_v = ibn_c->voltages[size - 2];
			}
		} else
			inhibitory_weights.push_back(0);

		if(learning) {
			if(inhibitory.size() > 0) {
				inhibitory_pre_v[0].push_back(ibn_c_v == 25);
				if(inhibitory_pre_v[0].size() > Constants::instance()->learning_window)
					inhibitory_pre_v[0].pop_front();
			}
			excitatory_pre_v[0].push_back(ebn_v == 25);
			if(excitatory_pre_v[0].size() > Constants::instance()->learning_window)
				excitatory_pre_v[0].pop_front();
		} else {
			excitatory_weights[0] = 125;
			inhibitory_weights[0] = 125;
		}

		return input_current
			+ to_current(ebn_v) * excitatory_weights[0]// * 1.0 * 125
			- to_current(ibn_c_v) * inhibitory_weights[0];// * 1.0 * 125;
	}

	void update_weights(double reward_in) override {
		double h_ji;
		if(inhibitory.size() > 0) {
			h_ji = hebbian(inhibitory_pre_v[0], post_v, 10.0, inhibitory_weights[0]);
			// update etrace
			inhibitory_etrace[0] += delta_etrace(inhibitory_etrace[0], h_ji);
			inhibitory_weights[0] += h_ji * inhibitory_etrace[0] * (1 - reward_in) * Constants::instance()->learning_rate;

			// save weights to file
			ibn_weights << inhibitory_weights[0] << endl;
		}
		h_ji = hebbian(excitatory_pre_v[0], post_v, 10.0, excitatory_weights[0]);
		// update etrace
		excitatory_etrace[0] += delta_etrace(excitatory_etrace[0], h_ji);
		excitatory_weights[0] += h_ji * excitatory_etrace[0] * (1 - reward_in) * Constants::instance()->learning_rate;
		// save weights to file
		ebn_weights << excitatory_weights[0] << endl;
	}

	void add_ebn_link(IzhikevichNeuron *ebn) {
		this->excitatory_synapse(ebn);
	}

	void add_ibn_link(IzhikevichNeuron *ibn_c) {
		this->inhibitory_synapse(ibn_c);
	}
};

#endif //ROBOT_CONTROL_IFN_NEURON_H