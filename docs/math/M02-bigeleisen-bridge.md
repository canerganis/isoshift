# M02: Bigeleisen bridge between polymorph-boundary isotope shift and D/H fractionation

Status: accepted

## Task

Relate (i) the isotope shift of a solid-solid polymorph boundary to (ii) the equilibrium D/H fractionation factor between two coexisting polymorphs a and b of the same composition, with n_H hydrogen atoms per formula unit (f.u.), in the harmonic and quasi-harmonic approximation. This is the solid-state analogue of Bigeleisen's link between the vapor-pressure isotope effect and the liquid-vapor fractionation factor.

Deliver: (1) the exact bridge between n_H k_B T ln alpha and the isotope free-energy difference, with its assumptions; (2) first-order boundary shifts dP_iso and dT_iso; (3) sign rules; (4) limiting cases and a numeric test.

Test system: a = diaspore, b = delta-AlOOH, n_H = 1, 4 atoms per f.u.

## Status of the derivation

Two independent derivations were compared (one Astra-style, one Opus-style). They agree on every number in the test case and on the sign rules. They differ in how the trace-D versus full-substitution question is handled (see Differences). The formula below is accepted with the stated assumptions. No escalation to the board was needed.

## Definitions

Per formula unit, phases a and b of identical composition, X in {H, D} meaning full substitution of all n_H hydrogens.

1. ddG_iso(T,P) = [G_D^b - G_H^b] - [G_D^a - G_H^a]
2. ln beta_p = -[(F_D^p - F_H^p) - (F_D - F_H)_classical] / (n_H k_B T), for p in {a, b}
3. alpha_(a-b) = beta_a / beta_b (D/H fractionation of a relative to b at equilibrium)
4. dV = V_b - V_a and dS = S_b - S_a, per f.u., evaluated on the H coexistence boundary.
5. L = 1000 ln alpha_(a-b), in permil.

The classical term (F_D - F_H)_classical = -(3/2) n_H k_B T ln(m_D/m_H) comes only from the momentum integral. It is identical in both phases and cancels in ddG_iso.

## Formula

### Exact bridge (full substitution)

n_H k_B T ln alpha_(a-b) = ddG_iso(T,P)

This is an identity under the definitions above and the assumptions below. Non-harmonic form: ddG_iso = -integral from m_H to m_D of [K_b(mu) - K_a(mu)] / mu d(mu), where K is the total H kinetic energy per f.u. at H mass mu. This form was stated by one derivation and was not independently checked.

### Harmonic / QHA evaluation

F_X^p = k_B T sum over modes q, j of ln[2 sinh(h nu_qj^X / 2 k_B T)], with nu_D from the same mass-independent force constants with m_H replaced by m_D. The ratio is then per H, and per f.u. normalization is applied through n_H.

### Trace-D versus full substitution

Let delta_g_j,tr be the trace substitution free energy in phase j, and define R_j = delta_G_j - n_H delta_g_j,tr, R = R_b - R_a. Then

n_H k_B T ln alpha_(a-b),tr = ddG_iso - R

Equivalently, ddG_iso = n_H k_B T ln alpha_tr + R. The trace fractionation factor identifies with the full-substitution one only when R = 0. For n_s inequivalent H sites, the trace ratio uses arithmetic site means and the full ratio uses geometric means, so R is of order (1/2)[Var_a(ln beta_i) - Var_b(ln beta_i)] to leading order. This second-order estimate was given by one derivation and was not independently verified.

### Boundary shifts (first order)

With c = 0.006241509074460763 eV/(GPa Å^3), and boundary quantities evaluated at the H coexistence point:

1. dP_iso = P_t^D - P_t^H ≈ -ddG_iso / (c dV) = -n_H k_B T ln alpha_(a-b) / (c dV)
2. dT_iso = T_t^D - T_t^H ≈ ddG_iso / dS = n_H T_H ln alpha_(a-b) / (dS/k_B)

In permil units (L = 1000 ln alpha, dS in k_B per f.u., dV in Å^3 per f.u.):

