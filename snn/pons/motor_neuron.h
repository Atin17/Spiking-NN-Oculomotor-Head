#ifndef ROBOT_CONTROL_MOTOR_NEURON_H
#define ROBOT_CONTROL_MOTOR_NEURON_H

#include <vector>
#include <fstream>
#include <deque>
#include <string>

#include "../constants.h"
#include "../izhikevich_neuron/izhikevich.h"
#include "tonic_neuron.h"

using namespace std;

class MotorNeuron {
public:
    //Neuron parameters
    double Rm = 100;                 // Membrane resistance (kOhm)
    double Cm = 10;                  // Membrane capacitance (uF)
    double tau_m = Rm * Cm;          // Time constant (ms)
    double dt = 1.0;                 // Time difference - with 30 fps
    double spike_voltage = 15.0;     // Spike potential (mV)
    double resting_potential;        // Resting membrane potential (mV)
    int refractory_period = 1;       // Neuron refractory period (ms)
    int resting_time = 0;            // Neuron rest period after spike (ms)

    double v_th = 10;                 // Threshold membrane potential for spike (mV)
    double v_max = 25;                // Max membrane potential (mV)

    const string folderName = Constants::instance()->outputDir;
    string out_filename;
    ofstream memb_out;

    ofstream inputs;

    vector<IzhikevichNeuron*> inhibitory;
    vector<TonicNeuron*> excitatory;

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

    vector<double> voltages;
    double w_tn_v, w_tn_vv, w_tn_cv;
    ofstream tnv_weights, tnvv_weights, tncv_weights, ibn_weights;
    bool learning = false;
    int window_position = 0;

