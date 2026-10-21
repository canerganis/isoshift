# M01: Harmonic H/D isotope formulas

Status: accepted

## Task

One set of formulas for every isotope quantity IsoShift computes, so code can rely on this document.

Force constants Phi are mass independent (Born-Oppenheimer). For each structure we have harmonic phonon frequencies on a q-mesh for the H variant (all H masses) and the D variant (H replaced by 2.014 u). The D variant comes from re-diagonalising D(q) = M^-1/2 Phi(q) M^-1/2 with the D masses. Only M changes between variants.

Quantities covered: (1) harmonic F_vib(T), ZPE and S(T) per variant; (2) the polymorph double difference ddF_iso(T); (3) transition temperature shift; (4) pressure shift at fixed T; (5) QHA volume isotope effect; (6) the H-stretch fraction used for the anharmonic-sensitive flag.

## Accepted formulas

Both independent derivations (Astra xhigh, Opus high) agree on every numerically comparable output. Where the brief had errors, the corrected form is given here.

### Conventions

1. E = hbar * omega in meV. phonopy prints nu in THz (linear frequency, no 2 pi). E[meV] = 4.135667696 * nu[THz]. From cm^-1: E[meV] = nu[cm^-1] / 8.065543937. 1800 cm^-1 = 223.17155718 meV.
2. kB = 0.08617333262 meV/K.
3. Masses in u. Task values: m_H = 1.008, m_D = 2.014. Physical values are m_H = 1.00782503 and m_D = 2.01410178; use the values the calculation was run with and record them.
4. Sums over the q-mesh use weights w_q with sum_q w_q = 1. Every F, ZPE and S is per cell actually diagonalised.
5. Before differencing structures a and b, scale both to the same number of formula units.
6. Per atom divides by N_atom of the common cell. Per H divides by N_H of the common cell.
7. Pressure: 1 meV/A^3 = 0.1602176634 GPa. 1 eV/A^3 = 160.2176634 GPa.

### (1) Harmonic thermodynamics per variant X in {H, D}

Eigenvalues omega_{q,nu}^2 come from D_X(q). Keep spectra as (nq, nband) and apply the q-weight w_q to every band at that q. Default weights are 1/nq; supplied weights (phonopy multiplicities) are renormalised to sum 1. A flattened spectrum with unknown nq is not accepted.

Acoustic modes: locate the Gamma row explicitly (or state that the mesh has none). At Gamma drop exactly the 3 modes of smallest |E| (the translations), in both isotopes, and require them to lie within the acoustic tolerance (0.5 meV default). Keep every other positive mode, however small: a soft mode at E = 1e-6 meV still contributes kB T ln(x) to F and its H/D ratio gives the correct classical kB T ln(E_D/E_H). An energy cut such as E <= 1e-6 meV is wrong here, because it can drop the D copy of a soft mode and keep the H copy. Any non-acoustic mode with E <= 0 (imaginary beyond tolerance, or exactly zero) stops the calculation.

ZPE_X = sum_q w_q sum_nu E/2

F_X(T) = ZPE_X + kB T sum_q w_q sum_nu ln(1 - exp(-x)), with x = E/(kB T)

S_X(T) = kB sum_q w_q sum_nu [ x/(exp(x) - 1) - ln(1 - exp(-x)) ]

Units: meV per cell for F and ZPE, meV/K per cell for S.

### (2) Isotope double difference

ddF_iso(T) = [F_D(b) - F_H(b)] - [F_D(a) - F_H(a)]

Sign: ddF > 0 means deuteration destabilises b relative to a. Normalise per cell, then divide by N_atom (meV/atom) or N_H (meV per H).

Exact mass identity, which is also the basis of the mode-resolved decomposition in (6). Hellmann-Feynman on Phi u = omega^2 M u gives d(omega_nu^2)/d m_i = -omega_nu^2 |e_{i,nu}|^2 / m_i. Integrating over ln m from m_H to m_D:

F_D - F_H = -integral from ln m_H to ln m_D of <K_H>(m) d ln m

<K_H> = sum_{q,nu} w_q w^H_{q,nu} (E/4) coth(E/(2 kB T)), with w^H = sum over H atoms i of |e_{i,nu}|^2.

Limits:

* T = 0: ddF_iso = ddZPE = (1/2) sum [(E_D - E_H)_b - (E_D - E_H)_a].
* Classical limit: <K_H> goes to (3 N_H / 2) kB T. Therefore F_D - F_H per structure goes to -(3 N_H kB T / 2) ln(m_D/m_H). The sign is negative (deuteration lowers F). This structure-level term is the same for a and b of the same composition, so it cancels in ddF_iso.
* Wigner-Kirkwood correction, which is what survives at high T: ddF_iso(T) goes to (hbar^2 / (24 kB T)) (1/m_D - 1/m_H) sum over H atoms i of [Tr Phi^b_ii - Tr Phi^a_ii]. Phi_ii is the on-site self force constant (q-mesh average of the diagonal block). Equivalently, from frequencies: ddF goes to (1/(24 kB T)) [sum(E_D^2 - E_H^2)_b - sum(E_D^2 - E_H^2)_a]. So ddF decays as 1/T.

