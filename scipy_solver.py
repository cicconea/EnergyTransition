from scipy.optimize import minimize



# initial values of capital in each sector
HpVar = [H0]
HnVar = [0]
LpVar = [L0]
LnVar = [0]

# generate variables
Hp = ["Hp_" + str(i) for i in range(1, period+1)]
Hn = ["Hn_" + str(i) for i in range(1, period+1)]

Lp = ["Lp_" + str(i) for i in range(1, period+1)]
Ln = ["Ln_" + str(i) for i in range(1, period+1)]

Hp = HpVar + Hp
Hn = HnVar + Hn
Lp = LpVar + Lp
Ln = LnVar + Ln

# set up cost function
def costObjective(Hp, Lp):
	return [(Hp[i]+Lp[i])/((1 + r)**i) + 0 * (Hn[i] + Ln[i]) for i in range(period)]

# set up constraint functions to call later
# emissions constraint first:
def emitConstraint(ehList, elList, FhList, FlList, nh, nl, alpha, period): 
	emit = 0
	maxEmit = alpha*period*(ehList[0]*FhList[0]*Hp[0] + elList[0]*FlList[0]*Lp[0])
	for t in range(1, period): # index through the summation for clarity/ease
		for i in range(0,t):
			highEmit = ehList[t] * FhList[t] * (Hp[i] + Hn[i]) * (1.0-1.0/float(nh))**(t-i)		
			lowEmit  = elList[t] * FlList[t] * (Lp[i] + Ln[i]) * (1.0-1.0/float(nl))**(t-i)
			emit += highEmit + lowEmit
	return maxEmit - emit


# need to create list of generation constraints
# returns list of period-1 constraints
def EnergyGeneratorConstraints(FhList, FlList, nh, nl, period):
	genConsList = []
	for t in range(1, period): # index through the summation for clarity/ease
		gen = 0
		for i in range(1,t):
			iGen = FhList[t] * (Hp[i] + Hn[i]) * (1.0-1.0/float(nh))**(t-i) + FlList[t] * (Lp[i] + Ln[i]) * (1.0-1.0/float(nl))**(t-i)	
			gen += iGen
		gen = gen - float(GList[t])

		genConsList.append(gen)	

	return genConsList


# set up emissions constraint in appropriate format
emitConstraint = ({"type": "ineq" , "fun": emitConstraint(ehList, elList, FhList, FlList, nh, nl, alpha, period), "args": [ehList, elList, FhList, FlList, nh, nl, alpha, period})

# set up generation constraints in appropriate format
genConstraint = ()
genValues = EnergyGeneratorConstraints(FhList, FlList, nh, nl, period)
for i in range(len(genValues)):
	genDict = {}
	genDict["type"] = "eq"
	genDict["fun"] = genValues[i]
	genDict["args"] = [FhList, FlList, nh, nl, period]
	genConstraint += (genDict)


emissionAndDemandConstraints = (emitConstraint, genConstraint)

# set up bounds for all decision variables
# must be non-negative

nonNegative = (0, None)
bounds = ()
initGuess = ()
guess = (0.0, 0.0)
for i in range(1, period+1):
	bounds += bounds + nonNegative
	initGuess += initGuess + guess



#The optimization problem is solved using the SLSQP method as:

minSolver = minimize(costObjective, initGuess, method='SLSQP', bounds=bounds, constraints=emissionAndDemandConstraints)



print minSolver.success





