#ifndef ROBOT_CONTROL_OPN_NEURON_H
#define ROBOT_CONTROL_OPN_NEURON_H

#include "../izhikevich_neuron/izhikevich.h"

using namespace std;

class OPN : public IzhikevichNeuron {
private:
	double bias_current = 40;
	ofstream ibn_i_weights, ibn_c_weights;
public:
	OPN(string filename, IzhikevichNeuron *ibn_i, IzhikevichNeuron *ibn_c) : IzhikevichNeuron(filename) {
		// Initialize parameters here
		params.a = 0.02;
		params.b = 0.2;
		params.c = -65;
		params.d = 2;
		params.v_rest = -70;
		params.tau = 0.25;
		v = params.v_rest;
		u = params.b * v;

		add_ibn_link(ibn_i);
		add_ibn_link(ibn_c);
		if(learning) {
			ibn_i_weights.open(Constants::instance()->outputDir + filename + "_ibn_i", ios::out);
			ibn_c_weights.open(Constants::instance()->outputDir + filename + "_ibn_c", ios::out);
		}
	}

	//ORDER
	// Inhibitory: IBN_L - IBN_R
	// input_current = weak input from sc
	double alter_current(double input_current) override {
		//IBN_L
		IzhikevichNeuron *ibn_l = inhibitory[0];
		int size = ibn_l->voltages.size();
		double ibn_l_v = 0;
		if(size > 1) {
			ibn_l_v = ibn_l->voltages[size - 2];
		}
		//IBN_R
		IzhikevichNeuron *ibn_r = inhibitory[1];
		size = ibn_r->voltages.size();
		double ibn_r_v = 0;
		if(size > 1) {
			ibn_r_v = ibn_r->voltages[size - 2];
		}

		if(learning) {
			inhibitory_pre_v[0].push_back(ibn_l_v == 25);
			if(inhibitory_pre_v[0].size() > Constants::instance()->learning_window)
				inhibitory_pre_v[0].pop_front();
			inhibitory_pre_v[1].push_back(ibn_r_v == 25);
			if(inhibitory_pre_v[1].size() > Constants::instance()->learning_window)
				inhibitory_pre_v[1].pop_front();
		} else {
			inhibitory_weights[0] = 0.18 * 100;
			inhibitory_weights[1] = 0.18 * 100;
		}

		return bias_current
			- input_current * 250 * 0.075// * 0.075 * 250
			- to_current(ibn_l_v) * inhibitory_weights[0] // * 0.18 * 100
			- to_current(ibn_r_v) * inhibitory_weights[1]; //* 0.18 * 100;
		// input = sc_l + sc_r + ibn_l + ibn_r
	}

	void update_weights(double reward_in) override {
		double h_ji = hebbian(inhibitory_pre_v[0], post_v, 10.0, inhibitory_weights[0]);
		// update etrace
		inhibitory_etrace[0] += delta_etrace(inhibitory_etrace[0], h_ji);
		inhibitory_weights[0] += h_ji * inhibitory_etrace[0] * (1 - reward_in) * Constants::instance()->learning_rate;

		h_ji = hebbian(inhibitory_pre_v[1], post_v, 10.0, inhibitory_weights[1]);
		// update etrace
		inhibitory_etrace[1] += delta_etrace(inhibitory_etrace[1], h_ji);
		inhibitory_weights[1] += h_ji * inhibitory_etrace[1] * (1 - reward_in) * Constants::instance()->learning_rate;

		// save weights to file
		ibn_i_weights << inhibitory_weights[0] << endl;
		ibn_c_weights << inhibitory_weights[1] << endl;
	}

	void add_ibn_link(IzhikevichNeuron *ibn) {
		this->inhibitory_synapse(ibn);
	}
};

#endif //ROBOT_CONTROL_OPN_NEURON_H