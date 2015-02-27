import pulp

L0 = 0.0 # initial low emitting capital
H0 = 1000.0 # intial high emitting capital

alpha = 0.5 # emissions reduction fraction
r = 0.05 # interest rate

Fh_0 = 0.1 # base high emitting efficiency MW/unit
Fh_m = 0.01 # slope high emitting efficiency
Fl_0 = 0.05 # base low emitting efficiency MW/unit
Fl_m = 0.1 # slope low emitting efficiency

el_0 = 1.0 # base emissions for low-intensity capital
el_m = -0.1 # slope emissions for low-intensity capital
eh_0 = 5.0 # base emissions for high-intensity capital
eh_m = -0.1 # slope emissions for high-intensity capital

maxLEff = 0.3 # maximum Fl efficiency MW/$


G_0 = 1000.0 # MW electricity demanded
G_m = 50.0 # annual growth in demand for MW



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


	# sum over positive investments as objective function, ignoring first investments
	#cost_model += sum([LpVar[i] for i in range(len(LpVar))]) + sum([HpVar[i] for i in range(len(HpVar))]) - H0 - L0

	costSum = 0
	for i in range(1, period+1):
		costSum += LpVar[i] + HpVar[i]
	cost_model += costSum



	# emissions constraint
	emit = 0
	for t in range(0, period): # index through the summation for clarity/ease
		for i in range(0,t):
			highEmit = ehList[t] * FhList[t] * (HpVar[i] + HnVar[i]) * (1.0-1.0/float(nh))**(t-i)		
			lowEmit  = elList[t] * FlList[t] * (LpVar[i] + LnVar[i]) * (1.0-1.0/float(nl))**(t-i)
			emit += highEmit + lowEmit

	cost_model += emit <= alpha*period*(eh_0*Fh_0*H0 + el_0*Fl_0*L0)


	# energy demand constraints
	for t in range(0, period): # index through the summation for clarity/ease
		gen = 0
		for i in range(0,t):
			iGen = FhList[t] * (HpVar[i] + HnVar[i]) * (1.0-1.0/float(nh))**(t-i) + FlList[t] * (LpVar[i] + LnVar[i]) * (1.0-1.0/float(nl))**(t-i)	
			gen += iGen
		cost_model += gen == float(GList[t])


	# investments cannot be negative
	for i in range(1, period+1):
		cost_model += HpVar[i] >= 0
		cost_model += HnVar[i] >= 0
		cost_model += LpVar[i] >= 0
		cost_model += LnVar[i] >= 0


	# solve model
	cost_model.solve()


	# create list of optimal decision variable values
	HinvestSolution = []
	LinvestSolution = []
	for i in range(1, period+1):
		HinvestSolution.append((pulp.value(HpVar[i]), pulp.value(HnVar[i])))
		LinvestSolution.append((pulp.value(LpVar[i]), pulp.value(LnVar[i])))



	cost_model.writeLP("capital.lp", writeSOS=1, mip=1)
	
	return HinvestSolution, LinvestSolution

