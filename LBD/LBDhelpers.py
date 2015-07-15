from func_gen import *
from pyomo.opt import SolverFactory, SolverStatus, TerminationCondition
from six import StringIO, iteritems
import seaborn
import numpy as np
from matplotlib import pyplot as plt
import matplotlib



def genData():
	''' 
	This function generates all parameters used in the simulation. 
	This function is called in the post-process module and
	passed to the solver function to provide data to the model object. 
	'''
	params = {}

	params["period"] = 5 # simulation length (!= to n)
	params["alpha"] = 0.8 # percentof business as usual emissions allowed


	# Learning by Doing Parameters
	params["k"] = 1 # Turning on Learning by doing k = 1, otherwise no LBD k=0
	params["autonomousTech"] = 0.005 # autonomous rate of tech progress - rate of F without LBD
	params["M"] = 0.0022
	params["gamma"] = 0.5 # LBD gamma, not the fractional gamma in the rest of this module
	params["phi"] = 0.5


	# Electricity Demand Data
	G_0 = 2843.3 * 10**9 # billion kWh electricity demanded
	G_m = 32.2 * 10**9 # annual growth in demand for electricity in billion kWh
	

	# Productivity costs and other parameters
	kWperYearTokWh = 8760.0 # conversion of 1 kW power capacity for 1 year to kWh energy
	HCap = 0.5 # capacity factor for high - percent of time asset is generating
	LCap = 0.3 # capacity factor for low - percent of time asset is generating
	occH = 3500 # $/kWh overnight capital cost high
	occL = 3700 # $/kWh overnight capital cost low


	# Productivity parameters
	params["Fh_0"] = (1.0/occH) * HCap * kWperYearTokWh # base high emitting efficiency kW/$ * kWh conversion * capacity factor
	Fh_m = 3*0.5*10**-6 * kWperYearTokWh # linear slope high emitting efficiency * kWh conversion * capacity factor 
	params["Fl_0"] = (1.0/occL) * LCap * kWperYearTokWh # base low emitting efficiency kW/$ * kWh conversion * capacity factor
	FlMax = (1.0/917.0) * LCap * kWperYearTokWh # max is efficiency of natural gas ($917/kW) at 30% capacity


	# Emissions parameters
	el_0 = 0.0 # base emissions for low-intensity capital in lbs CO2/kWh
	el_m = -0.1 # linear slope emissions for low-intensity capital
	eh_0 = 1.6984 # base emissions for high intensity capital in lbs CO2/kWh
	eh_m = -0.0031 # slope emissions for high-intensity capital


	# Setting up initial values of capital
	LBase = 2005.0 * 10**3 * 0.3 * 3827.0 # initial low emitting capital 
	HBase = (336341.0 + 485957.0) * 10**3 * 0.5 * 1714.0 # intial coal + ng high emitting capital 
		# MW * 1000kW/MW * capacity * $/kW from Fh_0 or Fl_0
	gamma = HBase/(HBase + LBase)
	
	# adjusted initial amounts preserving initial capital stock ratio
	# but taking in to account current costs to avoid weird first-period issues
	params["H0"] = G_0/(params["Fh_0"] + params["Fl_0"]*(1-gamma)/gamma)
	params["L0"] = (G_0 - params["Fh_0"]*params["H0"])/params["Fl_0"]


	# Operating Cost Data
	params["betah"] = 0.0096 # fraction of yearly operating costs
	params["betal"] = 0.0076 # fraction of yearly operating costs

	# Depreciation parameters
	params["nh"] = 30 # depreciation factor for high emitting
	params["nl"] = 10 # depreciation factor for low emitting
	params["r"] = 0.05 # interest rate


	# Generate functions of electricity demand, productivity and emissions
	# functions come from func_gen module. Low emitting productivity is 
	# generated in the solver module because it is now a function of learning
	# by doing
	params["GList"] = linGen(params["period"] + 1, G_0, G_m, minimum = 0.0, maximum = 6.0 *10.0 **12) # energy demand over time
	params["FhList"] = linGen(params["period"]+1, params["Fh_0"], Fh_m, maximum=4.7764449) # high emitting efficiency trajectory weighted average of coal and NG. Max is 1/917 * 8760 * 0.5
	params["mlList"] = consGen(params["period"]+1, el_0) # low emitting carbon intensity trajectory
	params["mhList"] = linGen(params["period"]+1, eh_0, eh_m, minimum=1.22) # high emitting carbon intensity trajectory - minimum is emission from 100% natural gas.


	FlScale, FlList = logistic(params["period"]+1, params["Fl_0"], True, False, scale = 10.0/100.0, minVal=0.34334988, maxVal=FlMax) # low emitting efficiency trajectory
		# min is half of base, max is efficiency of natural gas ($917/kW) at 30% capacity

	params["FlList"] = FlList

	return params





def NLmodelSolve(model):
	'''
	This function imports the constructed model object and solves it using
	the specified options (IPOPT using ASL interface). It also prints to 
	sdout the status of the solution it finds. To change the maximum 
	number of iterations allowed before the solver terminates, change the 
	ipopt.opt file in this directory to the desired number of iterations
	'''

	# Create the ipopt solver plugin using the ASL interface
	solver = 'asl:ipopt'
	solver_io = 'nl'
	opt = SolverFactory(solver,solver_io=solver_io)

	# Send the model to ipopt and collect the solution
	print "\t Solving the Model:"
	instance = model.create()
	results = opt.solve(instance, tee=False) # False = run quietly with no stdout. 

	# Load the results
	instance.load(results)

	# Check termination conditions and return status of solver to sdout
	if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
		print "\t\t Model feasible and optimal"
	elif (results.solver.termination_condition == TerminationCondition.infeasible):
		print "\t\t Model infeasible"
	else:
		print "\t\t Solver Status: ",  results.solver.status
		print "\t\t Termination Condition: ",  results.solver.termination_condition

	return instance