### (3) Transition temperature shift

Static energy difference dE = E_b - E_a (static, cell basis). Free energy differences: dF^X(T) = F_X(b) - F_X(a). Fixed-volume harmonic free-energy difference: dA^X(T) = dE + dF^X(T) (written dG below for brevity). This is a Helmholtz difference at the relaxed 0 K volumes, so T_c from it is a fixed-volume harmonic estimate and must be labelled so. A constant-pressure T_c needs G_X(T,P) = min_V [E(V) + F_vib^X(V,T) + PV] per phase and per isotope (QHA), used only for top candidates. The transition temperature T_c^X is the root of dG^X(T) = 0.

Entropy difference: dS^X = S_X(b) - S_X(a) = -d(dF^X)/dT.

Primary result: the exact roots of dG^H and dG^D, found by brentq on a temperature grid. Report every sign change with its direction (dG going + to - on heating is a -> b, - to + is b -> a). Never pair the first H root with the first D root: with re-entrant behaviour the first H transition can vanish in D, and the first D root is then the partner of the second, opposite H transition. Pair roots by tracking them along the mass path from m_H to m_D (re-diagonalised spectra when force constants are available, otherwise band-wise interpolation of the H and D spectra), allowing only same-direction, order-preserving links and refining the mass step where the root set changes. Report each H transition separately. A transition whose root leaves [Tmin, Tmax] or annihilates with a neighbour along the path has no D partner: dT_exact is null, never a number. D roots without an H partner are reported as unmatched.

Linear estimate. Linearise dG^H about T_c^H, using dG^D = dG^H + ddF:

dT_iso = T_c^D - T_c^H ~ +ddF_iso(T_c^H) / dS^H(T_c^H)

The sign is positive because dS = S_b - S_a. The brief's minus sign applies to the other convention.

Better first order: one Newton step on the D curve, dT ~ ddF(T_c^H) / dS^D(T_c^H), since dS^D = dS^H + ddS and ddS = -d(ddF)/dT.

Validity conditions: |dT| * |d(dS)/dT| << |dS| and |ddS| << |dS|. Relative error is about |ddS/dS| + |dT (d dS/dT)| / (2 |dS|).

Slope guard: require |dS^H| and |dS^D| >= 0.01 meV/atom/K at T_c^H, checked before any division. The guard is necessary, not sufficient: it does not replace the validity conditions. Each estimate is checked on its own and reported only when all of these hold:

* the slope guard passes;
* its estimated relative error is at most 0.2: |ddS/dS^H| + |dT d(dS^H)/dT| / (2 |dS^H|) for the linear estimate, |dT d(dS^D)/dT| / (2 |dS^D|) for the Newton step (curvatures by central difference at T_c^H);
* its predicted T_c^D = T_c^H + dT is positive;
* the H transition has a matched D transition.

Otherwise the estimate is null and the failed conditions are listed.

Model spread: for each model k, compute (dE_k, dF^H_k, dF^D_k) from the same Phi, then dT_k. Report the median and min/max. Do not propagate independent errors for ddF and dS, because they are strongly correlated within a model.

Linearised uncertainty, if needed: sigma(dT)^2 ~ (sigma_ddF / dS)^2 + (ddF sigma_dS / dS^2)^2 - 2 ddF cov(ddF, dS) / dS^3. The uncertainty in dE enters through the shift of T_c^H, sigma_Tc = sigma_dE / |dS|, and adds |d(ddF/dS)/dT| sigma_Tc.

Limits: T -> 0 gives dS -> 0, so the linear estimate diverges and the guard catches it. Near a root with |dS| < 0.01 meV/atom/K, use the exact roots.

### (4) Pressure shift at fixed T

Assume dV = V_b - V_a (same formula units) is independent of isotope and pressure over the shift. Then dG^X(P) ~ dG^X(P0) + (P - P0) dV, so P_t^X = P0 - dG^X(P0) / dV.

dP_iso(T) = P_t^D - P_t^H = -ddF_iso(T) / dV

In GPa: dP_iso[GPa] = -160.2176634 * ddF_iso[eV/cell] / dV[A^3/cell]. With meV units: dP[GPa] = -0.1602176634 * ddF[meV/cell] / dV[A^3/cell].

