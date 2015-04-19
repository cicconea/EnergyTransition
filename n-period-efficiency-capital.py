import pulp
import matplotlib.pyplot as plt
import math


Kl = 0.0 # initial low emitting capital
Kh = 1000.0 # intial high emitting capital
CER_0 = 1.0 # base early retirement cost
CER_m = 0.1 # slope early retirement cost
alpha = 0.001 # emissions reduction fraction
el_0 = 0.0 # base emissions for low-intensity capital
eh_0 = 100.0 # base emissions for high-intensity capital
r = 0.05 # interest rate

Fh_0 = 0.1 # base high emitting efficiency MW/unit
Fh_m = 0.01 # slope high emitting efficiency
Fl_0 = 0.05 # base low emitting efficiency MW/unit
Fl_m = 0.01 # slope low emitting efficiency

el_0 = 1.0 # base emissions for low-intensity capital
el_m = 0.1 # slope emissions for low-intensity capital
eh_0 = 5.0 # base emissions for high-intensity capital
eh_m = 0.1 # slope emissions for high-intensity capital


G = 1000.0 # MW electricity demanded


# generates a n-length list w/ initial base and decay mod (mod must be negative)
def expGen(n, base, mod):
	returnList = []
	for i in range(1, n+1):
		number = base * math.exp(mod*i)
		returnList.append(number)
	return returnList			

# generates a n-length list w/ intercept base and slope mod
def linGen(n, base, mod):
	returnList = []
	for i in range(1, n+1):
		number = base + mod*i
		returnList.append(number)
	return returnList			

# generates a n-length list of constant values = base
def consGen(n, base):
	returnList = []
	for i in range(1, n+1):
		returnList.append(base)
	return returnList


# where n is # of periods to consider
def Solver(n):
	#initialise the model
	cost_model = pulp.LpProblem("n-period-cost-min", pulp.LpMinimize)

	# initialize variable names
	# "H" are positive infrastructure investments in high-emitting K
	# "L" are positive infrastructure investments in low-emitting K
	Hvalues = ["H_" + str(i) for i in range(1, n+1)]
	Lvalues = ["L_" + str(i) for i in range(1, n+1)]

	# create a dictionary of pulp variables with keys from values
	Hvar = pulp.LpVariable.dict("%s", Hvalues)
	Lvar = pulp.LpVariable.dict("%s", Lvalues)

	# generate efficiency and carbon intensity data

	Fl = linGen(n, Fl_0, Fl_m) # low emitting efficiency trajectory
	Fh = linGen(n, Fh_0, Fh_m) # high emitting efficiency trajectory

	el = linGen(n, el_0, el_m) # low emitting carbon intensity trajectory
	eh = linGen(n, eh_0, eh_m) # high emitting carbon intensity trajectory



	# Early Retirement Cost Data
	#ER = [] # for coefficents that modify L_t in the cost function
	#ERListCost = linGen(n, CER_0, CER_m)
	#for i in range(1,n+1):
	#	ERcost_t = ERListCost[i-1]/(1+r)**(i)
	#	ER.append(ERcost_t)

	#ERcost = dict(zip(Lvalues, ER))


	# create the objective FIXED
	cost_model += sum([Lvar[i] for i in Lvalues if Lvar[i]>0]) + sum([Hvar[i] for i in Hvalues if Hvar[i]>0])


	# emissions constraint
	emit = 0
	for t in range(n): # index through the summation for clarity/ease
		highEmit = eh[t] * Fh[t]*(H0 * (1.0-1.0/float(n))**t + sum([Hvar[i] for i in Hvalues[:t]]) - sum([Lvar[i] for i in Lvalues[:t]]))
		lowEmit  = el[t] * Fl[t]*(L0 * (1.0-1.0/float(n))**t  - sum([Hvar[i] for i in Hvalues[:t]]) + sum([Lvar[i] for i in Lvalues[:t]]))
		emit += highEmit + lowEmit

	cost_model += emit <= alpha*n*(eh_0*Fh_0*Kh + el_0*Fl_0*Kl)


	# capital constraints  FIXED
	for t in range(1, n+1):
		cost_model += sum([Hvar[i] for i in Hvalues[:t]]) - sum([Lvar[i] for i in Lvalues[:t]]) >= -Kl - Kh*(float(t)/float(n))
		cost_model += sum([Hvar[i] for i in Hvalues[:t]]) - sum([Lvar[i] for i in Lvalues[:t]]) <= Kh*(1 - float(t)/float(n))

	# energy demand constraints
	for t in range(1, n+1):
		cost_model += sum([Hvar[i] for i in Hvalues[:t]]) - sum([Lvar[i] for i in Lvalues[:t]]) >=-G/Fh[t-1] + Kl + Kh*(float(t)/float(n))
		cost_model += sum([Hvar[i] for i in Hvalues[:t]]) - sum([Lvar[i] for i in Lvalues[:t]]) <= G/Fl[t-1] - Kh*(1 - float(t)/float(n))




	# fixed capital constraints - cannot invest more than total amount of capital in economy
	#for i in values:
	#	cost_model += variables[i] <= Kl + Kh
	#	cost_model += variables[i] >= -Kl - Kh

	# investments cannot be negative
	for i in Hvalues:
		cost_model += Hvar[i] >= 0
	for i in Lvalues:
		cost_model += Lvar[i] >= 0

	# investment can't be greater than total electricity demanded
	for j in range(n):
		cost_model += Hvar[Hvalues[j]]<= G/Fh[j]
		cost_model += Lvar[Lvalues[j]]<= G/Fl[j]




	cost_model.solve()

	HinvestSolution = []
	for i in Hvalues:
		HinvestSolution.append(pulp.value(Hvar[i]))

	LinvestSolution = []
	for i in Lvalues:
		LinvestSolution.append(pulp.value(Lvar[i]))

	cost_model.writeLP("10-period-efficiency-model.lp", writeSOS=1, mip=1)
	
	return HinvestSolution, LinvestSolution



print costSolver(10)

