# M02 line 47: trace-D versus full-substitution correction

## Task

In `docs/math/M02-bigeleisen-bridge.md` (section "Trace-D versus full substitution"), check the claimed correction for two polymorphs a and b, each with n_H hydrogens per formula unit, possibly on inequivalent sites i with per-site reduced partition function ratios beta_i (l_i = ln beta_i, site-weighted).

Define R_j = delta_G_j - n_H delta_g_j,tr and R = R_b - R_a, so that

    n_H k_B T ln alpha_(a-b),tr = ddG_iso - R,   ddG_iso = delta_G_b - delta_G_a.

Derive R to second order in the site spread of l, and check whether R ~ (n_H k_B T / 2)[Var_b(l) - Var_a(l)] plus a site-nonadditivity term.

## Status

**accepted**

Two independent derivations (Astra and Opus) agree on the result, the sign, and the prefactor. Numeric cross-check was run on the shared test case by both. The old line 47 text, "(1/2)[Var_a - Var_b]", is wrong in sign and lacks the n_H k_B T factor. The erratum already in that line is correct.

## Accepted formula

Notation: weights w_ji >= 0 with sum_i w_ji = 1 (hydrogen-site fractions); mu_j = sum_i w_ji l_ji; Var_j = sum_i w_ji (l_ji - mu_j)^2; L_j = ln[sum_i w_ji exp(l_ji)] (so beta_j,tr = exp(L_j)).

Full substitution, site-additive part plus remainder:

    delta_G_j = n_H c - n_H k_B T mu_j + eta_j

where c is the common mass reference (cancels) and eta_j is the site-nonadditivity term (zero under site additivity).

Trace substitution: delta_g_j,tr = c - k_B T L_j per H.

Exact:

    R_j = n_H k_B T (L_j - mu_j) + eta_j
    R   = n_H k_B T [(L_b - mu_b) - (L_a - mu_a)] + (eta_b - eta_a)

Cumulant expansion with L_j - mu_j = ln mean_j(exp(epsilon)) = Var_j/2 + kappa3_j/6 + kappa4_j/24 + ..., where kappa3_j = mean_j(epsilon^3), kappa4_j = mean_j(epsilon^4) - 3 Var_j^2:

    R = (n_H k_B T / 2)[Var_b(l) - Var_a(l)] + (eta_b - eta_a) + (n_H k_B T / 6)(kappa3_b - kappa3_a) + O(kappa4)

For symmetric centered site distributions kappa3 = 0 and the first omitted term is fourth order.

Bridge identity check: n_H k_B T ln alpha_(a-b),tr = n_H k_B T (L_a - L_b) = ddG_iso - R, which holds exactly.

## Sign convention

* delta_G_j = G_D^j - G_H^j (per formula unit).
* ddG_iso and R are both b minus a.
* alpha_(a-b),tr = (D/H)_a / (D/H)_b = beta_a,tr / beta_b,tr. alpha_tr > 1 means trace D prefers phase a.
* R > 0 when phase b has the larger spread of l. Each R_j >= 0 under additivity (Jensen), but R_b - R_a can have either sign.

## Assumptions

1. Same composition and same n_H per formula unit, compared at the same T and P. T > 0.
2. Trace D is dilute and equilibrated among accessible sites with ideal isotope mixing. Weights are hydrogen-site multiplicities (normalized), not equal weights over labels unless multiplicities are equal.
3. Site additivity of full substitution is an extra assumption. Harmonic separability and mass-independent force constants alone do not imply it. eta_j collects departures (coupled modes, composition-dependent relaxation, volume relaxation in QHA).
4. The second-order expansion needs small centered spreads |l_ji - mu_j|, not small mu_j. The exact log-mean form does not need small spreads.
5. Same Born-Oppenheimer force constants Phi for H and D, mass matrix changed: D_X = M_X^(-1/2) Phi M_X^(-1/2). Fixed-volume harmonic free energy F_vib,X = k_B T sum_modes ln[2 sinh(h nu / (2 k_B T))]. QHA Gibbs: G_X(T,P) = min_V [U(V) + F_vib,X(T,V) + P V], evaluated consistently at the same T and P. Reference: https://phonopy.github.io/phonopy/formulation.html and https://github.com/phonopy/phonopy/blob/main/doc/qha.md
6. Classical mass and symmetry factors are identical for every H to D swap and cancel in every R_j and in R. The momentum factor c(T) = -(3/2) k_B T ln(m_D/m_H) cancels as well.

## Units

