#!/usr/bin/python3

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager

path = '/home/praveen/Downloads/Calibri.ttf'
title_prop = font_manager.FontProperties(fname=path, size=20)
axis_prop = font_manager.FontProperties(fname=path, size=17)
label_prop = font_manager.FontProperties(fname=path, size=18)


from itertools import islice
import numpy as np
import time
import random
from collections import deque
import sys
from math import ceil
import math
import os
import servo_angle_calibration
import jsonpickle


folder = "tmp"
files = [
    'mn_ll', 'mn_lr', 'mn_rl', 'mn_rr',
    'mn_u', 'mn_d',
    'neck_mn_l', 'neck_mn_r',
    'n_mn_u', 'neck_mn_d'
    ]
y_values = [
    'Left Eye - Left', 'Left Eye - Right', 'Right Eye - Left', 'Right Eye - Right',
    'Eyes - Up', 'Eyes - Down',
    'Neck - Left', 'Neck - Right',
    'Neck - Up', 'Neck - Down'
]
files.reverse()
y_values.reverse()

motor_commands = [
    'pos_out_left', 'pos_out_right', 'pos_out_neck'
]
#inputs = ['opn_input_f', 'llbn_input_lf', 'llbn_input_rf']
inputs = [
    'llbn_input_llf', 'llbn_input_lrf', 'llbn_input_rlf', 'llbn_input_rrf',
    'llbn_input_uf', 'llbn_input_df'
    ]
outputs = [
    'pos_out_left', 'pos_out_right', 'pos_out_neck'
]

laser_position_file = 'laser_position'

laser_pan_c, laser_tilt_c, lpan_c, ltilt_c, rpan_c, rtilt_c, npan_c, ntilt_c = servo_angle_calibration.calibrate()

after_time = None

