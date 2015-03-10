import pulp
import numpy as np

# where n is # of periods to consider
def Solver(period, nh, nl, FlList, FhList, elList, ehList, alpha, H0, L0, r, GList):

	#initialise the model
	cost_model = pulp.LpProblem("n-period-capital-min", pulp.LpMinimize)

	# initialize variable names
	# "H" are positive infrastructure investments in high-emitting K
	# "L" are positive infrastructure investments in low-emitting K
	Hp = ["Hp_" + str(i) for i in range(1, period+1)]
	Hn = ["Hn_" + str(i) for i in range(1, period+1)]

	Lp = ["Lp_" + str(i) for i in range(1, period+1)]
	Ln = ["Ln_" + str(i) for i in range(1, period+1)]

	# initial values of capital in each sector
	HpVar = [H0]
	HnVar = [0]
	LpVar = [L0]
	LnVar = [0]

	# add variables to pulp and put them in lists for access later
	for hval in Hp:
		val = pulp.LpVariable(hval, lowBound=0.0, upBound=None, cat='Continuous', e = None)
		HpVar.append(val)

	for hval in Hn:
		val = pulp.LpVariable(hval, lowBound=0.0, upBound=None, cat='Continuous', e = None)
		HnVar.append(val)

	for lval in Lp:
		val = pulp.LpVariable(lval, lowBound=0.0, upBound=None, cat='Continuous', e = None)
		LpVar.append(val)

	for lval in Ln:
		val = pulp.LpVariable(lval, lowBound=0.0, upBound=None, cat='Continuous', e = None)
		LnVar.append(val)


	# sum over positive investments as objective function, ignoring first investments
	#cost_model += sum([LpVar[i] for i in range(len(LpVar))]) + sum([HpVar[i] for i in range(len(HpVar))]) - H0 - L0

	costSum = 0
	for i in range(1, period+1):
		costSum += (LpVar[i] + HpVar[i])/(1 + r)**i

	cost_model += costSum

	# emissions constraint
	emit = 0
	for t in range(0, period+1): # index through the summation for clarity/ease
		for i in range(0,t+1):
			highEmit = ehList[t] * FhList[t] * (HpVar[i] - HnVar[i]) * (1.0-1.0/float(nh))**(t-i)		
			lowEmit  = elList[t] * FlList[t] * (LpVar[i] - LnVar[i]) * (1.0-1.0/float(nl))**(t-i)
			emit += highEmit + lowEmit

	cost_model += emit <= alpha*(period+1)*(ehList[0]*FhList[0]*H0 + elList[0]*FlList[0]*L0)
	
	#print "Emissions Constraint is:"
	#print emit
	#print alpha*(period+1)*(ehList[0]*FhList[0]*H0 + elList[0]*FlList[0]*L0)
	#print 

	# energy demand constraints
	for t in range(1, period+1): # index through the summation for clarity/ease
		gen = 0
		for i in range(1,t+1):
			iGen = FhList[t] * (HpVar[i] - HnVar[i]) * (1.0-1.0/float(nh))**(t-i) + FlList[t] * (LpVar[i] - LnVar[i]) * (1.0-1.0/float(nl))**(t-i)	
			gen += iGen
		cost_model += gen + FhList[t]*H0*(1-1.0/float(nh))**t + FlList[t]*L0*(1-1.0/float(nl))**t == float(GList[t])

		
		#print 
		#print "Generation Constraint in Year ", t
		#print gen
		#print gen + FhList[t]*H0*(1-1.0/float(nh))**t + FlList[t]*L0*(1-1.0/float(nl))**t, " must equal ", float(GList[t])
		#print 

	# investments cannot be negative
	for i in range(1, period+1):
		cost_model += HpVar[i] >= 0.0
		cost_model += HnVar[i] >= 0.0
		cost_model += LpVar[i] >= 0.0
		cost_model += LnVar[i] >= 0.0


	# solve model
	cost_model.solve()

	minCost = pulp.value(cost_model.objective)

	# create list of optimal decision variable values
	HpinvestSolution = []
	HninvestSolution = []
	LpinvestSolution = []
	LninvestSolution = []

	for i in range(1, period+1):
		HpinvestSolution.append(pulp.value(HpVar[i]))
		HninvestSolution.append(pulp.value(HnVar[i]))
		LpinvestSolution.append(pulp.value(LpVar[i]))
		LninvestSolution.append(pulp.value(LnVar[i]))


	cost_model.writeLP("capital.lp", writeSOS=1, mip=1)
	
	solved = cost_model.status

	return minCost, solved, np.array(HpinvestSolution), np.array(HninvestSolution), np.array(LpinvestSolution), np.array(LninvestSolution)

