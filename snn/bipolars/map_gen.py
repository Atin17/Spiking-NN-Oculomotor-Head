#!/bin/python3


import jsonpickle


def abcd(start_left, start_right, start_top, start_bottom, divisor):
    neurons = []
    width = (start_right - start_left)
    height = (start_bottom - start_top)
    print("Width: %d, Height: %d, Divisor: %d" % (width, height, divisor))
    side = int(height/divisor)
    index = -1
    for col in range(start_left, start_right):
        if (col - start_left) % (side) == 0:
            # rethink the need for x,y
            neurons.append({'x': int(start_top + side/2), 'y': int(col + side/2), 'field': []})
            index += 1
        for row in range(start_top, start_top + (side)):
            neurons[index]['field'].append("%d,%d" % (row, col))
    
    for col in range(start_left, start_right):
        if (col - start_left) % (side) == 0:
            neurons.append({'x': int(start_bottom - side/2), 'y': int(col + side/2), 'field': []})
            index += 1
        for row in range(start_bottom-1, start_bottom - (side) - 1, -1):
            neurons[index]['field'].append("%d,%d" % (row, col))
    
    for row in range(start_top + side, start_bottom - (side)):
        if (row - start_top) % (side) == 0:
            neurons.append({'x': int(row + side/2), 'y': int(start_left + side/2), 'field': []})
            index += 1
        for col in range(start_left, start_left + (side)):
            neurons[index]['field'].append("%d,%d" % (row, col))
    
    for row in range(start_top + (side), start_bottom - (side)):
        if (row - start_top) % (side) == 0:
            neurons.append({'x': int(row + side/2), 'y':int(start_right - side/2), 'field': []})
            index += 1
        for col in range(start_right-1, start_right - (side) - 1, -1):
            neurons[index]['field'].append("%d,%d" %(row, col))
    return neurons


#left,right,top,bottom,split
l1 = abcd(0, 720, 0, 720, 5)
l2 = abcd(144,576,144,576,4)
l3 = abcd(252,468,252,468,4)
l4 = abcd(306,414,306,414,4)
l5 = abcd(333,387,333,387,6)
l6 = abcd(342,378,342,378,4)
l7 = abcd(351,369,351,369,6)
l8 = abcd(354,366,354,366,6)
#l9 = abcd(356,364,356,364,8)

l9 = []
for row in range(356, 364):
    for col in range(356, 364):
        l9.append({'x': row, 'y': col, 'field': ["%d,%d" % (row, col)]})


print(len(l1))
print(len(l2))
print(len(l3))
print(len(l4))
print(len(l5))
print(len(l6))
print(len(l7))
print(len(l8))
print(len(l9))


bipolars = []
bipolars.append(l1)
bipolars.append(l2)
bipolars.append(l3)
bipolars.append(l4)
bipolars.append(l5)
bipolars.append(l6)
bipolars.append(l7)
bipolars.append(l8)
bipolars.append(l9)

json_string = jsonpickle.encode(bipolars)

f = open('simple_map.json', 'w')
f.write(json_string)

