from func_gen import *
import re
import json
from pyomo.opt import SolverFactory, SolverStatus, TerminationCondition
from six import StringIO, iteritems




def genDataVint(i, FlFrac):



	LBase = 2005.0 * 10**3 * 0.3 * 3827.0 # initial low emitting capital 
	HBase = (336341.0 + 485957.0) * 10**3 * 0.5 * 1714.0 # intial coal + ng high emitting capital 
		# MW * 1000kW/MW * capacity * $/kW from Fh_0 or Fl_0

	gamma = HBase/(HBase + LBase)

	betah = 0.0096 # fraction of yearly operating costs
	betal = 0.0076 # fraction of yearly operating costs

	r = 0.05 # interest rate

	kWperYearTokWh = 8760.0 # conversion of 1 kW power capacity for 1 year to kWh energy
	HCap = 0.5
	LCap = 0.3

	occH = 3500 + 646 # $/kW of overnight capital cost + PV(operating costs over 50 years)
	occL = 3700 + 260 # $/kW of overnight capital cost + PV(operating costs over 50 years)


	el_0 = 0.0 # base emissions for low-intensity capital in lbs CO2/kWh
	el_m = -0.1 # linear slope emissions for low-intensity capital
	eh_0 = 1.6984 # base emissions for high intensity capital in lbs CO2/kWh
	eh_m = -0.0031 # slope emissions for high-intensity capital

	period = 5 # simulation length (!= to n)
	nh = 30 # depreciation length for high emitting
	nl = 10 # depreciation length for low emitting



	# Version in kWh
	Fh_0 = (1.0/occH) * HCap * kWperYearTokWh # base high emitting efficiency kW/$ * kWh conversion * capacity factor
	Fh_m = 3*0.5*10**-6 * kWperYearTokWh # linear slope high emitting efficiency * kWh conversion * capacity factor 
	Fl_0 = (1.0/occL) * LCap * kWperYearTokWh # base low emitting efficiency kW/$ * kWh conversion * capacity factor
	FlMax = (1.0/917.0) * LCap * kWperYearTokWh # max is efficiency of natural gas ($917/kW) at 30% capacity




	G_0 = 2843.3 * 10**9 # billion kWh electricity demanded
	G_m = 32.2 * 10**9 # annual growth in demand for electricity in billion kWh



	# Version in W
	#Fh_0 = (1.0/occH) * HCap * 1000 # base high emitting efficiency kW/$ * kW > W conversion * capacity factor
	#Fh_m = 3*0.5*10**-6 * 1000 * HCap # linear slope high emitting efficiency * kW > W conversion * capacity factor 
	#Fl_0 = (1.0/occL) * 1000 * LCap # base low emitting efficiency kW/$ * kW > W conversion * capacity factor
	#FlMax = (1.0/917.0) * 1000 * LCap  # max is efficiency of natural gas ($0.917/W) at 30% capacity

	#G_0 = 2843.3 * 10**9 * 0.11 # in W instead of kWh
	#G_m = 32.2 * 10**9 * 0.11 # in W instead of kWh




	# adjusted initial amounts preserving initial capital stock ratio
	# but taking in to account current costs to avoid weird first-period issues
	H0 = G_0/(Fh_0 + Fl_0*(1-gamma)/gamma)
	L0 = (G_0 - Fh_0*H0)/Fl_0





	# generate efficiency and carbon intensity data
	GList = linGen(period, G_0, G_m, minimum = 0.0, maximum = 6.0 *10.0 **12) # energy demand over time
	# logistic arguments: (k, initial, increasing, randomAllowed, scale = 0.5, minVal= 0, maxVal=1)
	# randomAllowed = True varies scale (rate) of change of the trajectory


	FlScale, FlList = logistic(period, Fl_0, True, False, scale = i/100.0, minVal=0.34334988, maxVal=FlFrac*FlMax) # low emitting efficiency trajectory
		# min is half of base, max is efficiency of natural gas ($917/kW) at 30% capacity
	FhList = linGen(period, Fh_0, Fh_m, maximum=4.7764449) # high emitting efficiency trajectory 
		# weighted average of coal and NG. Max is 1/917 * 8760 * 0.5
		
	mlList = consGen(period, el_0) # low emitting carbon intensity trajectory
		# constant 
	mhList = linGen(period, eh_0, eh_m, minimum=1.22) # high emitting carbon intensity trajectory
		# minimum is emission from 100% natural gas.

	return GList, FlList, FhList, mlList, mhList, period, H0, L0, r, nh, nl, betah, betal