    MotorNeuron(string filename, TonicNeuron *tn = NULL) : out_filename(filename) {
        voltages.reserve(1000);
        voltages.push_back(-50);
        resting_potential = -50;
        learning = Constants::instance()->learning;

        if(!memb_out.is_open()) {
            memb_out.open((folderName + out_filename).c_str(), ios::out);
        }
        if(!inputs.is_open()) {
            inputs.open((folderName + "inp_" + out_filename).c_str(), ios::out);
        }
        w_tn_v = 1.0;
        w_tn_vv = 1.0;
        w_tn_cv = 1.0;

        if(tn != NULL)
            add_tn_link(tn);

        if(learning) {
            tnv_weights.open(folderName + filename + "_tnv", ios::out);
            tnvv_weights.open(folderName + filename + "_tnvv", ios::out);
            tncv_weights.open(folderName + filename + "_tncv", ios::out);
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

        inputs << I << endl;

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

    // input_current = inhibiting input from the direction selectivity neuron
    // Excitatory: TN_i and TN_cm
    // Inhibitory: IBN_c if lateral else IBN_i
    double alter_current(double input_current) {
        // double feedback_current = to_current(voltages.back());
        double ibn_v = 0;
        int size;
        if(inhibitory.size() > 0) {
            //IBN
            IzhikevichNeuron *ibn = inhibitory[0];
            size = ibn->voltages.size();
            if(size > 1) {
                ibn_v = ibn->voltages[size - 1];
            }
        } else {
            inhibitory_weights.push_back(4.0 * tau_m * 180.0 / 1000.0);
        }

        TonicNeuron *tn = excitatory[0];
        size = tn->voltages.size();
        double tn_v = 0;
        if(size > 0) {
            tn_v = tn->voltages[size - 1]; // Use last value / current value
        }

        double tn_vv = 0;
        if(excitatory.size() >= 2) {
            tn = excitatory[1];
            size = tn->voltages.size();
            if(size > 0) {
                tn_vv = tn->voltages[size - 1]; // Use last value / currrent value
            }
        } else {
            excitatory_weights.push_back(8.0 * tau_m * 175 / 1000.0);
        }

        double tn_cv = 0;
        if(excitatory.size() == 3) {
            tn = excitatory[2];
            size = tn->voltages.size();
            if(size > 0)
                tn_cv = tn->voltages[size - 1];
        } else {
            excitatory_weights.push_back(8.0 * tau_m * 175 / 1000.0);
        }

        if(learning) {
            if(inhibitory.size() > 0) {
                inhibitory_pre_v[0].push_back(ibn_v == 25);
                if(inhibitory_pre_v[0].size() > Constants::instance()->learning_window)
                    inhibitory_pre_v[0].pop_front();
            }

            excitatory_pre_v[0].push_back(tn_v == 25);
            if(excitatory_pre_v[0].size() > Constants::instance()->learning_window)
                excitatory_pre_v[0].pop_front();

            if(excitatory.size() >= 2) {
                excitatory_pre_v[1].push_back(tn_vv == 25);
                if(excitatory_pre_v[1].size() > Constants::instance()->learning_window)
                    excitatory_pre_v[1].pop_front();
            }

            if(excitatory.size() == 3) {
                excitatory_pre_v[2].push_back(tn_cv == 25);
                if(excitatory_pre_v[2].size() > Constants::instance()->learning_window)
                    excitatory_pre_v[2].pop_front();
            }
        } else {
            excitatory_weights[0] = 8.0 * tau_m * 175 / 1000.0;
            excitatory_weights[1] = 8.0 * tau_m * 175 / 1000.0;
            excitatory_weights[2] = 8.0 * tau_m * 175 / 1000.0;
            inhibitory_weights[0] = 4.0 * tau_m * 180 / 1000.0;
        }

        return input_current
            + to_current(tn_v) * w_tn_v * excitatory_weights[0] //8.0 * tau_m * 175 / 1000.0
            + to_current(tn_vv) * w_tn_vv * excitatory_weights[1] //8.0 * tau_m * 175 / 1000.0
            + to_current(tn_cv) * w_tn_cv * excitatory_weights[2] //8.0 * tau_m * 175 / 1000.0
            - to_current(ibn_v) * inhibitory_weights[0]; //4.0 * tau_m * 180 / 1000.0;
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

        if(excitatory.size() >= 2) {
            h_ji = hebbian(excitatory_pre_v[1], post_v, 10.0, excitatory_weights[1]);
            // update etrace
            excitatory_etrace[1] += delta_etrace(excitatory_etrace[1], h_ji);
            excitatory_weights[1] += h_ji * excitatory_etrace[1] * (1 - reward_in) * Constants::instance()->learning_rate;
        }

        if(excitatory.size() == 3) {
            h_ji = hebbian(excitatory_pre_v[2], post_v, 10.0, excitatory_weights[2]);
            // update etrace
            excitatory_etrace[2] += delta_etrace(excitatory_etrace[2], h_ji);
            excitatory_weights[2] += h_ji * excitatory_etrace[2] * (1 - reward_in) * Constants::instance()->learning_rate;
        }
        // save weights to file
        tnv_weights << excitatory_weights[0] << endl;
        tnvv_weights << excitatory_weights[1] << endl;
        tncv_weights << excitatory_weights[2] << endl;
    }

    void reset() {
        voltages.push_back(resting_potential);
    }

    void add_tn_link(TonicNeuron *tn) {
        excitatory.push_back(tn);
        excitatory_weights.push_back(100);
        excitatory_pre_v.push_back(deque<double>());
        excitatory_etrace.push_back(0);
    }

    void add_ibn_link(IzhikevichNeuron *ibn) {
        inhibitory.push_back(ibn);
        inhibitory_weights.push_back(100);
        inhibitory_pre_v.push_back(deque<double>());
        inhibitory_etrace.push_back(0);
    }

    double delta_etrace(double curr_value, double h_ji) {
        return (h_ji - curr_value) / (Constants::instance()->learning_window * 3.0);
    }
};

#endif //ROBOT_CONTROL_MOTOR_NEURON_H
