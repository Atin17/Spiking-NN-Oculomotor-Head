#ifndef ROBOT_CONTROL_C_LOG_NEURON_1_H_
#define ROBOT_CONTROL_C_LOG_NEURON_1_H_

#include <string>

#include "../lif_neuron/lif_neuron.h"
#include "../constants.h"

class LogNeuron1 : public LeakyIntegrateFireNeuron {
public:
	LogNeuron1(string filename) : LeakyIntegrateFireNeuron(filename, -60.0) {
		refractory_period = 1;
	}

	double alter_current(double input_current) override {
		return input_current * 5.0;
	}
};

class LogNeuron2 : public LeakyIntegrateFireNeuron {
private:
	LogNeuron1 *nrn1;
public:
	LogNeuron2(string filename, LogNeuron1 *nrn) : LeakyIntegrateFireNeuron(filename, -60.0) {
		nrn1 = nrn;
		refractory_period = 1;
	}

	double alter_current(double input_current) override {
		int size = nrn1->voltages.size();
		double out1 = 0;
		if(size > 0) {
			out1 = nrn1->voltages.back();
		}

		size = voltages.size();
		double out = 0;
		if(size > 0) {
			out = voltages.back();
		}

		return input_current * 10.0 * (-0.5) + to_current(out1) * 2.0 + to_current(out);
	}
};

class LogNeuron3 : public LeakyIntegrateFireNeuron {
private:
	LogNeuron1 *nrn1;
	LogNeuron2 *nrn2;
public:
	LogNeuron3(string filename, LogNeuron1 *nrn_1, LogNeuron2 *nrn_2) : LeakyIntegrateFireNeuron(filename, -60.0) {
		nrn1 = nrn_1;
		nrn2 = nrn_2;
		refractory_period = 1;
	}

	double alter_current(double input_current) override {
		int size = nrn1->voltages.size();
		double out1 = 0;
		if(size > 0) {
			out1 = nrn1->voltages.back();
		}

		size = nrn2->voltages.size();
		double out2 = 0;
		if(size > 0) {
			out2 = nrn2->voltages.back();
		}

		size = voltages.size();
		double out = 0;
		if(size > 0) {
			out = voltages.back();
		}

		return input_current * 15.0 * (1.0/3.0) + to_current(out1) * 3.0 + to_current(out2) * 2.0 + to_current(out);
	}
};

class LogNeuron4 : public LeakyIntegrateFireNeuron {
private:
	LogNeuron1 *nrn1;
	LogNeuron2 *nrn2;
	LogNeuron3 *nrn3;
public:
	LogNeuron4(string filename, LogNeuron1 *nrn_1, LogNeuron2 *nrn_2, LogNeuron3 *nrn_3) : LeakyIntegrateFireNeuron(filename, -60.0) {
		nrn1 = nrn_1;
		nrn2 = nrn_2;
		nrn3 = nrn_3;
		refractory_period = 1;
	}

	double alter_current(double input_current) override {
		int size = nrn1->voltages.size();
		double out1 = 0;
		if(size > 0) {
			out1 = nrn1->voltages.back();
		}

		size = nrn2->voltages.size();
		double out2 = 0;
		if(size > 0) {
			out2 = nrn2->voltages.back();
		}

		size = nrn3->voltages.size();
		double out3 = 0;
		if(size > 0) {
			out3 = nrn3->voltages.back();
		}

		size = voltages.size();
		double out = 0;
		if(size > 0) {
			out = voltages.back();
		}

		return input_current * 20.0 * (-1.0/4.0) + to_current(out1) * 4.0 + to_current(out2) * 3.0 + to_current(out3) * 2.0 + to_current(out);
	}
};

class LogNeuron5 : public LeakyIntegrateFireNeuron {
private:
	LogNeuron1 *nrn1;
	LogNeuron2 *nrn2;
	LogNeuron3 *nrn3;
	LogNeuron4 *nrn4;
public:
	LogNeuron5(string filename, LogNeuron1 *nrn_1, LogNeuron2 *nrn_2, LogNeuron3 *nrn_3, LogNeuron4 *nrn_4) : LeakyIntegrateFireNeuron(filename, -60.0) {
		nrn1 = nrn_1;
		nrn2 = nrn_2;
		nrn3 = nrn_3;
		nrn4 = nrn_4;
		refractory_period = 1;
	}

	double alter_current(double input_current) override {
		int size = nrn1->voltages.size();
		double out1 = 0;
		if(size > 0) {
			out1 = nrn1->voltages.back();
		}

		size = nrn2->voltages.size();
		double out2 = 0;
		if(size > 0) {
			out2 = nrn2->voltages.back();
		}

		size = nrn3->voltages.size();
		double out3 = 0;
		if(size > 0) {
			out3 = nrn3->voltages.back();
		}

		size = nrn4->voltages.size();
		double out4 = 0;
		if(size > 0) {
			out4 = nrn4->voltages.back();
		}

		size = voltages.size();
		double out = 0;
		if(size > 0) {
			out = voltages.back();
		}

		return input_current * 25.0 * (1.0/5.0) +
			to_current(out1) * 5.0 + to_current(out2) * 4.0 +
			to_current(out3) * 3.0 + to_current(out4) * 2.0 + to_current(out);
	}
};

#endif //ROBOT_CONTROL_C_LOG_NEURON_1_H_