if len(sys.argv) == 1:
    # get input from file
    def input_from(filename):
        f = open(folder + "/" + filename)
        values = [float(x.replace('\n','')) for x in f.readlines()]
        ret = []
        for i in values:
            if i == 25:
                ret.append(1)
            else:
                ret.append(0)
        return ret

    def eye_motor_input(filename):
        f = open(folder + "/" + filename)
        pan = []
        tilt = []
        postns = [x.replace('\n','').split(' ') for x in f.readlines()]
        for stmp, p, t in postns:
            if after_time is not None and int(stmp) < after_time:
                continue
            if(filename.find("left") != -1):
                p = lpan_c(int(p))
                t = ltilt_c(int(t))
            else:
                p = rpan_c(int(p))
                t = rtilt_c(int(t))
            pan.append(p)
            tilt.append(t)
        return pan,tilt

    def laser_positions():
        f = open(folder + '/laser_position')
        d = jsonpickle.decode(f.readlines()[0])
        keys = list(d.keys())
        keys = [int(x) for x in keys]
        keys = sorted(keys)
        return d, keys

    def get_laser_position_for_timestamp(positions, timestamp, keys):
        laser_pos = positions[str(keys[0])]
        for val in keys:
            if(timestamp > val):
                laser_pos = positions[str(val)]
                continue
            else:
                break
        return laser_pos

    def neck_motor_input(filename, input_pan, input_tilt):
        d, keys = laser_positions()
        f = open(folder + "/" + filename)
        pan = []
        tilt = []
        postns = [x.replace('\n','').split(' ') for x in f.readlines()]
        for stmp, p, t in postns:
            if after_time is not None and int(stmp) < after_time:
                continue
            l_pos_pan, l_pos_tilt = get_laser_position_for_timestamp(d, int(stmp), keys).split(':')
            input_pan.append(laser_pan_c(int(l_pos_pan)))
            input_tilt.append(servo_angle_calibration.laser_tilt_fn([int(l_pos_pan), int(l_pos_tilt)], **laser_tilt_c))
            p = npan_c(int(p))
            t = ntilt_c(int(t))
            pan.append(p)
            tilt.append(t)
        return pan,tilt


    xlim = 1000
    index = 1
    fig1 = plt.figure()
    ntrials = 1000
    '''
    ax = fig1.add_subplot(111)
    ax.set_title('Raster Plot - Oculomotor Neurons controlling movement', fontproperties=title_prop)
    data = []
    dat = []
    
    for index, filename in enumerate(files):
        data.append(input_from(filename))
        ntrials = len(data[index])
        dat.append(np.arange(ntrials)[np.array(data[index]) == 1])

    lines = []
    line_segments = []
    for ith, trial in enumerate(dat):
        color = '#000000'
        lines.append(plt.vlines(trial, ith + 0.8, ith + 1.2, color=color, linewidth=2))
        line_segments.append(lines[len(lines) - 1].get_segments())

    ax.set_xlim([0, ntrials+1])
    ax.set_ylim([0, len(files) + 2])

    y_values.insert(0, ' ')
    y_axis = np.linspace(0, len(files), len(files)+1, endpoint=True)
    plt.yticks(y_axis, y_values, fontproperties=axis_prop)
    plt.xticks(fontproperties=axis_prop)
    '''

    input_pan = []
    input_tilt = []

    lpan, ltilt = eye_motor_input(motor_commands[0])
    rpan, rtilt = eye_motor_input(motor_commands[1])
    npan, ntilt = neck_motor_input(motor_commands[2], input_pan, input_tilt)

    fovea_angle_pan = lpan_c(515) - lpan_c(510)
    fovea_angle_tilt = ltilt_c(515) - ltilt_c(510)

    ax2 = fig1.add_subplot(211)
    # ax2.set_xlim([0, ntrials+1])
    ax2.set_ylim([-50, 50])
    effective_lpan = np.add(lpan, npan)
    l1, = plt.plot(effective_lpan, 'k')
    l4, = plt.plot(np.add(effective_lpan, [fovea_angle_pan] * len(effective_lpan)), 'k--', linewidth=0.5)
    plt.plot(np.subtract(effective_lpan, [fovea_angle_pan] * len(effective_lpan)), 'k--', linewidth=0.5)
    
    l3, = plt.plot(input_pan, 'b')

    effective_rpan = np.add(rpan, npan)
    l2, = plt.plot(effective_rpan, 'r')
    l5, = plt.plot(np.add(effective_rpan, [fovea_angle_pan] * len(effective_rpan)), 'r--', linewidth=0.5)
    plt.plot(np.subtract(effective_rpan, [fovea_angle_pan] * len(effective_rpan)), 'r--', linewidth=0.5)
    
    ax2.set_title('Horizontal Position with respect to Origin', fontproperties=title_prop)
    ax2.set_ylabel('Angle (degrees)', fontproperties=label_prop)
    plt.xticks(fontproperties=axis_prop)
    plt.yticks(fontproperties=axis_prop)

    ax3 = fig1.add_subplot(212)
    # ax3.set_xlim([0, ntrials+1])
    # ax3.set_ylim([-50, 50])
    effective_ltilt = np.add(ntilt, ltilt)
    l1, = plt.plot(effective_ltilt, 'k')
    l4, = plt.plot(np.add(effective_ltilt, [fovea_angle_tilt] * len(effective_ltilt)), 'k--', linewidth=0.5)
    plt.plot(np.subtract(effective_ltilt, [fovea_angle_tilt] * len(effective_ltilt)), 'k--', linewidth=0.5)

    l3, = plt.plot(input_tilt, 'b')

    effective_rtilt = np.add(ntilt, rtilt)
    l2, = plt.plot(effective_rtilt, 'r')
    l5, = plt.plot(np.add(effective_ltilt, [fovea_angle_tilt] * len(effective_ltilt)), 'r--', linewidth=0.5)
    plt.plot(np.subtract(effective_ltilt, [fovea_angle_tilt] * len(effective_ltilt)), 'r--', linewidth=0.5)

    ax3.set_title('Vertical Position with respect to Origin', fontproperties=title_prop)
    ax3.set_xlabel('Time (ms)', fontproperties=label_prop)
    ax3.set_ylabel('Angle (degrees)', fontproperties=label_prop)
    plt.xticks(fontproperties=axis_prop)
    plt.yticks(fontproperties=axis_prop)
    
    leg = ax3.legend(
        (l3, l1, l2, l4, l5),
        ('Input Position', 'Left Fovea Position (center)', 'Right Fovea Position (center)', 'Left Fovea Boundaries', 'Right Fovea Boundaries'))
    plt.setp(leg.texts, fontproperties=axis_prop)

    lpan_err = math.sqrt(np.mean(np.square(np.subtract(input_pan, effective_lpan))))
    rpan_err = math.sqrt(np.mean(np.square(np.subtract(input_pan, effective_rpan))))
    ltilt_err = math.sqrt(np.mean(np.square(np.subtract(input_tilt, effective_ltilt))))
    rtilt_err = math.sqrt(np.mean(np.square(np.subtract(input_tilt, effective_rtilt))))

    print(lpan_err)
    print(rpan_err)
    print(ltilt_err)
    print(rtilt_err)
    print(np.mean(np.array([lpan_err, rpan_err, ltilt_err, rtilt_err])))

    plt.show()
