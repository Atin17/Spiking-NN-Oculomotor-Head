#ifndef ROBOT_CONTROL_TONIC_NEURON_H
#define ROBOT_CONTROL_TONIC_NEURON_H

#include <vector>
#include <string>
#include <fstream>
#include <deque>

#include "../constants.h"
#include "../izhikevich_neuron/izhikevich.h"

using namespace std;

class TonicNeuron {
protected:
    //Neuron parameters
    double Rm = 100;                 // Membrane resistance (kOhm)
    double Cm = 10;                  // Membrane capacitance (uF)
    double tau_m = Rm * Cm;          // Time constant (ms)
    double dt = 1;                   // Time difference - with 30 fps
    double spike_voltage = 15.0;     // Spike potential (mV)
    double resting_potential;        // Resting membrane potential (mV)
    int refractory_period = 1;       // Neuron refractory period (ms)
    int resting_time = 0;            // Neuron rest period after spike (ms)

    double v_th = 10;                 // Threshold membrane potential for spike (mV)
    double v_max = 25;                // Max membrane potential (mV)

    const string folderName = Constants::instance()->outputDir;
    string out_filename;
    ofstream memb_out;

    vector<IzhikevichNeuron*> inhibitory;
    vector<IzhikevichNeuron*> excitatory;

    vector<double> inhibitory_weights, excitatory_weights;

    deque<double> post_v;
    vector<deque<double>> inhibitory_pre_v, excitatory_pre_v;
    vector<double> inhibitory_etrace, excitatory_etrace;

    double to_current(double membrane_potential) {
        if(membrane_potential == 25) { // Action potential
            return 1;
        }
        return 0;
    }

    ofstream ebn_weights, ibn_weights;
    bool learning = false;
    int window_position = 0;
public:
    vector<double> voltages;

    TonicNeuron(string filename, IzhikevichNeuron *ebn, IzhikevichNeuron *ibn = NULL) : out_filename(filename) {
        voltages.reserve(1000);
        voltages.push_back(-60);
        resting_potential = -60;
        learning = Constants::instance()->learning;

        if(!memb_out.is_open()) {
            memb_out.open((folderName + out_filename).c_str(), ios::out);
        }

        add_ebn_link(ebn);
        if(ibn != NULL)
            add_ibn_link(ibn);

        if(learning) {
            ebn_weights.open(folderName + filename + "_ebn", ios::out);
            if(ibn != NULL)
                ibn_weights.open(folderName + filename + "_ibn", ios::out);
        }
    }

    double process(double input_current, double reward_in = 0) {
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

        double membrane_potential = voltages.back();
        double I = alter_current(input_current);
        if(I < 0)
            I = 0;
        double voltage_delta = ((I * Rm) - membrane_potential) * (dt/tau_m);

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

        if(learning) {
            post_v.push_back(new_membrane_potential == 25);
            if(post_v.size() > Constants::instance()->learning_window)
                post_v.pop_front();
            window_position++;
            if(window_position % Constants::instance()->learning_window == 0) {
                window_position = 0;
                update_weights(reward_in);
            }
        }

        memb_out << new_membrane_potential << endl;
        return new_membrane_potential;
    }

    void update_weights(double reward_in) {
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

    // input_current = 0 (always)
    virtual double alter_current(double input_current) {
        double feedback_current = to_current(voltages.back());
        double ibn_c_v = 0;
        int size;
        //IBN_c - only LL/RR not LR/RL
        if(inhibitory.size() > 0) {
            //IBN
            IzhikevichNeuron *ibn_c = inhibitory[0];
            size = ibn_c->voltages.size();
            if(size > 1) {
                ibn_c_v = ibn_c->voltages[size - 2];
            }
        } else {
            inhibitory_weights.push_back(3.8 * tau_m * 40);
        }
        //EBN
        IzhikevichNeuron *ebn_i = excitatory[0];
        size = ebn_i->voltages.size();
        double ebn_i_v = 0;
        if(size > 1) {
            ebn_i_v = ebn_i->voltages[size - 2];
        }

        if(learning) {
            if(inhibitory.size() > 0) {
                inhibitory_pre_v[0].push_back(ibn_c_v == 25);
                if(inhibitory_pre_v[0].size() > Constants::instance()->learning_window)
                    inhibitory_pre_v[0].pop_front();
            }
            excitatory_pre_v[0].push_back(ebn_i_v == 25);
            if(excitatory_pre_v[0].size() > Constants::instance()->learning_window)
                excitatory_pre_v[0].pop_front();
        } else {
            excitatory_weights[0] = 3.8 * tau_m * 30;
            inhibitory_weights[0] = 3.8 * tau_m * 40;
        }

        return feedback_current +
            to_current(ebn_i_v) * excitatory_weights[0] // * 3.8 * tau_m * 30
            - to_current(ibn_c_v) * inhibitory_weights[0]; // * 3.8 * tau_m * 40;
    }

    void reset() {
        voltages.push_back(resting_potential);
    }

    void inhibitory_synapse(IzhikevichNeuron *nrn) {
        inhibitory.push_back(nrn);
        inhibitory_weights.push_back(100);
        inhibitory_pre_v.push_back(deque<double>());
        inhibitory_etrace.push_back(0);
    }

    void excitatory_synapse(IzhikevichNeuron *nrn) {
        excitatory.push_back(nrn);
        excitatory_weights.push_back(100);
        excitatory_pre_v.push_back(deque<double>());
        excitatory_etrace.push_back(0);
    }

    void add_ibn_link(IzhikevichNeuron *ibn_c) {
        this->inhibitory_synapse(ibn_c);
    }

    void add_ebn_link(IzhikevichNeuron *ebn_i) {
        this->excitatory_synapse(ebn_i);
    }

    double delta_etrace(double curr_value, double h_ji) {
        return (h_ji - curr_value) / (Constants::instance()->learning_window * 3.0);
    }
};

#endif //ROBOT_CONTROL_TONIC_NEURON_H