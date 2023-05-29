#ifndef ROBOT_CONTROL_REWARD_NEURON_H_
#define ROBOT_CONTROL_REWARD_NEURON_H_

#include "../izhikevich_neuron/izhikevich.h"
#include "../constants.h"
#include <deque>
#include <algorithm>

using namespace std;

class RewardNeuron : public IzhikevichNeuron {
private:
	// learning related
	bool learning = false;
	deque<double> v_pre, v_post;
	int window_size, window_position, window_count;
	double prev_input;
public:
	RewardNeuron(string filename, IzhikevichNeuron *llbn, IzhikevichNeuron *ebn) : IzhikevichNeuron(filename) {
		// Initialize parameters here
		params.a=0.1;
		params.b=-0.075;
		params.c=-55;
		params.d= 6; //6
		params.v_rest=-60;
		params.tau = 1.0;
		v = params.v_rest;
		u = params.b*v;

		add_llbn_link(llbn);
		add_ebn_link(ebn);

		// learning related
		learning = Constants::instance()->learning;
		window_size = 1000 / 45;
		window_position = 0;
		window_count = 0;
		prev_input = -1;
	}

	double delta_v(double input_current) override {
		double I = alter_current(input_current);
		if(I < 0)
			I = 0;
		return params.tau * (0.04 * pow(v, 2) + 4.1 * v + 108 - u + I);
	}

	// input_current = sc_input (same input that is given to LLBN)
	// Excitatory: EBN, LLBN
	double alter_current(double input_current) override {
		double curr = 0;
		// Learning
		if(learning) {
			int size;
			//LLBN
			double llbn_v = excitatory[0]->voltages.back();
			//EBN
			double ebn_v = excitatory[1]->voltages.back();

			// start with low value of llbn_weight
			// 1. store v_pre and v_post for some duration of time, and the input_current during that time
			// 2. use input_current = sc_input as the error signal
			// 3. compute reward from the error signal
			// 4. use reward to determine change in the weight

			//step 1 - store v_pre and v_post, input_current
			if(prev_input == -1)
				prev_input = input_current;
			v_pre.push_back(llbn_v == 25);
			v_post.push_back(ebn_v == 25);

			if(v_pre.size() > window_size)
				v_pre.pop_front();

			if(v_post.size() > window_size)
				v_post.pop_front();

			window_position++;
			if(window_position % window_size == 0) {
				// step 2 - compute error
				double err = input_current + (prev_input - input_current) / 2.0;
				curr = err * 10.0 + (accumulate(v_pre.begin(), v_pre.end(), 0) - accumulate(v_post.begin(), v_post.end(), 0));
				// update input
				prev_input = input_current;
				window_position = 0;
				window_count++;
			}
		}
		return curr;
	}

	void add_ebn_link(IzhikevichNeuron *ebn) {
		this->excitatory_synapse(ebn);
	}

	void add_llbn_link(IzhikevichNeuron *llbn) {
		this->excitatory_synapse(llbn);
	}
};

#endif //ROBOT_CONTROL_REWARD_NEURON_H_