def genData():

	params = {}

	# Learning by Doing Parameters
	params["k"] = 1 # Turning on Learning by doing k = 1, otherwise no LBD k=0
	params["autonomousTech"] = 0.005 # autonomous rate of tech progress - rate of F without LBD
	params["M"] = 0.0022
	params["LBDgamma"] = 0.5
	params["phi"] = 0.5



	params["LBase"] = 2005.0 * 10**3 * 0.3 * 3827.0 # initial low emitting capital 
	params["HBase"] = (336341.0 + 485957.0) * 10**3 * 0.5 * 1714.0 # intial coal + ng high emitting capital 
		# MW * 1000kW/MW * capacity * $/kW from Fh_0 or Fl_0

	params["gamma"] = params["HBase"]/(params["HBase"] + params["LBase"])

	params["betah"] = 0.0096 # fraction of yearly operating costs
	params["betal"] = 0.0076 # fraction of yearly operating costs


	params["r"] = 0.05 # interest rate
	params["kWperYearTokWh"] = 8760.0 # conversion of 1 kW power capacity for 1 year to kWh energy
	params["HCap"] = 0.5 
	params["LCap"] = 0.3

	params["occH"] = 3500 # $/kWh
	params["occL"] = 3700 # $/kWh

	params["el_0"] = 0.0 # base emissions for low-intensity capital in lbs CO2/kWh
	params["el_m"] = -0.1 # linear slope emissions for low-intensity capital
	params["eh_0"] = 1.6984 # base emissions for high intensity capital in lbs CO2/kWh
	params["eh_m"] = -0.0031 # slope emissions for high-intensity capital

	params["G_0"] = 2843.3 * 10**9 # billion kWh electricity demanded
	params["G_m"] = 32.2 * 10**9 # annual growth in demand for electricity in billion kWh

	params["period"] = 5 # simulation length (!= to n)
	params["nh"] = 30 # depreciation length for high emitting
	params["nl"] = 10 # depreciation length for low emitting


	params["Fh_0"] = (1.0/params["occH"]) * params["HCap"] * params["kWperYearTokWh"] # base high emitting efficiency kW/$ * kWh conversion * capacity factor
	params["Fh_m"] = 3*0.5*10**-6 * params["kWperYearTokWh"] # linear slope high emitting efficiency * kWh conversion * capacity factor 
	params["Fl_0"] = (1.0/params["occL"]) * params["LCap"] * params["kWperYearTokWh"] # base low emitting efficiency kW/$ * kWh conversion * capacity factor
	params["FlMax"] = (1.0/917.0) * params["LCap"] * params["kWperYearTokWh"] # max is efficiency of natural gas ($917/kW) at 30% capacity




	# adjusted initial amounts preserving initial capital stock ratio
	# but taking in to account current costs to avoid weird first-period issues
	params["H0"] = params["G_0"]/(params["Fh_0"] + params["Fl_0"]*(1-params["gamma"])/params["gamma"])
	params["L0"] = (params["G_0"] - params["Fh_0"]*params["H0"])/params["Fl_0"]




	# generate efficiency and carbon intensity data
	params["GList"] = linGen(params["period"] + 1, params["G_0"], params["G_m"], minimum = 0.0, maximum = 6.0 *10.0 **12) # energy demand over time
	# logistic arguments: (k, initial, increasing, randomAllowed, scale = 0.5, minVal= 0, maxVal=1)
	# randomAllowed = True varies scale (rate) of change of the trajectory


	params["FhList"] = linGen(params["period"]+1, params["Fh_0"], params["Fh_m"], maximum=4.7764449) # high emitting efficiency trajectory 
		# weighted average of coal and NG. Max is 1/917 * 8760 * 0.5

	#params["FhList"] = consGen(params["period"]+1, params["Fh_0"])

	params["mlList"] = consGen(params["period"]+1, params["el_0"]) # low emitting carbon intensity trajectory
		# constant 
	params["mhList"] = linGen(params["period"]+1, params["eh_0"], params["eh_m"], minimum=1.22) # high emitting carbon intensity trajectory
		# minimum is emission from 100% natural gas.

	return params





def NLmodelSolve(model):
	### Create the ipopt solver plugin using the ASL interface
	solver = 'asl:ipopt'
	solver_io = 'nl'
	stream_solver = False    # True prints solver output to screen
	keepfiles =     False    # True prints intermediate file names (.nl,.sol,...)
	opt = SolverFactory(solver,solver_io=solver_io)

	### Send the model to ipopt and collect the solution

	print "Solving the Model"
	instance = model.create()
	results = opt.solve(instance)

	# load the results (including any values for previously declared
	instance.load(results)

	if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
		print "Model feasible and optimal"
	elif (results.solver.termination_condition == TerminationCondition.infeasible):
		print "Model infeasible"
	else:
		print "Solver Status: ",  result.solver.status

	return instance


def getConstraints(instance):
	from pyomo.core import Constraint

	constraintDict = {}

	for c in instance.active_components(Constraint):
		thing = getattr(instance, c)._data
		for k,v in iteritems(thing):
			constraintDict[c] = v.body()

	return constraintDict


def getVars(instance):
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





