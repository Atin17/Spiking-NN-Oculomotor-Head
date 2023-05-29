import math
import numpy as np

d_wall = 55.3

def calc_angle(D, dist=None):
    global d_wall
    if dist is None:
        val = D/d_wall
    else:
        val = D/dist
    return math.degrees(math.atan(val))

def dp(pan):
    global d_wall
    global laser_pan_c
    return d_wall / math.cos(laser_pan_c(pan) * math.pi / 90)

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

# laser pan calib
distances = [-26, -17.8, -9.5, 0, 7.0, 12, 24.8]
angles = []
positions = [122, 112, 101, 84, 75, 65, 50]
# print("Angles for distances")
for d in distances:
    ang = calc_angle(d)
    angles.append(ang)
    # print("Distance from origin: %s, Angle: %s" % (d, ang))

laser_pan_c = compute_coeff(distances, angles, positions)

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
        dist = dp(pan)
        ang = calc_angle(h, dist)
        angs.append(int(ang))
        angles.append(ang)
        pans.append(pan)
        tilts.append(tilt)
    tangles.append(angs)

print(tangles)

from scipy.optimize import curve_fit
import scipy

def fn(x, a, b, c, d, e, f, g):
    return a + b * x[0] + c * (x[0]**2) + d * (x[0]**3) + e * x[1] + f * (x[1] ** 2) + g * (x[1]**3)

xs = []
xs.append(pans)
xs.append(tilts)

x = scipy.array(xs)
y = scipy.array(angles)

popt, pcov = curve_fit(fn, x, y)
a,b,c,d,e,f,g = popt

t = [84, 114]
print(fn(t, a, b, c, d, e, f, g))
t = [115, 114]
print(fn(t, a, b, c, d, e, f, g))
t = [90, 90]
print(fn(t, a, b, c, d, e, f, g))
t = [120, 70]
print(fn(t, a, b, c, d, e, f, g))

import matplotlib.pyplot as plt

fig = plt.figure()
xr = range(50, 130)
for tilt in range(70, 130):
    vals = []
    for x in xr:
        vals.append(fn([x, tilt], a, b, c, d, e, f, g))
    plt.plot(xr, vals)
plt.show()
