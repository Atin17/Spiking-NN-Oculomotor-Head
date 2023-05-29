#ifndef ROBOT_CONTROL_COLLICULUS_NEURON_H
#define ROBOT_CONTROL_COLLICULUS_NEURON_H

#include <vector>
#include <string>
#include "opencv2/opencv.hpp"
#include <fstream>

#include "../utilities/string_utilities.h"
#include "../debug/debug.h"

#include "../constants.h"

using namespace std;

class ColliculusNeuron {
private:
    // Center of receptive field - position
    int x;
    int y;

    // Receptive Field
    vector<string> field;

    // Membrane potential
    vector<double> voltages;

    const string folderName = Constants::instance()->outputDir;
    string out_filename;

    // Neuron parameters - LIF
    double Rm = 100;
    double Cm = 10;
    double tau = Rm * Cm;
    double dt = 30;
    double spike_voltage = 15.0;
    double resting_potential = -70;

    double v_th = 10;
    double v_max = 25;
public:
    ColliculusNeuron(int x, int y, string eye) : x(x), y(y),
        out_filename("sc_" + eye + "_" + to_string(x) + "_" + to_string(y)) {
        voltages.reserve(1000);
        voltages.push_back(resting_potential);
    }

    void setField(vector<string> defined_field) {
        for(string val : defined_field) {
            if(field.size() == field.capacity() - 10) {
                field.reserve(field.capacity() + 1000);
            }
            field.push_back(val);
        }
    }

    double process(double input) {
        // ofstream memb_out;
        // if(!memb_out.is_open()) {
        //     memb_out.open((folderName + out_filename).c_str(), ios::ate);
        // }
        double v = voltages.back();
        double dV = ((input * 100.0 * Rm) - v) * (dt / tau);
        v += dV;

        if(v > v_th) {
            v += spike_voltage;
        }

        if(v > v_max)
            v = v_max;

        if(v < resting_potential)
            v = resting_potential;

        if(voltages.size() == voltages.capacity() - 10) {
            voltages.reserve(voltages.capacity() + 1000);
        }

        voltages.push_back(v);
        // memb_out << v << endl;
        // memb_out.close();
        return v;
    }

    void reset() {
        voltages.push_back(resting_potential);
    }

    double process(cv::Mat frame) {
        vector<string> elements;

        double input = 0;

        for(string xy : field) {
            elements = str_split(xy, ',');
            int x_v = stoi(elements[0]);
            int y_v = stoi(elements[1]);
            int val = (int) frame.at<uchar>(y_v, x_v);

            if(val > 240) { //TODO: Convert this into inhibitory synaptic behavior for thresholding
                if(Debug::debug_level <= DEBUG_VERBOSE)
                    cout << "X: " << x << ", Y: " << y << ", val: " << val << endl;
                input += 1;
            }
        }

        return process(input);
    }

    int getX() {
        return x;
    }

    int getY() {
        return y;
    }

    int getLastOutput() {
        return voltages.back();
    }

    ColliculusNeuron() { }
};

#endif //ROBOT_CONTROL_COLLICULUS_NEURON_H