Ill conditioned as dV -> 0. A small dV does not establish a large shift.

### (5) QHA volume isotope effect

Exact: V_X(T) = argmin over V of [E(V) + F_X^vib(V, T)] (+PV at pressure P). Fit E + F per variant on the same V grid (Vinet or Birch-Murnaghan). Report V_H / V_D - 1.

Linearised estimate, with P_vib = -dF_vib/dV = (1/V) sum gamma_nu E_nu(T), E_nu = (E/2) coth(E/(2 kB T)), and gamma_nu = -d ln omega / d ln V:

(V_D - V_H) / V ~ -(1/B_T) d(F_D - F_H)/dV = (P_vib^D - P_vib^H) / B_T

V_H / V_D - 1 ~ +(1/B_T) d(F_D - F_H)/dV = (1/(B_T V)) d(F_D - F_H)/d ln V

Note: the brief omitted a factor of V. The form with d/d ln V is the correct one.

Sign: for pure H modes, omega_D = omega_H sqrt(m_H/m_D), so gamma is mass independent, and E_D < E_H. For normal positive gamma, V_H > V_D (the H compound is larger). Negative gamma modes (the O-H stretch in strong H-bonds, for example in ice) reverse this. When they dominate the zero-point pressure, the D compound is larger. Ice Ih: V_D2O > V_H2O at low T (Pamuk et al., PRL 108, 193003, 2012).

Classical limit: E_nu -> kB T for both isotopes, so the effect vanishes as 1/T.

Compute gamma per variant by finite difference of Phi(V). Mixed modes make the effect weakly mass dependent.

### (6) Mode-resolved fraction of ddF_iso (anharmonic-sensitive flag)

The 1800 cm^-1 frequency cut is not well defined. Modes have no one-to-one correspondence across variants. A D stretch sits near omega_H / 1.41, so an M-H or strongly H-bonded O-H stretch between 1500 and 2500 cm^-1 falls on different sides of the cut for H and D.

The well-defined choice is an eigenvector projection of the exact mass integral in (2):

F_D - F_H = -integral d ln m sum_{q,nu} w_q K_nu [ w^str_{q,nu} + w^perp_{q,nu} ]

* w^str = sum over H atoms i of |bhat_i . e_{i,nu}|^2, where bhat_i is the unit X-H bond vector to the nearest heavy neighbour.
* w^perp = w^H - w^str.
* K_nu = (E/4) coth(E / (2 kB T)).

Evaluate the integral with 6 to 8 point Gauss-Legendre quadrature in ln m. Re-diagonalise D(q) at intermediate H masses, which is cheap because Phi is fixed. Check that the quadrature total reproduces the direct F_D - F_H to better than 1e-3 meV/cell.

Then ddF_str = I_str(b) - I_str(a), and f_str = ddF_str / ddF_iso.

Flag "anharmonic-sensitive" if f_str > 0.70, and only when |ddF_iso| is at or above the noise floor (for example 0.1 meV/atom). Otherwise f_str is ill conditioned, can exceed 1 or go negative, and is reported as undefined.

A cheap endpoint-only proxy (trapezoid with weights from H and D only) is acceptable for screening. Label it approximate.

## Assumptions

1. Born-Oppenheimer: Phi(q) is identical for the H and D variants. Only M changes. The D variant replaces every H.
2. Harmonic phonons on a converged uniform q-mesh with weights summing to 1. Imaginary modes beyond tolerance abort the structure. The 3 acoustic Gamma modes are dropped.
3. Polymorphs a and b are normalised to identical composition before any difference. Per-atom and per-H values divide by N_atom and N_H of that common cell.
4. Sign conventions: ddF = [F_D - F_H]_b - [F_D - F_H]_a. dE = E_b - E_a. dV = V_b - V_a. dS = S_b - S_a.
5. Transition linearisation assumes |dT| is small against the curvature scale and |ddS| << |dS|. Enforced by the estimated relative error (<= 0.2) together with the slope guard |dS| >= 0.01 meV/atom/K on both variants, a positive predicted T_c^D and a matched D transition. Exact roots, paired by mass tracking, are primary.
6. Pressure shift assumes dV does not depend on isotope or pressure over the shift (first order in dP).
7. The linear QHA estimate takes B_T at V_H and gamma from finite differences of Phi(V) per variant. It is harmonic within each volume. No explicit anharmonicity and no nuclear quantum anharmonic corrections. These matter for H-bond stretches, which is what the 70% flag warns about.
8. The classical high-T limit uses the full classical partition function. Mass enters only through the kinetic term, so it is structure independent.
9. The volume minimiser assumes one smooth interior minimum in the supplied interval.
10. Electronic, magnetic, configurational, nuclear-spin and explicit anharmonic terms are excluded.
11. Compare equal stoichiometric amounts. Rescale if primitive cells differ.

