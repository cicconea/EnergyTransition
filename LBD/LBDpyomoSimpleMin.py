from __future__ import division
from pyomo.environ import *



# this function builds an expression for capital in time t for capital Hp/Hn/Lp/Ln
def genK(params, pVar, nVar, t, capitalType):
	if capitalType == "High":
		capital = params["H0"] * exp(-t/params["nh"]) + sum([pVar[j] * exp((j-t)/params["nh"]) - nVar[j] for j in range(1, t+1)])
	elif capitalType == "Low":
		capital = params["L0"] * exp(-t/params["nl"]) + sum([pVar[j] * exp((j-t)/params["nl"]) - nVar[j] for j in range(1, t+1)])
	return capital


def genLBDF(params, modelVars, capitalType, k=1,):
	autonomousTech = 0.005
	M = 0.0022
	gamma = 0.5
	phi = 0.5
	if capitalType == "High":
		Fprev = params["Fh_0"]
		dFdt = autonomousTech * Fprev + k * M * (params["H0"]**gamma) * (Fprev**phi)
	elif capitalType == "Low":
		Fprev = params["Fl_0"]
		dFdt = autonomousTech * Fprev + k * M * (params["L0"]**gamma) * (Fprev**phi)

	F = dFdt + Fprev
	FList = [F]
	for previous in range(1, params["period"]+1):
		dFdt = autonomousTech * Fprev + k * M * (modelVars[previous]**gamma) * (Fprev**phi)
		F = dFdt + Fprev
		FList.append(F)
		previous += 1
		Fprev = F
	return FList


def simpleModel(params):

	# initialize model
	model = ConcreteModel()

	N = range(1, params["period"]+1)

	# create variables
	model.Hp = Var(N, domain=NonNegativeReals, initialize = 0.05)
	model.Hn = Var(N, domain=NonNegativeReals, initialize = 500000)
	model.Lp = Var(N, domain=NonNegativeReals, initialize = 500000)
	model.Ln = Var(N, domain=NonNegativeReals, initialize = 0.05)


	# create expressions for productivities:
	FlList = genLBDF(params, model.Lp, "Low")
	#FhList = genLBDF(params, model.Hp, "High")


	# also set all non-negativity constraints for capital
	for t in range(1, params["period"]+1):
		setattr(model, "KhNonNeg"+str(t), Constraint(expr = genK(params, model.Hp, model.Hn, t, "High") >= 0))
		setattr(model, "KlNonNeg"+str(t), Constraint(expr = genK(params, model.Lp, model.Ln, t, "Low") >= 0))

	# generation constraints
	for t in range(1, params["period"]+1):
		setattr(model, "Gen"+str(t), Constraint(expr = params["FhList"][t]*genK(params, model.Hp, model.Hn, t, "High") + FlList[t]*genK(params, model.Lp, model.Ln, t, "Low") >= params["GList"][t]))

	# emission constraint
	emit = 0
	for t in range(1, params["period"]+1):
		emit += params["mhList"][t]*params["FhList"][t]*genK(params, model.Hp, model.Hn, t, "High") + params["mlList"][t]*FlList[t]*genK(params, model.Lp, model.Ln, t, "Low")
	model.emissions = Constraint(expr = emit <= params["alpha"] * params["period"] *(params["mhList"][0]*params["FhList"][0]*params["H0"] + params["mlList"][0]*FlList[0]*params["L0"]))


	# sum over positive investments as objective function
	model.OBJ = Objective(expr = sum([(model.Hp[i] + model.Lp[i])*exp(-params["r"]*i) for i in N]))

	return model






