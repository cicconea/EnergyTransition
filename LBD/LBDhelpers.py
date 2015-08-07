from func_gen import *
from pyomo.opt import SolverFactory, SolverStatus, TerminationCondition
from six import StringIO, iteritems
import numpy as np
from matplotlib import pyplot as plt
import matplotlib
import seaborn
import csv




def genData(period):
	''' 
	This function generates all parameters used in the simulation. 
	This function is called in the post-process module and
	passed to the solver function to provide data to the model object. 
	'''
	params = {}

	# the commited reduction list is the alpha for each year from 2015 of cumulative emissions reductions
	# based on US commitments with several assumptions. See the documentation for more details
	params["CommittedReduction"] = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0.998918381, 0.996990567, 0.994389016, 0.991242947,0.987651088,0.983449867,0.978741773,0.973609292,0.968119532,0.962327629,0.956279285,0.950012681,0.943559952,0.936948319,0.929986142,0.923261965,0.916747158,0.910417271,0.904251299,0.898231095,0.892340892,0.886566932,0.880897148,0.875320915,0.869828838,0.864412576,0.8590647,0.853778569,0.848548228,0.84336832,0.838234012,0.833140931,0.828085111,0.823062945,0.818071144,0.813106704,0.808166871,0.80324912,0.798351126,0.793470748,0.788606007,0.783755073,0.77891625,0.774087962,0.769268742,0.764457226,0.759652139,0.754852287,0.750056555,0.745263897,0.740473329,0.735683926,0.730894817,0.726105179,0.721314237,0.716521255,0.711725537,0.706926424,0.702123288,0.697315533,0.69250259,0.687683918,0.682859,0.678027342,0.67318847,0.668457832,0.663831062,0.659304024,0.654872788,0.650533623,0.646282984,0.642117498,0.638033956,0.634029303,0.630100626,0.62624515,0.622460225,0.618743326,0.615092038,0.611504054,0.607977169,0.604509274,0.601098349,0.597742463,0.594439764,0.591188476,0.587986897,0.584833396,0.581726404,0.578664418,0.575645992,0.572669737,0.569734317,0.566838447,0.563980893,0.561160462,0.558376011,0.555626434,0.552910668,0.550227687,0.547576501,0.544956157,0.542365733,0.539804338,0.537271115,0.534765233,0.532285889,0.529832309,0.52740374,0.524999458,0.52261876,0.520260966,0.517925418,0.515611476,0.513318523,0.51104596,0.508793205,0.506559694,0.504344881,0.502148235,0.499969241,0.497807398,0.495662221,0.493533237,0.491419988,0.489322026,0.487238919,0.485170245,0.483115592,0.481074561,0.479046764,0.477031821,0.475029363,0.473039031,0.471060475,0.469093353,0.467137332,0.465192087,0.463257302,0.461332667,0.45941788,0.457512648,0.455616681,0.4537297,0.451851429,0.4499816,0.44811995,0.446266224,0.44442017,0.442581542]

	params["period"] = period # simulation length
	params["alpha"] = 0.45 # percent of cumulative business as usual emissions allowed


	# Learning by Doing Parameters
	params["k"] = 1 # Turning on Learning by doing k = 1, otherwise no LBD k=0
	params["autonomousTech"] = 0.005 # autonomous rate of tech progress - rate of F without LBD
	params["M"] = 0.0022 # default parameter from G&M, but superceded in practice
	params["gamma"] = 0.5 # LBD gamma - returns to investment, not the fractional gamma in the rest of this module
	params["phi"] = 0.5 # intertemporal knowledge spillover. Default is 0.5 but superceded in FList generation
						# see documentation for more details. 


	# Electricity Demand Data
	G_0 = 2843.3 * 10**9 # billion kWh electricity demanded
	G_m = 32.2 * 10**9 # annual growth in demand for electricity in billion kWh
	

	# Productivity costs and other parameters
	kWperYearTokWh = 8760.0 # conversion of 1 kW power capacity for 1 year to kWh energy
	HCap = 0.5 # capacity factor for high - percent of time asset is generating
	LCap = 0.3 # capacity factor for low - percent of time asset is generating
	occH = 3500 # $/kW overnight capital cost high
	occL = 3700 # $/kW overnight capital cost low


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
	# where G_0 != to Fh_0 * kh_0 + Fl_0 * kl_0
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
	# generated in the solver module because it is now a function of learning by doing
	params["GList"] = linGen(params["period"] + 1, G_0, G_m, minimum = 0.0, maximum = 6.0 *10.0 **12) # energy demand over time
	params["FhList"] = linGen(params["period"]+1, params["Fh_0"], Fh_m, maximum=4.7764449) # high emitting efficiency trajectory weighted average of coal and NG. Max is 1/917 * 8760 * 0.5
	params["mlList"] = consGen(params["period"]+1, el_0) # low emitting carbon intensity trajectory
	params["mhList"] = linGen(params["period"]+1, eh_0, eh_m, minimum=1.22) # high emitting carbon intensity trajectory - minimum is emission from 100% natural gas.

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
	solver = 'gurobi' #on local machine "asl:ipopt" Gurobi only works on RCC
	#solver_io = 'nl' for use with asl:ipopt only
	opt = SolverFactory(solver) #,solver_io=solver_io) <- add for running on local machine

	# Send the model to ipopt and collect the solution
	print "\t Solving the Model:"
	instance = model.create()
	results = opt.solve(instance, tee=True) # False = run quietly with no stdout. 

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

	return instance, results.solver.status, results.solver.termination_condition


