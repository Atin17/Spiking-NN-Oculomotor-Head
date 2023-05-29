from collections import deque
import sys, os
from snn.Constants import Constants

def sejnowski(pre_v, post_v, rate = 0.5):
    if not post_v:
        return 0
    return float(rate) * (float(post_v[-1]) - float(sum(post_v)) / float(len(post_v))) * (float(pre_v[-1]) - float(sum(pre_v)) / float(len(pre_v)))

def hebbian(pre_v, post_v, rate, curr_weight):
    return sejnowski(pre_v, post_v, rate)

def moving_average(avg, new_val):
    avg -= avg / Constants.instance().learning_window
    avg += new_val / Constants.instance().learning_window
    return avg
