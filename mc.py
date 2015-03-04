from capital_min_model import *
from func_gen import *
import matplotlib as plt


L0 = 0.0 # initial low emitting capital
H0 = 1000.0 # intial high emitting capital

alpha = 0.5 # emissions reduction fraction
r = 0.05 # interest rate

Fh_0 = 0.1 # base high emitting efficiency MW/unit
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

FlList = logGen(period, Fl_0, Fl_m, maxLEff) # low emitting efficiency trajectory
FhList = consGen(period, Fh_0) # high emitting efficiency trajectory assuming no efficiency improvement

elList = consGen(period, el_0) # low emitting carbon intensity trajectory
ehList = linGen(period, eh_0, eh_m, 0) # high emitting carbon intensity trajectory

GList = consGen(period, G_0) # energy demand over time


print Solver(period, nh, nl, FlList, FhList, elList, ehList, alpha, H0, L0, r, GList)