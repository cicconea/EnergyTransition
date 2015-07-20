from __future__ import division
from pyomo.environ import *
from math import exp
from LBDhelpers import genData
from six import StringIO, iteritems
import time
import pympler


# this function builds an expression for capital in time t for capital Hp/Hn/Lp/Ln of age i
# sum from initial investment period i through existing time period t
def genK(params, model, pVar, nVar, i, t):
	if t<i:
		K = 0
	elif t >= i:
		if pVar == "Hp":
			if i == 0: 
				K = params["H0"] * exp((i-t)/params["nh"]) - sum([getattr(model, nVar+str(i))[j] for j in range(i, t+1)])
			elif i > 0:
				K = getattr(model, pVar+str(i)) * exp((i-t)/params["nh"]) - sum([getattr(model, nVar+str(i))[j] for j in range(i, t+1)])
		
		if pVar == "Lp":
			if i == 0:
				K = params["L0"] * exp((i-t)/params["nl"]) - sum([getattr(model, nVar+str(i))[j] for j in range(i, t+1)])
			elif i > 0:
				K = getattr(model, pVar+str(i)) * exp((i-t)/params["nl"]) - sum([getattr(model, nVar+str(i))[j] for j in range(i, t+1)])

	return K


def genLBDF(params, model, ts):
	Fprev = params["Fl_0"]
	FList = [Fprev]
	print
	for previous in range(1, params["period"]+1):
		print "\t \t \t start index", previous, "in", (time.time() - ts)
		invest = getattr(model, "Lp" + str(previous))
		print "\t \t \t get previous investment in", (time.time() - ts)
		dFdt = params["autonomousTech"] * Fprev + params["k"] * params["M"] * (invest**params["gamma"]) * (Fprev**params["phi"])
		print "\t \t \t calculate differential in", (time.time() - ts)
		F = dFdt + Fprev
		print "\t \t \t got new productivity in", (time.time() - ts)
		FList.append(F)
		print "\t \t \t LBD year ", previous, "complete in ", (time.time() - ts)

		print "\t \t \t \t ", F
		Fprev = F
		print "\t \t \t size of F at time", previous, "is", pympler.asizeof.asizeof(F)
		print

	return FList


def genCumLBDF(params, model):
	progressRatio = 1.05
	doublingTime = 10
	Fprev = params["Fl_0"]
	FList = [Fprev]
	for i in range(1, params["period"] + 1):
		avgInvest = (params["L0"] + sum([getattr(model, "Lp" + str(j)) for j in range(1, i)]))/params["L0"]
		Fi = avgInvest * (progressRatio*i) ** doublingTime
		FList.append(Fi)
	return FList


def vintageModel(params):
	ts = time.time()

	model = ConcreteModel()
	
	print "\t \t create concrete model in ", (time.time() - ts)

	N = range(0, params["period"]+1)

	# create variables
	# Hp_i is the positive investment in high over all years list of all years
	for i in range(1, params["period"] + 1):
		setattr(model,"Hp"+str(i),Var(domain=NonNegativeReals, initialize = 0.005))
		setattr(model,"Lp"+str(i),Var(domain=NonNegativeReals, initialize = params["L0"]))
	for i in range(0, params["period"] + 1):	
		setattr(model,"Hn"+str(i),Var(N, domain=NonNegativeReals, initialize = params["H0"]))
		setattr(model,"Ln"+str(i),Var(N, domain=NonNegativeReals, initialize = 0.005))

	print "\t \t initialize variables in ", (time.time() - ts)
	print "\t \t Hp1 memory is ", pympler.asizeof.asizeof(model.Hp1)
	print "\t \t Hn1 memory is ", pympler.asizeof.asizeof(model.Hn1)



	# generate expressions for Low-emitting productivities via the learning by doing function
	#FlList = genLBDF(params, model, ts)
	FlList = genCumLBDF(params, model)

	print "\t \t generate learning by doing function in ", (time.time() - ts)
	print "\t \t Flist memory is ", pympler.asizeof.asizeof(FlList)

	# Can't have negative capital in active periods
	for i in range(0, params["period"] + 1):
		for t in range(0, params["period"] + 1):
			if t>=i:
				setattr(model, "KhNonNeg"+str(i)+"-"+str(t), Constraint(expr = genK(params, model, "Hp", "Hn", i, t) >= 0))
				setattr(model, "KlNonNeg"+str(i)+"-"+str(t), Constraint(expr = genK(params, model, "Lp", "Ln", i, t) >= 0))

			if t<i:
				setattr(model, "HnTimeLogic"+str(i)+"-"+str(t), Constraint(expr = getattr(model, "Hn"+str(i))[t] == 0))
				setattr(model, "LnTimeLogic"+str(i)+"-"+str(t), Constraint(expr = getattr(model, "Ln"+str(i))[t] == 0))

	print "\t \t set nonegativity constraints in ", (time.time() - ts)


	# generation constraints
	for t in range(1, params["period"] + 1):
		genSum = 0
		for i in range(0, t+1):
			genSum += params["FhList"][i]*genK(params, model, "Hp", "Hn", i, t) + FlList[i]*genK(params, model, "Lp", "Ln", i, t)
		setattr(model, "Gen"+str(t), Constraint(expr = genSum >= params["GList"][t]))

	print "\t \t create generation constraints in ", (time.time() - ts)


	# emission constraint
	emit = params["H0"] * params["FhList"][0]* params["mhList"][0] + params["L0"]*FlList[0]*params["mlList"][0]
	for t in range(1, params["period"]):
		for i in range(1, t+1):
			emit += params["mhList"][i]*params["FhList"][i]*genK(params, model, "Hp", "Hn", i, t) + params["mlList"][i] * FlList[i]*genK(params, model, "Lp", "Ln", i, t)

	maxEmit = params["alpha"] * sum([params["mhList"][i]*params["FhList"][i]*params["H0"] + params["mlList"][i]*FlList[0]*params["L0"] for i in N])
	setattr(model, "emissions", Constraint(expr = emit <= maxEmit))

	print "\t \t create emissions constraints in ", (time.time() - ts)


	# objective function is present value of investment cost minus operating cost savings

	OCh = 0
	OCl = 0
	for i in range(1, len(N)):
		for t in range(i, len(N)):
			subh = 0
			subl = 0
			for x in range(i, t+1):
				subh += getattr(model, "Hn"+str(i))[x]
				subl += getattr(model, "Ln"+str(i))[x]
			subh *= exp(-params["r"]*t)
			subl *= exp(-params["r"]*t)
			OCh += subh
			OCl += subl

	print "\t \t define operating costs in ", (time.time() - ts)


	# objective with operating costs
	model.OBJ = Objective(expr = sum([(getattr(model, "Hp"+str(i)) + getattr(model, "Lp"+str(i)))*exp(-params["r"]*i) for i in range(1, params["period"]+1)]) - params["betah"]*OCh - params["betal"]*OCl)

	print "\t \t set objective in ", (time.time() - ts)

	print "\t \t total model size is ", pympler.asizeof.asizeof(model)

	return model


