import sys
from vintageHelpers import *
import seaborn
import numpy as np
from matplotlib import pyplot as plt
import matplotlib
from pyomoVintageMin import getConstraints, getVars




# use this file to create the capital and generation values to export in CSV
f = open("mc.txt", "r")
lastCount = int(f.read())
f.close()

GList, FlList, FhList, mlList, mhList, period, H0, L0, alpha, r, nh, nl, betah, betal = genData(lastCount)




currentFile = "VintResults/simpleResult.json"
H, L = getInvestments(currentFile, period)

constraintDict = getConstraints()
varDict = getVars()

print varDict


Kh = []
Kl = []
for i in range(period):
	KhVint = []
	KlVint = []
	for t in range(period):
		try:
			KhVint.append(constraintDict["KhNonNeg"+str(i)+"-"+str(t)])
		except KeyError:
			KhVint.append(0)

		try:
			KlVint.append(constraintDict["KlNonNeg"+str(i)+"-"+str(t)])
		except KeyError:
			KlVint.append(0)

	Kh.append(KhVint)
	Kl.append(KlVint)




# generate matplotlib plot for investment
fig = plt.figure(figsize=(10, 7), dpi=100, facecolor='w', edgecolor='k')
fig.subplots_adjust(hspace=0.5)

ax1 = fig.add_subplot(2,2,1)
ax2 = fig.add_subplot(2,2,2)
ax3 = fig.add_subplot(2,2,3)
ax4 = fig.add_subplot(2,2,4)


# plot the data
for i in range(period):
	dateRange = range(i, len(H))
	ax1.plot(dateRange, H[i], label= "H Vintage: "+str(i))
	ax3.plot(dateRange, L[i], label= "L Vintage: "+str(i))

years = range(period)
ax2.stackplot(years, Kh)
ax4.stackplot(years, Kl)



# labels
ax1.set_xlabel('Years of Simulation')
ax1.set_ylabel('Investment ($)')
ax1.set_title("High Emitting Investments")

ax2.set_xlabel('Years of Simulation')
ax2.set_ylabel('Capital ($)')
ax2.set_title("High Emitting Capital")
		
ax3.set_xlabel('Years of Simulation')
ax3.set_ylabel('Capital ($)')
ax3.set_title("Low Emitting Investments")

ax4.set_xlabel('Years of Simulation')
ax4.set_ylabel('Capital ($)')
ax4.set_title("Low Emitting Capital")

plt.show()

totalKh = []
totalKl = []
totalGh = []
totalGl = []

for t in range(period):
	totalKhInst = sum([Kh[i][t] for i in range(len(Kh[i]))])
	totalKlInst = sum([Kl[i][t] for i in range(len(Kl[i]))])
	totalKh.append(totalKhInst)
	totalKl.append(totalKlInst)

	totalGhInst = sum([FhList[i] * Kh[i][t] for i in range(len(Kh[i]))])
	totalGlInst = sum([FlList[i] * Kl[i][t] for i in range(len(Kl[i]))])
	totalGh.append(totalGhInst)
	totalGl.append(totalGlInst)


fig = plt.figure(figsize=(10, 7), dpi=100, facecolor='w', edgecolor='k')
fig.subplots_adjust(hspace=0.5)

ax1 = fig.add_subplot(1,2,1)
ax2 = fig.add_subplot(1,2,2)

ax1.stackplot(range(period), totalKh, totalKl)
ax2.stackplot(range(period), totalGh, totalGl)

ax1.set_xlabel('Years of Simulation')
ax1.set_ylabel('Total Capital ($)')
ax1.set_title("Total Capital")

ax2.set_title("Total Generating Capacity")
ax2.set_xlabel('Years of Simulation')
ax2.set_ylabel('Billion kWh/year')


plt.show()


########################################




#		currentFile = "VintResults/constraints_"+str(count)+".txt"
#		kh, kl = getCapital(currentFile)		

#		font = {'size'   : 10}
#		matplotlib.rc('font', **font)

#		kh = [float(i) for i in kh]
#		kl = [float(i) for i in kl]
#		totalk = [kh[i]+kl[i] for i in range(len(kh))]
#		frach = [kh[i]/totalk[i] for i in range(len(kh))]
#		fracl = [kl[i]/totalk[i] for i in range(len(kl))]

#		dateRange = range(1, len(H)+1)

#		genH = [kh[i]*FhList[i+1] for i in range(len(kh))]
#		genL = [kl[i]*FlList[i+1] for i in range(len(kl))]



		# generate matplotlib plot for investment
#		fig = plt.figure(figsize=(10, 7), dpi=100, facecolor='w', edgecolor='k')

#		ax1 = fig.add_subplot(2,2,1)
		# plot the data
#		ax1.plot(dateRange, H, label= "Dirty Capital Invesment")
#		ax1.plot(dateRange, L, label= "Clean Capital Investment")

		# labels
#		ax1.set_xlabel('Years of Simulation')
#		ax1.set_ylabel('Investment ($)')
#		ax1.set_title("Investment")


		# generate matplotlib plot for investment
#		ax2 = fig.add_subplot(2,2,3)
		# plot the data
#		ax2.plot(dateRange, kh, label= "Dirty Capital Stock")
#		ax2.plot(dateRange, kl, label= "Clean Capital Stock")

		# labels
#		ax2.set_xlabel('Years of Simulation')
#		ax2.set_ylabel('Investment ($)')
#		ax2.set_title("$ of Capital")
#		plt.legend(loc = 0)
		
#		fig.subplots_adjust(hspace=0.5)

#		ax3 = fig.add_subplot(2,2,2)
#		ax3.stackplot(dateRange, frach, fracl)
#		ax3.set_title("Fractional Capital")
#		ax3.set_xlabel('Years of Simulation')
#		ax3.set_ylabel('Fraction of Capital')

#		ax4 = fig.add_subplot(2,2,4)
#		ax4.stackplot(dateRange, genH, genL)
#		ax4.set_title("Total Generating Capacity")
#		ax4.set_xlabel('Years of Simulation')
#		ax4.set_ylabel('Billion kWh/year')



#		plt.savefig('FlResults/cap_and_invest_results_Fl_' + str(count) + '.png', bbox_inches='tight')
#		plt.close()


#		print "done with model "+str(count)
#		count += 1

#	except IOError: 
#		stillRunning = False
#	except:
#		stillRunning = False
#		print sys.exc_info()


#cost = []
#for i in range(1, count):
#	cost.append(getOptimalCost("FlResults/simpleResult_"+str(i)+".json"))

#plt.plot(range(1,count), cost)
#plt.xlabel("Speed of Transition")
#plt.ylabel("Net Present Value Cost - $")
#plt.title("Cost of Transition as a Function of Transition Speed")
#plt.savefig('FlResults/cost_as_func_of_Fl_emissions_' + str(alpha) + '.png', bbox_inches='tight')
#plt.close()