def getConstraints(instance):
	'''
	This function takes the solved instance of the model object
	and puts the name of each constraint and it's value in to 
	a dictionary. From this you can get the value of total emissions, 
	total generation, or total capital in each period - used for
	generating graphs in the postprocess module
	'''
	from pyomo.core import Constraint

	constraintDict = {}

	for c in instance.active_components(Constraint):
		thing = getattr(instance, c)._data
		for k,v in iteritems(thing):
			constraintDict[c] = v.body()

	return constraintDict


def getVars(instance):
	'''
	Collects the solver's values at the end of the optimization and 
	stores them in a dictionary with the name of the variable and 
	it's value. Note that the dictionary either has components that 
	are single floats or a list depending on how the variable 
	was initialized in the model object.
	'''

	from pyomo.core import Var
	varDict = {}

	for v in instance.active_components(Var):
		varobject = getattr(instance, v)
		for index in varobject:
			if varobject[index].value is None:
				varDict[v] = varobject.value
				continue
			elif varobject[index].value is not None:
				tempList = []
				for index in varobject:
					tempList.append(varobject[index].value)
				varDict[v] = tempList	
	return varDict


def genPlot(params, constraintDict, varDict):

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
	fig.subplots_adjust(hspace=0.5)
	dateRange = range(1, len(H)+1) # x-axis for all plots

	# Create plots for 2x2 graph
	ax1 = fig.add_subplot(2,2,1) # top left
	ax2 = fig.add_subplot(2,2,3) # bottom left
	ax3 = fig.add_subplot(2,2,2) # top right
	ax4 = fig.add_subplot(2,2,4) # bottom right 

	# add the data
	ax1.plot(dateRange, H, label= "Dirty Capital Invesment")
	ax1.plot(dateRange, L, label= "Clean Capital Investment")
	ax2.plot(dateRange, kh, label= "Dirty Capital Stock")
	ax2.plot(dateRange, kl, label= "Clean Capital Stock")
	ax3.stackplot(dateRange, frach, fracl)
	ax4.stackplot(dateRange, genH, genL)

	# create labels for axes
	ax1.set_title("Investment")
	ax1.legend(loc = 0)
	ax1.set_xlabel('Years of Simulation')
	ax1.set_ylabel('Investment ($)')

	ax2.set_title("$ of Capital")
	ax2.set_xlabel('Years of Simulation')
	ax2.set_ylabel('Investment ($)')

	ax3.set_title("Fractional Capital")
	ax3.set_xlabel('Years of Simulation')
	ax3.set_ylabel('Fraction of Capital')

	ax4.set_title("Total Generating Capacity")
	ax4.set_xlabel('Years of Simulation')
	ax4.set_ylabel('Billion kWh per Year')


	plt.savefig('simpleResult_LBD_alpha_' + str(params["alpha"]) + '.png', bbox_inches='tight')
	plt.close()
	#plt.show()


def genVintPlot(params, constraintDict, varDict):

	H = []
	L = []

	for i in range(0, params["period"]+1):

		Htemp = []
		Ltemp = []
		for t in range(0, params["period"]+1):
			if (t == i) and (t==0):
				Htemp.append(params["H0"])
				Ltemp.append(params["L0"])
			elif (t == i) and (t != 0):
				Htemp.append(varDict["Hp"+str(i)][0])
				Ltemp.append(varDict["Lp"+str(i)][0])
			elif t > i:
				Htemp.append(-varDict["Hn"+str(i)][t])
				Ltemp.append(-varDict["Ln"+str(i)][t])

		H.append(Htemp)
		L.append(Ltemp)


	Kh = []
	Kl = []
	for i in range(0, params["period"]+1):
		KhVint = []
		KlVint = []
		for t in range(0, params["period"]+1):
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
	for i in range(0, params["period"]+1):
		dateRange = range(i, len(H))
		ax1.plot(dateRange, H[i], label= "H Vintage: "+str(i))
		ax4.plot(dateRange, L[i], label= "L Vintage: "+str(i))

	years = range(0, params["period"]+1)
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

	for t in range(params["period"]+1):
		totalKhInst = sum([Kh[i][t] for i in range(len(Kh[i]))])
		totalKlInst = sum([Kl[i][t] for i in range(len(Kl[i]))])
		totalKh.append(totalKhInst)
		totalKl.append(totalKlInst)

		totalGhInst = sum([params["FhList"][i] * Kh[i][t] for i in range(len(Kh[i]))])
		totalGh.append(totalGhInst)
		totalGl.append(params["GList"][t] - totalGh[t])


	ax3.plot(years, totalKh, label = "High Emitting Capital")
	ax3.plot(years, totalKl, label = "Low Emitting Capital")

	ax6.stackplot(years, totalGh, totalGl)
	
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

	plt.savefig('vintageResult_LBD_alpha_' + str(params["alpha"]) + '.png', bbox_inches='tight')
	plt.close()
	#plt.show()


