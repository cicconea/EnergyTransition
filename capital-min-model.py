import pulp
import matplotlib.pyplot as plt
import math


L0 = 0.0 # initial low emitting capital
H0 = 1000.0 # intial high emitting capital

alpha = 0.5 # emissions reduction fraction
r = 0.05 # interest rate

Fh_0 = 0.1 # base high emitting efficiency MW/unit
Fh_m = 0.01 # slope high emitting efficiency
Fl_0 = 0.05 # base low emitting efficiency MW/unit
Fl_m = 0.01 # slope low emitting efficiency

el_0 = 1.0 # base emissions for low-intensity capital
el_m = -0.1 # slope emissions for low-intensity capital
eh_0 = 5.0 # base emissions for high-intensity capital
eh_m = -0.1 # slope emissions for high-intensity capital

maxLEff = 0.3 # maximum Fl efficiency MW/$


G_0 = 1000.0 # MW electricity demanded
G_m = 50.0 # annual growth in demand for MW

# generates a n-length log growth list w/ initial base and decay mod (mod must be negative)
# add minimum to allow a theoretical limit to efficiency/carbon intensity

def logGen(n, base, mod, maximum):
	returnList = [base]
	for i in range(1, n):
		number = base * math.log(mod*i) + base
		if number > maximum:
			number = maximum
		returnList.append(number)
	return returnList

# generates a n-length exponential decay list w/ initial base and decay mod (mod must be negative)
# add minimum to allow a theoretical limit to efficiency/carbon intensity

def expGen(n, base, mod, minimum):
	returnList = []
	for i in range(n):
		number = base * math.exp(mod*i)
		if number < minimum:
			number = minimum
		returnList.append(number)
	return returnList			

# generates a n-length list w/ intercept base and slope mod
# add minimum to allow a theoretical limit to efficiency/carbon intensity
def linGen(n, base, mod, minimum):
	returnList = []
	for i in range(n):
		number = base + mod*i
		if number < minimum:
			number = minimum
		returnList.append(number)
	return returnList			

# generates a n-length list of constant values = base
def consGen(n, base):
	returnList = []
	for i in range(n):
		returnList.append(base)
	return returnList


# where n is # of periods to consider
def Solver(n):
	#initialise the model
	cost_model = pulp.LpProblem("n-period-capital-min", pulp.LpMinimize)

	# initialize variable names
	# "H" are positive infrastructure investments in high-emitting K
	# "L" are positive infrastructure investments in low-emitting K
	Hp = ["Hp_" + str(i) for i in range(1, n+1)]
	Hn = ["Hn_" + str(i) for i in range(1, n+1)]

	Lp = ["Lp_" + str(i) for i in range(1, n+1)]
	Ln = ["Ln_" + str(i) for i in range(1, n+1)]

	# initial values of capital in each sector
	HpVar = [H0]
	HnVar = [0]
	LpVar = [L0]
	LnVar = [0]

	# add variables to pulp and put them in lists for access later
	for hval in Hp:
		val = pulp.LpVariable(hval, lowBound=0.0, cat='Continuous')
		HpVar.append(val)

	for hval in Hn:
		val = pulp.LpVariable(hval, lowBound=0.0, cat='Continuous')
		HnVar.append(val)

	for lval in Lp:
		val = pulp.LpVariable(lval, lowBound=0.0, cat='Continuous')
		LpVar.append(val)

	for lval in Ln:
		val = pulp.LpVariable(lval, lowBound=0.0, cat='Continuous')
		LnVar.append(val)


	print LnVar

	# generate efficiency and carbon intensity data

	Fl = logGen(n, Fl_0, Fl_m, maxLEff) # low emitting efficiency trajectory
	Fh = consGen(n, Fh_0) # high emitting efficiency trajectory assuming no efficiency improvement

	el = consGen(n, el_0) # low emitting carbon intensity trajectory
	eh = linGen(n, eh_0, eh_m, 0) # high emitting carbon intensity trajectory

	G = consGen(n, G_0) # energy demand over time


	# sum over positive investments as objective function, ignoring first investments
	#cost_model += sum([LpVar[i] for i in range(len(LpVar))]) + sum([HpVar[i] for i in range(len(HpVar))]) - H0 - L0


	costSum = 0
	for i in range(1, n+1):
		costSum += LpVar[i] + HpVar[i]

	cost_model += costSum


	# emissions constraint
	emit = 0
	for t in range(0, n): # index through the summation for clarity/ease
		for i in range(0,t):
			highEmit = eh[t] * Fh[t] * (HpVar[i] + HnVar[i]) * (1.0-1.0/float(n))**(t-i)		
			lowEmit  = el[t] * Fl[t] * (LpVar[i] + LnVar[i]) * (1.0-1.0/float(n))**(t-i)
			emit += highEmit + lowEmit

	cost_model += emit <= alpha*n*(eh_0*Fh_0*H0 + el_0*Fl_0*L0)


	# energy demand constraints
	for t in range(0, n): # index through the summation for clarity/ease
		gen = 0
		for i in range(0,t):
			iGen = Fh[t] * (HpVar[i] + HnVar[i]) * (1.0-1.0/float(n))**(t-i) + Fl[t] * (LpVar[i] + LnVar[i]) * (1.0-1.0/float(n))**(t-i)	
			gen += iGen
		cost_model += gen == float(G[t])




	# investments cannot be negative
	for i in range(1, n+1):
		cost_model += HpVar[i] >= 0
		cost_model += HnVar[i] >= 0
		cost_model += LpVar[i] >= 0
		cost_model += LnVar[i] >= 0




	cost_model.solve()

	HinvestSolution = []
	LinvestSolution = []
	for i in range(1, n+1):
		HinvestSolution.append((pulp.value(HpVar[i]), pulp.value(HnVar[i])))
		LinvestSolution.append((pulp.value(LpVar[i]), pulp.value(LnVar[i])))



	#cost_model.writeLP("10-period-efficiency-model.lp", writeSOS=1, mip=1)
	
	return HinvestSolution, LinvestSolution



print Solver(10)

