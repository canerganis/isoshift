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
