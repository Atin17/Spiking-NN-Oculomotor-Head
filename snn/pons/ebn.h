#ifndef ROBOT_CONTROL_EBN_NEURON_H
#define ROBOT_CONTROL_EBN_NEURON_H

#include "../izhikevich_neuron/izhikevich.h"
#include "../constants.h"

using namespace std;

class EBN : public IzhikevichNeuron {
private:
	double bias_current = 10;
	ofstream llbn_weights, opn_weights, ibn_weights;
public:
	EBN(string filename, IzhikevichNeuron *llbn, IzhikevichNeuron *opn = NULL, IzhikevichNeuron *ibn = NULL) : IzhikevichNeuron(filename) {
		// Initialize parameters here
		params.a = 0.02;
		params.b = 0.2;
		params.c = -65;
		params.d = 2;
		params.v_rest = -70;
		params.tau = 0.25;
		v = params.v_rest;
		u = params.b * v;

		add_llbn_link(llbn);
		llbn_weights.open(Constants::instance()->outputDir + filename + "_llbn", ios::out);
		if(opn != NULL) {
			add_opn_link(opn);
			opn_weights.open(Constants::instance()->outputDir + filename + "_opn", ios::out);
		}
		if(ibn != NULL) {
			add_ibn_link(ibn);
			ibn_weights.open(Constants::instance()->outputDir + filename + "_ibn", ios::out);
		}
	}

	// input_current = sc_input (same input that is given to LLBN)
	// Excitatory: LLBN
	// Inhibitory: OPN - IBN_c
	double alter_current(double input_current) override {
		int size;
		//LLBN
		double llbn_v = excitatory[0]->voltages.back();
		double opn_v = 0, ibn_c_v = 0;
		//OPN - IBN_c - only for LL / RR , not LR/RL
		if(inhibitory.size() > 0) {
			//OPN
			IzhikevichNeuron *opn = inhibitory[0];
			size = opn->voltages.size();
			if(size > 1) {
				opn_v = opn->voltages[size - 2];
			}
			//IBN_c
			IzhikevichNeuron *ibn_c = inhibitory[1];
			size = ibn_c->voltages.size();
			if(size > 1) {
				ibn_c_v = ibn_c->voltages[size - 2];
			}
		} else {
			inhibitory_weights.push_back(10.4 * 130);
			inhibitory_weights.push_back(0.5 * 130);
		}

		// Learning
		if(learning) {
			if(inhibitory.size() > 0) {
				inhibitory_pre_v[0].push_back(opn_v == 25);
				if(inhibitory_pre_v[0].size() > Constants::instance()->learning_window)
					inhibitory_pre_v[0].pop_front();
				inhibitory_pre_v[1].push_back(ibn_c_v == 25);
				if(inhibitory_pre_v[1].size() > Constants::instance()->learning_window)
					inhibitory_pre_v[1].pop_front();
			}
			excitatory_pre_v[0].push_back(llbn_v == 25);
			if(excitatory_pre_v[0].size() > Constants::instance()->learning_window)
				excitatory_pre_v[0].pop_front();
		} else {
			// original llbn_weight = 1.2 * 140
			excitatory_weights[0] = 1.2 * 140;
			inhibitory_weights.push_back(10.4 * 130);
			inhibitory_weights.push_back(0.5 * 130);
		}

		return input_current
			+ bias_current
			+ to_current(llbn_v) * excitatory_weights[0]
			- to_current(ibn_c_v) * inhibitory_weights[1] //* 0.5 * 130
			- to_current(opn_v) * inhibitory_weights[0]; //* 10.4 * 130;
	}

	void update_weights(double reward_in) override {
		double h_ji;
		if(inhibitory.size() > 0) {
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
		}
		h_ji = hebbian(excitatory_pre_v[0], post_v, 10.0, excitatory_weights[0]);
		// update etrace
		excitatory_etrace[0] += delta_etrace(excitatory_etrace[0], h_ji);
		excitatory_weights[0] += h_ji * excitatory_etrace[0] * (1 - reward_in) * Constants::instance()->learning_rate;
		// save weights to file
		llbn_weights << excitatory_weights[0] << endl;
	}

	void add_opn_link(IzhikevichNeuron *opn) {
		this->inhibitory_synapse(opn);
	}

	void add_ibn_link(IzhikevichNeuron *ibn) {
		this->inhibitory_synapse(ibn);
	}

	void add_llbn_link(IzhikevichNeuron *llbn) {
		this->excitatory_synapse(llbn);
	}
};

#endif //ROBOT_CONTROL_EBN_NEURON_H