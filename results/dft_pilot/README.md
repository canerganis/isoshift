# DFT timing pilot for W5 (9 Nov 2026)

Pair mp-23807 (delta-AlOOH) / mp-625054, MACE phonopy supercells (96 and 144 atoms; 16 and 24 displacements).
PBEsol on SSSP efficiency 1.3 PBE pseudopotentials, 60/480 Ry, k from 0.3 1/A, nosym (as for displaced cells). Geometry is the MLIP one, for timing only.

| run | where | result |
|---|---|---|
| GPU, QE 7.6 (~/opt/qe-gpu-7.6), 4 OMP threads | WSL Ubuntu-22.04 | mp-23807 96 atoms, 14 k: full SCF 19.5 min wall, 14 iterations |
| CPU, conda QE (~/mamba/envs/qe), mpirun -np 8 -nk 4 | WSL | about 70 s per iteration, same as GPU within about 10% |

Estimate for the full pair: about 23 h on one channel, about 12 h with GPU and CPU in parallel, plus PBEsol relaxations. Not started (Can, 9 Nov: "Şimdilik kalsın").
