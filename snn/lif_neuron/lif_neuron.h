#ifndef ROBOT_CONTROL_LIF_NEURON_H_H
#define ROBOT_CONTROL_LIF_NEURON_H_H

#include <vector>
#include <string>
#include <fstream>

#include "../constants.h"

using namespace std;

class LeakyIntegrateFireNeuron {
protected:
    //Neuron parameters
    double Rm = 100;                 // Membrane resistance (kOhm)
    double Cm = 10;                  // Membrane capacitance (uF)
    double tau_m = Rm * Cm;          // Time constant (ms)
    double spike_voltage = 15.0;     // Spike potential (mV)
    double resting_potential;        // Resting membrane potential (mV)
    int refractory_period = 0;       // Neuron refractory period (ms)
    int resting_time = 0;            // Neuron rest period after spike (ms)

    double v_th = 10;                 // Threshold membrane potential for spike (mV)
    double v_max = 25;                // Max membrane potential (mV)

    const string folderName = Constants::instance()->outputDir;
    string out_filename;
    ofstream memb_out;
public:
    double dt = 60.0;                // Time difference - with 30 fps
    vector<double> voltages;

    LeakyIntegrateFireNeuron(string filename, double rest_potential = -70.0) : out_filename(filename), resting_potential(rest_potential) {
        voltages.reserve(1000);
        voltages.push_back(rest_potential);

        if(!memb_out.is_open()) {
            memb_out.open((folderName + out_filename).c_str(), ios::out);
        }
    }

    virtual double alter_current(double input_current) {
        return input_current;
    }

    double process(double input_current) {
        if(voltages.size() == voltages.capacity() - 10) {
            voltages.reserve(voltages.size() + 1000);
        }

        double new_membrane_potential = resting_potential;

        if(resting_time > 0) {
            resting_time -= 1;
            new_membrane_potential = resting_potential;
            voltages.push_back(new_membrane_potential);
            return new_membrane_potential;
        }

        input_current = alter_current(input_current);

        if(input_current < 0)
            input_current = 0;

        double membrane_potential = voltages.back();
        double voltage_delta = ((input_current * Rm) - membrane_potential) * (dt/tau_m);

        new_membrane_potential = membrane_potential + voltage_delta;

        if(new_membrane_potential > v_th) {
            new_membrane_potential += spike_voltage;
            resting_time = refractory_period;
        }

        if(new_membrane_potential > v_max)
            new_membrane_potential = v_max;

        if(new_membrane_potential < resting_potential)
            new_membrane_potential = resting_potential;

        voltages.push_back(new_membrane_potential);
        return new_membrane_potential;
    }

    int getSize() {
	    cout << voltages.size() << ":" << voltages.capacity() << endl;
	    return voltages.size();
    }

    void reset() {
        voltages.push_back(resting_potential);
    }

    double to_current(double voltage) {
        return voltage == 25;
    }
};

#endif //ROBOT_CONTROL_LIF_NEURON_H_H
