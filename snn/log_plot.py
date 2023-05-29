import matplotlib.pyplot as plt

x = range(720)
def input_(xval):
  from math import log, sqrt
  max_w = log(1 + 360/288)
  #return 7.7 * log(xval + sqrt(-1) * yval + 0.33)
  if(xval > 360):
    w = log(1 + (720-xval)/288.0)
  else:
    w = log(1 + (xval)/288.0)
  return w / max_w#, (0.23 + (w) * (0.85 / 5.662960480135946))


# def gauss(xval):
# 	from math import exp, sqrt, pi, log
# 	return 0.23 + log(exp(-0.5 * ((xval-360)/50)**2) / (sqrt(2 * pi) * 50))

w = []
#y = range(720)
y = []
for i in x:
	#r = []
	#for j in y:
	#	r.append(input_(i,j))
	#w.append(r)
	a = input_(i)
	w.append(a)
	#y.append(b)

	# y.append(1/gauss(i))

print(w)
print(min(w))
print(max(w))

plt.figure()
plt.plot(x, w)
#plt.figure()
#plt.plot(x, w)
plt.show()
