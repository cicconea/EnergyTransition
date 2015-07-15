from LBDhelpers import *
from LBDpyomoVintageMin import vintageModel
import time

if __name__ == "__main__":
	'''
	This module should be called from the command line to set up all parameters,
	create the model, solve and plot the results. 
	'''
	
	start = time.time()

	# generate the parameter data from the LBDhelpers module.
	params = genData()
	print
	print "\t Imported parameters successfully in ", (time.time() - start)

	# Create the model
	model = vintageModel(params)
	print "\t Constructed model in ", (time.time() - start)

	# Solve the model
	instance = NLmodelSolve(model)

	# Get solution and constraint values
	constraintDict = getConstraints(instance)
	varDict = getVars(instance)

	print "\t Generating graphs in ", (time.time() - start)
	genVintPlot(params, constraintDict, varDict)

	print "\t Done in ", (time.time() - start)






