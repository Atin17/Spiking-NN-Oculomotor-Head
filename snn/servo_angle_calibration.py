import math
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import scipy

d_wall = 55.3

# def separator():
	# print("-" * 80)
	# print("=" * 80)
	# print("-" * 80)

def laser_tilt_fn(x, a, b, c, d, e, f, g):
	return a + b * x[0] + c * (x[0]**2) + d * (x[0]**3) + e * x[1] + f * (x[1] ** 2) + g * (x[1]**3)

def dp(pan, laser_pan_c):
    global d_wall
    return d_wall / math.cos(laser_pan_c(pan) * math.pi / 180)

def calc_angle(D, dist=None):
	# ratio of distance of point on the wall from origin of wall
	# to distance of wall from the camera
	global d_wall
	if dist is None:
		val = D/d_wall
	else:
		val = D/dist
	return math.degrees(math.atan(val))

# def printNormal(vec, prefix=''):
	# st = prefix + "["
	# for x in vec:
	# 	val = '{:4f}'.format(x)
	# 	if float(val) == 0:
	# 		val = '{:4f}'.format(0)
	# 	st += val
	# 	st += ' '
	# st += ']'
	# print(st)

def compute_coeff(distances, angles, positions):
	# separator()
	# print("Find coefficients".upper())
	coeff = []
	rhs = []
	for i in range(4):
		a = []
		a.append(distances[i] ** 3)
		a.append(distances[i] ** 2)
		a.append(distances[i] ** 1)
		a.append(1)
		coeff.append(a)
		rhs.append(angles[i])

	a = np.array(coeff)
	b = np.array(rhs)
	x = np.linalg.solve(a, b)

	# print("Parameters: ".upper())
	# printNormal(x)

	for i in range(4, len(distances)):
		a = []
		a.append(distances[i] ** 3)
		a.append(distances[i] ** 2)
		a.append(distances[i] ** 1)
		a.append(1)
		coeff.append(a)
		rhs.append(angles[i])

	a = np.array(coeff)
	b = np.array(rhs)

	# print("Compare validity of parameters: ")
	# print('Positions: %s' % positions)
	# printNormal(np.dot(a, x), 'LINSPACE: ')
	# printNormal(b, 'ORIG: ')

	a = np.array(angles)
	b = np.array(positions)
	c = np.polyfit(b, a, 4)

	p = np.poly1d(c)
	y = []
	for x in positions:
		y.append(p(x))
	# printNormal(y, 'FROM SERVO POSITION:')

	return p

