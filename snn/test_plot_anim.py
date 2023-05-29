import matplotlib.pyplot as plt
from itertools import islice
import numpy as np
import time
import random
from collections import deque
import sys
from math import ceil
import os
import matplotlib.animation as animation

folder = "tmp"
files = [
    #'ebn_l', 'ebn_r', 'ebn_lr', 'ebn_rl', 'ibn_l', 'ibn_r', 'ifn_l', 'ifn_r', 'ifn_lr', 'ifn_rl',
    #'llbn_l', 'llbn_r', 'llbn_lr', 'llbn_rl',
    'tn_l', 'tn_r', 'tn_lr', 'tn_rl',
    's1_r_mn_lr', 's1_r_mn_rr', 's2_r_mn_lr', 's2_r_mn_rr', 's3_r_mn_lr', 's3_r_mn_rr', 
    's4_r_mn_lr', 's4_r_mn_rr', 'r_mn_lr', 'r_mn_rr', 's1_l_mn_rl', 's1_l_mn_ll', 
    's2_l_mn_rl', 's2_l_mn_ll', 's3_l_mn_rl', 's3_l_mn_ll', 's4_l_mn_rl', 's4_l_mn_ll', 'l_mn_rl', 'l_mn_ll'
    #'opn',
    # 'tn_u', 'tn_d',
    # 'mn_u', 'mn_d',
    # 'tn_nl', 'tn_nr',
    # 'mn_nl', 'mn_nr'
    ]

batch_size = 500
plt_delay = 0.00001
if(len(sys.argv) == 2):
    plt_delay = float(sys.argv[1])

def raster_input_from(filename):
    while not os.path.exists(folder + "/" + filename):
        time.sleep(0.05)
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

def get_input_from(filenames):
    while not os.path.exists(folder + "/" + filenames[0]) or \
        not os.path.exists(folder + "/" + filenames[1]):
        time.sleep(0.05)
    f1 = open(folder + "/" + filenames[0])
    f2 = open(folder + "/" + filenames[1])
    arr = []
    count = 0
    while True:
        if not f1.readable() or not f2.readable():
            time.sleep(0.001)
            continue
        else:
            s1 = f1.readline()
            s2 = f2.readline()
            if s1 is None or s1 == '\n' or s2 is None or s2 == '\n':
                continue
            try:
                val1 = float(s1.replace('\n',''))
                val2 = float(s2.replace('\n', ''))
            except:
                continue
            arr.append(val1 - val2)
            count += 1
            if(count == batch_size):
                yield(arr)
                arr = []
                count = 0

def get_position_from(filename):
    while not os.path.exists(folder + "/" + filename):
        time.sleep(0.05)
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
                val = [int(x) for x in s.replace('\n','').split(' ')]
            except:
                continue
            arr.append(val)
            count += 1
            if(count == batch_size):
                yield(arr)
                arr = []
                count = 0

def plot_pan_tilt_position(subplot, filename):
    subplot.set_xlim([0, ntrials+1])
    subplot.set_xlabel('Time (ms)')
    subplot.set_ylabel('Position')
    subplot.set_ylim([400, 650])
    data_pan = deque([512] * ntrials)
    data_tilt = deque([512] * ntrials)

    gen = get_position_from(filename)

    plot_pan, = subplot.plot(data_pan, color='#ff0000')
    plot_tilt, = subplot.plot(data_tilt, color='#00ff00')

    return data_pan, data_tilt, plot_pan, plot_tilt, gen

ntrials = 1000 #1000 ms viewing window
fig = plt.figure()

# setup raster plot
# Left Plot - Spike raster
spikes = plt.subplot2grid((4,4), (0,0), rowspan=4, colspan=2)
generators = []

lines = []
line_segments = []
    
dat = []
data = []

for index, filename in enumerate(files):
    data.append(deque([0] * ntrials))
    dat.append(np.arange(ntrials)[np.array(data[index]) == 1])

for ith, trial in enumerate(dat):
    color = '#000000'
    lines.append(spikes.vlines(trial, ith + 0.8, ith + 1.2, color=color, linewidth=2))
    line_segments.append(lines[len(lines) - 1].get_segments())

spikes.set_xlim([0, ntrials+1])
spikes.set_ylim([0, len(files) + 2])
spikes.set_xlabel('Time (ms)')

y_values = list(files)
y_values.insert(0, ' ')
y_axis = np.linspace(0, len(files), len(files)+1, endpoint=True)
spikes.set_yticks(y_axis, y_values)

for filename in files:
    generators.append(raster_input_from(filename))

#
left_eye = plt.subplot2grid((4,4), (0,2))
# TODO: Imshow left frame
right_eye = plt.subplot2grid((4,4), (0,3))
# TODO: imshow right frame

# Left eye input from SC
left_in = plt.subplot2grid((4,4), (1, 2))
left_in.set_xlim([0, ntrials+1])
left_in.set_xlabel('Time (ms)')
left_in.set_ylabel('mV')
left_in.set_ylim([-5, 5])
left_in_data_hor = deque([0] * ntrials)
in_data_ver = deque([0] * ntrials)