## Units

| Quantity | Unit |
|---|---|
| Temperature | K |
| F, ZPE, dE, ddF | eV per comparison cell internally; reported in meV per cell, meV/atom, meV per H |
| S, dS | meV/(K cell); meV/(atom K) for the guard |
| Phonon energy | meV (hbar * omega) |
| Volume | A^3 per cell |
| Pressure | GPa |
| B_T | GPa |
| V_H/V_D - 1, gamma, f_str | dimensionless |

Note on the "toy_notation" key in the brief: omega = 100 meV means hbar * omega = 100 meV.

## Limiting cases

1. T -> 0: F_vib -> ZPE and S -> 0. ddF -> ddZPE. The transition shift estimate is singular at zero entropy slope.
2. Equal masses: every D frequency equals the H frequency, so dF = 0 and ddF_iso = 0 exactly at all T. dT = 0, dP = 0, V_H = V_D.
3. Swapping H and D reverses ddF_iso. Swapping a and b also reverses it.
4. Identical structures give ddF = 0, even though each F_D - F_H may be nonzero.
5. Classical limit: F_D - F_H per structure goes to -(3 N_H kB T / 2) ln(m_D/m_H). ddF_iso goes to 0 for equal composition, provided all relevant modes are classical. The first correction is the 1/T Wigner-Kirkwood term above.
6. Classical limit: the structure term is independent of volume, so the QHA isotope volume difference vanishes.
7. Pure isolated H oscillator: omega_D / omega_H = sqrt(m_H / m_D) = 0.70746 for task masses. Mixed modes scale less.
8. Heavy-only modes (zero H eigenvector weight) are mass independent. They cancel inside each F_D - F_H and contribute zero to ddF and to the H-projected decomposition.
9. dS -> 0 at T_c (|dS| < 0.01 meV/atom/K): the linear dT diverges. Use exact roots. If a variant has no root, report "no transition".
10. QHA: when every mode has gamma > 0 and the isotope only lowers E_nu (pure H modes, gamma mass independent), V_H > V_D. Mixed modes make gamma weakly mass dependent, so this is a tendency, not a guarantee; the sign is decided by computing P_vib per isotope (or the full QHA minimum). A dominant negative gamma (H-bonded O-H stretch, ice) can give V_D > V_H.
11. Ill-conditioned limits: dP diverges as dV -> 0, and dT diverges as dS -> 0. Neither divergence establishes a large shift. If A = ddF is near 0, report cancellation, not a percentage.

Toy coefficient in the classical limit: delta F_s / T -> -0.029822635348 meV/K per cell in 1D. Per substituted H site in 3D: -0.089467906043 meV/K.

## Test case

Toy system, 1D: 2 atoms per cell, 1 H per cell. Mass ratio r = sqrt(1.008 / 2.014) = 0.7074577897865654.

Spectra (meV):

* a, H: [100, 20]
* a, D: [70.74577897865654, 20]
* b, H: [90, 25]
* b, D: [63.67120108079089, 25]

Static energy difference dE = +2 meV per cell (b minus a).

### Thermal result

| T (K) | ddF (meV/cell) | ddF (meV/atom) | ddF (meV/H) |
|---|---|---|---|
| 0 | 1.46271105106718 | 0.73135552553359 | 1.46271105106718 |
| 300 | 1.15461886298206 | 0.57730943149103 | 1.15461886298206 |
| 3000 | 0.15244706658962 | 0.07622353329481 | 0.15244706658962 |

Both derivations agree to a relative difference of 1.6e-11 at 0, 300 and 3000 K.

Hand check at T = 0: ZPE shift for a is (70.7458 - 100) / 2 = -14.6271. For b it is (63.6712 - 90) / 2 = -13.1644. The difference is +1.4627.

Wigner-Kirkwood check: (r^2 - 1)(90^2 - 100^2) / (24 kB T) = +0.1530 at 3000 K, and +0.01530 at 30000 K (direct 0.01530). The 1/T decay is confirmed.

Per-structure F_D - F_H for a at 3000 K is -90.27 meV. The classical value -(kB T / 2) ln(2.014/1.008) is -89.47 meV. The exact value approaches it from below.

### Transition result (dE = +2 meV)

* dG^H(0) = 2 + (57.5 - 60) = -0.5 meV. b is stable at 0 K. dG^D(0) = 2 - 1.0373 = +0.9627 meV.
* dS = S_b - S_a < 0 at all T. dG rises with T.
* Exact T_c^H = 108.2738654918 K (b to a on heating). Both derivations agree.
* No D root exists. a is stable at all T for D, because g_D(0) = 0.96271105106718 meV > 0 and increases. So dT_exact is undefined.
* dS_H = -0.00605497 meV/atom/K and dS_D = -0.00590 meV/atom/K. Both are below the 0.01 guard, so guard_ok = False.
* Formal linear dT = +ddF / dS_H = -120.3731666880 K. That gives a predicted T_c^D of -12.1 K, which is negative. The Newton estimate on D is -123.6 K. Both are unreliable and must not be reported. The guarded result is null.