def calibrate():
	# separator()
	# print("Left, right error values: CALIBRATION".upper())
	ld_0 = 9.5
	rd_0 = 7.0
	l_err = calc_angle(ld_0) * (-1)
	r_err = calc_angle(rd_0)
	# print(l_err)
	# print(r_err)

	distances = [-26, -17.8, -9.5, 0, 7.0, 12, 24.8]
	angles = []
	positions = [122, 112, 101, 84, 75, 65, 50]
	# print("Angles for distances")
	for d in distances:
		ang = calc_angle(d)
		angles.append(ang)
		# print("Distance from origin: %s, Angle: %s" % (d, ang))

	laser_pan_c = compute_coeff(distances, angles, positions)

	# separator()
	# print("laser up, down error values: CALIBRATION".upper())

	tilt_positions = [114, 130, 90, 70]
	pan_positions = [84, 80, 70, 60, 50, 100, 110, 120]

	heights = {
	114: [0, 0.4, 1.5, 3.5, 6.5, 0.2, 1.2, 3.5],
	130: [18, 18.2, 19.6, 23, 31, 18.7, 21, 27.5],
	90: [-19, -18.5, -18, -18.4, -17.4, -16.5, -19.4, -19.6, -19.5],
	70: [-32, -31.7, -31.6, -32, -32.5, -33, -34, -35.5]
	}

	tilts = []
	pans = []
	angles = []
	tangles = []

	for tilt in tilt_positions:
		angs = []
		for index, pan in enumerate(pan_positions):
			h = heights[tilt][index]
			dist = dp(pan, laser_pan_c)
			ang = calc_angle(h, dist)
			angs.append(int(ang))
			angles.append(ang)
			pans.append(pan)
			tilts.append(tilt)
		tangles.append(angs)

	xs = []
	xs.append(pans)
	xs.append(tilts)

	x = scipy.array(xs)
	y = scipy.array(angles)

	popt, pcov = curve_fit(laser_tilt_fn, x, y)
	a,b,c,d,e,f,g = popt
	laser_tilt_c = {'a': a, 'b': b, 'c': c, 'd': d, 'e': e, 'f': f, 'g': g}

	# separator()
	# print("Calibrating Left Eye Pan".upper())

	distances = [-26.7, -20.6, -14.4, -12, -9.5, -6.3, -4.0, 2.5, 7.8, 14.0, 21.8]
	angles = []
	positions = [572, 552, 532, 522, 512, 502, 492, 472, 452, 432, 412]
	for d in distances:
		ang = calc_angle(d)
		angles.append(ang)
		# print("Distance from origin: %s, Angle: %s", (d, ang))

	lpan_c = compute_coeff(distances, angles, positions)

	# separator()
	# print("Calibrating Right Eye Pan".upper())

	distances = [-17.7, -8.2, -1.6, 4.3, 7, 9.5, 12, 18, 23.5]
	angles = []
	positions = [592, 562, 542, 522, 512, 502, 492, 472, 452]
	for d in distances:
		ang = calc_angle(d)
		angles.append(ang)
		# print("Distance from origin: %s, Angle: %s", (d, ang))

	rpan_c = compute_coeff(distances, angles, positions)

	# separator()
	# print("Calibrating Left Eye Tilt".upper())

	distances = [16.2, 10, 4.8, 1.4, -1.5, -7, -10, -13]
	angles = []
	positions = [462, 482, 502, 512, 522, 542, 552, 562]
	for d in distances:
		d = d - 1.4
		ang = calc_angle(d)
		angles.append(ang)
		# print("Distance from origin: %s, Angle: %s", (d, ang))

	ltilt_c = compute_coeff(distances, angles, positions)

	# separator()
	# print("Calibrating Right Eye Tilt".upper())

	distances = [15.8, 10, 4.6, 1.4, -2.5, -7.5, -10.5, -12.5]
	angles = []
	positions = [462, 482, 502, 512, 522, 542, 552, 562]
	for d in distances:
		d = d - 1.4
		ang = calc_angle(d)
		angles.append(ang)
		# print("Distance from origin: %s, Angle: %s", (d, ang))

	rtilt_c = compute_coeff(distances, angles, positions)

	# separator()
	# print("Calibrating Neck Pan".upper())

	distances = [-30, -18.5, -10, -4.5, 0, 6, 13, 21, 30]
	angles = []
	positions = [622, 582, 552, 532, 512, 492, 462, 432, 402]
	for d in distances:
		ang = calc_angle(d)
		angles.append(ang)
		# print("Distance from origin: %s, Angle: %s", (d, ang))

	npan_c = compute_coeff(distances, angles, positions)

	# separator()
	# print("Calibrating Neck Tilt".upper())

	distances = [-28, -19, -10.5, -6.5, -3.5, 7.5]
	angles = []
	positions = [482, 512, 542, 562, 582, 612]
	for d in distances:
		d = d + 19 # Neck tilt offset
		ang = calc_angle(d)
		angles.append(ang)
		# print("Distance from origin: %s, Angle: %s", (d, ang))

	ntilt_c = compute_coeff(distances, angles, positions)

	# separator()

	return laser_pan_c, laser_tilt_c, lpan_c, ltilt_c, rpan_c, rtilt_c, npan_c, ntilt_c