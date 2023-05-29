// Izhikevich Neuron Parameters to create different types of neuron firing patterns

#ifndef ROBOT_CONTROL_IZHIKEVICH_PARAMS_H
#define ROBOT_CONTROL_IZHIKEVICH_PARAMS_H

class IzhikevichParams {
public:
	double a;
	double b;
	double c;
	double d;
	double v_rest;
	double tau;

	IzhikevichParams(double a, double b, double c, double d, double v_rest, double tau) :
		a(a), b(b), c(c), d(d), v_rest(v_rest), tau(tau) {
	}

	IzhikevichParams() : a(0.02), b(0.2), c(-65), d(6), v_rest(-70), tau(0.25) {}
};

#endif //ROBOT_CONTROL_IZHIKEVICH_PARAMS_H