* beta, alpha, l = ln beta, L, Var(l) are dimensionless. Logs are natural.
* delta_G_j, eta_j, R_j, R, ddG_iso: eV per formula unit (eV/f.u.). Reported in meV/f.u. in the test. Divide by n_H for per-H values.
* delta_g_j,tr: eV per substituted H.
* k_B = 8.617333262145e-5 eV/K. At 300 K the test uses the rounded k_B T = 0.025852 eV = 25.852 meV.
* Frequencies: nu in THz (1 THz = 10^12 Hz). h nu [eV] = 0.004135667696 nu[THz]. Zero-point energy h nu / 2.
* QHA pressure-volume: P in GPa and V in angstrom^3 per f.u. gives P V [eV/f.u.] = 0.00624150907446 P V.
* Atoms-based meV/atom is not used: n_H is not the total atom count and the test gives none.

## Limiting cases

1. One site type, or zero within-phase spread: L_j = mu_j, so R_j = eta_j. If both phases have zero spread and are additive, R = 0 and trace D equals full substitution.
2. Identical centered site distributions in a and b: Jensen gaps cancel, R = eta_b - eta_a, even if the means differ.
3. Equal variances cancel only the second-order term. Unequal third or fourth cumulants can leave a nonzero exact R.
4. Adding a constant to all l within a phase leaves its Jensen gap and variance unchanged.
5. Reversing a and b reverses R and ddG_iso and inverts alpha_tr.
6. Rescaling formula-unit normalization scales n_H, eta_j and R together. alpha_tr is unchanged.
7. Harmonic classical limit, l_i = O(T^-2): spread correction R = O(T^-3). At low T the spread can grow, so use the exact expression instead of the truncation.
8. Large spread (|l_i - mu| of order 1): the series fails. Use R_j = n_H k_B T [ln mean(e^l) - mean(l)] + eta_j.

## Test case

Inputs: l_a = [0.1, 0.3] with weights [0.5, 0.5]; l_b = [0.2] with weight [1.0]; n_H = 1; T = 300 K with k_B T = 0.025852 eV; eta_a = eta_b = 0.

Analytic values: mu_a = mu_b = 0.20; Var_a = 0.01, Var_b = 0; L_a - mu_a = ln cosh(0.10) = 0.0049916888216465; L_b - mu_b = 0.

| Quantity | Value |
|---|---|
| ln alpha_tr | 0.004991688822 |
| alpha_tr | 1.005004168056 |
| delta_G_a = delta_G_b (mass term removed) | -5.1704 meV/f.u. |
| delta_g_a,tr | -5.299445139417 meV/H |
| delta_g_b,tr | -5.1704 meV/H |
| R_a | +0.129045139417 meV/f.u. |
| R_b | 0 |
| ddG_iso | 0 meV/f.u. |
| R exact (= R_b - R_a) | -0.129045139417 meV/f.u. |
| R second order | -0.129260000000 meV/f.u. |
| n_H k_B T ln alpha_tr | +0.129045139417 meV/f.u. (equals ddG_iso - R) |

Numeric results from the cross-check, both implementations:

* Astra function: R_exact = -0.1290451394172058 meV, R_second_order = -0.12926 meV.
* Opus function: R_exact = -0.12904513941720303 meV (relative difference 2e-14 from Astra), R_second_order = -0.12926 meV, R_fourth_cumulant = -0.12904457 meV.

Comparison: second order is -0.129260 vs exact -0.129045 meV/f.u. Absolute error 0.000215 meV/f.u. (0.000000215 eV). Relative error +0.167%. The second-order form overestimates the magnitude because kappa4_a < 0 here (kappa4_a = 1e-4 - 3e-4 = -2e-4).

Extra check (Opus cross-check, weights [2,1,1], n_H = 4, l_a = [0.1, 0.5, 0.9], l_b = [0.3, 0.4]): R_exact = -5.82104 meV/f.u. Both implementations agree to 3e-15 relative. R_second_order = -5.5905 meV/f.u.

## Python function

Astra version (validates inputs, returns the bridge residual and per-phase data):

