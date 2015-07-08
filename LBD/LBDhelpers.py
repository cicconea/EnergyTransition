from func_gen import *
from pyomo.opt import SolverFactory, SolverStatus, TerminationCondition
from six import StringIO, iteritems



def genData():
	''' 
	This function generates all parameters used in the simulation. 
	This function is called in the post-process module and
	passed to the solver function to provide data to the model object. 
	'''
	params = {}



	params["period"] = 5 # simulation length (!= to n)
	params["alpha"] = 0.5 # percentof business as usual emissions allowed


	# Learning by Doing Parameters
	params["k"] = 1 # Turning on Learning by doing k = 1, otherwise no LBD k=0
	params["autonomousTech"] = 0.005 # autonomous rate of tech progress - rate of F without LBD
	params["M"] = 0.0022
	params["LBDgamma"] = 0.5
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
	print "Solving the Model"
	instance = model.create()
	results = opt.solve(instance)

	# Load the results
	instance.load(results)

	# Check termination conditions and return status of solver to sdout
	if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
		print "Model feasible and optimal"
	elif (results.solver.termination_condition == TerminationCondition.infeasible):
		print "Model infeasible"
	else:
		print "Solver Status: ",  result.solver.status

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





