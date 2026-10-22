# Data and model sources

Raw downloads are not committed (`data/isoshift/*` is git-ignored except small curated files). Licences below are as stated by the sources or the installed packages. Check the source before redistributing.

Derived Materials Project and JARVIS-DFT subsets under `data/isoshift` are committed: `mp_h.csv`, `structures.csv`, `pairs.csv`, `jarvis_h_pairs.csv`, `structs/*.cif` and `validation_structures/*.cif`. Materials Project data are CC BY 4.0; please cite A. Jain et al., APL Materials 1, 011002 (2013), doi 10.1063/1.4812323. The JARVIS data licence caveat below applies to the redistributed JARVIS CIFs.

## Structure and energy data

| source | use | licence | notes |
|---|---|---|---|
| Materials Project | H-compound structures, energies, hull distances, MP phonon records, experimental flag | CC BY 4.0 | fetched with mp-api on 21 Oct 2026, 4421 entries (`data/isoshift/mp_h.csv`) |
| JARVIS-DFT (`dft_3d`, via jarvis-tools) | H-compound structures, OptB88vdW formation energies | NIST public data. The jarvis-tools code is MIT. No data licence statement was found in the installed package, so the exact data licence is not verified. | snapshot `jdft_3d-9-24-2025`, 3436 H/no-C entries |
| Petretto et al. 2018 phonons | PBEsol DFPT reference phonons, Sci. Data 5:180065 | CC0 | figshare article 5649298, 40 compounds used |
| MDR phonondb (Togo, NIMS Materials Data Repository) | PBEsol force constants for the isotope benchmark | set per dataset on the MDR page; not checked in the downloaded files. Dataset URLs are in `data/isoshift/dft_phonons/mdr_phonondb/index.json`. | 40 datasets used out of 257 qualifying |

## Experimental reference values

Taken from the cited papers via Valency Bond and cross-checked by a second model. DOIs per row are in `data/isoshift/validation.csv`. Query log: `logs/bond_queries.jsonl`.

## Model checkpoints

| model | exact id in `isoshift/calculators.py` | package (version) | licence |
|---|---|---|---|
| MACE | `medium-mpa-0` | mace-torch 0.3.16 | code MIT. The installed loader does not list MPA-0 among its Academic Software License checkpoints. |
| ORB | `orb_v3_conservative_inf_mpa` | orb-models 0.5.5 | code Apache-2.0. The package does not state a separate weights licence. |
| SevenNet | `7net-mf-ompa`, modal `mpa` | sevenn 0.13.0 | code MIT. The package does not state a checkpoint licence. The training data includes OMat24, so check upstream terms before redistributing weights. |
| MatterSim | `MatterSim-v1.0.0-5M.pth` | mattersim 1.2.5 | MIT (Microsoft) |

Checkpoints are downloaded or read from the packages at first use and are not stored in this repository.
