# M00: Plumbing test, diatomic zero-point energy isotope ratio

Status: accepted

## Task

Compute the ratio E0(D)/E0(H) of the zero-point energy (ZPE) of an isolated harmonic X-H stretch and the matching X-D stretch, with finite X mass. Input is the X mass M in atomic mass units (u). Required value: X = Li, M = 6.94 u.

This is a plumbing test of the mathcheck workflow, not a physics result.

## Accepted formula

Let m_H = 1.00784 u and m_D = 2.01410 u. For isotope i, the reduced mass is mu_i = M m_i / (M + m_i). Then

E0(D)/E0(H) = sqrt(mu_H / mu_D) = sqrt[ m_H (M + m_D) / ( m_D (M + m_H) ) ]

Derivation: omega_i = sqrt(k / mu_i) and E0_i = (hbar/2) omega_i. The force constant k is the same for both isotopes (Born-Oppenheimer), so k and hbar cancel in the ratio.

Both candidate formulas (Astra and Opus) are algebraically identical. No escalation.

## Assumptions

1. The molecule is an isolated diatomic with one harmonic stretch, V(q) = k q^2 / 2, k > 0.
2. The force constant and equilibrium geometry are the same for H and D. Isotope substitution changes only the mass.
3. Finite X mass enters through the reduced mass. Both atoms move.
4. Only the stretching ZPE is compared. Excluded: anharmonicity, thermal excitation, electronic isotope corrections, quasi-harmonic volume effects, bend or phonon coupling.
5. Masses are model inputs in u. Electron-mass corrections to the reduced mass are neglected.
6. The test uses M = 6.94 u, the natural-abundance standard atomic weight of Li, not pure 7Li (7.016 u).
7. The ratio does not need k. Absolute ZPE values do.

## Units

- The ratio is dimensionless. All masses must share one unit (u here).
- Absolute ZPE, if k or a frequency is given: E0 = h nu / 2 = hbar omega / 2.
- With 1 eV = 1.602176634e-19 J and k_B = 8.61733326215e-5 eV/K:
  - E0 per molecule = 2.06783384846 meV per THz of nu
  - E0 per atom (half of the molecular value) = 1.03391692423 meV per THz of nu
  - E0 / k_B = 23.9962153668 K per THz of nu. This is an energy written in kelvin units, not a physical temperature.
- Conversion check: 1 eV = 241.798924 THz (h = 4.135667696e-15 eV s).
- Per-molecule or per-atom normalization does not change the ratio.

## Limiting cases

- M -> infinity (rigid host): R -> sqrt(m_H / m_D) = 0.707384078662. This is close to 1/sqrt(2) = 0.707107, but not equal, because m_D / m_H = 1.99843.
- M -> 0 from above: both reduced masses approach M, so R -> 1. Zero mass itself is excluded.
- m_D -> m_H: R -> 1 identically.
- M = m_H: R = sqrt[(m_H + m_D) / (2 m_D)] = 0.866138625.
- For every finite M > 0: sqrt(m_H / m_D) < R(M) < 1, and R decreases monotonically as M increases.

## Test case

Inputs: M = 6.94 u, m_H = 1.00784 u, m_D = 2.01410 u.

- mu_H = 0.880039054636 u
- mu_D = 1.561056275896 u
- mu_H / mu_D = 0.563744
- R = sqrt(0.563744) = 0.750830131803

Numeric results from both implementations:
- Astra: 0.7508301318030713
- Opus: 0.7508301318030713

Call: `print(f"{zpe_ratio(6.94):.12f}")`. Expected output: `0.750830131803`.

So the D stretch ZPE is 75.0830% of the H value, a drop of 24.917%.

## Python function

```python
def zpe_ratio(m_x_u):
    """Return dimensionless E0(X-D)/E0(X-H) for positive finite X mass in u."""
    import math

    m_x_u = float(m_x_u)
    if not math.isfinite(m_x_u) or m_x_u <= 0.0:
        raise ValueError("m_x_u must be positive and finite")
    m_h_u = 1.00784
    m_d_u = 2.01410
    return math.sqrt(
        (m_h_u / m_d_u)
        * ((m_x_u + m_d_u) / (m_x_u + m_h_u))
    )


if __name__ == "__main__":
    print(f"{zpe_ratio(6.94):.12f}")
```

Note: this accepted version does not evaluate M = inf. The rigid-host limit sqrt(m_H / m_D) is documented above and can be computed directly.

## Differences list

Astra and Opus agree on every printed numeric value, including the second check at M = m_H (0.8661386248) and M = 1e-9. Differences:

1. Interface. Astra hard-codes m_H and m_D and rejects non-finite M. Opus takes m_H and m_D as arguments and returns sqrt(m_H / m_D) for M = inf. The accepted function is Astra's; the infinite limit is not computed by it.
2. Closed form at M = m_H. Opus writes sqrt(2 m_H / (m_H + m_D)). That expression evaluates to about 0.818, not 0.866. The correct closed form is sqrt[(m_H + m_D) / (2 m_D)] = 0.866139, which Opus's number matches.
3. Frequency conversion. Opus gives 1 eV = 241.79884 THz. The correct value is 241.798924 THz. The difference is about 3e-7 relative and does not affect the ratio. Astra's per-THz conversions (2.067834 meV, 1.033917 meV per atom, 23.9962 K) are correct.
4. Assumptions. Opus adds that the test mass is natural-abundance Li, and gives an anharmonic correction of about 1e-3. That size is an estimate, not computed here. Astra labels X generically and states the electronic isotope exclusion explicitly.
5. Normalization. Astra gives per-molecule and per-atom conversions. Opus mentions the per-atom halving only in passing. The ratio is unaffected in both.
6. Sign and presentation. Both give E0(D)/E0(H) < 1. Astra states the result as 75.0830% of H. Opus states it as a 24.92% drop. These are the same number.
