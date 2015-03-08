import matplotlib.pyplot as plt
import seaborn as sns
import csv
import pandas as pd
import numpy as np


period = 50

investmentTrajectories = pd.DataFrame.from_csv('Period50_MC10000_Random_Fl_Output.csv', header=0, sep=',', index_col=None)

#plt.scatter(investmentTrajectories["FlScale"], investmentTrajectories["minCost"])
#plt.title("Cost as Function of Transition Speed - Low-Intensity Efficiency")
#plt.ylabel("Optimized Minimum Cost")
#plt.xlabel("Low-Intensity Efficiency Scale")

#plt.show()


# Bin the data frame by "a" with 10 bins...
bins = np.linspace(investmentTrajectories["FlScale"].min(), investmentTrajectories["FlScale"].max(), 10)
groups = investmentTrajectories.groupby(np.digitize(investmentTrajectories["FlScale"], bins))

# Get the mean of each bin and store as numpy array
meanArray = groups.mean().values

# header = genericHeader + HpHeader + HnHeader + LpHeader + LnHeader
# genericHeader = ["FlScale", "FhScale", "elScale", "ehScale", "minCost", "solved"]

np.set_printoptions(threshold='nan')



Array = []
plottingArray = np.ndarray((10, 101)) # initializes nonempty array. We truncate later for no good reason
for i in range(len(meanArray)):
	line = np.array([meanArray[i,0]])
	for j in range(6, period+6):
		Hval = meanArray[i,j] + meanArray[i, 1*period +j]
		line = np.append(line, Hval)

	for j in range(6, period+6):
		Lval = meanArray[i,2*period +j] + meanArray[i, 3*period +j]
		line = np.append(line, Lval)

	plottingArray = np.append(plottingArray, [line], axis = 0)

plottingArray = plottingArray[10:, :] # bad, but whatevs

#for i in range(len(plottingArray)):
#	print i
#	print len(plottingArray[i, 1:51])
#	print len(plottingArray[i,51:])
#	print 

xRange = range(period)

for i in range(len(plottingArray)):
	plt.plot(xRange, plottingArray[i, 1:51],  label = plottingArray[i,0])
	plt.plot(xRange, -plottingArray[i, 51:], label = plottingArray[i,0])



plt.title("Investments by Speed of Low-Intensity Efficiency Improvement")
plt.ylabel("Investment Amounts")
plt.xlabel("Low-Intensity Efficiency Scale (Higher Values Indicate Slower Transition")
plt.legend(loc = 0)

plt.show()











