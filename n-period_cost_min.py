import pulp
import matplotlib.pyplot as plt

Kh = 100
C1 = 1
C2 = 3
CER1 = 2
CER2 = 2
alpha = 1.0

n=10

for i in range(1, 2*n+2, 2):
	print i

def costSolver(d, n):
	#initialise the model
	cost_model = pulp.LpProblem("n-period-cost-min", pulp.LpMinimize)

	# initialize variable names
	values = ["I_" + str(i) for i in range(1, n+1)]
	# create a dictionary of pulp variables with keys from values
	variables = pulp.LpVariable.dict("%s", values)


	# cost data
	cost = dict(zip(values, [0.013, 0.008, 0.010, 0.002, 0.005, 0.001]))
	# create the objective
	whiskas_model += sum( [cost[i] * x[i] for i in values])



	# create the objective
	cost_model += ((I1 + Kh/n)*(C1) + I1*CER1)*d + ((I2 + Kh/n)*(C2) + I2*CER2)*(d**2)

	# describe constraints


	# emissions constraint
	cost_model += sum([variables[i] for i in values]) - (Kh/n)*(2*alpha - 1) >= 0.0 
	
	# capital constraints 
	for i in range(1, 2*n+1, 2):
		print i
		cost_model += I1 >= 0.0 
		cost_model += I1 <= Kh
		cost_model += I1 + I2 + Kh/n >= 0.0  
		cost_model += I1 + I2 <= Kh/2 

	cost_model.solve()

	return pulp.value(I1), pulp.value(I2)


investments1 = []
investments2 = []
delta = []

for d in range(0,100, 1):
	delt = d/100.0
	delta.append(delt)
	#invest1, invest2 = costSolver(delt)
	#investments1.append(invest1)
	#investments2.append(invest2)
	#print delt, invest1, invest2



#plt.plot(delta, investments1)
#plt.plot(delta, investments2)
#plt.show()

