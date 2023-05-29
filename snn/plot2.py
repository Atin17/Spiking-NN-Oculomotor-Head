import matplotlib.pyplot as plt
import numpy as np
import os
import math


dirList = os.listdir("/Users/praveen/projects/robot-control-c/out/Left")
nFrames = len(dirList) - 1
print(nFrames)
panL = [360]
tiltL = [360]
panR = [360]
tiltR = [360]

'''
for index in range(nFrames):
	lpanF = open("/Users/praveen/projects/robot-control-c/out/Left/%d/pan.dat" % index, 'r')
	ltiltF = open("/Users/praveen/projects/robot-control-c/out/Left/%d/tilt.dat" % index, 'r')
	rpanF = open("/Users/praveen/projects/robot-control-c/out/Right/%d/pan.dat" % index, 'r')
	rtiltF = open("/Users/praveen/projects/robot-control-c/out/Right/%d/tilt.dat" % index, 'r')

	ltmp_pan = [int(x.replace('\n', '')) for x in lpanF.readlines() if (x != '' and x != ' ' and x != '\n')]
	ltmp_tilt = [int(x.replace('\n', '')) for x in ltiltF.readlines() if (x != '' and x != ' ' and x != '\n')]

	rtmp_pan = [int(x.replace('\n', '')) for x in rpanF.readlines() if (x != '' and x != ' ' and x != '\n')]
	rtmp_tilt = [int(x.replace('\n', '')) for x in rtiltF.readlines() if (x != '' and x != ' ' and x != '\n')]

	# Adjust for relative movement directions of motors
	if(ltmp_pan[0] >= 512):
		ltmp_pan[0] = 512 - (ltmp_pan[0] - 512)
	else:
		ltmp_pan[0] = 512 + (512 - ltmp_pan[0])
	
	if(ltmp_tilt[0] <= 512):
		ltmp_tilt[0] = 512 + (512 - ltmp_tilt[0])
	else:
		ltmp_tilt[0] = 512 - (ltmp_tilt[0] - 512)
	
	if(rtmp_pan[0] >= 512):
		rtmp_pan[0] = 512 - (rtmp_pan[0] - 512)
	else:
		rtmp_pan[0] = 512 + (512 - rtmp_pan[0])
	
	if(rtmp_tilt[0] <= 512):
		rtmp_tilt[0] = 512 + (512 - rtmp_tilt[0])
	else:
		rtmp_tilt[0] = 512 - (rtmp_tilt[0] - 512)

	panL.extend(ltmp_pan)
	tiltL.extend(ltmp_tilt)
	panR.extend(rtmp_pan)
	tiltR.extend(rtmp_tilt)

	lpanF.close()
	ltiltF.close()
	rpanF.close()
	rtiltF.close()
'''

lpan = []
ltilt = []
rpan = []
rtilt = []

for index in range(nFrames):
	left = open("/Users/praveen/projects/robot-control-c/out/Left/%d/laser_position.dat" % index, 'r')
	right = open("/Users/praveen/projects/robot-control-c/out/Right/%d/laser_position.dat" % index, 'r')

	tmp_lpan = [x.replace('\n', '') for x in left.readlines() if (x != '' and x != ' ' and x != '\n')]
	tmp_lpan = [int(y) for y in tmp_lpan[0].split(',')]
	tmp_rpan = [x.replace('\n', '') for x in right.readlines() if (x != '' and x != ' ' and x != '\n')]
	tmp_rpan = [int(y) for y in tmp_rpan[0].split(',')]

	# Adjust for relative movement directions of motors
	# if(tmp_lpan[0] >= 360):
	# 	tmp_lpan[0] = 360 - (tmp_lpan[0] - 360)
	# else:
	# 	tmp_lpan[0] = 360 + (360 - tmp_lpan[0])
	
	if(tmp_lpan[1] <= 360):
		tmp_lpan[1] = 360 + (360 - tmp_lpan[1])
	else:
		tmp_lpan[1] = 360 - (tmp_lpan[1] - 360)
	
	# if(tmp_rpan[0] >= 360):
	# 	tmp_rpan[0] = 360 - (tmp_rpan[0] - 360)
	# else:
	# 	tmp_rpan[0] = 360 + (360 - tmp_rpan[0])
	
	if(tmp_rpan[1] <= 360):
		tmp_rpan[1] = 360 + (360 - tmp_rpan[1])
	else:
		tmp_rpan[1] = 360 - (tmp_rpan[1] - 360)

	lpan.append(tmp_lpan[0])
	ltilt.append(tmp_lpan[1])
	rpan.append(tmp_rpan[0])
	rtilt.append(tmp_rpan[1])

	left.close()
	right.close()

fig = plt.figure()
ax = fig.add_subplot(111)
line, = ax.plot(lpan, ltilt, 'bs-')
ax.set_xlim([0, 719])
ax.set_ylim([0, 719])
plt.title('Path To Target - Left Eye')
plt.xlabel('Frame Width (pixels)')
plt.ylabel('Frame Height(pixels)')


fig2 = plt.figure()
ax2 = fig2.add_subplot(111)
line2, = ax2.plot(rpan, rtilt, 'bs-')
ax2.set_xlim([0, 719])
ax2.set_ylim([0, 719])
plt.title('Path To Target - Right Eye')
plt.xlabel('Frame Width (pixels)')
plt.ylabel('Frame Height (pixels)')

plt.show()
