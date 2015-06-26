import sys
from helpers import *
import seaborn
import numpy as np
from matplotlib import pyplot as plt
import matplotlib
from pyomoVintageMin import vintageModel
from pyomo.core.base import objective


alphaRange = range(25, 76, 25) # % emissions reduction
countRange = [5, 10, 15] # scale of transition
FlMaxRange = range(50, 101, 50) # % of max emissions can't be lower that 25%


for alpha in alphaRange:
	alpha = alpha/100.0
	for count in countRange:
		for FlMax in FlMaxRange:
			FlMax = FlMax/100.0
			print "Vintage ", count, alpha, FlMax

			GList, FlList, FhList, mlList, mhList, period, H0, L0, r, nh, nl, betah, betal = genDataVint(count, FlMax)
			


			model = vintageModel(alpha, count, FlMax)
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
						Htemp.append(-varDict["Hn"+str(i)][t])
						Ltemp.append(-varDict["Ln"+str(i)][t])
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
			fig = plt.figure(figsize=(15, 10), dpi=100, facecolor='w', edgecolor='k')
			fig.subplots_adjust(hspace=0.5)

			ax1 = fig.add_subplot(2,3,1)
			ax2 = fig.add_subplot(2,3,2)
			ax3 = fig.add_subplot(2,3,3)
			ax4 = fig.add_subplot(2,3,4)
			ax5 = fig.add_subplot(2,3,5)
			ax6 = fig.add_subplot(2,3,6)

			# plot the data
			for i in range(period):
				dateRange = range(i, len(H[0]))
				ax1.plot(dateRange, H[i], label= "H Vintage: "+str(i))
				ax4.plot(dateRange, L[i], label= "L Vintage: "+str(i))

			years = range(period)
			ax2.stackplot(years, Kh)
			ax5.stackplot(years, Kl)



			# labels
			ax1.set_xlabel('Years of Simulation')
			ax1.set_ylabel('Investment ($)')
			ax1.set_title("High Emitting Investments")

			ax2.set_xlabel('Years of Simulation')
			ax2.set_ylabel('Capital ($)')
			ax2.set_title("High Emitting Capital")
					
			ax4.set_xlabel('Years of Simulation')
			ax4.set_ylabel('Capital ($)')
			ax4.set_title("Low Emitting Investments")

			ax5.set_xlabel('Years of Simulation')
			ax5.set_ylabel('Capital ($)')
			ax5.set_title("Low Emitting Capital")


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



			ax3.plot(range(period), totalKh, label = "High Emitting Capital")
			ax3.plot(range(period), totalKl, label = "Low Emitting Capital")

			ax6.stackplot(range(period), totalGh, totalGl)
			#ax3.plot(range(period), FhList, label = "High Emitting Cost")
			#ax3.plot(range(period), FlList, label = "Low Emitting Cost")

			ax3.set_xlabel('Years of Simulation')
			ax3.set_ylabel('Total Capital ($)')
			ax3.legend(loc=0)
			ax3.set_title("Total Capital")

			ax6.set_title("Total Generating Capacity")
			ax6.set_xlabel('Years of Simulation')
			ax6.set_ylabel('Billion kWh per Year')

			#ax3.set_title("Cost Forecast")
			#ax3.set_xlabel('Years of Simulation')
			#ax3.set_ylabel('kWh/year per $')

			plt.savefig('VintResults/vint_cap_and_invest_results_Fl_' + str(count) + '_alpha_' + str(alpha)+ '_FLFrac_' + str(FlMax)+'.png', bbox_inches='tight')
			plt.close()





#cost = []
#for i in range(1, count):
#	cost.append(getOptimalCost("FlResults/simpleResult_"+str(i)+".json"))

#plt.plot(range(1,count), cost)
#plt.xlabel("Speed of Transition")
#plt.ylabel("Net Present Value Cost - $")
#plt.title("Cost of Transition as a Function of Transition Speed")
#plt.savefig('FlResults/cost_as_func_of_Fl_emissions_' + str(alpha) + '.png', bbox_inches='tight')
#plt.close()







