from capital_min_model import *
from func_gen import *
import matplotlib.pyplot as plt
import seaborn as sns
import csv


L0 = 2005.0* 10**3 # initial low emitting capital in kW installed capacity
H0 = 390130.0 * 10**3 # intial high emitting capital in kW installed capacity

alpha = 0.5 # emissions reduction fraction
r = 0.05 # interest rate

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

period = 100 # simulation length (!= to n)
nh = 30 # depreciation length for high emitting
nl = 30 # depreciation length for low emitting


# generate efficiency and carbon intensity data

# logistic(k, initial, increasing, randomAllowed, scale = 0.5, minVal= 0, maxVal=1):


GList = linGen(period + 1, G_0, G_m, 0) # energy demand over time

HpMeanList = np.ndarray((period,))
HnMeanList = np.ndarray((period,))
LpMeanList = np.ndarray((period,))
LnMeanList = np.ndarray((period,))

mcRange = 1


f = open('Period100ActualDataFlScaleVary.csv', 'wb')
writer = csv.writer(f)



#genericHeader = ["FlScale", "FhScale", "elScale", "ehScale", "minCost", "solved"]
genericHeader = ["FlScale", "minCost", "solved"]


HpHeader = ["Hp_" + str(i) for i in range(1, period+1)]
HnHeader = ["Hn_" + str(i) for i in range(1, period+1)]

LpHeader = ["Lp_" + str(i) for i in range(1, period+1)]
LnHeader = ["Ln_" + str(i) for i in range(1, period+1)]

header = genericHeader + HpHeader + HnHeader + LpHeader + LnHeader
writer.writerow(header)


#for i in range(mcRange):
for i in range(0, 30, 1):
	print i

	line = []

	# logistic arguments: (k, initial, increasing, randomAllowed, scale = 0.5, minVal= 0, maxVal=1)
	# randomAllowed = True varies scale (rate) of change of the trajectory
	FlScale, FlList = logistic(period+1, Fl_0, True, False, scale = i/10.0, minVal=0.34334988, maxVal=2.8658669) # low emitting efficiency trajectory
		# min is half of base, max is efficiency of natural gas ($917/kW) at 30% capacity
	FhList = linGen(period+1, Fh_0, Fh_m, maximum=4.7764449) # high emitting efficiency trajectory 
		# weighted average of coal and NG. Max is 1/917 * 8760 * 0.5
	
	elList = consGen(period+1, el_0) # low emitting carbon intensity trajectory
		# constant 
	ehList = linGen(period+1, eh_0, eh_m, minimum=1.22) # high emitting carbon intensity trajectory
		# minimum is emission from 100% natural gas.


	minCost, solved, Hp, Hn, Lp, Ln = Solver(period, nh, nl, FlList, FhList, elList, ehList, alpha, H0, L0, r, GList)



#	line.extend([FlScale, FhScale, elScale, ehScale])
	line.extend([FlScale])
	line.extend([minCost, solved])
	line.extend(Hp)
	line.extend(Hn)
	line.extend(Lp)
	line.extend(Ln)

	writer.writerow(line)




f.close()

#print HpMean
#print HnMean
#print LpMean
#print LnMean



#xRange = range(period)

#plt.plot(xRange, HpMean, label="Positive Investment in High-Emitting")
#plt.plot(xRange, -HnMean, label="Negative Investment in High-Emitting")
#plt.plot(xRange, LpMean, label="Positive Investment in Low-Emitting")
#plt.plot(xRange, -LnMean, label="Negative Investment in Low-Emitting")

#plt.title("Investment over Time")
#plt.ylabel("Investment")
#plt.xlabel("Years after Simulation Start")
#plt.legend(loc = 0)
#plt.show()












