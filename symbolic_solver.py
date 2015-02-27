import sympy


# generate variables

Hp = ["Hp_" + str(i) for i in range(0, n+1)]
Hn = ["Hn_" + str(i) for i in range(0, n+1)]

Lp = ["Lp_" + str(i) for i in range(0, n+1)]
Ln = ["Ln_" + str(i) for i in range(0, n+1)]


# create symbolic variables
for val in Hp: 
	val = HpVar.append(symbols(str(val)))

for val in Hn: 
	val = HnVar.append(symbols(str(val)))

for val in Lp: 
	val = LpVar.append(symbols(str(val)))

for val in Ln: 
	val = LnVar.append(symbols(str(val)))

      

#Capital Constraints


# k_t^h = \sum\limits_{T=0}^{T=t}H_T \left ( 1-\frac{1}{n}\right )^{t-T}

# k_t^l = \sum\limits_{T=0}^{T=t}L_T \left ( 1-\frac{1}{n}\right )^{t-T}

# k^h_t, k^l_t \geq 0 \quad \forall t



# Fixed Energy Demand

# bar{G_t} = F_t^h\left(\sum\limits_{T=0}^{T=t}H_T \left ( 1-\frac{1}{n}\right )^{t-T}\right) + F_t^l \left (\sum\limits_{T=0}^{T=t}L_T \left ( 1-\frac{1}{n}\right )^{t-T}\right )


#Emissions Constraints

# E_{BAU} = \alpha n\left [ (e^h_0 F^h_0 k^h_0) + (e^l_0 F^l_0 k^l_0) \right ]


# E_m = \sum\limits_{t=1}^n \left [e^h_t F^h_t \left(\sum\limits_{T=0}^{T=t}H_T \left ( 1-\frac{1}{n}\right )^{t-T}\right) + e^l_t F^l_t \left(\sum\limits_{T=0}^{T=t}L_T \left ( 1-\frac{1}{n}\right )^{t-T}\right) \right ]

# E_{m} \leq \bar{E}


# Capital Minimization

# C(H,T) = \sum\limits_{t=1, H_t, L_t \geq 0}^n \left( \frac{H_t + L_t}{(1+r)^t}\right)
