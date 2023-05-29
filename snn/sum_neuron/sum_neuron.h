#ifndef ROBOT_CONTROL_SUM_NEURON_H_H
#define ROBOT_CONTROL_SUM_NEURON_H_H

#include <vector>
#include <fstream>
#include <string>

#include "../constants.h"

using namespace std;

class SumNeuron {
private:
    //Neuron parameters
    double v_max = 25;
    double resting_potential = -70;

    const string folderName = Constants::instance()->outputDir;
    string out_filename;
    ofstream memb_out;
public:
    vector<double> voltages;
    double out_3 = 0;

    SumNeuron(string filename) : out_filename(filename) {
        voltages.reserve(1000);
        voltages.push_back(resting_potential);

        if(!memb_out.is_open()) {
            memb_out.open((folderName + out_filename).c_str(), ios::out);
        }
    }

    double process(double input_current) {
        if(voltages.size() == voltages.capacity() - 10) {
            voltages.reserve(voltages.size() + 1000);
        }

        double new_membrane_potential = resting_potential;

        if(input_current > 0) {
            new_membrane_potential = v_max;
        }

        voltages.push_back(new_membrane_potential);

        memb_out << new_membrane_potential << endl;

        return new_membrane_potential;
    }

    void reset() {
        voltages.push_back(resting_potential);
    }
};

#endif //ROBOT_CONTROL_SUM_NEURON_H_H
