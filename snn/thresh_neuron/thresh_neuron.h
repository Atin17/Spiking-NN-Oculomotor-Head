#ifndef ROBOT_CONTROL_THRESH_NEURON_H_H
#define ROBOT_CONTROL_THRESH_NEURON_H_H

#include <vector>
#include <fstream>
#include <deque>
#include <string>

#include "../constants.h"

using namespace std;

class ThreshNeuron {
private:
    //Neuron parameters
    double window_size = 20;
    double threshold = 10;
    double v_max = 25;
    double resting_potential = -70;

    const string folderName = Constants::instance()->outputDir;
    string out_filename;
    ofstream memb_out;

    deque<double> inputs;
    double effective_input;
    deque<double> outs;
public:
    vector<double> voltages;
    double out_3 = 0;

    ThreshNeuron(string filename, double window = 20, double thresh = 10) {
        voltages.reserve(1000);
        voltages.push_back(resting_potential);
        window_size = window;
        threshold = thresh;

        if(!memb_out.is_open()) {
            memb_out.open((folderName + out_filename).c_str(), ios::out);
        }
    }

    double process(double input_current) {
        if(voltages.size() == voltages.capacity() - 10) {
            voltages.reserve(voltages.size() + 1000);
        }

        double new_membrane_potential = resting_potential;

        bool negative = false;

        if(input_current < 0) {
            input_current = 0;
            negative = true;
        }

        effective_input += input_current;

        inputs.push_back(input_current);
        if(inputs.size() > window_size) {
            effective_input -= inputs.front();
            inputs.pop_front();
        }

        if(effective_input > threshold && !negative)
            new_membrane_potential = v_max;

        voltages.push_back(new_membrane_potential);

        outs.push_back(new_membrane_potential == 25 ? 1 : 0);
        out_3 += new_membrane_potential == 25 ? 1 : 0;
        if(outs.size() > 3) {
            out_3 -= outs.front();
            outs.pop_front();
        }

        memb_out << new_membrane_potential << endl;

        return new_membrane_potential;
    }

    void reset() {
        inputs.clear();
    }
};

#endif //ROBOT_CONTROL_THRESH_NEURON_H_H