- ddG_iso [eV/f.u.] = 8.617333262145e-5 x n_H x T[K] x L / 1000
- dP_iso [GPa] ≈ -1.380649e-5 x n_H x T[K] x L / dV[Å^3]
- dT_iso [K] ≈ n_H x T_H[K] x L / (1000 x s_H), with s_H = dS_H / k_B per f.u.

If R is nonzero, add R to the energy numerator before dividing by -c dV or dS.

Equivalently, dP_iso = -(1000 ln alpha) dV / (160.21766 n_H k_B T) with the sign convention above, using 1 eV/Å^3 = 160.21766 GPa.

Second-order option (one derivation only): dP_iso = -ddG_iso / [c (dV + ddV_iso + (1/2)(d dV/dP) dP_iso)], with ddV_iso = (V_D^b - V_H^b) - (V_D^a - V_H^a). This is a fixed-point iteration, not exercised by the test case.

### Signs

1. alpha_(a-b) > 1 (D prefers a) implies ddG_iso > 0 when R = 0.
2. If b is the denser high-pressure phase (dV < 0), dP_iso > 0. Deuteration stabilizes a relative to b and the deuterated boundary moves to higher pressure, widening the a field.
3. At fixed P, dT_iso has the sign of dS_H. For a positive Clapeyron slope with dV < 0, dS_H < 0, so dT_iso < 0.

A trace preference alone does not fix the sign of the full-substitution shift when R is unknown.

## Assumptions

