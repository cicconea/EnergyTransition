import sys
from helpers import *
import seaborn
import numpy as np
from matplotlib import pyplot as plt
import matplotlib




# use this file to create the capital and generation values to export in CSV
count = 1
stillRunning = True

GList, FlList, FhList, mlList, mhList, period, H0, L0, r, n = genDataA()

while stillRunning == True:
	try:
		currentFile = "alphaResults/simpleResult_"+str(count)+".json"
		H, L = getInvestments(currentFile, period)

		currentFile = "alphaResults/constraints_"+str(count)+".txt"
		kh, kl = getCapital(currentFile)		

		font = {'size'   : 10}
		matplotlib.rc('font', **font)

		kh = [float(i) for i in kh]
		kl = [float(i) for i in kl]
		totalk = [kh[i]+kl[i] for i in range(len(kh))]
		frach = [kh[i]/totalk[i] for i in range(len(kh))]
		fracl = [kl[i]/totalk[i] for i in range(len(kl))]

		dateRange = range(1, len(H)+1)

		genH = [kh[i]*FhList[i+1] for i in range(len(kh))]
		genL = [kl[i]*FlList[i+1] for i in range(len(kl))]



		# generate matplotlib plot for investment
		fig = plt.figure(figsize=(10, 7), dpi=100, facecolor='w', edgecolor='k')

		ax1 = fig.add_subplot(2,2,1)
		# plot the data
		ax1.plot(dateRange, H, label= "Dirty Capital Invesment")
		ax1.plot(dateRange, L, label= "Clean Capital Investment")

		# labels
		ax1.set_xlabel('Years of Simulation')
		ax1.set_ylabel('Investment ($)')
		ax1.set_title("Investment")


		# generate matplotlib plot for investment
		ax2 = fig.add_subplot(2,2,3)
		# plot the data
		ax2.plot(dateRange, kh, label= "Dirty Capital Stock")
		ax2.plot(dateRange, kl, label= "Clean Capital Stock")

		# labels
		ax2.set_xlabel('Years of Simulation')
		ax2.set_ylabel('Investment ($)')
		ax2.set_title("$ of Capital")
		plt.legend(loc = 0)
		
		fig.subplots_adjust(hspace=0.5)

		ax3 = fig.add_subplot(2,2,2)
		ax3.stackplot(dateRange, frach, fracl)
		ax3.set_title("Fractional Capital")
		ax3.set_xlabel('Years of Simulation')
		ax3.set_ylabel('Fraction of Capital')

		ax4 = fig.add_subplot(2,2,4)
		ax4.stackplot(dateRange, genH, genL)
		ax4.set_title("Total Generating Capacity")
		ax4.set_xlabel('Years of Simulation')
		ax4.set_ylabel('Billion kWh/year')



		plt.savefig('alphaResults/cap_and_invest_results_' + str(count) + '.png', bbox_inches='tight')
		plt.close()


		print "done with model "+str(count)
		count += 1

	except IOError: 
		stillRunning = False
	except:
		stillRunning = False
		print sys.exc_info()


cost = []
for i in range(1, count):
	cost.append(getOptimalCost("alphaResults/simpleResult_"+str(i)+".json"))

plt.plot(range(1,count), cost)
plt.xlabel("Percent Emissions of Business as Usual")
plt.ylabel("Net Present Value Cost - $")
plt.title("Cost of Transition as a Function of Emission Reduction")
plt.savefig('alphaResults/cost_as_func_of_Alpha.png', bbox_inches='tight')
plt.close()







