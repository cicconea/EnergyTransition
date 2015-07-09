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


def genDataSimple(i, FlFrac):
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

	occH = 3500 # $/kW
	occL = 3700 # $/kW

	Fh_0 = (1.0/occH) * HCap * kWperYearTokWh # base high emitting efficiency kW/$ * kWh conversion * capacity factor
	Fh_m = 3*0.5*10**-6 * kWperYearTokWh # linear slope high emitting efficiency * kWh conversion * capacity factor 
	Fl_0 = (1.0/occL) * LCap * kWperYearTokWh # base low emitting efficiency kW/$ * kWh conversion * capacity factor
	FlMax = (1.0/917.0) * LCap * kWperYearTokWh # max is efficiency of natural gas ($917/kW) at 30% capacity


	el_0 = 0.0 # base emissions for low-intensity capital in lbs CO2/kWh
	el_m = -0.1 # linear slope emissions for low-intensity capital
	eh_0 = 1.6984 # base emissions for high intensity capital in lbs CO2/kWh
	eh_m = -0.0031 # slope emissions for high-intensity capital

	G_0 = 2843.3 * 10**9 # billion kWh electricity demanded
	G_m = 32.2 * 10**9 # annual growth in demand for electricity in billion kWh


	# adjusted initial amounts preserving initial capital stock ratio
	# but taking in to account current costs to avoid weird first-period issues
	H0 = G_0/(Fh_0 + Fl_0*(1-gamma)/gamma)
	L0 = (G_0 - Fh_0*H0)/Fl_0



	period = 5 # simulation length (!= to n)
	nh = 30 # depreciation length for high emitting
	nl = 10 # depreciation length for low emitting

	# generate efficiency and carbon intensity data
	GList = linGen(period + 1, G_0, G_m, minimum = 0.0, maximum = 6.0 *10.0 **12) # energy demand over time
	# logistic arguments: (k, initial, increasing, randomAllowed, scale = 0.5, minVal= 0, maxVal=1)
	# randomAllowed = True varies scale (rate) of change of the trajectory

	FlMax = 2.8658669 #max is efficiency of natural gas ($917/kW) at 30% capacity

	FlScale, FlList = logistic(period+1, Fl_0, True, False, scale = i/100.0, minVal=0.34334988, maxVal=FlFrac * FlMax) # low emitting efficiency trajectory
		# min is half of base, max is efficiency of natural gas ($917/kW) at 30% capacity
	FhList = linGen(period+1, Fh_0, Fh_m, maximum=4.7764449) # high emitting efficiency trajectory 
		# weighted average of coal and NG. Max is 1/917 * 8760 * 0.5
		
	mlList = consGen(period+1, el_0) # low emitting carbon intensity trajectory
		# constant 
	mhList = linGen(period+1, eh_0, eh_m, minimum=1.22) # high emitting carbon intensity trajectory
		# minimum is emission from 100% natural gas.

	return GList, FlList, FhList, mlList, mhList, period, H0, L0, r, nh, nl











def getCapital(filename):
	with open(filename) as f:
		data = f.read()
		f.close()

	constraintList = re.split(r'None\n--\n', data)
	constraintList = [re.sub(r'\n', ' ', item) for item in constraintList ]

	kh = []
	kl = []

	for constraint in constraintList:
		constraints = constraint.split(":")

		if re.search("KlNonNeg", constraints[0]) is not None:
			kl.append(constraints[3])
		elif re.search("KhNonNeg", constraints[0]) is not None:
			kh.append(constraints[3])


	return kh, kl


def getInvestments(filename, period):
		with open(filename) as json_data:
			data = json.load(json_data)
			json_data.close()
		
		Hp = []
		Hn = []
		Lp = []
		Ln = []

		#create lists of investments
		for j in range(1, period+1):

			try: HpVal = data["Solution"][1]["Variable"]["Hp["+str(j)+"]"]["Value"]
			except KeyError: HpVal = 0

			try: HnVal = data["Solution"][1]["Variable"]["Hn["+str(j)+"]"]["Value"]
			except KeyError: HnVal = 0

			try: LpVal = data["Solution"][1]["Variable"]["Lp["+str(j)+"]"]["Value"]
			except KeyError: LpVal = 0

			try: LnVal = data["Solution"][1]["Variable"]["Ln["+str(j)+"]"]["Value"]
			except KeyError: LnVal = 0


			Hp.append(HpVal)
			Hn.append(HnVal)
			Lp.append(LpVal)
			Ln.append(LnVal)

		Hinvest = result = [x - y for x, y in zip(Hp, Hn)]
		Linvest = result = [x - y for x, y in zip(Lp, Ln)]


		return Hinvest, Linvest



def getOptimalCost(filename):
		with open(filename) as json_data:
			data = json.load(json_data)
			json_data.close()
		
		try: cost = data["Solution"][1]["Objective"]["OBJ"]["Value"]
		except KeyError: cost = 0

		return cost


def modelSolve(model):
	opt = SolverFactory('glpk')

	# Create a model instance and optimize
	instance = model.create()
	results = opt.solve(instance)
	# get the results back into the instance for easy access
	instance.load(results)
	
	# Check termination conditions and return status of solver to sdout
	if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
		print "\t\t Model feasible and optimal"
	elif (results.solver.termination_condition == TerminationCondition.infeasible):
		print "\t\t Model infeasible"
	else:
		print "\t\t Solver Status: ",  result.solver.status

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





