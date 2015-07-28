kW = c(18000, 31000, 44000, 64000, 92000, 132000, 238000, 303000, 506000, 981000, 1174000, 1098000)


dFdt = c(0.027062348, 0.025449541, 0.015236549, 0.008588235, -0.001677732, 0, 0.016609551, 0.038647059, 0.058461864, 0.069564706, 0.069288136, 0.0584) 

################################################################
################################################################
################################################################
################################################################

library(deSolve)

productivity = function(year, state, parameters) {
    with(as.list(c(state, parameters)), {


	FList = c(0.241100917, 0.268163265, 0.292, 0.298636364, 0.309176471, 0.295280899, 0.309176471, 0.3285, 0.386470588, 0.445423729, 0.5256, 0.584)

	dollarsInvested = c(196200000, 303800000, 396000000, 563200000, 782000000, 1174800000, 2023000000, 2424000000, 3440800000, 5787900000, 5870000000, 4941000000)


        # rate of change
        dF = 0.005 * FList + M * dollarsInvested^0.5 * FList^0.5 
        
        # return the rate of change
        list(c(dF))
    })
}


ssq = function(params) {

    ## Range and initial condition as before.
    year = c(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11)
    state = c(0.241100917, 0.268163265, 0.292, 0.298636364, 0.309176471, 0.295280899, 0.309176471, 0.3285, 0.386470588, 0.445423729, 0.5256, 0.584)

    ## Resolve the ODE.
    
    out = ode(y = state, times = year, func = productivity, parms = params, method = "rk4")

	out 
	
    ## modeled - observed
    ##ssq = out[, "FList"] - FList
}


library(minpack.lm)

## Start with Goulder & Mathai initial parameters
params.guessed = c(M = 0.0022)
params.fitted = nls.lm(par = params.guessed, fn = ssq)

summary(params.fitted)




