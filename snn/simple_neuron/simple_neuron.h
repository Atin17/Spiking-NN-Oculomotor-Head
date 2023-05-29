//
// Created by praveen on 11/1/16.
//

#ifndef ROBOT_CONTROL_SIMPLE_NEURON_H
#define ROBOT_CONTROL_SIMPLE_NEURON_H

#include <string>
#include "opencv2/opencv.hpp"
#include <vector>

using namespace std;

class SimpleNeuron {
private:
    int x;
    int y;

    vector<string> field;
    vector<int> voltages;
public:
    SimpleNeuron(int x, int y) : x(x), y(y) { }

    void setField(vector<string> defined_field) {
        for(string val : defined_field) {
	    	if(field.size() == field.capacity() - 10) {
				field.reserve(field.capacity() + 1000);
		    }
            field.push_back(val);
        }
    }

    int process(cv::Mat frame, vector<int> inhibitingNeuronOutputs);

    int getX() {
	    return x;
	}

	int getY() {
		return y;
	}

    int getLastOutput() {
        return voltages.back();
    }

    SimpleNeuron();

	static int white_value;
};

#endif //ROBOT_CONTROL_SIMPLE_NEURON_H
