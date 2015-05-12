from func_gen import *
import re
import json




def genData(i):
	LBase = 2005.0 * 10**3 * 0.3 * 3827.0 # initial low emitting capital 
	HBase = (336341.0 + 485957.0) * 10**3 * 0.5 * 1714.0 # intial coal + ng high emitting capital 
		# MW * 1000kW/MW * capacity * $/kW from Fh_0 or Fl_0

	gamma = HBase/(HBase + LBase)

	betah = 0.05 # fraction of yearly operating costs
	betal = 0.05 # fraction of yearly operating costs

	r = 0.05 # interest rate
	alpha = 0.5

	kWperYearTokWh = 8760.0 # conversion of 1 kW power capacity for 1 year to kWh energy

	Fh_0 = 0.0006 * 0.5 * kWperYearTokWh # base high emitting efficiency kW/$ * kWh conversion * capacity factor
	Fh_m = 3*0.5*10**-6 * kWperYearTokWh # linear slope high emitting efficiency * kWh conversion * capacity factor 
	Fl_0 = (1.0/3827.0)*0.3 * kWperYearTokWh # base low emitting efficiency kW/$ * kWh conversion * capacity factor
	Fl_m = 0.01 # linear slope low emitting efficiency

	el_0 = 0.0 # base emissions for low-intensity capital in lbs CO2/kWh
	el_m = -0.1 # linear slope emissions for low-intensity capital
	eh_0 = 1.6984 # base emissions for high intensity capital in lbs CO2/kWh
	eh_m = -0.0031 # slope emissions for high-intensity capital

	G_0 = 2798.5 * 10**9 # billion kWh electricity demanded
	G_m = 32.238 * 10**9 # annual growth in demand for electricity in billion kWh


	# adjusted initial amounts preserving initial capital stock ratio
	# but taking in to account current costs to avoid weird first-period issues
	H0 = G_0/(Fh_0 + Fl_0*(1-gamma)/gamma)
	L0 = (G_0 - Fh_0*H0)/Fl_0



	period = 50 # simulation length (!= to n)
	treaty = 100 # number of years of treaty length - must be less than period
	nh = 30 # depreciation length for high emitting
	nl = 10 # depreciation length for low emitting


	# generate efficiency and carbon intensity data
	GList = linGen(period, G_0, G_m, minimum = 0.0, maximum = 6.0 *10.0 **12) # energy demand over time
	# logistic arguments: (k, initial, increasing, randomAllowed, scale = 0.5, minVal= 0, maxVal=1)
	# randomAllowed = True varies scale (rate) of change of the trajectory

	FlMax = 2.8658669 #max is efficiency of natural gas ($917/kW) at 30% capacity

	FlScale, FlList = logistic(period, Fl_0, True, False, scale = i/100.0, minVal=0.34334988, maxVal=FlMax) # low emitting efficiency trajectory
		# min is half of base, max is efficiency of natural gas ($917/kW) at 30% capacity
	FhList = linGen(period, Fh_0, Fh_m, maximum=4.7764449) # high emitting efficiency trajectory 
		# weighted average of coal and NG. Max is 1/917 * 8760 * 0.5
		
	mlList = consGen(period, el_0) # low emitting carbon intensity trajectory
		# constant 
	mhList = linGen(period, eh_0, eh_m, minimum=1.22) # high emitting carbon intensity trajectory
		# minimum is emission from 100% natural gas.

	return GList, FlList, FhList, mlList, mhList, period, H0, L0, alpha, r, nh, nl, betah, betal






def getInvestments(filename, period):
		with open(filename) as json_data:
			data = json.load(json_data)
			json_data.close()
		
		HList = []
		LList = []	


		#create lists of investments
		for j in range(0, period):
			#H = [0] * j
			#L = [0] * j

			H = []
			L = []

			try: HpVal = data["Solution"][1]["Variable"]["Hp"+str(j)]["Value"]
			except KeyError: HpVal = 0
			H.append(HpVal)

			try: LpVal = data["Solution"][1]["Variable"]["Lp"+str(j)]["Value"]
			except KeyError: LpVal = 0
			L.append(LpVal)

			for x in range(j+1, period):



				try: HnVal = data["Solution"][1]["Variable"]["Hn"+str(j)+"["+str(x)+"]"]["Value"]
				except KeyError: HnVal = 0

				try: LnVal = data["Solution"][1]["Variable"]["Ln"+str(j)+"["+str(x)+"]"]["Value"]
				except KeyError: LnVal = 0


				H.append(-HnVal)
				L.append(-LnVal)


			HList.append(H)
			LList.append(L)

		return HList, LList



def getOptimalCost(filename):
		with open(filename) as json_data:
			data = json.load(json_data)
			json_data.close()
		
		try: cost = data["Solution"][1]["Objective"]["OBJ"]["Value"]
		except KeyError: cost = 0

		return cost







