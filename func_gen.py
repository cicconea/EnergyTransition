import math

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