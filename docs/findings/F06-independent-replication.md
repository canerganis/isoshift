# F06: Independent replication of F01

**Status: computed (second implementation of the same harmonic quantity from the same cached force constants; checks code and bookkeeping, not the potentials or the physics).**

Script: src/isoshift_event/replicate_f01.py, written by a separate model (Codex) without access to our decomposition code. It recomputes ddF_iso and its stretch/perpendicular split from cached force constants (own q-mesh convergence, Gauss-Legendre integration over ln(m_H), same-mask imaginary-mode policy, nearest non-H atom as stretch direction, per-primitive-atom normalisation). The reference file results/decompose_pairs.csv was opened only after all independent numbers were written. Output: results/replicate_f01.json and results/replicate_f01.log.

Only the final comparison and summary code was patched (rows without a reference are listed separately and skipped in the statistics). The physics and numerics were not changed.

## Numbers

20 rows were computed. 9 have a reference row; 11 do not (pairs excluded from decompose_pairs.csv as not clean, including the proton-transfer and quarantined-imaginary-mode cases). Statistics cover the 9.

Absolute differences against our values (meV/atom):

| Quantity | Max | Median | Sign agreement |
|---|---|---|---|
| ddF_total vs ddF_direct | 1.0e-9 | 9e-14 | 9/9 |
| ddF_str | 1.5e-10 | 2e-14 | 9/9 |
| ddF_perp | 2.2e-10 | 2e-14 | 9/9 |

No row differs by more than 0.05 meV/atom, so there are no outliers to diagnose (mesh convergence, imaginary-mode masking, stretch definition and normalisation all agree on these rows).

## What it means for F01

On the 9 clean rows the independent route reproduces ddF_iso and the stretch/perpendicular split, including sign. F01's decomposition is not an artefact of our implementation on this subset. Limits: 9 rows is a small sample, agreement to 1e-9 means both codes read the same cached force constants and the same formula, so this tests the implementation and bookkeeping, not the force fields or the harmonic model. The 11 unreferenced rows are not validated by this check.
