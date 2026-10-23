# P12 PIMD: measured cost and accuracy facts (24 Oct 2026, before any production data)

Measured by the session that wrote the first pimd.py (commit 4bfe39e). No PIMD production numbers on the polymorph pairs.

## MACE medium-mpa-0 on the RTX 4060 laptop GPU (8 GB)

* float64: 0.41 to 0.49 s and 1.2 GB per bead-step at 96 to 108 atoms (mp-23807, mp-23940 supercells).
* float32: about 0.057 s and 0.6 GB per bead-step.
* float64 P = 8 does not fit in one batch. mp-23807 at P = 4 with --bead-chunk 2: 3.5 GB peak, 0.51 steps/s. Initial max |F| 1.1e-4 eV/A.
* A TorchScript out-of-memory error appears as a plain RuntimeError.

## Statistics (harmonic backend, real mp-23940 force constants, P = 32)

* 16k samples give 0.14 meV/H statistical error on K_H. Block plateau from about 64 steps. A few thousand steps per mass point suffice.

## Budget

* float64, P = 64, 4 mass points x 2500 steps: about 31 s/step, 87 h per structure, about 5 weeks for 9 structures. Not feasible.
* Ring-polymer contraction (harmonic part on 64 beads, MACE on 8 contracted beads) plus float32: about 0.5 s/step, about 1 day for all 9.

## Time step and beads, O-H diatomic at 108 THz

* O-B-A-B-O splitting at dt = 0.25 fs biases dF by about -0.4 meV.
* B-A-O-A-B ("middle") splitting removes it: -0.08 and +0.03 meV vs analytic at P = 128.
* Bead error at 108 THz: 0.41 meV at P = 64, 0.10 meV at P = 128.

## Budget set by Can (24 Oct)

1 to 2 days of GPU time in total ("1 2 günlük iş okeydir"). The float64 P = 64 plan is out.

## Open questions for the council

1. harmonic_samecell already returns the P-bead harmonic value dF_P_eV. If Delta_anh is taken against the same-P harmonic reference, most of the bead discretization error cancels per structure and again in the pair difference. Is that sound, and which P does it allow?
2. Contraction (MACE on 8 beads, harmonic FC part on 64) vs plain float32 at lower P vs float64 on fewer structures: which keeps the < 1 meV/H inconclusive bar on ddF_corr within about 1 day of GPU time?
3. Is float32 MACE force noise acceptable for a centroid-virial estimator, and how should it be checked (float32 vs float64 on a short run of one structure)?

## Smoke test, decision 18 row 0a (24 Oct, float32, P = 16, TF32 off, forces only, 10 ring steps)

| struct | PIMD sc | atoms | s per ring step (chunk 4) | peak GB chunk 4 | chunk 8 | max abs F at x0 (eV/A) |
|---|---|---|---|---|---|---|
| mp-625152 | 3x2x1 | 96 | 1.23 | 3.4 | 1.21 s, 6.7 GB | 3.8e-5 |
| mp-23807 | 3x2x2 | 96 | 1.26 | 3.4 | OOM | 1.1e-4 |
| mp-625054 | 3x2x2 | 96 | 1.13 | 3.1 | 1.12 s | 7.1e-5 |
| JVASP-54682 | 3x2x1 | 96 | 1.09 | 2.9 | 1.08 s | 2.6e-5 |
| JVASP-92228 | 3x2x2 | 96 | 1.15 | 3.1 | 1.13 s | 5.7e-5 |
| mp-626497 | 2x2x2 | 112 | 1.44 | 3.8 | OOM | 5.0e-5 |
| mp-985293 | 2x2x1 | 112 | 1.57 | 4.2 | OOM | 9.6e-5 |
| mp-23940 | 3x3x2 | 108 | 0.97 | 2.5 | 0.95 s | 3.1e-2 |
| mp-626000 | 3x3x2 | 108 | 1.11 | 2.8 | 1.09 s | 2.4e-4 |

Chunk 16 does not fit for any structure; chunk 8 is no faster than chunk 4, so production uses --bead-chunk 4. Throughput is 0.07 to 0.10 s per bead-step, 1.2 to 1.7 times the 0.057 s assumed in decision 18.

A13: mp-23940 fails the residual-force gate (3.1e-2 > 1e-3 eV/A), so pair 5 is an invalid reference and is not run. All other structures pass (largest 2.4e-4, mp-626000).

Recomputed run table (13000 steps per run, measured s/step): mp-625152 P16 4.4 h, P32 8.9 h, C2 about 0.8 h, mp-23807 4.6 h, mp-625054 4.1 h, JVASP-54682 3.9 h, JVASP-92228 4.2 h, second P32 check about 8.5 h: 39.4 h cumulative. Pair 4 adds mp-626497 5.2 h (44.6) and mp-985293 5.7 h (50.3), above the 48 h cap; by A11 pair 4 runs only if the measured cumulative time leaves room for both members.
