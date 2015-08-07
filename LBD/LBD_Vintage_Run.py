from LBDhelpers import *
from LBDpyomoVintageMin import vintageModel
import time
import sys

if __name__ == "__main__":
	'''
	This module should be called from the command line to set up all parameters,
	create the model, solve and plot the results. 

	python LBD_Vintage_Run.py nameString


	nameString comes from an option when LBD_Vintage_Run.py is called from the command
	line. It is optional but strongly recommended so that it's easier to remember the output
	associated with a particular query and also to avoid overwriting any documentation.
	'''
	
	# cases for learning by doing
	# phi is intertemporal knowledge spillover
	# k is degree of learning by doing transfer
	phiList = [-0.5, 0.0, 0.25, 0.5, 0.75, 1.0] 
	kList =  [0, 0.5, 1]

	#alphaRange = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
	#years = [25, 50, 75, 100, 150]


	nameString = sys.argv[1]


	for phi in phiList:
		for k in kList:
				

			start = time.time()

			# generate the parameter data from the LBDhelpers module.
			# it takes the argument 'period' to generate the appropriate length
			# exogenous parameter strings. 
			params = genData(50)

			#update parameters in the case of multiple simulations
			params["phi"] = phi
			params["k"] = k



			print
			print "\t Imported parameters successfully in ", (time.time() - start)

			# Create the model and write it to disk
			model = vintageModel(params)
			print "\t Constructed model in ", (time.time() - start)
			model.write("results/model_alpha_" + str(params["alpha"])+'_years_'+str(params["period"])+ '_phi_' + str(params["phi"]) + '_k_' + str(params["k"]) + "_" + nameString + ".nl", "nl")


			# Solve the model and collect output information
			instance, solverStatus, terminationCondition = NLmodelSolve(model)

			# Get solution and constraint values
			constraintDict = getConstraints(instance)
			varDict = getVars(instance)

			# generate all the graphs
			print "\t Generating graphs in ", (time.time() - start)
			genVintPlot(params, constraintDict, varDict, nameString)


			# optional check whether constraints are feasible in stdout. The 
			# 'writesolution' module below will do the same check and write to a csv
			# for checking at some later point. Turning on 'checkconstraintfeasibility'
			# below is useful for real-time debugging
			print "\t Checking Constraints in ", (time.time() - start)
			#checkConstraintFeasibility(params, varDict, constraintDict)
			writeSolution(params, varDict, constraintDict, nameString = nameString)


			# update solverstatus.txt with new information. 
			# note that "a" means that new information will be appended to an existing file
			# and that you should be careful to check the timestamp of the runs you see
			# in the document to verify you're looking at the correct line
			f = open("results/solverStatus.txt", "a")
			f.write(time.asctime() + " alpha " + str(params["alpha"])+ " years " + str(params["period"]) + " phi " +str(params["phi"]) + ' k ' + str(params["k"]) + " type of simulation " + nameString +" solver status " + str(solverStatus) + " termination condition is " + str(terminationCondition) + "\n")

			print
			print
			print "\t Done in ", (time.time() - start)






