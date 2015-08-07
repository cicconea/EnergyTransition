from LBDhelpers import *
from LBDpyomoVintageMin import vintageModel
import time
import sys

if __name__ == "__main__":
	'''
	This module should be called from the command line to set up all parameters,
	create the model, solve and plot the results. 
	'''
	
	# cases for learning by doing
	# phi is intertemporal knowledge spillover
	# k is degree of learning by doing transfer
	#phiList = [-0.5, 0.0, 0.25, 0.5, 0.75, 1.0, 1.5] 
	#kList =  [0, 0.5, 1]

	yearRange = [25, 50, 75, 100, 150]

	for year in yearRange:

		start = time.time()

		# generate the parameter data from the LBDhelpers module.
		params = genData()

		#update parameters for multiple simulations
		params["period"] = year
		params["alpha"] = params["CommittedReduction"][year]



		print
		print "\t Imported parameters successfully in ", (time.time() - start)

		# Create the model
		model = vintageModel(params)
		print "\t Constructed model in ", (time.time() - start)
		model.write("model_alpha_" +  str(params["alpha"]) + "_period_" + str(params["period"]) + ".nl", "nl")


		# Solve the model
		instance, solverStatus, terminationCondition = NLmodelSolve(model)

		# Get solution and constraint values
		constraintDict = getConstraints(instance)
		varDict = getVars(instance)


		#if str(solverStatus) != "warning":
		print "\t Generating graphs in ", (time.time() - start)
		genVintPlot(params, constraintDict, varDict)

		print "\t Checking Constraints in ", (time.time() - start)
		checkConstraintFeasibility(params, varDict, constraintDict)


		f = open("solverStatus.txt", "a")
		f.write(time.asctime() + " alpha is " + str(params["alpha"])+ " years are " + str(params["period"]) + " " +str(solverStatus) + " " + str(terminationCondition) + '\n')
		f.close

		writeSolution(params, varDict, constraintDict, nameString = sys.argv[1])



		print
		print
		print "\t Done in ", (time.time() - start)






