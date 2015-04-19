from sympy import *


t = Symbol('t')
x = Symbol("x")
r = Symbol('r')
N = Symbol('N')

lambd = Symbol("lambda")
mu = Symbol("mu")
rho = Symbol("rho")
pi = Symbol("pi")
sigma = Symbol("sigma")
phi = Symbol("phi")
gamma = Symbol("gamma")
delta = Symbol("delta")
tau = Symbol("tau")

G = Symbol("G")
Fh = Symbol("Fh")
Fl = Symbol("Fl")
H0 = Symbol("H0")
L0 = Symbol("L0")
m = Symbol("m")
E = Symbol("E")
nh = Symbol("nh")
nl = Symbol("nl")

n = Symbol("n")


Hp = Function("Hp")(t)
Hn = Function("Hn")(t)
Lp = Function("Lp")(t)
Ln = Function("Ln")(t)

Hpx = Function("Hp")(x)
Hnx = Function("Hn")(x)
Lpx = Function("Lp")(x)
Lnx = Function("Ln")(x)

kh = H0 * exp(-t/nh) + integrate(exp((x-t)/nh)*Hpx, (x, 0, t)) - integrate(Hnx, (x, 0, t))
kl = L0 * exp(-t/nl) + integrate(exp((x-t)/nl)*Lpx, (x, 0, t)) - integrate(Lnx, (x, 0, t))


cost = - integrate((Hpx + Hnx)*exp(-r*x), (x, 0, N))
GenConstraint = lambd * (G - Fh*kh - Fl* (1-exp(-t/tau) * kl))
EmitConstraint = mu * (E - m*Fh*kh)
KhConstraint = rho * kh
KlConstraint = pi * kl
HpConstraint = sigma * Hp
HnConstraint = phi * Hn
LpConstraint = gamma * Lp
LnConstraint = delta * Ln


lagrangian = cost + GenConstraint + EmitConstraint + KhConstraint + KlConstraint + HpConstraint + HnConstraint + LpConstraint + LnConstraint


#print "d/dHp: ", diff(lagrangian, Hp)
#print "d/dHn: ", diff(lagrangian, Hn)
#print "d/dLp: ", diff(lagrangian, Lp)
#print "d/dLn: ", diff(lagrangian, Ln)
#print "d/dlambda: ", diff(lagrangian, lambd)
#print "d/dmu: ", diff(lagrangian, mu)
#print "d/drho: ", diff(lagrangian, rho)
#print "d/dpi: ", diff(lagrangian, pi)
#print "d/dsigma: ", diff(lagrangian, sigma)
#print "d/dphi: ", diff(lagrangian, phi)
#print "d/dgamma: ", diff(lagrangian, gamma)
#print "d/delta: ", diff(lagrangian, delta)


dHp = (1/r)*(exp(-r*N) - 1) + n*(1-exp(-t/n))*(rho - lambd*Fh - mu*m*Fh) + sigma
dHn = (lambd*Fh + mu*m*Fh - rho)*t + phi
dLp = (1/r)*(exp(-r*N) - 1) + n*(1-exp(-t/n))*(pi - lambd*Fl*(1-exp(-t/tau))) + gamma
dLn = (lambd*Fl*(1-exp(-t/tau)) - pi)*t + delta
dlambdFh = - Fh*(H0*exp(-t/n)*(1-n) + n*Hp - n**2 * (1-exp(-t/n)))
dlambdFl = -Fl*(1-exp(-t/tau))*(L0*exp(-t/n)*(1-n) - n*Lp - n**2 * (1-exp(-t/n)))
dlambda = G + dlambdFh + dlambdFl

print solve_poly_system([dHp, dHn, dLp, dLn, dlambda], rho, sigma, lambd, phi, pi, gamma, delta, Hp, Lp)



