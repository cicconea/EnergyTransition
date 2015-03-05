from capital_min_model import *
from func_gen import *
import matplotlib.pyplot as plt
import seaborn as sns


L0 = 0.0 # initial low emitting capital
H0 = 1000.0 # intial high emitting capital

alpha = 0.5 # emissions reduction fraction
r = 0.05 # interest rate

Fh_0 = 0.5 # base high emitting efficiency MW/unit
Fh_m = 0.01 # slope high emitting efficiency
Fl_0 = 0.05 # base low emitting efficiency MW/unit
Fl_m = 0.01 # slope low emitting efficiency

el_0 = 1.0 # base emissions for low-intensity capital
el_m = -0.1 # slope emissions for low-intensity capital
eh_0 = 5.0 # base emissions for high-intensity capital
eh_m = -0.1 # slope emissions for high-intensity capital

maxLEff = 0.3 # maximum Fl efficiency MW/$

G_0 = 1000.0 # MW electricity demanded
G_m = 50.0 # annual growth in demand for MW

period = 50 # simulation length (!= to n)
nh = 30 # depreciation length for high emitting
nl = 30 # depreciation length for low emitting


# generate efficiency and carbon intensity data

# logistic(k, initial, increasing, randomAllowed, scale = 0.5, minVal= 0, maxVal=1):


GList = consGen(period, G_0) # energy demand over time

HpMeanList = np.ndarray((period,))
HnMeanList = np.ndarray((period,))
LpMeanList = np.ndarray((period,))
LnMeanList = np.ndarray((period,))

mcRange = 1000

for i in range(mcRange):
	FlList = logistic(period, Fl_0, True, True, minVal=0., maxVal=0.5) # low emitting efficiency trajectory
	FhList = logistic(period, Fh_0, True, True, minVal=0., maxVal=0.6) # high emitting efficiency trajectory assuming no efficiency improvement

	elList = logistic(period, el_0, False, True, minVal=1, maxVal=2) # low emitting carbon intensity trajectory
	ehList = logistic(period, eh_0, False, True, minVal=5, maxVal=10) # high emitting carbon intensity trajectory


	Hp, Hn, Lp, Ln = Solver(period, nh, nl, FlList, FhList, elList, ehList, alpha, H0, L0, r, GList)
	HpMeanList = np.append(HpMeanList, Hp, axis = 1)
	HnMeanList = np.append(HnMeanList, Hn, axis = 1)
	LpMeanList = np.append(LpMeanList, Lp, axis = 1)
	LnMeanList = np.append(LnMeanList, Ln, axis = 1)


HpMeanList = np.reshape(HpMeanList, (period, mcRange + 1))
HnMeanList = np.reshape(HnMeanList, (period, mcRange + 1))
LpMeanList = np.reshape(LpMeanList, (period, mcRange + 1))
LnMeanList = np.reshape(LnMeanList, (period, mcRange + 1))

HpMean = np.mean(HpMeanList, axis = 1)
HnMean = np.mean(HnMeanList, axis = 1)
LpMean = np.mean(LpMeanList, axis = 1)
LnMean = np.mean(LnMeanList, axis = 1)


xRange = range(period)

plt.plot(xRange, HpMean, label="HpMean")
plt.plot(xRange, -HnMean, label="HnMean")
plt.plot(xRange, LpMean, label="LpMean")
plt.plot(xRange, -LnMean, label="LnMean")

#axarr.title("Difference in Temperature of Air vs Altitude")
#axarr.ylabel("Altitude (m)")
#axarr.xlabel("Difference between Temperature and Dewpoint Temperature")
plt.legend(loc = 0)
plt.show()












