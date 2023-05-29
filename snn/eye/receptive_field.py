import json
import os

from snn.simple_neuron.simple_neuron import SimpleNeuron
from snn.midbrain.colliculus_neuron import ColliculusNeuron
from snn.Constants import Constants

def read_receptive_field():
    bipolars = []

    with open(os.path.join([Constants.instance().rootDir, "bipolars/new_map.json"])) as receptive_field_fs:
        bipolars_json = json.load(receptive_field_fs)

        ix = 0
        while ix < len(bipolars_json):
            neuron_zone = bipolars_json[ix]
            for inner_ix in range(len(neuron_zone)):
                bipolar = neuron_zone[inner_ix]

                neuron = SimpleNeuron(bipolar["x"], bipolar["y"])
                neuron.set_field(bipolar["field"])

                bipolars.append(neuron)

            ix += 1

    return bipolars

def read_frontal_receptive_field(eye):
    sc_neurons = []

    with open(os.path.join([Constants.instance().rootDir, "bipolars/new_map.json"])) as receptive_field_fs:
        frontal_field_json = json.load(receptive_field_fs)

        ix = 0
        while ix < len(frontal_field_json):
            neuron_zone = frontal_field_json[ix]
            for inner_ix in range(len(neuron_zone)):
                field_center = neuron_zone[inner_ix]

                neuron = ColliculusNeuron(field_center["x"], field_center["y"], "left" if eye == 0 else "right")
                neuron.set_field(field_center["field"])

                sc_neurons.append(neuron)

            ix += 1

    return sc_neurons

def read_inverse_receptive_field():
    with open(os.path.join([Constants.instance().rootDir, "bipolars/new_map.json.inverse"])) as bipolar_inverse_fs:
        inverse_json = json.load(bipolar_inverse_fs)

    return inverse_json