1. Both phases have the same composition and the same n_H. Quantities are per f.u. at the same (T, P).
2. Born-Oppenheimer: force constants do not depend on isotope mass at fixed geometry. Nuclear-spin and statistical factors are treated consistently or cancel between phases. Classical mass factors cancel (Bigeleisen and Mayer, 1947, https://doi.org/10.1063/1.1746492).
3. The trace-D construction (one H replaced in an otherwise protonated solid) is distinct from G_D - G_H (all H replaced). The dilute-substitution construction is illustrated in Markland and Berne (2012), https://pmc.ncbi.nlm.nih.gov/articles/PMC3361433/.
4. R = 0 holds when the H sites are equivalent and independent with composition-independent substitution free energies, together with ideal isotope mixing. More generally, R = 0 needs only identical R_j corrections in the two phases. This is not established by harmonicity alone.
5. Rule of the geometric mean: multi-substitution partition ratios equal products of single-substitution ratios. Ideal mixing supplies mixing entropy but does not impose this rule on internal partition functions (Albery and Davies, 1969, https://doi.org/10.1039/TF9696501059).
6. Harmonic separability into normal modes does not imply separability into isotope sites. Independent local oscillator blocks give a sufficient harmonic realization of additivity.
7. In QHA, volume relaxation must be included consistently in G and in trace substitution potentials. Fixed-volume harmonic beta values approximate the Gibbs bridge to first order at the unperturbed equilibrium volumes.
8. First-order boundary formulas require nonzero dV_H or dS_H and small slope changes over the displacement. They do not require alpha ≈ 1. Retaining ln alpha is exact within the bridge assumptions.
9. Both phase branches must be mechanically meaningful over the integration interval. Imaginary phonons invalidate the ordinary harmonic free energy.

## Units

- Energies: eV per f.u. (meV per atom = 1000 x E[eV/f.u.] / N_atoms).
- k_B = 8.617333262145e-5 eV/K. Temperature in K.
- Volumes: Å^3 per f.u. (multiply Å^3/atom by N_atoms).
- Pressure: GPa. 1 GPa Å^3 = 0.006241509074460763 eV. 1 eV/Å^3 = 160.2176634 GPa.
- Entropy: eV/(f.u. K), or k_B per f.u.
- L = 1000 ln alpha is dimensionless, reported in permil. alpha = exp(L/1000), not 1 + L/1000 except for small L.
- Phonons: h nu [eV] = 0.004135667696 nu[THz]. h nu / k_B ≈ 47.99243 nu[THz] K. Zero-point energy is h nu / 2.

## Limiting cases

1. High T: ln beta_end ≈ sum over modes of [(h nu_H)^2 - (h nu_D)^2] / [24 n_H (k_B T)^2], so ln alpha = O(T^-2) and ddG_iso = O(T^-1). Boundary shifts vanish as T grows, if thermodynamic slopes stay finite and nonzero.
2. T to 0: ddG_iso approaches the difference of isotope-dependent zero-point energies, which is finite. ln alpha diverges as 1/T, but dP_iso stays finite at -ddZPE / dV. A temperature-shift formula becomes unreliable when dS_H tends to zero.
3. Equal phases: ddG_iso = 0 and alpha = 1, so dP_iso = dT_iso = 0. If dV tends to 0 while ddG is nonzero, the first-order dP diverges. Use dT or the second-order form in that case.
4. n_H scaling: at fixed per-H alpha, ddG_iso scales with n_H. Redefining the formula unit (doubling n_H and dV together) leaves dP_iso and L unchanged.
5. Trace versus full: for one H site type with no H-H coupling, alpha_tr = alpha_full exactly.
6. Not applicable at 300 K: the Replace-ln-alpha-by-(alpha - 1) approximation. At ln alpha ≈ 0.359 it is inappropriate.

## Test case

System: a = diaspore, b = delta-AlOOH, n_H = 1, N_atoms = 4 per f.u. dV = V_b - V_a = -0.31 x 4 = -1.24 Å^3/f.u. R = 0 assumed. First-order boundary formula.

### Case 1: 300 K, dP_iso = +1.2 GPa

- ddG_iso = -c dV dP = 0.006241509 x 1.24 x 1.2 = 0.0092873655 eV/f.u. = 9.287 meV/f.u. = 2.3218 meV/atom
- ln alpha = ddG / (k_B T) = 0.0092873655 / 0.025852 = 0.3592513
- Result: 1000 ln alpha(diaspore - delta) = +359.25 permil, alpha = 1.432257

### Case 2: 1000 K, 1000 ln alpha = 40 permil

- alpha = exp(0.040) = 1.040811
- ddG_iso = k_B T ln alpha = 8.617333e-5 x 1000 x 0.040 = 0.0034469 eV/f.u. = 3.447 meV/f.u.
- dP_iso = -ddG / (c dV) = 0.0034469 / (0.006241509 x 1.24) = +0.44537 GPa
- Illustrative dS_H = -0.5 k_B per f.u.: dT_iso = ddG / dS = 0.0034469 / (-0.5 x 8.617333e-5) = -80.0 K

Both derivations report these values. The two derivations agree to a relative difference of at most about 1e-8, from constant rounding. The arithmetic was rechecked by hand here. Python was run by one derivation only; the other reported an environment problem. The results are conditional conversions of the supplied inputs, not a validation of AlOOH fractionation or of its phase boundary.

## Python function

Standard library only. Source: the Astra-style implementation, which also includes input validation and the correction term.

```python
import math


def isoshift_bridge(T_K, n_H, dV_A3_fu, *, L_permille=None,
                    dP_GPa=None, ddG_eV_fu=None, dS_eV_K_fu=None,
                    n_atoms_fu=1, correction_eV_fu=0.0):
    """First-order boundary conversion; standard-library only.
    Supply exactly one of L_permille=1000*ln(alpha_trace), dP_GPa,
    or ddG_eV_fu. dV and dS are b-a on the H coexistence boundary.
    correction = ddG - n_H*kB*T*ln(alpha_trace).
    Zero correction assumes the trace/endmember bridge is valid;
    alternatively, L can be interpreted as the endmember log ratio.
    The function does not compute phonons or solve the exact boundary.
    """
    kB = 8.617333262145e-5  # eV/K
    pv = 0.006241509074460763  # eV/(GPa*A^3)
    vals = [T_K, n_H, dV_A3_fu, n_atoms_fu, correction_eV_fu]
    vals += [v for v in (L_permille, dP_GPa, ddG_eV_fu,
                         dS_eV_K_fu) if v is not None]
    if not all(math.isfinite(v) for v in vals):
        raise ValueError('All supplied values must be finite.')
    if T_K <= 0 or n_H <= 0 or n_atoms_fu <= 0:
        raise ValueError('T_K, n_H and n_atoms_fu must be positive.')
    if dV_A3_fu == 0 or dS_eV_K_fu == 0:
        raise ValueError('A supplied boundary slope must be nonzero.')
    if sum(v is not None for v in
           (L_permille, dP_GPa, ddG_eV_fu)) != 1:
        raise ValueError('Supply exactly one of L_permille, dP_GPa, ddG_eV_fu.')
    scale = n_H * kB * T_K
    if L_permille is not None:
        ddG = scale * L_permille / 1000.0 + correction_eV_fu
    elif dP_GPa is not None:
        ddG = -pv * dV_A3_fu * dP_GPa
    else:
        ddG = ddG_eV_fu
    log_alpha = (ddG - correction_eV_fu) / scale
    try:
        alpha = math.exp(log_alpha)
    except OverflowError:
        alpha = float('inf')
    return {
        'L_permille': 1000.0 * log_alpha,
        'alpha': alpha,
        'ddG_eV_fu': ddG,
        'ddG_meV_atom': 1000.0 * ddG / n_atoms_fu,
        'dP_GPa': -ddG / (pv * dV_A3_fu),
        'dT_K': None if dS_eV_K_fu is None else ddG / dS_eV_K_fu,
    }


if __name__ == '__main__':
    a = isoshift_bridge(300, 1, -1.24, dP_GPa=1.2, n_atoms_fu=4)
    b = isoshift_bridge(1000, 1, -1.24, L_permille=40, n_atoms_fu=4)
    print(f"{a['L_permille']:.6f} permil; alpha={a['alpha']:.9f}")
    print(f"{b['dP_GPa']:.9f} GPa")
```

Expected output:

```
359.251338 permil; alpha=1.432256736
0.445370645 GPa
```

Note: the dT branch needs dS_eV_K_fu in eV/(K f.u.). For dS = -0.5 k_B, pass -0.5 * 8.617333262145e-5.

## Differences between the two derivations

1. Numerical agreement: both agree on both test cases to a relative difference of at most 8.3e-9, far below the 1e-3 threshold. Both give alpha = 1.040811 and dT = -80 K in Case 2.
2. Constants: one uses kB = 8.617333262145e-5 and c = 0.006241509074460763. The other uses kB = 8.617333262e-5 and 160.21766208 GPa per eV/Å^3. These are the same factors rounded.
3. dS units: one takes dS in eV/(K f.u.), the other in k_B per f.u. For dS = -0.5 k_B both give -80 K.
4. Trace versus full: one derivation writes an explicit correction R, with R = 0 as the default. The other states the full-substitution identity exactly and treats the trace-versus-full difference as a rule-of-geometric-mean correction of about (1/2)Var(ln beta_i) per phase, which it does not code. Both agree that R = 0 (or a single H site type) is needed to identify the trace alpha with the full alpha.
5. Higher order: one derivation gives a second-order fixed-point option for dP. The other is strictly first order. The second-order terms are not exercised by the tests.
6. Boundary evaluation point: one derivation evaluates ddG at P_t^H, the other writes the exact condition at P_t^D. The first-order formulas use the H boundary in both.
7. Validation: one function checks finiteness, positivity, nonzero slopes and exactly one input. The other checks only that exactly one of permil or dP is given, plus a zero-division check for dV. The other does not accept a direct ddG input.
8. Extra claim: one derivation includes a kinetic-energy-theorem form of ddG_iso. This was not independently checked and does not affect the numbers.
9. Sanity remark: one derivation estimates a ZPE-dominated origin of the 359 permil value, with a softened O-H stretch. This is a plausibility remark, not a computed result.
10. Environment note: one derivation reported Python unavailable and checked in JavaScript. The other ran the function in a project venv. The output above matches the second run.
