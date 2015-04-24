import sys
from helpers import *



# use this file to create the capital and generation values to export in CSV
count = 1
stillRunning = True


GList, FlList, FhList, mlList, mhList, period, H0, L0, alpha, r, n = genData(int(count))

while stillRunning == True:
	print count
	try:
		currentFile = "jsonResults/simpleResult_"+str(count)+".json"
		H, L = getInvestments(currentFile, period)

		currentFile = "jsonResults/constraints_"+str(count)+".txt"
		kh, kl = getCapital(currentFile)		


		dateRange = range(len(H))
		# generate matplotlib plot for investment
		fig = plt.figure(figsize=(8,6),dpi=100)
		ax1 = fig.add_subplot(1,2,1)
		# plot the data
		ax1.plot(dateRange, H, label= "Dirty Capital Invesment")
		ax1.plot(dateRange, L, label= "Clean Capital Investment")

		# labels
		ax1.set_xlabel('Years of Simulation')
		ax1.set_ylabel('Investment ($)')
		ax1.set_title("Investment")


		# generate matplotlib plot for investment
		ax2 = fig.add_subplot(1,2,2)
		# plot the data
		ax2.plot(dateRange, kh, label= "Dirty Capital Stock")
		ax2.plot(dateRange, kl, label= "Clean Capital Stock")

		# labels
		ax2.set_xlabel('Years of Simulation')
		ax2.set_ylabel('Investment ($)')
		ax2.set_title("Capital")
		plt.legend(loc = 0)
		plt.show()
		plt.close()



		print "done with model "+str(count)
		count += 1



	except IOError: 
		print sys.exc_info()
		stillRunning = False
	except:
		stillRunning = False
		print sys.exc_info()



