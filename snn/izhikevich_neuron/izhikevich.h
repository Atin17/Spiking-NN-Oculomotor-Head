#ifndef ROBOT_CONTROL_IZHIKEVICH_NEURON_H
#define ROBOT_CONTROL_IZHIKEVICH_NEURON_H

#include <vector>
#include <cmath>
#include <fstream>
#include <string>

#include "izhikevich_params.h"
#include "../constants.h"
#include "../learning/rules.h"

using namespace std;

class IzhikevichNeuron {
public:
	IzhikevichParams params;
	vector<double> uValues;
	double u, v;

	vector<IzhikevichNeuron*> inhibitory;
	vector<IzhikevichNeuron*> excitatory;

	vector<double> inhibitory_weights;
	vector<double> excitatory_weights;

	deque<double> post_v;
	vector<deque<double>> inhibitory_pre_v, excitatory_pre_v;
	vector<double> inhibitory_etrace, excitatory_etrace;

	const string folderName = Constants::instance()->outputDir;
	string out_filename;
	ofstream memb_out;

	bool learning = Constants::instance()->learning;
	int window_position = 0;

	double v_max = 25;

	double to_current(double membrane_potential) {
		return membrane_potential == 25; // Action potential
	}

	IzhikevichNeuron(string filename) : out_filename(filename) {
		voltages.reserve(1000);
		uValues.reserve(1000);

		if(!memb_out.is_open()) {
			memb_out.open((folderName + out_filename).c_str(), ios::out);
		}
	}

	virtual double delta_v(double input_current) {
		double I = alter_current(input_current);
		if(I < 0)
			I = 0;
		return params.tau * (0.04 * pow(v, 2) + 5 * v + 140 - u + I);
	}

	vector<double> voltages;

	IzhikevichNeuron(string filename, IzhikevichParams parameters) : out_filename(filename), params(parameters) {
		v = parameters.v_rest;
		u = parameters.b * v;
		voltages.reserve(1000);
		uValues.reserve(1000);

		if(!memb_out.is_open()) {
			memb_out.open((folderName + out_filename).c_str(), ios::out);
		}
	}

	virtual double process(double input_current, double reward_in = 0) {
		if(input_current < 0)
			input_current = 0;

		v += delta_v(input_current);
		u += params.tau * params.a * (params.b * v - u);

		if(voltages.size() == voltages.capacity() - 10)
			voltages.reserve(voltages.size() + 1000);

		if(uValues.size() == uValues.capacity() - 10)
			uValues.reserve(uValues.size() + 1000);

		if(v > v_max) {
			voltages.push_back(v_max);
			v = params.c;
			u += params.d;
		} else
			voltages.push_back(v);
		uValues.push_back(u);

		double v_out = voltages.back();

		if(learning) {
			post_v.push_back(v_out == 25);
			if(post_v.size() > Constants::instance()->learning_window)
				post_v.pop_front();
			window_position++;
			if(window_position % Constants::instance()->learning_window == 0) {
				window_position = 0;
				update_weights(reward_in);
			}
		}

		memb_out << v_out << endl;
		return v_out;
	}

	void reset() {
		v = params.v_rest;
		u = params.b * v;
	}

	void inhibitory_synapse(IzhikevichNeuron *nrn) {
		inhibitory.push_back(nrn);
		inhibitory_weights.push_back(100); //learning - initialize to random value?
		inhibitory_pre_v.push_back(deque<double>());
		inhibitory_etrace.push_back(0);
	}

	void excitatory_synapse(IzhikevichNeuron *nrn) {
		excitatory.push_back(nrn);
		excitatory_weights.push_back(100); //learning - initialize to random value?
		excitatory_pre_v.push_back(deque<double>());
		excitatory_etrace.push_back(0);
	}

	virtual double alter_current(double input_current) {
		return input_current;
	}

	double delta_etrace(double curr_value, double h_ji) {
		return (h_ji - curr_value) / (Constants::instance()->learning_window * 3.0);
	}

	virtual void update_weights(double reward_in) {}
};

class ExcitableIzhikevichNeuron : public IzhikevichNeuron {
protected:
	double delta_v(double input_current) override {
		double I = alter_current(input_current);
		if(I < 0)
			I = 0;
		return params.tau * (0.04 * pow(v, 2) + 4.1 * v + 108 - u + I);
	}
public:
	ExcitableIzhikevichNeuron(string filename) : IzhikevichNeuron(filename) {
		// Initialize parameters here
		params.a = 0.1;
		params.b = -0.1;
		params.c = -55;
		params.d = 6.0;
		params.v_rest = -60;
		params.tau = 0.5;
		v = params.v_rest;
		u = params.b*v;
	}
};

#endif //ROBOT_CONTROL_IZHIKEVICH_NEURON_H
