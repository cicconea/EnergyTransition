from func_gen import *
import matplotlib.pyplot as plt
import seaborn as sns
import csv
from pyomoSimpleMin import *
import datetime


L0 = 2005.0 * 10**3 * 0.3 * 3827.0 # initial low emitting capital 
H0 = (336341.0 + 485957.0) * 10**3 * 0.5 * 1714.0 # intial coal + ng high emitting capital 
	# MW * 1000kW/MW * capacity * $/kW from Fh_0 or Fl_0

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
nh = 10 # depreciation length for high emitting
nl = 10 # depreciation length for low emitting




Header = ["FlScale", "minCost", "solved", "Hp", "Hn", "Lp", "Ln", "Kh", "Kl", "G", "Fh", "Fl", "mh", "ml"]
#f = open("pyomoSimple@{0}.csv".format(datetime.datetime.now()),  'wb')
#writer = csv.writer(f)
#writer.writerow(header)


i = 5

# generate efficiency and carbon intensity data
GList = linGen(period + 1, G_0, G_m, minimum = 0.0, maximum = 6.0 *10.0 **12) # energy demand over time
# logistic arguments: (k, initial, increasing, randomAllowed, scale = 0.5, minVal= 0, maxVal=1)
# randomAllowed = True varies scale (rate) of change of the trajectory
FlScale, FlList = logistic(period+1, Fl_0, True, False, scale = i/100.0, minVal=0.34334988, maxVal=2.8658669) # low emitting efficiency trajectory
	# min is half of base, max is efficiency of natural gas ($917/kW) at 30% capacity
FhList = linGen(period+1, Fh_0, Fh_m, maximum=4.7764449) # high emitting efficiency trajectory 
	# weighted average of coal and NG. Max is 1/917 * 8760 * 0.5
	
mlList = consGen(period+1, el_0) # low emitting carbon intensity trajectory
	# constant 
mhList = linGen(period+1, eh_0, eh_m, minimum=1.22) # high emitting carbon intensity trajectory
	# minimum is emission from 100% natural gas.


print pyomoSimple(period, GList, FhList, FlList, mhList, mlList, alpha, H0, L0, r, n)






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












