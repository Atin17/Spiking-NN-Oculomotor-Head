import matplotlib.pyplot as plt

folder = 'tmp'
# files = ['mn_r', 'inp_mn_r']
files = ['mn_rr', 'inp_r_mn_rr']

def input_from(filename):
    f = open(folder + "/" + filename)
    return [float(x.replace('\n','')) for x in f.readlines()]

fig1 = plt.figure()
fig1.suptitle('Membrane potentials and current')
index = 1
for filename in files:
    data = input_from(filename)
    plt.subplot(len(files), 1, index)
    plt.title(filename)
    plt.xlabel('ms')
    line, = plt.plot(data)
    index += 1

plt.show()
