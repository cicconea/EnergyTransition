from __future__ import division
from pyomo.environ import *
from math import exp
from func_gen_simple import *
from pyomo.opt import SolverFactory



L0 = 2005.0 * 10**3 * 0.3 * 3827.0 # initial low emitting capital 
H0 = (336341.0 + 485957.0) * 10**3 * 0.5 * 1714.0 # intial coal + ng high emitting capital 
	# MW * 1000kW/MW * capacity * $/kW from Fh_0 or Fl_0

alpha = 0.5 # emissions reduction fraction
beta = 0.4 # fraction of yearly operating costs
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

period = 50 # simulation length (!= to n)
treaty = 100 # number of years of treaty length - must be less than period
n = 20 # depreciation length for high emitting
#nl = 10 # depreciation length for low emitting




# generate efficiency and carbon intensity data
GList = linGen(period + 1, G_0, G_m, minimum = 0.0, maximum = 6.0 *10.0 **12) # energy demand over time
# logistic arguments: (k, initial, increasing, randomAllowed, scale = 0.5, minVal= 0, maxVal=1)
# randomAllowed = True varies scale (rate) of change of the trajectory
FlScale, FlList = logistic(period+1, Fl_0, True, False, scale = 5/100.0, minVal=0.34334988, maxVal=2.8658669) # low emitting efficiency trajectory
	# min is half of base, max is efficiency of natural gas ($917/kW) at 30% capacity
FhList = linGen(period+1, Fh_0, Fh_m, maximum=4.7764449) # high emitting efficiency trajectory 
	# weighted average of coal and NG. Max is 1/917 * 8760 * 0.5
	
mlList = consGen(period+1, el_0) # low emitting carbon intensity trajectory
	# constant 
mhList = linGen(period+1, eh_0, eh_m, minimum=1.22) # high emitting carbon intensity trajectory
	# minimum is emission from 100% natural gas.




def pyomoSimple(period, GList, FhList, FlList, mhList, mlList, alpha, H0, L0, r, n):
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
		return initial * exp(-t/n) + sum([pVar[j] * exp(j-t/n) - nVar[j] for j in range(1, t+1)])

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


	# Create a model instance and optimize
	opt = SolverFactory('glpk')
	instance = model.create()
	results = opt.solve(instance)
	return results