### Transition result (dE = +1 meV, both roots exist)

* T_c^H = 178.5162 K and T_c^D = 52.6772 K. dT_exact = -125.8390 K.
* Linear +ddF / dS_H = -90.2729 K (28 percent error). Newton on D = -100.22 K (20 percent error).
* dS_H = -0.00771 and dS_D = -0.00695 meV/atom/K. Guard fails.

### Pressure

For dV = +1 A^3/cell at 300 K: dP_linear = -0.184990336344551 GPa. Illustrative only, because the toy has no volume dependence. Both derivations agree.

For dV = -0.5 A^3 with ddF(300 K) = 1.1546 meV: dP = +0.370 GPa.

### QHA toy

Positive gamma: R = V_H/V_D - 1 = +0.0014332524 (exact). The linear estimate is +0.0014271379. Negative gamma: exact R = -0.001467904, linear -0.0014700614. These were derived by formula only in the second derivation, so treat them as checked by one derivation.

### Stretch fraction toy

The H-like modes sit at 806.55 and 725.90 cm^-1, below the 1800 cm^-1 cut. Cut-based stretch fraction is 0.0, and anharmonic_sensitive_proxy = false.

Mass-integral check, single H mode, 8-point Gauss-Legendre in ln m: at 1 K, -14.627111 against direct -14.627111. At 300 K, -15.812907 against -15.812907. At 3000 K, -90.271473 against -90.271473 meV. In this toy the H mode carries all H weight, so f_H = 1.0 for the 100 meV mode if it is an X-H stretch.

## Python function

Standard library plus numpy and scipy. Units: energies in meV, temperatures in K. Spectra are (nq, nband) arrays, one row per q-point, so the q-point count is always known; a flattened multi-q list is rejected. The function returns per-cell, per-atom and per-H values, one record per H transition with its matched D transition and guarded estimates, and the pressure shift.

