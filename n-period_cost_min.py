import pulp
import matplotlib.pyplot as plt



Kl = 0.0
Kh = 1000.0
Ch_t = 1.0
Cl_t = 1.0
CER_t = 1.0
alpha = 0.001
el = 0.0
eh = 100.0 #some sort of colinearity happening in emissions constraint
r = 0.05

# TODO
# cost generating function more generally
# solve simple version analytically


def costSolver(n):
	#initialise the model
	cost_model = pulp.LpProblem("n-period-cost-min", pulp.LpMinimize)

	# initialize variable names
	values = ["I_" + str(i) for i in range(1, n+1)]
	# create a dictionary of pulp variables with keys from values
	variables = pulp.LpVariable.dict("%s", values)


	# cost data
	investCost = [] # for coefficents that modify I_t in the cost function
	fixedCost = [] # for all othe terms independent of I_t but t-dependent

	for i in range(0,n):
		icost_t = (Cl_t - Ch_t + CER_t)/(1+r)**(i+1)
		fcost_t = (Kh*(Cl_t - Ch_t))/(n*(1+r)**(i+1))
		investCost.append(icost_t)
		fixedCost.append(fcost_t)


	icost = dict(zip(values, investCost))
	fcost = dict(zip(values, fixedCost))

	# create the objective
	cost_model += sum([icost[i] * variables[i] + fcost[i] for i in values])


	# emissions constraint
	# writing on several lines because otherwise impossible to read:
	emis = eh*Kh*(alpha*float(n) - 0.5*n + 0.5) + el*Kl*float(n)*(alpha - 1) - 0.5*el*Kh*(float(n)+1)
	cost_model += sum([variables[i] for i in values])*float(n)*(el - eh) <= emis
	

	# capital constraints 
	for t in range(1, n+1):
		cost_model += sum([variables[i] for i in values[:t]]) >= -Kl - Kh*(float(t)/float(n))
		cost_model += sum([variables[i] for i in values[:t]]) <= Kh*(1 - float(t)/float(n))

	# fixed capital constraints - weird that they are not automatically happening 
	# investigate further
	for i in values:
		cost_model += variables[i] <= Kl + Kh
		cost_model += variables[i] >= -Kl - Kh

	cost_model.solve()

	investSolution = []
	for i in values:
		investSolution.append(pulp.value(variables[i]))

	cost_model.writeLP("10-period-model.lp", writeSOS=1, mip=1)
	return investSolution


print costSolver(10)