def getConstraints(instance):
	'''
	This function takes the solved instance of the model object
	and puts the name of each constraint and it's value in to 
	a dictionary. From this you can get the value of total emissions, 
	total generation, or total capital in each period - used for
	generating graphs
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
	'''
	This function generates plots for the simple/nonvintaged version of the model
	'''


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


def genVintPlot(params, constraintDict, varDict, nameString):
	'''
	This function generates plots for the vintaged version of the model
	'''

	# First create lists of each vintage net investment
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


	# create lists of total capital of each vintage over simulation length
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


	# generate matplotlib figure and add each graph to the figure
	fig = plt.figure(figsize=(10, 8), dpi=100, facecolor='w', edgecolor='k')
	fig.subplots_adjust(hspace=0.5)
	ax1 = fig.add_subplot(2,3,1)
	ax2 = fig.add_subplot(2,3,2)
	ax3 = fig.add_subplot(2,3,3)
	ax4 = fig.add_subplot(2,3,4)
	ax5 = fig.add_subplot(2,3,5)
	ax6 = fig.add_subplot(2,3,6)

	# plot each vintage net investment
	for i in range(0, params["period"]+1):
		dateRange = range(i, len(H))
		ax1.plot(dateRange, H[i], label= "H Vintage: "+str(i))
		ax4.plot(dateRange, L[i], label= "L Vintage: "+str(i))

	# plot vintages of capital
	years = range(0, params["period"]+1)
	ax2.stackplot(years, Kh)
	ax5.stackplot(years, Kl)

	# create total capital of each type
	# and create total generation breakdowns by type
	totalKh = []
	totalKl = []
	totalGh = []
	totalGl = [params["Fl_0"]*params["L0"]]

	for t in range(params["period"]+1):
		totalKhInst = sum([Kh[i][t] for i in range(len(Kh[i]))])
		totalKlInst = sum([Kl[i][t] for i in range(len(Kl[i]))])
		totalKh.append(totalKhInst)
		totalKl.append(totalKlInst)

		totalGhInst = sum([params["FhList"][i] * Kh[i][t] for i in range(len(Kh[i]))])
		totalGh.append(totalGhInst)

	for i in range(1, params["period"]+1):
		totalGl.append(constraintDict["GenUpper"+str(i)] - totalGh[i])

	# plot total capital of each type & generation breakdown by type
	ax3.plot(years, totalKh, label = "High Emitting Capital")
	ax3.plot(years, totalKl, label = "Low Emitting Capital")
	ax6.stackplot(years, totalGh, totalGl)


	
	# label plots and save/show file
	ax1.set_xlabel('Years of Simulation')
	ax1.set_ylabel('Investment ($)')
	ax1.set_title("High Emitting Investments")

	ax2.set_xlabel('Years of Simulation')
	ax2.set_ylabel('Capital ($)')
	ax2.set_title("High Emitting Capital")

	ax3.set_xlabel('Years of Simulation')
	ax3.set_ylabel('Total Capital ($)')
	ax3.legend(loc=0)
	ax3.set_title("Total Capital")
			
	ax4.set_xlabel('Years of Simulation')
	ax4.set_ylabel('Capital ($)')
	ax4.set_title("Low Emitting Investments")

	ax5.set_xlabel('Years of Simulation')
	ax5.set_ylabel('Capital ($)')
	ax5.set_title("Low Emitting Capital")

	ax6.set_title("Total Generating Capacity")
	ax6.set_xlabel('Years of Simulation')
	ax6.set_ylabel('Billion kWh per Year')

	plt.savefig('results/vintageResult_LBD_alpha_'+ str(params["alpha"])+'_years_'+str(params["period"])+ '_phi_' + str(params["phi"]) + '_k_' + str(params["k"]) + nameString + '.png', bbox_inches='tight')
	plt.close()
	#plt.show()
	return


def checkConstraintFeasibility(params, varDict, constraintDict):
	'''
	This module examines each constraint from the solved model
	and compares it to it's required value with a true/False
	flag, printed to stdout
	'''

	#check non-negativity constraints
	print "Checking Time Logic Constraints"
	print "Vintage \t Year \t Name \t\t Value \t\tTarget \t Flag"

	for i in range(0, params["period"] + 1):
		for t in range(0, params["period"] + 1):
			if t<i:
				print i, "\t\t",  t, "\t HnTimeLogic\t" ,constraintDict["HnTimeLogic"+str(i)+"-"+str(t)], "\t", "Zero", "\t" ,constraintDict["HnTimeLogic"+str(i)+"-"+str(t)] == 0
				print i, "\t\t",  t, "\t LnTimeLogic\t" ,constraintDict["LnTimeLogic"+str(i)+"-"+str(t)], "\t", "Zero", "\t" ,constraintDict["LnTimeLogic"+str(i)+"-"+str(t)] == 0

				try:
					temp = constraintDict["KhZERO"+str(i)+"-"+str(t)]
				except KeyError:
					temp = 0
				print i, "\t\t",  t, "\t KhZero \t" ,temp , "\t", "Zero","\t" , temp == 0

				try:
					temp = constraintDict["KlZERO"+str(i)+"-"+str(t)]
				except KeyError:
					temp = 0
				print i, "\t\t",  t, "\t KlZero \t" ,temp , "\t", "Zero","\t" , temp == 0

	print
	print
	print "Checking Capital Non-Negativity Constraints"
	print "Vintage \tYear\tName \t\t Value \t\t\t\t Target \t Flag"

	for i in range(0, params["period"] + 1):
		for t in range(0, params["period"] + 1):
			if t>=i:
				print i, "\t\t",  t, "\tKhNonNeg\t" ,round(constraintDict["KhNonNeg"+str(i)+"-"+str(t)],5), "\t\t", "Non-Negative", "\t" ,constraintDict["KhNonNeg"+str(i)+"-"+str(t)] >= 0
				print i, "\t\t",  t, "\tKlNonNeg\t" ,round(constraintDict["KlNonNeg"+str(i)+"-"+str(t)],5), "\t\t", "Non-Negative", "\t" ,constraintDict["KlNonNeg"+str(i)+"-"+str(t)] >= 0


	print
	print
	print "Checking Generation Constraints"
	print "Year \t Name \t\t\tValue \t\t\tTarget \t\tFlag"

	for t in range(1, params["period"] + 1):
		print t, "\t Generation Upper"+str(t), "\t", round(constraintDict["GenUpper"+str(t)],5), "\t", round(params["GList"][t],5), "\t" ,constraintDict["GenUpper"+str(t)] <= params["GList"][t] * 1.001
		print t, "\t Generation Lower"+str(t), "\t", round(constraintDict["GenLower"+str(t)],5), "\t", round(params["GList"][t],5), "\t" ,constraintDict["GenLower"+str(t)] >= params["GList"][t] * 0.999



	print
	print
	print "Checking Emission Constraint"
	print "Name \t\tAlpha \tValue \t\t\tTarget \t\t\tFlag"
	maxEmit = sum([params["mhList"][i]*params["FhList"][i]*params["H0"] + params["mlList"][i]*params["Fl_0"]*params["L0"] for i in range(0, params["period"]+1)])
	print "Emission \t", params["alpha"], "\t",  constraintDict["emissions"], "\t", params["alpha"] * maxEmit, "\t" , constraintDict["emissions"] <= params["alpha"]*maxEmit


	return


def writeSolution(params, varDict, constraintDict, nameString=""):
	'''
	This module writes the same thing as checkConstraintFeasibility - making sure that 
	for the solved model that none of the constraints are violated and saving all the 
	constraint and variable values in case they're needed for further analysis. 

	nameString comes from an option when LBD_Vintage_Run.py is called from the command
	line. It is optional but strongly recommended so that it's easier to remember the output
	associated with a particular query and also to avoid overwriting any documentation.
	'''



	# save output to files
	f = open( "results/alpha_" + str(params["alpha"])+'_years_'+str(params["period"])+ '_phi_' + str(params["phi"]) + '_k_' + str(params["k"]) + "_" + nameString +"_constraints.csv", 'wb')
	writer = csv.writer(f)
	for key, value in constraintDict.items():
		writer.writerow([key, value])
	f.close()

	f = open( "results/alpha_" + str(params["alpha"])+'_years_'+str(params["period"])+ '_phi_' + str(params["phi"]) + '_k_' + str(params["k"]) + "_" + nameString +"_variables.csv", 'wb')
	writer = csv.writer(f)
	for key, value in varDict.items():
		writer.writerow([key, value])
	f.close()

	# save constraint checks:
	f = open( "results/alpha_" + str(params["alpha"])+'_years_'+str(params["period"])+ '_phi_' + str(params["phi"]) + '_k_' + str(params["k"]) + "_" + nameString +"_checks.csv", 'wb')
	writer = csv.writer(f)

	writer.writerow(["Checking Time Logic Constraints"])
	writer.writerow(["Vintage","Year", "Name", "Value", "Target", "Flag"])

	for i in range(0, params["period"] + 1):
		for t in range(0, params["period"] + 1):
			if t<i:
				writer.writerow([i, t, "HnTimeLogic", constraintDict["HnTimeLogic"+str(i)+"-"+str(t)], "Zero", constraintDict["HnTimeLogic"+str(i)+"-"+str(t)] == 0])
				writer.writerow([i, t, "LnTimeLogic", constraintDict["LnTimeLogic"+str(i)+"-"+str(t)], "Zero", constraintDict["LnTimeLogic"+str(i)+"-"+str(t)] == 0])

			try:
				temp = constraintDict["KhZERO"+str(i)+"-"+str(t)]
			except KeyError:
				temp = "Null"
			writer.writerow([i, t, "KhZero", temp, "Zero", temp == 0])

			try:
				temp = constraintDict["KlZERO"+str(i)+"-"+str(t)]
			except KeyError:
				temp = "Null"
			writer.writerow([i, t, "KlZero", temp, "Zero", temp == 0])


	writer.writerow(["Checking Capital Non-Negativity Constraints"])
	writer.writerow(["Vintage", "Year", "Name", "Value", "Target", "Flag"])

	for i in range(0, params["period"] + 1):
		for t in range(0, params["period"] + 1):
			if t>=i:
				writer.writerow([i, t, "KhNonNeg", constraintDict["KhNonNeg"+str(i)+"-"+str(t)], "Non-Negative", constraintDict["KhNonNeg"+str(i)+"-"+str(t)] >= 0])
				writer.writerow([i, t, "KlNonNeg", constraintDict["KlNonNeg"+str(i)+"-"+str(t)], "Non-Negative", constraintDict["KlNonNeg"+str(i)+"-"+str(t)] >= 0])

	writer.writerow(["Checking Generation Constraints"])
	writer.writerow(["Year", "Name", "Value", "Target", "Flag"])

	for t in range(1, params["period"] + 1):
		writer.writerow([t, "Generation Upper"+str(t), constraintDict["GenUpper"+str(t)], params["GList"][t], constraintDict["GenUpper"+str(t)] <= params["GList"][t] * 1.001])
		writer.writerow([t, "Generation Lower"+str(t), constraintDict["GenLower"+str(t)], params["GList"][t], constraintDict["GenLower"+str(t)] <= params["GList"][t] * 0.999])

	writer.writerow(["Checking Emission Constraint"])
	writer.writerow(["Name", "Alpha", "Value", "Target", "Flag"])
	maxEmit = sum([params["mhList"][i]*params["FhList"][i]*params["H0"] + params["mlList"][i]*params["Fl_0"]*params["L0"] for i in range(0, params["period"]+1)])
	writer.writerow(["Emission", params["alpha"], constraintDict["emissions"], params["alpha"] * maxEmit, constraintDict["emissions"] <= params["alpha"]*maxEmit])

	f.close()
	return






















