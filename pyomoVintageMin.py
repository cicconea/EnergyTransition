from __future__ import division
from pyomo.environ import *
from math import exp
from vintageHelpers import * 
from pyomo.opt import SolverFactory

from six import StringIO, iteritems

f = open("mc.txt", "r")
i = int(f.read())
f.close()



GList, FlList, FhList, mlList, mhList, period, H0, L0, alpha, r, n, betah, betal = genData(i)


# initialize model
model = ConcreteModel()
 

N = range(0, period)

# create variables
# Hp_i is the positive investment in high over all years list of all years
for i in range(0, period):
	setattr(model,"Hp"+str(i),Var(domain=NonNegativeReals))
	setattr(model,"Hn"+str(i),Var(N, domain=NonNegativeReals))
	setattr(model,"Lp"+str(i),Var(domain=NonNegativeReals))
	setattr(model,"Ln"+str(i),Var(N, domain=NonNegativeReals))


# this function builds an expression for capital in time t for capital Hp/Hn/Lp/Ln of age i
# varRange is model.Hp_
# sum from initial investment period i through existing time period t
def genKExprsn(pVar, nVar, i, t):
	K = getattr(model, pVar+str(i)) * exp((i-t)/n) - sum([getattr(model, nVar+str(i))[j] for j in range(0, t+1)])
	return K

# can't have values for investments that happen before the year in which they're initialized
for i in range(0, period):
	for t in range(0, period):
		if t<i:
			setattr(model, "HnTimeLogic"+str(i)+str(t), Constraint(expr = getattr(model, "Hn"+str(i))[t] == 0))
			setattr(model, "LnTimeLogic"+str(i)+str(t), Constraint(expr = getattr(model, "Ln"+str(i))[t] == 0))


			# also set all non-negativity constraints for capital
			#setattr(model, "KhNonNeg"+str(i)+"-"+str(t), Constraint(expr = genKExprsn("Hp", "Hn", i, t) == 0))
			#setattr(model, "KlNonNeg"+str(i)+"-"+str(t), Constraint(expr = genKExprsn("Lp", "Ln", i, t) == 0))

		elif t>=i:
			setattr(model, "KhNonNeg"+str(i)+"-"+str(t), Constraint(expr = genKExprsn("Hp", "Hn", i, t) >= 0))
			setattr(model, "KlNonNeg"+str(i)+"-"+str(t), Constraint(expr = genKExprsn("Lp", "Ln", i, t) >= 0))




#initialize starting points
model.Hp0Cons = Constraint(expr = model.Hp0 == H0)
model.Lp0Cons = Constraint(expr = model.Lp0 == L0)



# generation constraints
for t in range(1, period):
	genSum = 0
	for i in range(0, t+1):
		genSum += FhList[i]*genKExprsn("Hp", "Hn", i, t) + FlList[i]*genKExprsn("Lp", "Ln", i, t)
	setattr(model, "Gen"+str(t), Constraint(expr = genSum == GList[t]))


# emission constraint
emit = 0
for t in range(0, period):
	for i in range(0, t+1):
		emit += mhList[i]*FhList[i]*genKExprsn("Hp", "Hn", i, t) + mlList[i] * FlList[i]*genKExprsn("Lp", "Ln", i, t)

maxEmit = alpha * sum([mhList[i]*FhList[i]*H0 + mlList[i]*FlList[i]*L0 for i in N])
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
		subh *= exp(-r*t)
		subl *= exp(-r*t)
		OCh += subh
		OCl += subl



# objective with operating costs
model.OBJ = Objective(expr = sum([(getattr(model, "Hp"+str(i)) + getattr(model, "Lp"+str(i)))*exp(-r*i) for i in N]) - betah*OCh - betal*OCl)

# objective without operating costs
#model.OBJ = Objective(expr = sum([(getattr(model, "Hp"+str(i)) + getattr(model, "Lp"+str(i)))*exp(-r*i) for i in N]), sense=minimize)





def getConstraints():
	constraintDict = {}
	# Create a solver
	opt = SolverFactory('glpk')

	# Create a model instance and optimize
	instance = model.create()
	results = opt.solve(instance)

	# get the results back into the instance for easy access
	instance.load(results)

	from pyomo.core import Constraint
	for c in instance.active_components(Constraint):
		thing = getattr(instance, c)._data
		for k,v in iteritems(thing):
			constraintDict[c] = v.body()

	return constraintDict













