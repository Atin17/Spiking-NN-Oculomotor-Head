import servo_angle_calibration
import jsonpickle
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager

path = '/home/praveen/Downloads/Calibri.ttf'
title_prop = font_manager.FontProperties(fname=path, size=20)
axis_prop = font_manager.FontProperties(fname=path, size=17)
label_prop = font_manager.FontProperties(fname=path, size=18)

motor_commands = [
    'pos_out_left', 'pos_out_right', 'pos_out_neck'
]
laser_pan_c, laser_tilt_c, lpan_c, ltilt_c, rpan_c, rtilt_c, npan_c, ntilt_c = servo_angle_calibration.calibrate()
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

def neck_motor_input(filename, input_pan, input_tilt, trial_start_indexes):
    d, keys = laser_positions()
    f = open(folder + "/" + filename)
    pan = []
    tilt = []
    postns = [x.replace('\n','').split(' ') for x in f.readlines()]
    i = 0
    prev_val = False
    for stmp, p, t in postns:
        l_pos_pan, l_pos_tilt = get_laser_position_for_timestamp(d, int(stmp), keys).split(':')
        if l_pos_pan == '84' and l_pos_tilt == '113' and not prev_val:
        	trial_start_indexes.append(i)
        	prev_val = True
        if l_pos_pan != '84' and l_pos_tilt != '113' and prev_val:
        	prev_val = False
        input_pan.append(laser_pan_c(int(l_pos_pan)))
        input_tilt.append(servo_angle_calibration.laser_tilt_fn([int(l_pos_pan), int(l_pos_tilt)], **laser_tilt_c))
        p = npan_c(int(p))
        t = ntilt_c(int(t))
        pan.append(p)
        tilt.append(t)
        i += 1
    return pan,tilt


parent_folder = ''
# folders = [parent_folder + 'tmp_1', parent_folder + 'tmp_2', parent_folder + 'tmp_3']
folders = [parent_folder + 'tmp']
lpans =[]; rpans = []; ltilts = []; rtilts = []; 
trial_start_indexes = []
dat_length = None
for folder in folders: 
	input_pan = []; input_tilt = []; indices = [] 
	lpan, ltilt = eye_motor_input(motor_commands[0])
	rpan, rtilt = eye_motor_input(motor_commands[1])
	npan, ntilt = neck_motor_input(motor_commands[2], input_pan, input_tilt, indices)
	if dat_length is None or len(lpan) < dat_length:
		dat_length = len(lpan)
	lpans.append(np.subtract(np.add(lpan, npan), input_pan));
	rpans.append(np.subtract(np.add(rpan, npan), input_pan));
	ltilts.append(np.subtract(np.add(ltilt, ntilt), input_tilt));
	rtilts.append(np.subtract(np.add(rtilt, ntilt), input_tilt))
	trial_start_indexes.append(indices)


for i in range(len(folders)):
	lpans[i] = lpans[i][:dat_length]
	rpans[i] = rpans[i][:dat_length]
	ltilts[i] = ltilts[i][:dat_length]
	rtilts[i] = rtilts[i][:dat_length]

def compute_mean_var(values):
	mean_errors = []
	error_vars = []
	for i in range(len(folders)):
		means = []
		var = []
		start = 0
		for x in trial_start_indexes[i]:
			end = x - 1
			means.append(np.mean(np.array(values[i][start:end])))
			var.append(np.std(np.array(values[i][start:end])))
			start = x
		means.append(np.mean(np.array(values[i][start:])))
		var.append(np.std(np.array(values[i][start:])))
		mean_errors.append(means)
		error_vars.append(var)
	return mean_errors, error_vars

lpm, lpv = compute_mean_var(lpans)
rpm, rpv = compute_mean_var(rpans)
ltm, ltv = compute_mean_var(ltilts)
rtm, rtv = compute_mean_var(rtilts)

plts = []
x = range(11)
fig = plt.figure()
fig.suptitle('Change Eye Position Error with Reward based Learning', fontproperties=title_prop)
fig.text(0.04, 0.5, 'Mean Error (degrees)', va='center', rotation='vertical', fontproperties=label_prop)

plt.subplot(411)
for i in range(3):
	plts.append(plt.errorbar(x, lpm[i], lpv[i], linestyle='--', marker='o', fmt='o', capsize=10))
plt.title('Left Eye - Pan Error', fontproperties=title_prop)
# plt.ylabel('Mean Error (degrees)', fontproperties=label_prop)
plt.xticks(fontproperties=axis_prop)
plt.yticks(fontproperties=axis_prop)

plts = []
plt.subplot(412)
for i in range(3):
	plts.append(plt.errorbar(x, rpm[i], rpv[i], linestyle='--', marker='o', fmt='o', capsize=10))
plt.title('Right Eye - Pan Error', fontproperties=title_prop)
# plt.ylabel('Mean Error (degrees)', fontproperties=label_prop)
plt.xticks(fontproperties=axis_prop)
plt.yticks(fontproperties=axis_prop)

plts = []
plt.subplot(413)
for i in range(3):
	plts.append(plt.errorbar(x, ltm[i], ltv[i], linestyle='--', marker='o', fmt='o', capsize=10))
plt.title('Left Eye - Tilt Error', fontproperties=title_prop)
# plt.ylabel('Mean Error (degrees)', fontproperties=label_prop)
plt.xticks(fontproperties=axis_prop)
plt.yticks(fontproperties=axis_prop)

plt.subplot(414)
plts = []
for i in range(3):
	plts.append(plt.errorbar(x, rtm[i], rtv[i], linestyle='--', marker='o', fmt='o', capsize=10))
plt.title('Right Eye - Tilt Error', fontproperties=title_prop)
plt.xlabel('Trial #', fontproperties=label_prop)
# plt.ylabel('Mean Error (degrees)', fontproperties=label_prop)
plt.xticks(fontproperties=axis_prop)
plt.yticks(fontproperties=axis_prop)

leg = plt.legend((plts[0], plts[1], plts[2]), ('Run 1', 'Run 2', 'Run 3'))
plt.setp(leg.texts, fontproperties=axis_prop)

plt.show()

# m1 = np.mean(np.array(lpans), axis=0)
# v1 = np.std(np.array(lpans), axis=0)
# m2 = np.mean(np.array(rpans), axis=0)
# v2 = np.std(np.array(rpans), axis=0)
# m3 = np.mean(np.array(ltilts), axis=0)
# v3 = np.std(np.array(ltilts), axis=0)
# m4 = np.mean(np.array(rtilts), axis=0)
# v4 = np.std(np.array(rtilts), axis=0)

# x = range(int(dat_length/10))
# fig = plt.figure()
# plt.subplot(411)
# plt.errorbar(x, m1[:len(x)], v1[:len(x)], linestyle='None', marker='.')
# plt.subplot(412)
# plt.errorbar(x, m2[:len(x)], v2[:len(x)], linestyle='None', marker='.')
# plt.subplot(413)
# plt.errorbar(x, m3[:len(x)], v3[:len(x)], linestyle='None', marker='.')
# plt.subplot(414)
# plt.errorbar(x, m4[:len(x)], v4[:len(x)], linestyle='None', marker='.')

# plt.show()