```python
def isoshift(Ea_H, Ea_D, Eb_H, Eb_D, T, dE=None, natom=1, nH=1, dV_A3=None,
             wa=None, wb=None, gamma_a=None, gamma_b=None, acoustic_tol=0.5,
             Tgrid=(1.0, 3000.0, 600), guard=0.01, valid_tol=0.2,
             path=None, n_lam=16, jump_tol=None, max_depth=8):
    """Harmonic H/D isotope quantities for polymorphs a,b of identical composition.
    E*_X: phonon energies hbar*omega in meV (THz -> meV: *4.135667696, cm^-1 -> meV: /8.065543937),
    shape (nq, nband), one row per q-point; a single q-point is [[...]]. Imaginary modes are
    negative numbers (phonopy convention). wa/wb: one weight per q-point (phonopy multiplicities
    are fine), renormalised to sum 1; default 1/nq. gamma_a/gamma_b: row index of Gamma in each
    mesh, or None if the mesh has no Gamma point. At Gamma exactly the 3 modes of smallest |E|
    are dropped (acoustic translations) in both isotopes and must lie within acoustic_tol meV.
    Any other mode with E <= 0 raises. Cells a,b hold the same number of formula units.
    path(lam) -> (Ea, Eb) raw spectra at an intermediate H mass (lam=0 is H, lam=1 is D) is used
    to match H and D roots; the default is linear interpolation between the H and D spectra.
    Returns dict: energies meV/cell (+ per atom, per H), S meV/K/cell, T K, P GPa."""
    import numpy as np
    from scipy.optimize import brentq
    KB = 0.08617333262  # meV/K

    def prep(E, w, g, tag):
        E = np.array(E, float)
        if E.ndim != 2:
            raise ValueError(f"{tag}: pass spectra as (nq, nband); a single q-point is [[...]]")
        nq = E.shape[0]
        w = np.full(nq, 1.0 / nq) if w is None else np.asarray(w, float).ravel()
        if w.shape != (nq,) or np.any(w <= 0):
            raise ValueError(f"{tag}: need one positive weight per q-point ({nq} rows)")
        w = w / w.sum()
        keep = np.ones(E.shape, bool)
        if g is not None:
            ac = np.argsort(np.abs(E[g]))[:3]
            if len(ac) < 3 or np.any(np.abs(E[g, ac]) > acoustic_tol):
                raise ValueError(f"{tag}: Gamma row {g} lacks 3 acoustic modes within {acoustic_tol} meV")
            keep[g, ac] = False
        if np.any(E[keep] <= 0):
            raise ValueError(f"{tag}: imaginary or zero mode outside the Gamma acoustic set "
                             f"(min {E[keep].min():.4g} meV); stop, or pass gamma_a/gamma_b")
        Ek = np.concatenate([np.sort(E[i][keep[i]]) for i in range(nq)])
        wk = np.concatenate([np.full(keep[i].sum(), w[i]) for i in range(nq)])
        return Ek, wk

    aH, wa_ = prep(Ea_H, wa, gamma_a, "a,H"); aD, _ = prep(Ea_D, wa, gamma_a, "a,D")
    bH, wb_ = prep(Eb_H, wb, gamma_b, "b,H"); bD, _ = prep(Eb_D, wb, gamma_b, "b,D")
    if aH.shape != aD.shape or bH.shape != bD.shape:
        raise ValueError("H and D spectra of one structure must have the same shape")
    wa_in, wb_in, wa, wb = wa, wb, wa_, wb_

    def th(E, T, w):
        zpe = float(np.sum(w * 0.5 * E))
        if T <= 0: return zpe, zpe, 0.0
        x = E / (KB * T)
        L = np.log(-np.expm1(-x))            # ln(1 - exp(-x)), accurate for small and large x
        xs = np.minimum(x, 700.0)
        F = zpe + KB * T * float(np.sum(w * L))
        S = KB * float(np.sum(w * (xs / np.expm1(xs) - L)))
        return F, zpe, S
    F = lambda E, w, t: th(E, t, w)[0]
    S = lambda E, w, t: th(E, t, w)[2]
    dd = lambda t: (F(bD, wb, t) - F(bH, wb, t)) - (F(aD, wa, t) - F(aH, wa, t))
    out = {}
    for X, Ea, Eb in (("H", aH, bH), ("D", aD, bD)):
        for s, E, w in (("a", Ea, wa), ("b", Eb, wb)):
            out[f"F_{X}{s}"], out[f"ZPE_{X}{s}"], out[f"S_{X}{s}"] = th(E, T, w)
    d = dd(T)
    out.update(ddF_cell=d, ddF_atom=d / natom, ddF_H=d / nH)
    if dV_A3:
        out["dP_iso_GPa"] = -d / dV_A3 * 0.1602176634   # P_t^D - P_t^H
    if dE is None:
        return out

    # transitions: roots of dG = dE + F_b - F_a, each with its direction
    Ts = np.linspace(*Tgrid)
    P = jump_tol if jump_tol is not None else 0.05 * (Ts[-1] - Ts[0])
    g = lambda t, Ea, Eb: dE + F(Eb, wb, t) - F(Ea, wa, t)
    def roots(Ea, Eb):
        s = np.where(np.array([g(t, Ea, Eb) for t in Ts]) >= 0, 1, -1)
        return [(brentq(g, Ts[i], Ts[i + 1], args=(Ea, Eb), xtol=1e-10), int(s[i + 1]))
                for i in range(len(Ts) - 1) if s[i] != s[i + 1]]
    def spec(lam):
        if lam == 0.0: return aH, bH
        if lam == 1.0: return aD, bD
        if path is None: return aH + lam * (aD - aH), bH + lam * (bD - bH)
        Ea, Eb = path(lam)
        return prep(Ea, wa_in, gamma_a, "a,path")[0], prep(Eb, wb_in, gamma_b, "b,path")[0]
    def align(A, B):
        # order-preserving, same-direction matching of root lists; skipping a root costs P
        n, m = len(A), len(B)
        ok = lambda i, j: A[i][1] == B[j][1] and abs(A[i][0] - B[j][0]) <= P
        C = np.zeros((n + 1, m + 1)); C[0, :] = P * np.arange(m + 1); C[:, 0] = P * np.arange(n + 1)
        for i in range(1, n + 1):
            for j in range(1, m + 1):
                c = min(C[i - 1, j], C[i, j - 1]) + P
                if ok(i - 1, j - 1): c = min(c, C[i - 1, j - 1] + abs(A[i - 1][0] - B[j - 1][0]))
                C[i, j] = c
        pairs, i, j = {}, n, m
        while i and j:
            if ok(i - 1, j - 1) and np.isclose(C[i, j], C[i - 1, j - 1] + abs(A[i - 1][0] - B[j - 1][0])):
                pairs[i - 1] = j - 1; i -= 1; j -= 1
            elif np.isclose(C[i, j], C[i - 1, j] + P): i -= 1
            else: j -= 1
        return pairs
    def track(l0, R0, l1, R1, depth):
        # follow roots from l0 to l1; refine where the root set changes or a root jumps
        m = align(R0, R1)
        smooth = len(m) == len(R0) == len(R1) and all(abs(R0[i][0] - R1[j][0]) <= P / 4 for i, j in m.items())
        if smooth or depth == 0: return m
        lm = 0.5 * (l0 + l1); Rm = roots(*spec(lm))
        m1, m2 = track(l0, R0, lm, Rm, depth - 1), track(lm, Rm, l1, R1, depth - 1)
        return {i: m2[j] for i, j in m1.items() if j in m2}
    lams = np.linspace(0.0, 1.0, n_lam + 1)
    R = [roots(*spec(float(l))) for l in lams]
    link = {i: i for i in range(len(R[0]))}
    for k in range(n_lam):
        m = track(float(lams[k]), R[k], float(lams[k + 1]), R[k + 1], max_depth)
        link = {i: m[j] for i, j in link.items() if j in m}
    RH, RD = R[0], R[-1]
    out.update(Tc_H=[t for t, _ in RH], Tc_D=[t for t, _ in RD],
               Tc_D_unmatched=[RD[j][0] for j in range(len(RD)) if j not in link.values()])

    dSX = lambda Ea, Eb, t: S(Eb, wb, t) - S(Ea, wa, t)
    trans = []
    for i, (T0, sgn) in enumerate(RH):
        tD = RD[link[i]][0] if i in link else None
        rec = dict(Tc_H=T0, direction="b->a on heating" if sgn > 0 else "a->b on heating",
                   Tc_D=tD, dT_exact=(tD - T0) if tD is not None else None,
                   dT_linear=None, dT_newtonD=None, reasons=[])
        ddc = dd(T0); sH = dSX(aH, bH, T0); sD = dSX(aD, bD, T0)
        h = 1e-3 * max(T0, 1.0)
        cH = (dSX(aH, bH, T0 + h) - dSX(aH, bH, T0 - h)) / (2 * h)   # d(dS^H)/dT
        cD = (dSX(aD, bD, T0 + h) - dSX(aD, bD, T0 - h)) / (2 * h)   # d(dS^D)/dT
        guard_ok = abs(sH / natom) >= guard and abs(sD / natom) >= guard
        rec.update(ddF_TcH=ddc, dS_H_atom=sH / natom, dS_D_atom=sD / natom, ddS_atom=(sD - sH) / natom,
                   guard_ok=guard_ok)
        if tD is None: rec["reasons"].append("no matched D transition")
        if not guard_ok: rec["reasons"].append("slope guard")
        else:   # guard precedes every division; each estimate is checked on its own
            dTl, dTn = ddc / sH, ddc / sD
            for key, dT, err in (("dT_linear", dTl, abs((sD - sH) / sH) + abs(dTl * cH) / (2 * abs(sH))),
                                 ("dT_newtonD", dTn, abs(dTn * cD) / (2 * abs(sD)))):
                rec[key + "_relerr"] = err
                bad = [why for why, b in (("validity", err > valid_tol),
                                          ("Tc_D <= 0", T0 + dT <= 0),
                                          ("no matched D transition", tD is None)) if b]
                if bad: rec["reasons"] += [f"{key}: {why}" for why in bad]
                else: rec[key] = dT
        trans.append(rec)
    out["transitions"] = trans
    return out

# Toy usage
# r = (1.008/2.014)**0.5
# isoshift([[100,20]],[[100*r,20]],[[90,25]],[[90*r,25]], 300.0, dE=2.0, natom=2, nH=1)
```

