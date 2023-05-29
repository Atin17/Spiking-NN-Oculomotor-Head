import numpy as np
import matplotlib.pyplot as plt
import os


LColors = {
	0: '#DE000D',
	1: '#C70E20',
	2: '#EF1B30',
	3: '#FF0000'
}

RColors = {
	0: '#FF0000',
	1: '#EF1B30',
	2: '#C70E20',
	3: '#DE000D'	
}

def raster(event_times_list, colors, **kwargs):
    """
    Creates a raster plot
    Parameters
    ----------
    event_times_list : iterable
                       a list of event time iterables
    color : string
            color of vlines
    Returns
    -------
    ax : an axis containing the raster plot
    """
    ax = plt.gca()
    for ith, trial in enumerate(event_times_list):
        plt.vlines(trial, ith + 0.8, ith + 1.2, color=colors[ith], linewidth=2, **kwargs)
    # plt.ylim(.5, len(event_times_list) + .25)
    return ax

nbins = 4
dirList = os.listdir("/Users/praveen/projects/robot-control-c/out/Left")
nFrames = len(dirList) - 1
print(nFrames)
nFrames = 10
ntrials = 30 * nFrames

lupr = []
ldownr = []
lleftr = []
lrightr = []
rupr = []
rdownr = []
rleftr = []
rrightr = []

for index in range(nFrames):
	lup = open("/Users/praveen/projects/robot-control-c/out/Left/%d/up.dat" % index, 'r')
	ldown = open("/Users/praveen/projects/robot-control-c/out/Left/%d/down.dat" % index, 'r')
	lleft = open("/Users/praveen/projects/robot-control-c/out/Left/%d/left.dat" % index, 'r')
	lright = open("/Users/praveen/projects/robot-control-c/out/Left/%d/right.dat" % index, 'r')

	rup = open("/Users/praveen/projects/robot-control-c/out/Right/%d/up.dat" % index, 'r')
	rdown = open("/Users/praveen/projects/robot-control-c/out/Right/%d/down.dat" % index, 'r')
	rleft = open("/Users/praveen/projects/robot-control-c/out/Right/%d/left.dat" % index, 'r')
	rright = open("/Users/praveen/projects/robot-control-c/out/Right/%d/right.dat" % index, 'r')

	tmp_lupr = [int(x.replace('\n', '')) for x in lup.readlines() if (x != '' and x != ' ' and x != '\n')]
	tmp_ldownr = [int(x.replace('\n', '')) for x in ldown.readlines() if (x != '' and x != ' ' and x != '\n')]
	tmp_lleftr = [int(x.replace('\n', '')) for x in lleft.readlines() if (x != '' and x != ' ' and x != '\n')]
	tmp_lrightr = [int(x.replace('\n', '')) for x in lright.readlines() if (x != '' and x != ' ' and x != '\n')]
	tmp_rupr = [int(x.replace('\n', '')) for x in rup.readlines() if (x != '' and x != ' ' and x != '\n')]
	tmp_rdownr = [int(x.replace('\n', '')) for x in rdown.readlines() if (x != '' and x != ' ' and x != '\n')]
	tmp_rleftr = [int(x.replace('\n', '')) for x in rleft.readlines() if (x != '' and x != ' ' and x != '\n')]
	tmp_rrightr = [int(x.replace('\n', '')) for x in rright.readlines() if (x != '' and x != ' ' and x != '\n')]

	lupr.extend(tmp_lupr)
	ldownr.extend(tmp_ldownr)
	lleftr.extend(tmp_lleftr)
	lrightr.extend(tmp_lrightr)

	rupr.extend(tmp_rupr)
	rdownr.extend(tmp_rdownr)
	rleftr.extend(tmp_rleftr)
	rrightr.extend(tmp_rrightr)

	lup.close()
	ldown.close()
	lleft.close()
	lright.close()
	rup.close()
	rdown.close()
	rleft.close()
	rright.close()

rasterL = []
rasterR = []

rasterL.append(np.arange(ntrials)[np.array(lupr) == 1])
rasterL.append(np.arange(ntrials)[np.array(ldownr) == 1])
rasterL.append(np.arange(ntrials)[np.array(lleftr) == 1])
rasterL.append(np.arange(ntrials)[np.array(lrightr) == 1])

rasterR.append(np.arange(ntrials)[np.array(rupr) == 1])
rasterR.append(np.arange(ntrials)[np.array(rdownr) == 1])
rasterR.append(np.arange(ntrials)[np.array(rleftr) == 1])
rasterR.append(np.arange(ntrials)[np.array(rrightr) == 1])

fig = plt.figure()
ax = raster(rasterL, LColors)
ax.set_xlim([0, 5])
ax.set_ylim([0, 5])
# plt.yticks(np.linspace(0,0,0))
plt.yticks(np.linspace(0,5,6, endpoint=True))
#plt.setp(ax, linewidth=2)
# plt.title('Spiking Pattern - Oculo Motor Neurons - Left Eye')
# plt.xlabel('Time (ms)')
# plt.ylabel('OC Neuron')

fig2 = plt.figure()
ax2 = raster(rasterR, RColors)
ax2.set_xlim([0, 5])
ax2.set_ylim([0, 5])
plt.yticks(np.linspace(0,5,6, endpoint=True))
#plt.setp(ax2, linewidth=2)
# plt.title('Spiking Pattern - Oculo Motor Neurons - Right Eye')
# plt.xlabel('Time (ms)')
# plt.ylabel('OC Neuron')

plt.show()
