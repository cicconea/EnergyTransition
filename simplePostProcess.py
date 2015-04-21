from __future__ import division
import json
import sys
from mc_simple import *
from math import exp



# use this file to create the capital and generation values to export in CSV
count = 1
stillRunning = True


GList, FlList, FhList, mlList, mhList, period, H0, L0, alpha, r, n = genData(int(count))

while stillRunning == True:
	print count
	try:
		currentFile = "jsonResults/simpleResult_"+str(count)+".json"
		with open(currentFile) as json_data:
			data = json.load(json_data)
			json_data.close()

		#print data["Solution"][1]["Variable"]["Hp[1]"]["Value"]
		
		Hp = []
		Hn = []
		Lp = []
		Ln = []

		#create lists of investments
		for j in range(1, period+1):

			try: HpVal = data["Solution"][1]["Variable"]["Hp["+str(j)+"]"]["Value"]
			except KeyError: HpVal = 0

			try: HnVal = data["Solution"][1]["Variable"]["Hn["+str(j)+"]"]["Value"]
			except KeyError: HnVal = 0

			try: LpVal = data["Solution"][1]["Variable"]["Lp["+str(j)+"]"]["Value"]
			except KeyError: LpVal = 0

			try: LnVal = data["Solution"][1]["Variable"]["Ln["+str(j)+"]"]["Value"]
			except KeyError: LnVal = 0


			Hp.append(HpVal)
			Hn.append(HnVal)
			Lp.append(LpVal)
			Ln.append(LnVal)

		Hinvest = result = [x - y for x, y in zip(Hp, Hn)]
		Linvest = result = [x - y for x, y in zip(Lp, Ln)]


		dateRange = range(period)
		# what is total capital in each period?
		# follow capital accumulation formulas from documenation
		HKap = [H0]
		LKap = [L0]
		for i in range(1, period):
			HKap.append(H0 * exp(-i/n) + sum([Hp[j] * exp((j-i)/n) - Hn[j] for j in range(1, i+1)]))
			LKap.append(L0 * exp(-i/n) + sum([Lp[j] * exp((j-i)/n) - Ln[j] for j in range(1, i+1)]))

	# generate matplotlib plot for investment
		fig = plt.figure(figsize=(8,6),dpi=100)
		axes = fig.add_subplot(1,1,1)
		# plot the data
		axes.plot(dateRange, Hinvest, label= "Dirty Capital Invesment")
		axes.plot(dateRange, Linvest, label= "Clean Capital Investment")


		# labels
		axes.set_xlabel('Years of Simulation')
		axes.set_ylabel('Investment ($)')
		axes.set_title("Investment")
		plt.legend(loc = 0)
		plt.show()


		print "done with model"+str(count)
		count += 1

	except IOError: 
		print sys.exc_info()
		stillRunning = False
	except:
		stillRunning = False
		print sys.exc_info()



