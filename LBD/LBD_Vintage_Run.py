from LBDhelpers import *
from LBDpyomoVintageMin import vintageModel
import time
import csv

if __name__ == "__main__":
	'''
	This module should be called from the command line to set up all parameters,
	create the model, solve and plot the results. 
	'''
	
	phiList = [0.5]#, 1.5]
	kList = [0, 0.5, 1]


	for phi in phiList:
		for k in kList:

			start = time.time()

			# generate the parameter data from the LBDhelpers module.
			params = genData()

			#update parameters for multiple simulations
			params["phi"] = phi
			params["k"] = k

			print
			print "\t Imported parameters successfully in ", (time.time() - start)

			# Create the model
			model = vintageModel(params)
			print "\t Constructed model in ", (time.time() - start)


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
			f.write(str(phi)+ " " + str(k) + " " +str(solverStatus) + " " + str(terminationCondition) + '\n')
			f.close


			# save output to files
			f = open( "results/" + str(phi)+ "_" + str(k)+ "constraints.csv", 'wb')
			writer = csv.writer(f)
			for key, value in constraintDict.items():
				writer.writerow([key, value])
			f.close()

			f = open( "results/" + str(phi)+ "_" + str(k)+ "variables.csv", 'wb')
			writer = csv.writer(f)
			for key, value in varDict.items():
				writer.writerow([key, value])
			f.close()

			# save constraint checks:
			f = open( "results/" + str(phi)+ "_" + str(k)+ "checks.csv", 'wb')
			writer = csv.writer(f)

			writer.writerow(["Checking Time Logic Constraints"])
			writer.writerow(["Vintage","Year", "Name", "Value", "Target", "Flag"])

			for i in range(0, params["period"] + 1):
				for t in range(0, params["period"] + 1):
					if t<i:
						writer.writerow([i, t, "HnTimeLogic", constraintDict["HnTimeLogic"+str(i)+"-"+str(t)], "Zero", constraintDict["HnTimeLogic"+str(i)+"-"+str(t)] == 0])
						writer.writerow([i, t, "LnTimeLogic", constraintDict["LnTimeLogic"+str(i)+"-"+str(t)], "Zero", constraintDict["LnTimeLogic"+str(i)+"-"+str(t)] == 0])

					try:
						temp = constraintDict["KhZERO"+str(i)+"-"+str(t)]
					except KeyError:
						temp = "Null"
					writer.writerow([i, t, "KhZero", temp, "Zero", temp == 0])

					try:
						temp = constraintDict["KlZERO"+str(i)+"-"+str(t)]
					except KeyError:
						temp = "Null"
					writer.writerow([i, t, "KlZero", temp, "Zero", temp == 0])


			writer.writerow(["Checking Capital Non-Negativity Constraints"])
			writer.writerow(["Vintage", "Year", "Name", "Value", "Target", "Flag"])

			for i in range(0, params["period"] + 1):
				for t in range(0, params["period"] + 1):
					if t>=i:
						writer.writerow([i, t, "KhNonNeg", constraintDict["KhNonNeg"+str(i)+"-"+str(t)], "Non-Negative", constraintDict["KhNonNeg"+str(i)+"-"+str(t)] >= 0])
						writer.writerow([i, t, "KlNonNeg", constraintDict["KlNonNeg"+str(i)+"-"+str(t)], "Non-Negative", constraintDict["KlNonNeg"+str(i)+"-"+str(t)] >= 0])

			writer.writerow(["Checking Generation Constraints"])
			writer.writerow(["Year", "Name", "Value", "Target", "Flag"])

			for t in range(1, params["period"] + 1):
				writer.writerow([t, "Generation Upper"+str(t), constraintDict["GenUpper"+str(t)], params["GList"][t], constraintDict["GenUpper"+str(t)] <= params["GList"][t] * 1.001])
				writer.writerow([t, "Generation Lower"+str(t), constraintDict["GenLower"+str(t)], params["GList"][t], constraintDict["GenLower"+str(t)] <= params["GList"][t] * 0.999])

			writer.writerow(["Checking Emission Constraint"])
			writer.writerow(["Name", "Alpha", "Value", "Target", "Flag"])
			maxEmit = sum([params["mhList"][i]*params["FhList"][i]*params["H0"] + params["mlList"][i]*params["Fl_0"]*params["L0"] for i in range(0, params["period"]+1)])
			writer.writerow(["Emission", params["alpha"], constraintDict["emissions"], params["alpha"] * maxEmit, constraintDict["emissions"] <= params["alpha"]*maxEmit])

			f.close()

			print
			print
			print "\t Done in ", (time.time() - start)






