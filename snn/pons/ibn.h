#ifndef ROBOT_CONTROL_IBN_NEURON_H
#define ROBOT_CONTROL_IBN_NEURON_H

#include "../izhikevich_neuron/izhikevich.h"

using namespace std;

class IBN : public IzhikevichNeuron {
private:
	double bias_current = 10;
	ofstream ebn_weights, opn_weights, ibn_weights;
public:
	IBN(string filename, IzhikevichNeuron *ebn, IzhikevichNeuron *opn, IzhikevichNeuron *ibn_c) : IzhikevichNeuron(filename) {
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
		add_opn_link(opn);
		opn_weights.open(Constants::instance()->outputDir + filename + "_opn", ios::out);
		add_ibn_link(ibn_c);
		ibn_weights.open(Constants::instance()->outputDir + filename + "_ibn", ios::out);
	}

	// ORDER - Excitatory: EBN
	// Inhibitory: OPN - IBNc
	// input_current = sc input (same as LLBN and IBN)
	double alter_current(double input_current) override {
		int size;
		//EBN
		double ebn_v = excitatory[0]->voltages.back();
		//OPN
		IzhikevichNeuron *opn = inhibitory[0];
		size = opn->voltages.size();
		double opn_v = 0;
		if(size > 1) {
			opn_v = opn->voltages[size - 2];
		}
		//IBN_c
		double ibn_c_v = 0;
		IzhikevichNeuron *ibn_c = inhibitory[1];
		size = ibn_c->voltages.size();
		if(size > 1) {
			ibn_c_v = ibn_c->voltages[size - 2];
		}

		if(learning) {
			inhibitory_pre_v[0].push_back(opn_v == 25);
			if(inhibitory_pre_v[0].size() > Constants::instance()->learning_window)
				inhibitory_pre_v[0].pop_front();
			inhibitory_pre_v[1].push_back(ibn_c_v == 25);
			if(inhibitory_pre_v[1].size() > Constants::instance()->learning_window)
				inhibitory_pre_v[1].pop_front();
			excitatory_pre_v[0].push_back(ebn_v == 25);
			if(excitatory_pre_v[0].size() > Constants::instance()->learning_window)
				excitatory_pre_v[0].pop_front();
		} else {
			excitatory_weights[0] = 0.10 * 125;
			inhibitory_weights[0] = 6.4 * 125;
			inhibitory_weights[1] = 0.15 * 125;
		}

		return input_current
			+ bias_current
			+ to_current(ebn_v) * excitatory_weights[0]// * 0.10 * 125
			- to_current(ibn_c_v) * inhibitory_weights[1]// * 0.15 * 125
			- to_current(opn_v) * inhibitory_weights[0];// * 6.4 * 125;
	}

	void update_weights(double reward_in) override {
		double h_ji;

		h_ji = hebbian(inhibitory_pre_v[0], post_v, 10.0, inhibitory_weights[0]);
		// update etrace
		inhibitory_etrace[0] += delta_etrace(inhibitory_etrace[0], h_ji);
		inhibitory_weights[0] += h_ji * inhibitory_etrace[0] * (1 - reward_in) * Constants::instance()->learning_rate;

		h_ji = hebbian(inhibitory_pre_v[1], post_v, 10.0, inhibitory_weights[1]);
		// update etrace
		inhibitory_etrace[1] += delta_etrace(inhibitory_etrace[1], h_ji);
		inhibitory_weights[1] += h_ji * inhibitory_etrace[1] * (1 - reward_in) * Constants::instance()->learning_rate;
		// save weights to file
		opn_weights << inhibitory_weights[0] << endl;
		ibn_weights << inhibitory_weights[1] << endl;

		h_ji = hebbian(excitatory_pre_v[0], post_v, 10.0, excitatory_weights[0]);
		// update etrace
		excitatory_etrace[0] += delta_etrace(excitatory_etrace[0], h_ji);
		excitatory_weights[0] += h_ji * excitatory_etrace[0] * (1 - reward_in) * Constants::instance()->learning_rate;
		// save weights to file
		ebn_weights << excitatory_weights[0] << endl;
	}

	void add_ibn_link(IzhikevichNeuron *ibn_c) {
		this->inhibitory_synapse(ibn_c);
	}

	void add_opn_link(IzhikevichNeuron *opn) {
		this->inhibitory_synapse(opn);
	}

	void add_ebn_link(IzhikevichNeuron *ebn) {
		this->excitatory_synapse(ebn);
	}
};

#endif //ROBOT_CONTROL_IBN_NEURON_H