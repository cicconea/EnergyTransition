import sys
from helpers import *
import seaborn
import numpy as np
from matplotlib import pyplot as plt
import matplotlib
from pyomoSimpleMin import simpleModel


alphaRange = [50] # % emissions reduction
countRange = [10] # scale of transition
FlMaxRange = [100] # % of max emissions can't be lower that 25%



for alpha in alphaRange:
	for count in countRange:
		for FlMax in FlMaxRange:
			print "Simple ", count, alpha, FlMax

			GList, FlList, FhList, mlList, mhList, period, H0, L0, r, nh, nl = genDataSimple(count, FlMax/100.0)
			model = simpleModel(float(alpha)/100.0,count, FlMax)
			instance = modelSolve(model)
			constraintDict = getConstraints(instance)
			varDict = getVars(instance)


			H = [H0]
			L = [L0]
			for t in range(1, period):
				H.append(varDict["Hp"][t] - varDict["Hn"][t])
				L.append(varDict["Lp"][t] - varDict["Ln"][t])


			kh = []
			kl = []
			for t in range(1, period+1):
				try:
					kh.append(constraintDict["KhNonNeg"+str(t)])
				except KeyError:
					kh.append(0)

				try:
					kl.append(constraintDict["KlNonNeg"+str(t)])
				except KeyError:
					kl.append(0)


			

			font = {'size'   : 10}
			matplotlib.rc('font', **font)

			#kh = [float(i) for i in kh]
			#kl = [float(i) for i in kl]
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
			ax4.set_ylabel('Billion kWh per Year')

			plt.show()
			#plt.savefig('simpleResult/simple_cap_and_invest_results_Fl_' + str(count) + '_alpha_' + str(alpha) + '_FLFrac_' + str(FlMax) + '.png', bbox_inches='tight')
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







