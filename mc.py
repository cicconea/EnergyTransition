from capital_min_model import *
from func_gen import *
import matplotlib.pyplot as plt
import seaborn as sns
import csv


L0 = 0.0 # initial low emitting capital
H0 = 1000.0 # intial high emitting capital

alpha = 0.5 # emissions reduction fraction
r = 0.05 # interest rate

Fh_0 = 0.5 # base high emitting efficiency MW/unit
Fh_m = 0.01 # slope high emitting efficiency
Fl_0 = 0.05 # base low emitting efficiency MW/unit
Fl_m = 0.01 # slope low emitting efficiency

el_0 = 0.0 # base emissions for low-intensity capital
el_m = -0.1 # slope emissions for low-intensity capital
eh_0 = 11.0 # base emissions for high-intensity capital
eh_m = -0.1 # slope emissions for high-intensity capital

maxLEff = 0.3 # maximum Fl efficiency MW/$

G_0 = 1000.0 # MW electricity demanded
G_m = 50.0 # annual growth in demand for MW

period = 5 # simulation length (!= to n)
nh = 30 # depreciation length for high emitting
nl = 30 # depreciation length for low emitting


# generate efficiency and carbon intensity data

# logistic(k, initial, increasing, randomAllowed, scale = 0.5, minVal= 0, maxVal=1):


GList = consGen(period+1, G_0) # energy demand over time

HpMeanList = np.ndarray((period,))
HnMeanList = np.ndarray((period,))
LpMeanList = np.ndarray((period,))
LnMeanList = np.ndarray((period,))

mcRange = 1000


f = open('testOutput.csv', 'wb')
writer = csv.writer(f)

for i in range(mcRange):

	print i

	line = []
	FlList = logistic(period+1, Fl_0, True, False, minVal=0., maxVal=0.5) # low emitting efficiency trajectory
	FhList = logistic(period+1, Fh_0, True, False, minVal=0., maxVal=0.6) # high emitting efficiency trajectory assuming no efficiency improvement

	elList = logistic(period+1, el_0, False, False, minVal=0., maxVal=1.) # low emitting carbon intensity trajectory
	ehList = logistic(period+1, eh_0, False, False, minVal=10, maxVal=20) # high emitting carbon intensity trajectory


	minCost, solved, Hp, Hn, Lp, Ln = Solver(period, nh, nl, FlList, FhList, elList, ehList, alpha, H0, L0, r, GList)

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












