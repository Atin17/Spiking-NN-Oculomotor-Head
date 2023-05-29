#ifndef ROBOT_CONTROL_RECEPTIVE_FIELD_H
#define ROBOT_CONTROL_RECEPTIVE_FIELD_H

#include <iostream>
#include <fstream>
#include <vector>
#include <exception>

#include "../json/json.hpp"

#include "../simple_neuron/simple_neuron.h"
#include "../midbrain/colliculus_neuron.h"

#include "../constants.h"

using json = nlohmann::json;
using namespace std;

vector<SimpleNeuron> readReceptiveField() {
	vector<SimpleNeuron> bipolars;
	bipolars.reserve(188 * 100);

	ifstream receptiveFieldFs(Constants::instance()->rootDir + "/bipolars/new_map.json");

	if(!receptiveFieldFs)
		throw -1;

	json bipolarsJson;
	receptiveFieldFs >> bipolarsJson;

	int ix = 0;
    while(ix < bipolarsJson.size()) {
        //Iterate
        json neuronZone = bipolarsJson[ix];
        for(int innerIx = 0; innerIx < neuronZone.size(); innerIx++) {
            json &bipolar = neuronZone[innerIx];

            SimpleNeuron neuron(bipolar["x"], bipolar["y"]);

            neuron.setField(bipolar["field"]);

            if(bipolars.size() < bipolars.capacity() - 100)
                bipolars.reserve(bipolars.capacity() + 1000);
            bipolars.push_back(neuron);
        }
        ix++;
    }

    receptiveFieldFs.close();
    return bipolars;
}

vector<ColliculusNeuron> readFrontalReceptiveField(int eye) {
    vector<ColliculusNeuron> sc_neurons;
    sc_neurons.reserve(188 * 100);

    ifstream receptiveFieldFs(Constants::instance()->rootDir + "/bipolars/new_map.json");

    if(!receptiveFieldFs)
        throw -1;

    json frontalFieldJson;
    receptiveFieldFs >> frontalFieldJson;

    int ix = 0;
    while(ix < frontalFieldJson.size()) {
        //Iterate
        json neuronZone = frontalFieldJson[ix];
        for(int innerIx = 0; innerIx < neuronZone.size(); innerIx++) {
            json &fieldCenter = neuronZone[innerIx];

            ColliculusNeuron neuron(fieldCenter["x"], fieldCenter["y"], eye == 0 ? "left" : "right");

            neuron.setField(fieldCenter["field"]);

            if(sc_neurons.size() < sc_neurons.capacity() - 100)
                sc_neurons.reserve(sc_neurons.capacity() + 1000);
            sc_neurons.push_back(neuron);
        }
        ix++;
    }

    receptiveFieldFs.close();
    return sc_neurons;
}

json readInverseReceptiveField() {
	json inverse_json;
	
	ifstream bipolarInverseFs(Constants::instance()->rootDir + "/bipolars/new_map.json.inverse");

    if(!bipolarInverseFs)
        throw -1;

    bipolarInverseFs >> inverse_json;

    bipolarInverseFs.close();

    return inverse_json;
}

#endif //ROBOT_CONTROL_RECEPTIVE_FIELD_H
