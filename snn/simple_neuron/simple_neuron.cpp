//
// Created by praveen on 11/1/16.
//

#include "simple_neuron.h"
#include "../utilities/string_utilities.h"
#include "../debug/debug.h"

using namespace std;
using namespace cv;

int SimpleNeuron::process(Mat frame, vector<int> inhibitingNeuronOutputs) {
    int out = 0;

    vector<string> elements;

    for(int val : inhibitingNeuronOutputs) {
        if(val == 1) {
            voltages.push_back(out); //NOTE: out = 0
            return out;
        }
    }
    
    for(string xy : field) {
        elements = str_split(xy, ',');
        int x_v = stoi(elements[0]);
        int y_v = stoi(elements[1]);
        int val = (int) frame.at<uchar>(y_v, x_v);

		if(val > 240) { //TODO: Convert this into inhibitory synaptic behavior for thresholding
			if(Debug::debug_level <= DEBUG_VERBOSE)
                cout << "X: " << x << ", Y: " << y << ", val: " << val << endl;
            out = 1;
            break;
        }
    }

    if(voltages.size() == voltages.capacity() - 10) {
		voltages.reserve(voltages.capacity() + 1000);
	}

    voltages.push_back(out);

    return out;
}

SimpleNeuron::SimpleNeuron() {
}
