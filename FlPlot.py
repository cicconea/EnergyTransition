from helpers import *
import seaborn
from matplotlib import pyplot as plt


fig = plt.figure(figsize=(10, 7), dpi=100, facecolor='w', edgecolor='k')

for i in range(5):
	for j in range(25, 101, 25):
		print i, j
		GList, FlList, FhList, mlList, mhList, period, H0, L0, r, nh, nl, betah, betal = genDataVint(i,float(j)/100.0)
		plt.plot(FlList)




plt.plot(FhList, label = "High Emitting Cost")



plt.xlabel("Length of Simulation")
plt.ylabel("kWh per year per dollar")
plt.title("Simulation of Low-Emitting Capital Costs")
plt.legend(loc=0)

plt.show()
plt.close()