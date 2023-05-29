#!/bin/python3

import jsonpickle

f = open('simple_map.json', 'r')
json_string = ''.join(f.readlines())

json = jsonpickle.decode(json_string)

arr = []
for i in range(720):
	a = []
	for j in range(720):
		a.append(1)
	arr.append(a)

inverse_map = {}

index = 0

for i in range(len(json)):
	zone = json[i]
	for j in range(len(zone)):
		nrn = zone[j]
		for xy in nrn['field']:
			x = int(xy.split(',')[0])
			y = int(xy.split(',')[1])
			try:
				arr[x][y] = 0
			except:
				print(x)
				print(y)
				raise
			if(inverse_map.get(xy) is not None):
				print("Multiple indexes for this pixel: %s" % xy)
				inverse_map[xy].append(index)
			else:
				inverse_map[xy] = [index]
		index += 1

of = open('simple_map.json.inverse', 'w')
of.write(jsonpickle.encode(inverse_map))

for i in range(720):
	for j in range(720):
		if(arr[i][j] == 1):
			print('%d,%d' % (i, j))

of.close()
f.close()