Known limits of this reference: the 600-point grid can miss tangent or double roots. The default root tracking interpolates the H and D spectra linearly band by band, which approximates the mass path; pass `path` with spectra re-diagonalised at intermediate H masses (as in (6)) when force constants are at hand. The mass-integral helper (mode-resolved decomposition) and the QHA minimiser are separate and are not included here.

## Differences between the two derivations

Both derivations were run on the same toy case with the project venv. Results agree. The differences below are in method or presentation.

1. Newton-on-D estimate: only the Opus derivation gives dT ~ ddF / dS^D. It is closer to the exact result (-123.6 K against the linear -120.4 K for dE = 2 meV; -100.2 K against -90.3 K for dE = 1 meV). Added to the spec, not a conflict.
2. Nonnegative T condition: the Astra function also nulls the linear dT when T_c^H + dT < 0. The Opus reference relies on the no-root report from exact roots. Same outcome in the toy. Both are kept in the spec.
3. Root finder: Astra uses bisection on one user-supplied bracket and returns None if there is no sign change, so it can miss multiple crossings. Opus scans a grid and returns all sign changes, then uses the first. A grid can miss tangent or double roots.
4. Units: Astra works in eV internally with explicit unit handling (eV, meV, THz, cm^-1, rad/s) and takes dE in eV. Opus works in meV and expects the caller to convert. kB differs only in units (8.617333262145e-5 eV/K against 0.08617333262 meV/K), which is negligible.
5. Mode handling: Opus drops E <= 1e-6 meV silently. Astra raises an error on any non-positive mode. Opus caps x at 700 and uses a minimum. Astra switches to the ZPE-only branch for x > 700. No effect on the test cases.
6. Weights: Astra requires per-structure weights of matching length and does not renormalise. Opus broadcasts weights and assumes they sum to 1. Both treat the toy as unit weights.
7. Sign and correction agreement: ddF definition, the negative classical F_D - F_H, dT = +ddF / dS with dS = S_b - S_a, and the missing factor V in the QHA formula all agree. The classical toy coefficient is -0.029822635348 meV/K per cell in Astra; the Opus 1D value is the same.
8. High-T asymptotics: Opus gives the Wigner-Kirkwood 1/T form (0.1530 against exact 0.1524 meV at 3000 K). Astra says only that ddF goes to 0. Added to the spec.
9. QHA: Astra gives an executable golden-section block. The toy R values were computed by Astra only. Opus gives the formula only. The two formulas are the same up to notation. The toy has no volume dependence in the spectra, so the QHA result was not cross-checked numerically.
10. Stretch fraction: not numerically comparable. Astra uses per-mode masks (tracked modes or band attribution, H participation sum |e_iH|^2, cut at 1800 cm^-1). Opus rejects the frequency cut as ill defined and uses the eigenvector-projected mass integral with a 0.70 threshold above a 0.1 meV/atom noise floor. The toy gives 0.0 under the cut and f_H = 1.0 under the projection. This is a definition difference, not a numerical bug. The accepted definition is the projection.

