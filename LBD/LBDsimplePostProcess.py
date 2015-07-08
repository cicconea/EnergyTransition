import sys
from LBDhelpers import *
import seaborn
import numpy as np
from matplotlib import pyplot as plt
import matplotlib
from LBDpyomoSimpleMin import simpleModel


'''
This module should be called from the command line to set up all parameters,
create the model, solve and plot the results. 
'''

# generate the parameter data from the LBDhelpers module.
params = genData()
print "Imported parameters successfully"

# Create the model
model = simpleModel(params)
print "Constructed model"

# Solve the model
instance = NLmodelSolve(model)

# Get solution and constraint values
constraintDict = getConstraints(instance)
varDict = getVars(instance)



print "Generating graphs"

# from the variable dictionary, put net investments in to a list
# postive investments - negative investments
H = [params["H0"]]
L = [params["L0"]]
for t in range(1, params["period"]):
	H.append(varDict["Hp"][t] - varDict["Hn"][t])
	L.append(varDict["Lp"][t] - varDict["Ln"][t])


# Pull out capital values from constraint dictionary. The constraint
# dictionary only keeps values != 0, so try/except to add in the zero-valued
# capital to generate a full set of results
kh = []
kl = []
for t in range(1, params["period"]+1):
	try:
		kh.append(constraintDict["KhNonNeg"+str(t)])
	except KeyError:
		kh.append(0)

	try:
		kl.append(constraintDict["KlNonNeg"+str(t)])
	except KeyError:
		kl.append(0)

# Create percentage split of capital for plotting
totalk = [kh[i]+kl[i] for i in range(len(kh))]
frach = [kh[i]/totalk[i] for i in range(len(kh))]
fracl = [kl[i]/totalk[i] for i in range(len(kl))]


# Generation split between high and low capital
genH = [kh[i]*params["FhList"][i+1] for i in range(len(kh))]
genL = [params["GList"][i+1] - genH[i] for i in range(len(kl))]



# generate matplotlib plot for investment
font = {'size'   : 10}
matplotlib.rc('font', **font)
fig = plt.figure(figsize=(10, 7), dpi=100, facecolor='w', edgecolor='k')
dateRange = range(1, len(H)+1) # x-axis for all plots




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


#plt.savefig('results/simpleResult_LBD_alpha' + str(alpha) + '.png', bbox_inches='tight')
#plt.close()

plt.show()









