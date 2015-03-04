import math
from scipy.stats import norm, truncnorm
import matplotlib.pyplot as plt

# generates a k-length log growth list w/ initial base and decay mod (mod must be negative)
# add minimum to allow a theoretical limit to efficiency/carbon intensity



def logGen(k, base, mod, maximum):
	returnList = [base]
	for i in range(1, k):
		number = base * math.log(mod*i) + base
		if number > maximum:
			number = maximum
		returnList.append(number)
	return returnList

# generates a k-length exponential decay list w/ initial base and decay mod (mod must be negative)
# add minimum to allow a theoretical limit to efficiency/carbon intensity

def expGen(k, base, mod, minimum):
	returnList = []
	for i in range(k):
		number = base * math.exp(mod*i)
		if number < minimum:
			number = minimum
		returnList.append(number)
	return returnList			

# generates a k-length list w/ intercept base and slope mod
# add minimum to allow a theoretical limit to efficiency/carbon intensity
def linGen(k, base, mod, minimum, ):
	returnList = []
	for i in range(k):
		number = base + mod*i
		if number < minimum:
			number = minimum
		returnList.append(number)
	return returnList			

# generates a k-length list of constant values = base
def consGen(k, base):
	returnList = []
	for i in range(k):
		random = truncGaussian(base, 0, 1)
		returnList.append(base)
	return returnList


def truncGaussian(var, minVal, maxVal):
# biases results towards middle of distribution. Maybe change?
	a = minVal - var
	b = maxVal - var
	print a, b
	x = truncnorm.rvs(a,b)
	print x
	return x


def Gaussian(var):
	return norm.rvs()


# mean, scale are positive, increasing is boolean and minVal/maxVal are limits of
# logistic curve. randomAllowed is boolean for adding random noise to simulation
def logistic(k, initial, increasing, randomAllowed, scale = 0.5, minVal= 0, maxVal=1):
	returnList = []	
	
	if increasing:
		priorY = initial - minVal
		diff = maxVal - minVal
		for i in range(k):
			dpdt = scale*priorY*(1-(priorY/diff))
			appendY = dpdt + priorY
			returnList.append(appendY + minVal)
			priorY = appendY        

	if not increasing:
		priorY = maxVal - initial
		for i in range(k):
			dpdt = scale*priorY*(1-(priorY/maxVal))
			appendY = dpdt + priorY
			returnList.append(maxVal - appendY + minVal)
			priorY = appendY

	if randomAllowed:
		for i in range(k):
			rdm = truncGaussian(returnList[i], minVal, maxVal)
			returnList[i] = returnList[i] + rdm

    
	return returnList


#randomTest = logistic(30, 0.1, True, True, minVal=0.05, maxVal=0.8)
#nonRandomTest = logistic(30, 0.1, True, False, minVal=0.05, maxVal=0.8)
#xRange = range(30)
#plt.plot(xRange,randomTest)
#plt.plot(xRange, nonRandomTest)

#plt.show()




