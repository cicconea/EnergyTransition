import sys
from helpers import *
import seaborn
import numpy as np
from matplotlib import pyplot as plt
import matplotlib
from pyomoVintageMin import vintageModel



for alpha in range(1,101,10):
	for i in range(1,101,10):
		GList, FlList, FhList, mlList, mhList, period, H0, L0, r, nh, nl, betah, betal = genDataVint(i)

		print i, alpha
		model = vintageModel(alpha,i)
		instance = modelSolve(model)
		constraintDict = getConstraints(instance)
		varDict = getVars(instance)


		H = []
		L = []
		for i in range(period):
			Htemp = []
			Ltemp = []
			for t in range(period):
				if t == i:
					Htemp.append(varDict["Hp"+str(i)][0])
					Ltemp.append(varDict["Lp"+str(i)][0])
				elif t > i:
					Htemp.append(varDict["Hn"+str(i)][t])
					Ltemp.append(varDict["Ln"+str(i)][t])
			H.append(Htemp)
			L.append(Ltemp)


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
			dateRange = range(i, len(H[0]))
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



#cost = []
#for i in range(1, count):
#	cost.append(getOptimalCost("FlResults/simpleResult_"+str(i)+".json"))

#plt.plot(range(1,count), cost)
#plt.xlabel("Speed of Transition")
#plt.ylabel("Net Present Value Cost - $")
#plt.title("Cost of Transition as a Function of Transition Speed")
#plt.savefig('FlResults/cost_as_func_of_Fl_emissions_' + str(alpha) + '.png', bbox_inches='tight')
#plt.close()







