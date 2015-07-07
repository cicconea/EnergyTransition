from __future__ import division
from pyomo.environ import *
from math import exp
from helpers import genData
from pyomo.opt import SolverFactory
from six import StringIO, iteritems



params = genData()
params["alpha"] = 0.80



# this function builds an expression for capital in time t for capital Hp/Hn/Lp/Ln of age i
# varRange is model.Hp_
# sum from initial investment period i through existing time period t
def genK(model, pVar, nVar, i, t):
	if pVar == "Hp":
		K = getattr(model, pVar+str(i)) * exp((i-t)/params["nh"]) - sum([getattr(model, nVar+str(i))[j] for j in range(0, t+1)])
	if pVar == "Lp":
		K = getattr(model, pVar+str(i)) * exp((i-t)/params["nl"]) - sum([getattr(model, nVar+str(i))[j] for j in range(0, t+1)])
	return K


def genLBDF(params, model, capitalType):
	if capitalType == "High":
		Fprev = params["Fh_0"]
		dFdt = params["autonomousTech"] * Fprev + params["k"] * params["M"] * (params["H0"]**params["LBDgamma"]) * (Fprev**params["phi"])
		F = dFdt + Fprev
		FList = [F]
		for previous in range(1, params["period"]+1):
			invest = getattr(model, "Hp" + str(previous))
			dFdt = params["autonomousTech"] * Fprev + params["k"] * params["M"] * (invest**params["LBDgamma"]) * (Fprev**params["phi"])
			F = dFdt + Fprev
			FList.append(F)
			previous += 1
			Fprev = F

	elif capitalType == "Low":
		Fprev = params["Fl_0"]
		dFdt = params["autonomousTech"] * Fprev + params["k"] * params["M"] * (params["H0"]**params["LBDgamma"]) * (Fprev**params["phi"])
		F = dFdt + Fprev
		FList = [F]
		for previous in range(1, params["period"]+1):
			invest = getattr(model, "Hp" + str(previous))
			dFdt = params["autonomousTech"] * Fprev + params["k"] * params["M"] * (invest**params["LBDgamma"]) * (Fprev**params["phi"])
			F = dFdt + Fprev
			FList.append(F)
			previous += 1
			Fprev = F

	return FList







#def vintageModel():



# initialize model
model = ConcreteModel()
 
N = range(0, params["period"]+1)

# create variables
# Hp_i is the positive investment in high over all years list of all years
for i in range(0, params["period"] + 1):
	setattr(model,"Hp"+str(i),Var(domain=NonNegativeReals))
	setattr(model,"Hn"+str(i),Var(N, domain=NonNegativeReals))
	setattr(model,"Lp"+str(i),Var(domain=NonNegativeReals))
	setattr(model,"Ln"+str(i),Var(N, domain=NonNegativeReals))

# generate expressions for Low-emitting productivities via the learning by doing function
FlList = genLBDF(params, model, "Low")

print len(model.Hn1)
print len(FlList)
print len(params["GList"])
print len(params["FhList"])
print len(params["mhList"])
print len(params["mlList"])




# can't have values for investments that happen before the year in which they're initialized
# also can't have negative capital in active periods
for i in range(0, params["period"] + 1):
	for t in range(0, params["period"] + 1):
		if t<i:
			setattr(model, "HnTimeLogic"+str(i)+str(t), Constraint(expr = getattr(model, "Hn"+str(i))[t] == 0))
			setattr(model, "LnTimeLogic"+str(i)+str(t), Constraint(expr = getattr(model, "Ln"+str(i))[t] == 0))

		elif t>=i:
			setattr(model, "KhNonNeg"+str(i)+"-"+str(t), Constraint(expr = genK(model, "Hp", "Hn", i, t) >= 0))
			setattr(model, "KlNonNeg"+str(i)+"-"+str(t), Constraint(expr = genK(model, "Lp", "Ln", i, t) >= 0))


#initialize starting points
model.Hp0Cons = Constraint(expr = model.Hp0 == params["H0"])
model.Lp0Cons = Constraint(expr = model.Lp0 == params["L0"])


# generation constraints
for t in range(1, params["period"] + 1):
	genSum = 0
	for i in range(0, t+1):
		genSum += params["FhList"][i]*genK(model, "Hp", "Hn", i, t) + FlList[i]*genK(model, "Lp", "Ln", i, t)
	setattr(model, "Gen"+str(t), Constraint(expr = genSum == params["GList"][t]))

# emission constraint
emit = 0
for t in range(0, params["period"]):
	for i in range(0, t+1):
		emit += params["mhList"][i]*params["FhList"][i]*genK(model, "Hp", "Hn", i, t) + params["mlList"][i] * FlList[i]*genK(model, "Lp", "Ln", i, t)

maxEmit = params["alpha"] * sum([params["mhList"][i]*params["FhList"][i]*params["H0"] + params["mlList"][i]*FlList[0]*params["L0"] for i in N])
setattr(model, "emissions", Constraint(expr = emit <= maxEmit))


# objective function is present value of investment cost minus operating cost savings

OCh = 0
OCl = 0
for i in range(0, len(N)):
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


# objective with operating costs
model.OBJ = Objective(expr = sum([(getattr(model, "Hp"+str(i)) + getattr(model, "Lp"+str(i)))*exp(-params["r"]*i) for i in N]) - params["betah"]*OCh - params["betal"]*OCl)

#	return model