else:
    if sys.argv[1] == 'raster':
        batch_size = 500
        plt_delay = 0.00001
        if(len(sys.argv) == 3):
            plt_delay = float(sys.argv[2])

        def input_from(filename):
            while not os.path.exists(folder + "/" + filename):
                time.sleep(0.1)
            f = open(folder + "/" + filename)
            arr = []
            count = 0
            while True:
                if not f.readable():
                    time.sleep(0.001)
                    continue
                else:
                    s = f.readline()
                    if s is None or s == '\n':
                        continue
                    try:
                        val = float(s.replace('\n',''))
                    except:
                        continue
                    if val == 25:
                        val = 1
                    else:
                        val = 0
                    arr.append(val)
                    count += 1
                    if(count == batch_size):
                        yield(arr)
                        arr = []
                        count = 0

        ntrials = 1000 #1000 ms viewing window
        data = []
        dat = []
        generators = []
        # setup raster plot
        fig = plt.figure()
        plt.ion()
        for index, filename in enumerate(files):
            data.append(deque([0] * ntrials))
            dat.append(np.arange(ntrials)[np.array(data[index]) == 1])

        lines = []
        line_segments = []
        ax = plt.gca()
        for ith, trial in enumerate(dat):
            color = '#000000'
            lines.append(plt.vlines(trial, ith + 0.8, ith + 1.2, color=color, linewidth=2))
            line_segments.append(lines[len(lines) - 1].get_segments())

        ax.set_xlim([0, ntrials+1])
        ax.set_ylim([0, len(files) + 2])

        y_values = list(files)
        y_values.insert(0, ' ')
        y_axis = np.linspace(0, len(files), len(files)+1, endpoint=True)

        plt.yticks(y_axis, y_values)

        plt.show()
        # update plot with time
        sim_time = 0
        plt.title('Time: %d ms' % sim_time)

        for filename in files:
            generators.append(input_from(filename))

        while True:
            for index, filename in enumerate(files):
                arr = next(generators[index])
                for val in arr:
                    for i in range(len(line_segments[index])):
                        if line_segments[index][i][0][0] >= ntrials - 1:
                            line_segments[index].pop(i)
                        else: 
                            line_segments[index][i][0][0] += 1
                            line_segments[index][i][1][0] += 1
                    if(val == 1):
                        line_segments[index].insert(0, np.array([[ 0 ,  index + 0.8], [ 0 ,  index + 1.2]]))
                lines[index].set_segments(line_segments[index])
            if plt_delay != 0.00001:
                time.sleep(plt_delay)

            plt.title('Time: %.3f s' % (sim_time/1000))
            plt.draw()
            sim_time += batch_size
            plt.pause(plt_delay)
    if sys.argv[1] == 'continuous':
        print("Continuous plotting of waveform from files")
        time.sleep(1) # seconds
        pause_duration = (1/1000000) / len(files)
        # get input from file
        def input_from(filename):
            f = open(folder + "/" + filename)
            while True:
                if(f.readable()):
                    val = float(f.readline().replace('\n',''))
                    yield val
                time.sleep(pause_duration)

        xlim = 1000
        plt.ion()

        dat = []
        data = []
        lineplots = []

        for index, filename in enumerate(files):
            dat.append(deque([0] * xlim))
            data.append(input_from(filename))
            plt.subplot(len(files), 2, index+1)
            plt.ylim([-80, 30])
            plt.title(filename)
            plt.ylabel('mV')
            plt.xlabel('ms')
            line, = plt.plot(dat[index])
            lineplots.append(line)

        plt.show()

        while True:
            for index in range(len(files)):
                val = next(data[index])
                if val is not None:
                    dat[index].appendleft(val)
                    dat[index].pop()
                    lineplots[index].set_ydata(dat[index])
            plt.draw()
            time.sleep(pause_duration)
            plt.pause(pause_duration)
