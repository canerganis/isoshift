# IsoShift prefetch (2026-10-21)

## validation_structures/ (Materials Project, mp-api, CIF conventional cells; index.json has mp_id, sg, nsites, e_hull)
42 CIFs, lowest energy plus polymorphs within 50 meV/atom of hull:
Mg(OH)2 2 (mp-30247 P-3m1, mp-626143 C2), Ca(OH)2 3 (mp-23879), LiH 1 (mp-23703), H2O 11, AlOOH 5, KOH 3, KDP 11 (mp-23959 Fdd2 hull 0), NH4Cl 1 (mp-34337 P-43m), MgH2 5 (mp-23710 rutile P4_2/mnm, mp-23711 Pbcn gamma).
- Ice: mp-697111 Cmc2_1 (12 sites, 0 meV, proton-ordered ice XI). Ordered Ih-type models: mp-1974803 Cc, mp-703459 P6_3cm, mp-24043 R-3 (ice-like, check).
- AlOOH: mp-625152 Pnma (hull 0), mp-625054 Cmc2_1, mp-625404, mp-625420 Pnma; mp-23807 Pmn2_1 (hull 41.7 meV, delta-AlOOH). Diaspore/boehmite labels not verified, check by structure.
- Gaps: only one NH4Cl phase (cubic, disordered H absent in MP ordered model). Mg(OH)2 has no MP phonon.

## dft_phonons/
All sources open without login.
1. petretto/ : 40 JSON (Petretto et al. 2018 PBEsol DFPT, Sci. Data 5:180065). Source: figshare article 5649298 (phonon.tar.bz2, 52.6 MB, https://ndownloader.figshare.com/files/9850858), license CC0. Archive kept in petretto_raw/. 72 H/C-free/<=16-atom entries exist in total (1521 compounds); 40 chosen (O/N/S-containing first). Contains qpts, ph_bandstructure (cm^-1), ph_dos, structure CIF string, dielectric.
2. mdr_phonondb/ : 40 datasets, Togo phonondb on MDR NIMS (PBEsol). Index of all: https://github.com/atztogo/phonondb/blob/master/mdr/phonondb/README.md ; per-entry zip https://mdr.nims.go.jp/download_all/<id>.zip (no login, 0.1 to few MB). Each: phonopy_params.yaml.xz (structure + force constants, usable with phonopy.load), PNG plots, VASP settings. 257 entries qualify (H, no C, <=16 atoms); candidates_le16.json lists them with zip URLs. License not checked in files (MDR page states per dataset).
3. mp_phonon/ : 40 JSON from mp-api `m.materials.phonon` (DFPT for few, pheasy otherwise): structure, bandstructure, dos (THz). Query: search(material_ids=[id]) -> identifier, then get_bandstructure_from_phonon_id(identifier, method) and get_dos_from_phonon_id. Some mp-ids have no phonon (e.g. Mg(OH)2 mp-30247). Index mp_phonon/index.json (formula None for dfpt entries; use mp_id).

## Gaps
- No Gamma-point frequencies pre-extracted; derive from bands (Petretto/MP) or phonopy_params (MDR).
- MP phonon terms: MP data CC BY 4.0.