No factor, sign or unit discrepancy was found in the numerically comparable outputs (ddF, dP, Tc, dS, linear dT).

## Decision

Accepted. No escalation to the board was needed. Both derivations agree on every numerical output. The only open point is the stretch-fraction definition, which is settled in favour of the eigenvector projection in section (6).

## Post-review corrections (Opus, 21 Oct)
Three blocking points from the screen build's Astra review were applied: (1) slope guard now precedes division, zero or tiny slopes give null, non-positive roots dropped; (2) dE + dF_vib is a fixed-volume Helmholtz difference, constant-pressure T_c needs per-isotope QHA; (3) positive Gruneisen parameters are a tendency for V_H > V_D, not a guarantee, so the sign is computed.

## Post-review corrections, second round (Opus, 21 Oct)
Four blocking points on the reference function were fixed and checked numerically with the function above.

1. q-weights. Spectra are (nq, nband); weights default to 1/nq and are renormalised. The same [10, 20] meV spectrum on two q-points gives ZPE 15 meV/cell, not 30. A flattened list is rejected.
2. Acoustic modes. Gamma is named explicitly and its 3 lowest |E| modes are dropped in both isotopes; other positive modes are kept and non-acoustic E <= 0 stops the run. A soft non-Gamma mode at 1.1e-6 meV (H) and 1.1e-6 r meV (D) now gives F_D - F_H = kB T ln r = -8.9468 meV at 300 K for that mode, the classical value, instead of the spurious +438.8 meV.
3. Root pairing. Toy a: H [100, 20], D [100 r, 20]; b: H [300, 12], D [300 r, 12]; dE = -90 meV. H roots 216.33 K (a -> b) and 1175.74 K (b -> a); one D root 1535.16 K (b -> a). The a -> b transition has no D partner (dT_exact null); the b -> a pair gives dT_exact = +359.42 K. First-root pairing would have reported +1318.8 K for a transition that does not exist in D.
4. Estimate checks. Main toy, dE = +2 meV, guard lowered to 1e-4 so both slopes pass: linear and Newton estimates are both null (relative error 0.50 and 0.43, predicted T_c^D negative, no matched D root). The doc toy values (ddF at 0, 300, 3000 K; T_c^H = 108.2739 K; dE = +1 meV dT_exact = -125.8390 K) are unchanged.

## Production check of the Gamma acoustic treatment (Opus, 21 Oct)
The screen uses isoshift.phonons.MeshFreqs (Gamma-centred mesh, modes below GAMMA_TOL_THZ dropped). `src/isoshift_event/refine.py` recomputes every pair on a denser Gamma-free shifted mesh from the same cached force constants. Measured |ddF_refined - ddF_screen| over 0/300/600 K on the first 21 identity-checked pair-model rows: median 2e-4, max 0.064 meV/atom. This difference is carried as `numerical_error_meV_atom` and enters the ranking threshold, so the finite-mesh Gamma term cannot create a candidate.