left_in_hor, = left_in.plot(left_in_data_hor, color='#ff0000')
left_in_ver, = left_in.plot(in_data_ver, color='#00ff00')

left_in_gen = []
left_in_gen.append(get_input_from(['llbn_input_llf', 'llbn_input_lrf']))

# common vertical input
up_down_gen = get_input_from(['llbn_input_uf', 'llbn_input_df'])

right_in_gen = []
right_in_gen.append(get_input_from(['llbn_input_rlf', 'llbn_input_rrf']))

# right eye input from SC
right_in = plt.subplot2grid((4,4), (1, 3))
right_in.set_xlim([0, ntrials+1])
right_in.set_xlabel('Time (ms)')
right_in.set_ylabel('mV')
right_in.set_ylim([-5, 5])
right_in_data_hor = deque([0] * ntrials)

right_in_hor, = right_in.plot(right_in_data_hor, color='#ff0000')
right_in_ver, = right_in.plot(in_data_ver, color='#00ff00')

# Position plots
# Left eye position display
left_pos = plt.subplot2grid((4,4), (2, 2))
left_data_pan, left_data_tilt, \
    left_plot_pan, left_plot_tilt, left_pos_gen = \
    plot_pan_tilt_position(left_pos, 'pos_out_left')

#  right eye position display
right_pos = plt.subplot2grid((4,4), (2, 3))
right_data_pan, right_data_tilt, \
    right_plot_pan, right_plot_tilt, right_pos_gen = \
    plot_pan_tilt_position(right_pos, 'pos_out_right')

# neck position display
neck_pos = plt.subplot2grid((4,4), (3, 2), colspan=2)
neck_data_pan, neck_data_tilt, \
    neck_plot_pan, neck_plot_tilt, neck_pos_gen = \
    plot_pan_tilt_position(neck_pos, 'pos_out_neck')

sim_time = 0

def update_raster(i):
    global generators
    global files
    global line_segments
    global lines
    global spikes
    global fig
    global sim_time
    # Spike raster
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
    
    sim_time += batch_size
    fig.suptitle("Time: %d ms" % sim_time)
    
    return spikes,

def update_inputs(i):
    global left_in_data_hor
    global left_in_hor
    global right_in_data_hor
    global right_in_hor
    global in_data_ver
    global left_in_ver
    global right_in_ver
    global left_in_gen
    global right_in_gen
    global up_down_gen
    
    # Left input Horizontal
    arr = next(left_in_gen[0])
    for val in arr:
        left_in_data_hor.pop()
        left_in_data_hor.insert(0, val)
    left_in_hor.set_ydata(left_in_data_hor)
    # Right input Horizontal
    arr = next(right_in_gen[0])
    for val in arr:
        right_in_data_hor.pop()
        right_in_data_hor.insert(0, val)
    right_in_hor.set_ydata(right_in_data_hor)

    # input vertical
    arr = next(up_down_gen)
    for val in arr:
        in_data_ver.pop()
        in_data_ver.insert(0, val)
    left_in_ver.set_ydata(in_data_ver)
    right_in_ver.set_ydata(in_data_ver)
    return left_in_hor,

def update_positions(i):
    global left_pos_gen
    global right_pos_gen
    global neck_pos_gen
    global left_data_pan
    global left_data_tilt
    global left_plot_pan
    global left_plot_tilt
    global right_data_pan
    global right_data_tilt
    global right_plot_pan
    global right_plot_tilt
    global neck_plot_pan
    global neck_plot_tilt
    global neck_data_pan
    global neck_data_tilt
    
    # Positions
    arr = next(left_pos_gen)
    for val in arr:
        left_data_pan.pop()
        left_data_tilt.pop()
        left_data_pan.insert(0, val[0])
        left_data_tilt.insert(0, val[1])
    left_plot_pan.set_ydata(left_data_pan)
    left_plot_tilt.set_ydata(left_data_tilt)

    arr = next(right_pos_gen)
    for val in arr:
        right_data_pan.pop()
        right_data_tilt.pop()
        right_data_pan.insert(0, val[0])
        right_data_tilt.insert(0, val[1])
    right_plot_pan.set_ydata(right_data_pan)
    right_plot_tilt.set_ydata(right_data_tilt)

    arr = next(neck_pos_gen)
    for val in arr:
        neck_data_pan.pop()
        neck_data_tilt.pop()
        neck_data_pan.insert(0, val[0])
        neck_data_tilt.insert(0, val[1])
    neck_plot_pan.set_ydata(neck_data_pan)
    neck_plot_tilt.set_ydata(neck_data_tilt)

    return neck_plot_tilt,

mng = plt.get_current_fig_manager()
mng.full_screen_toggle()
time.sleep(2.5)

raster_anim = animation.FuncAnimation(fig, update_raster, interval=batch_size)
input_anim = animation.FuncAnimation(fig, update_inputs, interval=batch_size, blit=True)
position_anim = animation.FuncAnimation(fig, update_positions, interval=batch_size, blit=True)

plt.show()