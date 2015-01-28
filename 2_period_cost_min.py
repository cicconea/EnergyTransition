import pulp
import matplotlib.pyplot as plt

Kh = 100
C1 = 1
C2 = 3
CER1 = 2
CER2 = 2
alpha = 1.0
n = 2.0


def costSolver(d):
	#initialise the model
	cost_model = pulp.LpProblem("2-period-cost-min", pulp.LpMinimize)

	# make a list of ingredients
	I1 = pulp.LpVariable("I1", -Kh, Kh)
	I2 = pulp.LpVariable("I2", -Kh, Kh)


	# create the objective
	cost_model += ((I1 + Kh/n)*(C1) + I1*CER1)*d + ((I2 + Kh/n)*(C2) + I2*CER2)*(d**2)

	# describe constraints
	cost_model += I1 + I2 - (Kh/n)*(2*alpha - 1) >= 0.0 
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
	invest1, invest2 = costSolver(delt)
	investments1.append(invest1)
	investments2.append(invest2)
	print delt, invest1, invest2



#plt.plot(delta, investments1)
#plt.plot(delta, investments2)
#plt.show()

