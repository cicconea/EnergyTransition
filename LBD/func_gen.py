import math


# generates a k-length list w/ intercept base and slope mod
# add minimum to allow a theoretical limit to efficiency/carbon intensity
def linGen(k, base, mod, minimum=0, maximum=10):
	if minimum > maximum:
		raise ValueError('Minimum greater than Max in LinGen')

	returnList = []
	for i in range(k):
		number = base + mod*i
		if number < minimum:
			number = minimum
		if number > maximum:
			number = maximum
		returnList.append(number)
	return returnList			

# generates a k-length list of constant values = base
def consGen(k, base):
	returnList = []
	for i in range(k):
		returnList.append(base)
	return returnList


# mean, scale are positive, increasing is boolean and minVal/maxVal are limits of
# logistic curve. randomAllowed is boolean for adding random noise to simulation
def logistic(k, initial, increasing, randomAllowed, scale = 0.5, minVal= 0, maxVal=1):
	returnList = [initial]	

	#print maxVal

	if randomAllowed == True:
		scale = truncGaussian(scale, 0, 5)
	
	if increasing == True:
		priorY = initial - minVal
		diff = maxVal - minVal
		for i in range(1, k):
			dpdt = scale*priorY*(1-(priorY/diff))
			appendY = dpdt + priorY
			if appendY + minVal > maxVal:
				appendY = maxVal-minVal
			if appendY + minVal < initial:
				appendY = initial-minVal

			returnList.append(appendY + minVal)
			priorY = appendY        

	if increasing == False:
		priorY = maxVal - initial
		diff = maxVal - minVal
		for i in range(1, k):
			dpdt = scale*priorY*(1-(priorY/diff))
			appendY = priorY + dpdt
			returnList.append(maxVal - appendY)
			priorY = appendY    
	return scale, returnList





