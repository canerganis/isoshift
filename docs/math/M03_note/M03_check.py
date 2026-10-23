import math
def isotope_oh(nu_H_cm1, s_cm1_per_mA, T_K=0.0, delta_r_mA=0.0, ratio=2.0**-0.5, bends=()):
    from math import expm1, isfinite, log, tanh
    C, kB = 0.1239842, 0.0861733
    bends = tuple(bends)
    modes = ((nu_H_cm1, -s_cm1_per_mA, ratio),) + bends
    def mode(nu, dnu, alpha):
        E = C*nu
        if T_K == 0:
            return 0.5*(alpha-1)*E, 0.5*C*dnu*(alpha-1)
        kT = kB*T_K; z = E/kT
        if z < 1e-3:
            g = kT*(log(alpha) + (alpha**2-1)*z**2/24 - (alpha**4-1)*z**4/2880 + (alpha**6-1)*z**6/181440)
            W = ((1-alpha**2)*z/6 - (1-alpha**4)*z**3/360 + (1-alpha**6)*z**5/15120)
        else:
            g = 0.5*(alpha-1)*E + kT*(log(-expm1(-alpha*z)) - log(-expm1(-z)))
            W = 1/tanh(z/2) - alpha/tanh(alpha*z/2)
        return g, -0.5*C*dnu*W
    g, st = mode(*modes[0])
    bs = sum(mode(*m)[1] for m in bends)
    return {'zpe':0.5*C*nu_H_cm1*(1-ratio),'dF':g,'stretch':st,'bend':bs,'total':st+bs,'comp':-bs/st if st else None}

def isoshift_bond_slope(nu_s=3400.0, s=18.0, T=0.0, nu_b=None, s_b=0.0, n_b=2,
                        m_X=15.99491462, m_H=1.00782503, m_D=2.01410178):
    CM, KB = 0.1239842, 0.0861733
    muH = m_X*m_H/(m_X+m_H); muD = m_X*m_D/(m_X+m_D)
    rho = math.sqrt(muD/muH)
    def dF(nu):
        E = CM*nu
        if T <= 0: return -0.5*E*(1-1/rho)
        kT = KB*T
        f = lambda e: kT*math.log(2*math.sinh(e/(2*kT)))
        return f(E/rho)-f(E)
    def dFdnu(nu):
        if T <= 0: return -0.5*CM*(1-1/rho)
        kT = KB*T; x = CM*nu/kT
        coth = lambda y: 1/math.tanh(y)
        return 0.5*CM*((1/rho)*coth(x/(2*rho))-coth(x/2))
    stretch = dFdnu(nu_s)*(-s)
    bend = n_b*dFdnu(nu_b)*s_b if nu_b else 0.0
    total = stretch+bend
    return {'rho':rho,'zpe':0.5*CM*nu_s*(1-1/rho),'dF':dF(nu_s),'stretch':stretch,'bend':bend,'total':total,'comp':(-bend/stretch) if stretch else float('nan')}

inv_rho = 1/isoshift_bond_slope()['rho']
print('inv_rho', inv_rho, 'sqrt(9/17)', (9/17)**.5)
def rel(a,b): return abs(a-b)/max(abs(a),abs(b),1e-30)
print("== Case 1: nu=3400 s=18 no bends; A with exact-mass ratio, A default 1/sqrt2, A int-mass")
for T in (0,300,600):
    B = isoshift_bond_slope(3400,18,T)
    for lab,r in (('A_exact',inv_rho),('A_sqrt2',2**-.5),('A_int',(9/17)**.5)):
        A = isotope_oh(3400,18,T,ratio=r)
        print(T,lab,'zpe %.6f dF %.6f slope %.9f | B zpe %.6f dF %.6f slope %.9f | rel dF %.2e slope %.2e'%(A['zpe'],A['dF'],A['stretch'],B['zpe'],B['dF'],B['stretch'],rel(A['dF'],B['dF']),rel(A['stretch'],B['stretch'])))
print("== Case 2: bends. B test: 2 bends 1400, s_b 4.5, T=0,300,600; A bends tuples (1400,+4.5,ratio)")
for T in (0,300,600):
    B = isoshift_bond_slope(3400,18,T,nu_b=1400,s_b=4.5)
    for lab,r in (('A_exact',inv_rho),('A_sqrt2',2**-.5)):
        A = isotope_oh(3400,18,T,ratio=r,bends=((1400,4.5,r),(1400,4.5,r)))
        print(T,lab,'tot %.6f comp %.6f | B tot %.6f comp %.6f | rel tot %.2e comp %.2e'%(A['total'],A['comp'],B['total'],B['comp'],rel(A['total'],B['total']),rel(A['comp'],B['comp'])))
print("== A's two-bend check 1000 cm-1, sqrt2, T=0:", isotope_oh(3400,18,0,1,bends=((1000,4.5,2**-.5),(1000,4.5,2**-.5))))
print("B same (exact mass) :", isoshift_bond_slope(3400,18,0,nu_b=1000,s_b=4.5))
print("== Slope table s=10..25, nu 3000,3600 T=300,600 exact mass")
for s in (10,15,20,25):
    for T in (300,600):
        print(s,T,[round(isoshift_bond_slope(n,s,T)['stretch'],4) for n in (3000,3600)],[round(isotope_oh(n,s,T,ratio=inv_rho)['stretch'],4) for n in (3000,3600)])
print("A 1000cm-1 bend + T=300 comp for s_b=5.063495:", isotope_oh(3400,18,300,ratio=2**-.5,bends=((1000,5.063495,2**-.5),)*2)['comp'])
print("B ZPE int ratio 1/1.3744:", 0.5*0.1239842*3400*(1-1/1.3744))
