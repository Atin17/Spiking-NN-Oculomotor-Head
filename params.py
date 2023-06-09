cfg = dict()

# Laser Pointer options
cfg['laser'] = dict()
cfg['laser']['exp'] = 'step'  # step, circle, or chirp
cfg['laser']['circle_num'] = 6  # only used for circle exp
cfg['laser']['chirp_max_circle_time'] = 20  # only used for chirp exp
cfg['laser']['chirp_decrease_rate'] = 1.2  # only used for chirp exp

# Head Control options
cfg['head'] = dict()
cfg['head']['eye_pan_inc'] = 0.0001
cfg['head']['eye_pan_lim'] = 0.8
cfg['head']['eye_tilt_inc'] = 0.002
cfg['head']['eye_tilt_lim'] = 0.8
cfg['head']['neck_pan_inc'] = 0.0008
cfg['head']['neck_pan_lim'] = 0.4
cfg['head']['neck_tilt_inc'] = 0.0008
cfg['head']['neck_tilt_lim'] = 0.4
cfg['head']['servo_move_spd'] = 2
cfg['head']['input_amp'] = 100
cfg['head']['ros_rate'] = 50
cfg['head']['run_time'] = 120
