from __future__ import division
from pyomo.environ import *
from math import exp
from helpers import *


f = open("mc.txt", "r")
alpha = float(f.read())/100
f.close()

GList, FlList, FhList, mlList, mhList, period, H0, L0, r, n = genDataA()


# initialize model
model = ConcreteModel()


N = range(1, period+1)

# create variables
model.Hp = Var(N, domain=NonNegativeReals)
model.Hn = Var(N, domain=NonNegativeReals)
model.Lp = Var(N, domain=NonNegativeReals)
model.Ln = Var(N, domain=NonNegativeReals)


# this function builds an expression for capital in time t for capital Hp/Hn/Lp/Ln
def genK(initial, pVar, nVar, t):
	capital = initial * exp(-t/n) + sum([pVar[j] * exp((j-t)/n) - nVar[j] for j in range(1, t+1)])
	return capital

# also set all non-negativity constraints for capital
for t in range(1, period+1):
	setattr(model, "KhNonNeg"+str(t), Constraint(expr = genK(H0, model.Hp, model.Hn, t) >= 0))
	setattr(model, "KlNonNeg"+str(t), Constraint(expr = genK(L0, model.Lp, model.Ln, t) >= 0))

# generation constraints
for t in range(1, period+1):
	setattr(model, "Gen"+str(t), Constraint(expr = FhList[t]*genK(H0, model.Hp, model.Hn, t) + FlList[t]*genK(L0, model.Lp, model.Ln, t) == GList[t]))

# emission constraint
emit = 0
for t in range(1, period+1):
	emit += mhList[t]*FhList[t]*genK(H0, model.Hp, model.Hn, t) + mlList[t]*FlList[t]*genK(L0, model.Lp, model.Ln, t)
model.emissions = Constraint(expr = emit <= alpha * period *(mhList[0]*FhList[0]*H0 + mlList[0]*FlList[0]*L0))

# sum over positive investments as objective function
model.OBJ = Objective(expr = sum([(model.Hp[i] + model.Lp[i])*exp(-r*i) for i in N]))





