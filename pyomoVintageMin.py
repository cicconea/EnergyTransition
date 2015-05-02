from __future__ import division
from pyomo.environ import *
from math import exp
from func_gen import *


L0 = 2005.0 * 10**3 * 0.3 * 3827.0 # initial low emitting capital 
H0 = (336341.0 + 485957.0) * 10**3 * 0.5 * 1714.0 # intial coal + ng high emitting capital 
	# MW * 1000kW/MW * capacity * $/kW from Fh_0 or Fl_0

alpha = 0.5 # emissions reduction fraction
betah = 0.4 # fraction of yearly operating costs
betal = 0.05 # fraction of yearly operating costs

r = 0.05 # interest rate

kWperYearTokWh = 8760.0 # conversion of 1 kW power capacity for 1 year to kWh energy

Fh_0 = 0.0006 * 0.5 * kWperYearTokWh # base high emitting efficiency kW/$ * kWh conversion * capacity factor
Fh_m = 3*0.5*10**-6 * kWperYearTokWh # linear slope high emitting efficiency * kWh conversion * capacity factor 
Fl_0 = (1.0/3827.0)*0.3 * kWperYearTokWh # base low emitting efficiency kW/$ * kWh conversion * capacity factor
Fl_m = 0.01 # linear slope low emitting efficiency

el_0 = 0.0 # base emissions for low-intensity capital in lbs CO2/kWh
el_m = -0.1 # linear slope emissions for low-intensity capital
eh_0 = 1.6984 # base emissions for high intensity capital in lbs CO2/kWh
eh_m = -0.0031 # slope emissions for high-intensity capital

G_0 = 2798.5 * 10**9 # billion kWh electricity demanded
G_m = 32.238 * 10**9 # annual growth in demand for electricity in billion kWh

period = 3 # simulation length (!= to n)
treaty = 100 # number of years of treaty length - must be less than period
n = 20 # depreciation length for high emitting
#nl = 10 # depreciation length for low emitting



# initialize model
model = ConcreteModel()
 
N = range(0, period)

# create variables
# Hp_i is the positive investment in high over all years list of all years
for i in range(0, period):
        setattr(model,"Hp"+str(i),Var(N, domain=NonNegativeReals))
        setattr(model,"Hn"+str(i),Var(N, domain=NonNegativeReals))
        setattr(model,"Lp"+str(i),Var(N, domain=NonNegativeReals))
        setattr(model,"Ln"+str(i),Var(N, domain=NonNegativeReals))


# this function builds an expression for capital in time t for capital Hp/Hn/Lp/Ln of age i
# varRange is model.Hp_
# sum from initial investment period i through existing time period t
def genKExprsn(pVar, nVar, i, t):
	K = getattr(model, pVar+str(i))[i] * exp((i-t)/n) - sum([getattr(model, nVar+str(i))[j] for j in range(i, t+1)])
	return K

# can't have values for investments that happen before the year in which they're initialized
for i in range(0, period):
	for t in range(0, period):
		if t<i:
			setattr(model, "HpTimeLogic"+str(i)+str(t), Constraint(expr = getattr(model, "Hp"+str(i))[t] == 0))
			setattr(model, "HnTimeLogic"+str(i)+str(t), Constraint(expr = getattr(model, "Hn"+str(i))[t] == 0))
			setattr(model, "LpTimeLogic"+str(i)+str(t), Constraint(expr = getattr(model, "Lp"+str(i))[t] == 0))
			setattr(model, "LnTimeLogic"+str(i)+str(t), Constraint(expr = getattr(model, "Ln"+str(i))[t] == 0))

		# also set all non-negativity constraints for capital
		setattr(model, "KhNonNeg"+str(i)+"-"+str(t), Constraint(expr = genKExprsn("Hp", "Hn", i, t) >= 0))
		setattr(model, "KlNonNeg"+str(i)+"-"+str(t), Constraint(expr = genKExprsn("Lp", "Ln", i, t) >= 0))


#initialize starting points
model.Hp0Cons = Constraint(expr = model.Hp0[0] == H0)
model.Hn0Cons = Constraint(expr = model.Hn0[0] == 0)
model.Lp0Cons = Constraint(expr = model.Lp0[0] == L0)
model.Ln0Cons = Constraint(expr = model.Ln0[0] == 0)



# generate power demand over time
GList = linGen(period, G_0, G_m, minimum = 0.0, maximum = 6.0 *10.0 **12) # energy demand over time
# generate costs and emissions levels 
# logistic arguments: (k, initial, increasing, randomAllowed, scale = 0.5, minVal= 0, maxVal=1)
# randomAllowed = True varies scale (rate) of change of the trajectory
# low emitting efficiency trajectory min is half of base, max is efficiency of natural gas ($917/kW) at 30% capacity
FlScale, FlList = logistic(period, Fl_0, True, False, scale = 5/100.0, minVal=0.34334988, maxVal=2.8658669) 
# weighted average of coal and NG. Max is 1/917 * 8760 * 0.5
FhList = linGen(period, Fh_0, Fh_m, maximum=4.7764449) # high emitting efficiency trajectory 
# low emitting carbon intensity trajectory - constant
mlList = consGen(period, el_0)
# high emitting carbon intensity trajectory - minimum is emission from 100% natural gas.
mhList = linGen(period, eh_0, eh_m, minimum=1.22) 

# generation constraints
for t in range(1, period):
	genSum = 0
	for i in range(0, t+1):
		genSum += FhList[i]*genKExprsn("Hp", "Hn", i, t) + FlList[i]*genKExprsn("Lp", "Ln", i, t)
	setattr(model, "Gen"+str(t), Constraint(expr = genSum == GList[t]))


# emission constraint
emit = 0
for t in range(0, period):
	for i in range(1, t+1):
		emit += mhList[i]*FhList[i]*genKExprsn("Hp", "Hn", i, t) + mhList[i] * FlList[i]*genKExprsn("Lp", "Ln", i, t)

setattr(model, "emissions", Constraint(expr = emit <= alpha * period *(mhList[0]*FhList[0]*H0 + mlList[0]*FlList[0]*L0)))


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


model.OBJ = Objective(expr = sum([(getattr(model, "Hp"+str(i))[i] + getattr(model, "Lp"+str(i))[i])*exp(-r*i) for i in N]) - betah*OCh - betal*OCl)