```python
import math

def trace_full_correction(l_a, l_b, T_K, n_H, *, weights_a=None,
                          weights_b=None, nonadd_a_eV_fu=0.0,
                          nonadd_b_eV_fu=0.0, kBT_eV=None):
    """Common mass term removed; energies in eV/f.u. or eV/H.
    Weights are site multiplicities. Nonadditivity inputs are eta_a, eta_b.
    kBT_eV optionally overrides k_B*T for rounded numerical examples.
    """
    vals = (T_K, n_H, nonadd_a_eV_fu, nonadd_b_eV_fu)
    if not all(math.isfinite(x) for x in vals) or T_K <= 0 or n_H <= 0:
        raise ValueError('Require finite inputs and positive T_K, n_H.')
    kt = 8.617333262145e-5 * T_K if kBT_eV is None else float(kBT_eV)
    if not math.isfinite(kt) or kt <= 0:
        raise ValueError('kBT_eV must be finite and positive.')

    def phase(values, weights, nonadd):
        x = [float(v) for v in values]
        w = [1.0] * len(x) if weights is None else list(map(float, weights))
        if (not x or len(x) != len(w)
                or not all(math.isfinite(v) for v in x + w)
                or any(v < 0 for v in w) or max(w) <= 0):
            raise ValueError('Require finite sites and nonnegative, nonzero weights.')
        scale = max(w)
        w = [v / scale for v in w]
        total = math.fsum(w)
        pairs = [(v, p / total) for v, p in zip(x, w) if p > 0]
        mu = math.fsum(p * v for v, p in pairs)
        var = math.fsum(p * (v - mu)**2 for v, p in pairs)
        d = [v - mu for v, _ in pairs]
        if max(map(abs, d)) <= 0.5:
            gap = math.log1p(math.fsum(p * math.expm1(z)
                                      for z, (_, p) in zip(d, pairs)))
        else:
            m = max(d)
            gap = m + math.log(math.fsum(p * math.exp(z - m)
                                        for z, (_, p) in zip(d, pairs)))
        log_beta = mu + gap
        return {'mean_l': mu, 'variance_l': var,
                'log_beta_trace': log_beta, 'jensen_gap': gap,
                'delta_G_eV_fu': -n_H * kt * mu + nonadd,
                'delta_g_trace_eV_per_H': -kt * log_beta,
                'R_eV_fu': n_H * kt * gap + nonadd}

    a = phase(l_a, weights_a, nonadd_a_eV_fu)
    b = phase(l_b, weights_b, nonadd_b_eV_fu)
    log_alpha = a['log_beta_trace'] - b['log_beta_trace']
    ddG = b['delta_G_eV_fu'] - a['delta_G_eV_fu']
    r = b['R_eV_fu'] - a['R_eV_fu']
    r2 = (0.5 * n_H * kt * (b['variance_l'] - a['variance_l'])
          + nonadd_b_eV_fu - nonadd_a_eV_fu)
    return {'a': a, 'b': b, 'kBT_eV': kt,
            'log_alpha_trace': log_alpha, 'ddG_iso_eV_fu': ddG,
            'R_exact_eV_fu': r, 'R_second_order_eV_fu': r2,
            'bridge_residual_eV_fu': ddG - r - n_H * kt * log_alpha}
```

Call for the test case: `trace_full_correction([0.1, 0.3], [0.2], 300, 1, weights_a=[0.5, 0.5], kBT_eV=0.025852)`.

## Differences between the two derivations

1. Numerics: both were run on the shared test case. R_exact agrees to 2e-14 relative. R_second_order agrees exactly. The Opus fourth-cumulant value (-0.12904457 meV) differs from the exact value by 5.7e-7 meV (about 4e-6 relative). Opus described this as matching "to about 1e-7 meV", which slightly understates the gap.
2. Units: Astra works in eV per f.u. and reports meV by scaling. Opus works in meV per f.u. throughout. k_B differs only in rounding (8.617333262145e-5 eV/K vs 8.617333262e-2 meV/K), negligible here.
3. Notation: Astra calls the Jensen gap L_j - mu_j and the nonadditivity term eta_j. Opus calls the nonadditivity term N_j and the Jensen gap "the Jensen gap in R_j". Same objects.
4. Function interface: Astra validates inputs, takes explicit weights (default equal weights), normalizes by max(w), uses log1p/expm1 for small spreads, and returns ln alpha_tr, ddG_iso, and a bridge residual. Opus has no input validation, uses equal weights by default, plain log-sum-exp, and returns R_exact, R_second_order, R_fourth_cumulant, and a relative error. Opus's ddG_iso is a stub in its script, so ln alpha and ddG_iso were only compared on the Astra side. Results do not change with these choices.
5. Higher-order terms: Astra gives the next omitted term as O(epsilon^3) and says the first omitted term is fourth order for symmetric distributions. Opus writes the third and fourth cumulant terms explicitly, with kappa4 = mu4 - 3 sigma^4 (same as Astra's definition). No sign or factor conflict.
6. Extra assumptions: Astra states that harmonic separability alone does not imply site additivity. Opus places volume relaxation of full deuteration in N_j. Opus also gives the high-T scaling as R ~ 1/T^3 (Astra gives the same order from the classical limit).
7. Sign and prefactor: both give R = (n_H k_B T / 2)(Var_b - Var_a) + (eta_b - eta_a) + higher orders, and both say the old line 47 "(1/2)(Var_a - Var_b)" is wrong. No disagreement.
8. Python execution: Astra's own note says its Python was not run. The cross-check ran both functions, so both are now exercised.
