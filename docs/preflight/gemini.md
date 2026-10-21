Here is your ranked pre-flight review (15 items across physics/method, validation, compute/throughput, orchestration, judging/story, and submission).

---

### 1. Gate Trap: Ice Ih Anomalous $\Delta V_{\text{iso}}$ + Trivial LiH ZPE Ratio `[Validation]`
* **Must fix before 17:00:** **YES** (update gate criteria in `PLAN.md`).
* **Why it matters:**
  1. Ice Ih has an **anomalous** volume isotope effect ($V_{\text{D}_2\text{O}} > V_{\text{H}_2\text{O}}$ by $\sim 0.09\%$ at 0 K; Pamuk *et al.*, PRL 2012) driven by a delicate balance between negative O–H stretch Grüneisen parameters and positive lattice modes. Standard PBE-trained universal MLIPs (without dispersion corrections tuned for water) frequently miss this $0.09\%$ sign while still predicting accurate harmonic $\Delta\Delta F_{\text{iso}}$ for solid hydrides/hydroxides.
  2. The LiH D/H ZPE ratio criterion (`0.78 to 0.80`) is a **kinematic mass identity**, not a potential test: for any rocksalt LiH force-constant matrix, mixing optical modes ($\sqrt{\mu_{\text{LiH}}/\mu_{\text{LiD}}} = 0.750$) and acoustic modes ($\sqrt{8/9} = 0.943$) yields $\sim 0.785$ regardless of bond stiffness error.
  3. Your gate tests *single-phase QHA volume shifts*, whereas your main screen computes *two-phase harmonic $\Delta\Delta F_{\text{iso}}$*.
* **Concrete fix:** Replace the LiH ratio check with **absolute** $\Delta\text{ZPE}(\text{LiH}-\text{LiD})$ in meV/f.u. (or $\Gamma$-optical frequency vs. neutron data), replace ice Ih QHA volume sign with **at least one two-phase or formation isotope shift** (e.g., $\text{PdH/D}$, $\text{MgH}_2/\text{MgD}_2$, or ice $\text{Ih}\to\text{XI}$ harmonic $\Delta\Delta F_{\text{iso}}$ sign), and require $3/4$ models on **brucite + portlandite** for QHA $\Delta V_{\text{iso}}$.

### 2. `FixSymmetry` + Fixed-Cell Trap on Brucite Imaginary Modes (`-37 THz` in ORB) `[Physics / Method]`
* **Must fix before 17:00:** **NO** (apply in Task 1.4 at 17:30).
* **Why it matters:** A $-37\text{ THz}$ ($-1230\text{ cm}^{-1}$) imaginary mode in ORB is a local H-atom saddle point or unrelaxed cell stress, not a supercell-cutoff artifact. Enforcing `FixSymmetry` (Task 1.4) when the high-symmetry H Wyckoff site is a saddle point on the MLIP PES **locks the structure onto the saddle point** and guarantees imaginary optical modes. Conversely, relaxing atomic coordinates without relaxing the cell tensor (`FrechetCellFilter`) leaves gigapascal residual pressures in layered hydroxides.
* **Concrete fix:** In Task 1.4, relax **cell + positions** with `FrechetCellFilter` (`hydrostatic_strain=False`, `fmax=1e-4` eV/Å). If imaginary optical modes persist under `FixSymmetry`, displace $0.02\text{ \AA}$ along the lowest imaginary eigenvector, drop `FixSymmetry`, re-relax, and check if `spglib` finds a lower-symmetry true minimum.

### 3. MLIP Static Energy Errors ($\delta\Delta E_0$) Will Erase $T_0 < 1000\text{ K}$ Crossings `[Physics / Method]`
* **Must fix before 17:00:** **NO** (bake into Task 1.5 / 4.1 spec).
* **Why it matters:** Universal MLIPs have polymorph static energy errors $\delta\Delta E_0 \sim 5\text{–}25\text{ meV/atom}$, whereas $\Delta S_{\text{vib}} \sim 0.01\text{–}0.05\text{ meV/atom/K}$. A $15\text{ meV/atom}$ error shifts the baseline transition temperature $T_0$ by $300\text{–}1000\text{ K}$. If Task 4.1 requires a raw MLIP free-energy crossing below 1000 K in all 4 models, disagreement on $\Delta E_0$ will reject true candidates even when all 4 models agree on $\Delta F_{\text{vib}}(T)$ and $\Delta\Delta F_{\text{iso}}(T)$.
* **Concrete fix:** Decouple vibrational thermodynamics from static energy error:
  1. Compute $\Delta\Delta F_{\text{iso}}(T) = [\Delta F_{\text{vib}}^D(T) - \Delta F_{\text{vib}}^H(T)]$ across all 4 MLIPs (purely vibrational, independent of $\Delta E_0$).
  2. Anchor $\Delta E_0$ to the DFT reference (MP/JARVIS) *or* evaluate $\Delta T_{\text{iso}}(T_{\text{ref}}) = -\Delta\Delta F_{\text{iso}}(T_{\text{ref}}) / \Delta S_{\text{vib}}^H(T_{\text{ref}})$ at $T_{\text{ref}} \in \{300, 600\}\text{ K}$ for any pair where $|\Delta S_{\text{vib}}|$ is large enough to drive a crossing within the DFT $\Delta E_0$ window.

### 4. Orchestration Ceremony (`mathcheck` + `build` + `board`) Will Blow Block 1 Wall-Clock & Claude Rolling Quota `[Orchestration]`
* **Must fix before 17:00:** **YES** (trim `docs/WORKFLOW.md`).
* **Why it matters:** Block 1 (`17:30–20:00`, 2.5 h) schedules 5 `mathcheck` derivations, 3 full `build` loops (Opus spec $\to$ Codex code $\to$ Sonnet test $\to$ dual Astra/Opus review $\to$ second-reader verification $\to$ 2 fix rounds), 2 `sweep` pipelines, and a 4-agent `board`. Sequential multi-model round-trips will take 5–6 hours of wall-clock latency and exhaust Claude's **5-hour rolling token window** before any GPU validation runs at 20:00.
* **Concrete fix:**
  1. Collapse all 5 formulas into **one batched `mathcheck` call** in WF1.
  2. Drop the "second reader verifies every review finding" step in `build`; run **one** parallel review (Astra physics + Opus edge cases) and only loop if acceptance tests fail.
  3. Reserve full 4-agent `board` strictly for **Gate (00:00)** and **Final Claims (Block 4.5)**.

### 5. Pair-By-Pair Redundancy & Subprocess Model-Reload Overhead on the RTX 4060 `[Compute / Throughput]`
* **Must fix before 17:00:** **NO** (fix in Task 1.5 `screen.py` design).
* **Why it matters:**
  1. Your 319 JARVIS pairs come from only 186 compositions (~400 unique structures, not 638). Screening by *pair* recomputes the ground-state polymorph 2–5 times per composition (~35% wasted GPU time).
  2. Spawning a fresh Python subprocess per job across `.venv` and `.venv-sevenn` reloads PyTorch + CUDA + model weights from disk every time (~10–15 s overhead per job on Windows = **2.5+ hours lost** over 800 structure-model evaluations).
* **Concrete fix:**
  1. Queue by **unique `(structure_id, model)`**, cache per-structure $F_{\text{vib}}^H(T)$, $F_{\text{vib}}^D(T)$, relaxed volume, and `min_freq` in `results/structures/`, and compute pairwise $\Delta\Delta F_{\text{iso}}$ in post-processing.
  2. Run a **persistent worker loop per venv/model** that loads `mace` once, processes all queued structures, then exits so `orb` starts next.
  3. Ensure D phonons are computed by swapping masses (`phonopy.masses = ...`) on the **in-memory force constants** (<0.5 s), never re-running supercell forces.

### 6. Thermal Decomposition Ceiling ($T_{\text{decomp}} < 1000\text{ K}$) & Missing Pressure Shift $\Delta P_{\text{iso}}$ `[Physics / Judging / Story]`
* **Must fix before 17:00:** **NO** (add to Task 4.1 & 4.3).
* **Why it matters:** Most hydrides, borohydrides, alanates, and hydroxides (including your top pilot hit, $\text{AlOOH}$ boehmite/diaspore) decompose via $\text{H}_2$ desorption or dehydration between $400\text{ K}$ and $650\text{ K}$ at 1 atm. Claiming a $850\text{ K}$ ambient-pressure polymorph crossing will draw immediate pushback from chemistry judges. Conversely, high-pressure transitions at 300 K in a diamond anvil cell (DAC) avoid decomposition entirely.
* **Concrete fix:**
  1. Compute the **pressure isotope shift** at 300 K for every pair at zero extra GPU cost: $\Delta P_{\text{iso}}(300\text{ K}) \approx -\Delta\Delta F_{\text{iso}}(300\text{ K}) / \Delta V_{\text{relaxed}}$ (in MPa/GPa, where $1\text{ meV/\AA}^3 = 0.1602\text{ GPa}$).
  2. Cap ambient-$P$ $\Delta T_{\text{iso}}$ claims at $600\text{ K}$ unless Bond literature confirms higher thermal stability, and report $\Delta P_{\text{iso}}(300\text{ K})$ for reconstructive/high-$P$ pairs like diaspore/boehmite.

### 7. Cross-Database (MP + JARVIS) Duplicate Structures Posing as Polymorphs `[Data Curation / Physics]`
* **Must fix before 17:00:** **NO** (fix in Task 1.3 `pairs.py`).
* **Why it matters:** Merging MP (PBE/r2SCAN) and JARVIS (OptB88vdW) creates false "polymorph pairs" that are actually the **same crystal phase** with different DFT interlayer spacings or slightly shifted X-ray H coordinates, evading default `StructureMatcher`. Upon MLIP relaxation, they collapse to the same minimum (giving noisy near-zero $\Delta\Delta F_{\text{iso}}$) or differ only by an unphysical H saddle point.
* **Concrete fix:**
  1. Require **different space group numbers** (at `symprec=0.1` *and* `0.01`) or widened `StructureMatcher(ltol=0.3, stol=0.4, angle_tol=7)` when pairing across MP and JARVIS.
  2. In `screen.py`, run `StructureMatcher` **again on the MLIP-relaxed structures** of each pair; immediately drop any pair that relaxes to the same crystal structure (`collapsed_to_same_phase=True`).

### 8. QHA Discontinuous Mode-Drop Artifact When High Volumes Go Imaginary `[Physics / Method]`
* **Must fix before 17:00:** **NO** (fix before Task 2.1 QHA runs).
* **Why it matters:** In `REPORT.md`, brucite QHA in ORB went out of window and flipped sign (`-0.03%`). When `phonopy` integrates $F_{\text{vib}}(V, T)$ at 7 volumes and 1–2 expanded volumes develop imaginary modes, `phonopy` silently omits those modes from the sum, reducing the active degrees of freedom $3N - N_{\text{imag}}(V)$. This creates a step discontinuity in $F(V)$ that corrupts the EOS fit and $\partial F/\partial V$.
* **Concrete fix:** Before fitting the QHA EOS, check `N_imag(V)` across all 7 volume points. Discard any volume point where imaginary modes jump above your threshold ($\omega < -0.5\text{ THz}$), require $\ge 5$ clean volume points spanning the minimum for EOS fitting, and log a hard `qha_invalid` flag if the minimum falls outside the clean volume bracket.

### 9. Supercell Mismatch (SevenNet 100-Atom Cap vs. 400-Atom MACE/ORB) & Autograd Graph Leak `[Compute / Physics]`
* **Must fix before 17:00:** **NO** (fix in Task 1.5 worker).
* **Why it matters:** Using a $\le 100$-atom supercell for SevenNet and a $\le 400$-atom supercell for MACE/ORB mixes finite-size Brillouin-zone folding error into your ensemble uncertainty spread. Furthermore, SevenNet taking 7.1 GB on 100 atoms during finite displacements usually indicates either unfreed PyTorch autograd graphs across the displacement loop or a large cutoff batch.
* **Concrete fix:**
  1. In the displacement loop, explicitly call `.detach().cpu().numpy()` on forces, `del atoms_batch`, and `torch.cuda.empty_cache()` every 10 displacements.
  2. Standardize the supercell matrix across **all 4 models** per structure (e.g., target minimum lattice length $L \ge 9.5\text{ \AA}$, capped at $\sim 120\text{–}160$ atoms) so all models sample the exact same phonon $q$-grid.

### 10. Uncancelled X–H Stretch Anharmonicity Between Different H-Bond Topologies `[Physics / Judging]`
* **Must fix before 17:00:** **NO** (add diagnostic in Task 4.1).
* **Why it matters:** O–H and N–H stretching modes ($2800\text{–}3700\text{ cm}^{-1}$) have intrinsic Morse anharmonicity of $\sim 10\text{–}15\text{ meV/H}$, which is $5\text{–}10\times$ larger than $\Delta\Delta F_{\text{iso}}$. Harmonic $\Delta\Delta F_{\text{iso}}$ is only reliable when stretch anharmonicity cancels between polymorphs (similar X–H bond lengths) or when the isotope shift comes from librational/bending modes ($<1600\text{ cm}^{-1}$).
* **Concrete fix:** Split the phonon DOS integral into **low/mid-frequency ($\le 1800\text{ cm}^{-1}$, lattice + librations + bends)** and **high-frequency ($> 1800\text{ cm}^{-1}$, X–H stretches)**. Report both contributions in the candidate table and flag pairs where $>70\%$ of $\Delta\Delta F_{\text{iso}}$ comes from a large shift in X–H stretch frequency ($\Delta\bar{\omega}_{\text{stretch}} > 150\text{ cm}^{-1}$) as "anharmonic-sensitive".

### 11. Windows Unattended GPU Watchdog Race Condition & Corrupt JSON Writes `[Orchestration / Compute]`
* **Must fix before 17:00:** **NO** (implement in Task 1.5 `screen.py`).
* **Why it matters:** If the 60-minute Haiku watchdog thinks the runner is stalled during a slow 130 s QHA job and spawns a second runner on Windows, **two processes will fight for the 8 GB RTX 4060**, causing every subsequent job to OOM-fail overnight. Also, if a job crashes mid-write of `results/<id>.json`, a half-written JSON will permanently skip or crash resume logic.
* **Concrete fix:**
  1. Use an OS-level single-instance lock (`msvcrt.locking` on `results/gpu.lock` or PID check via `psutil` / `tasklist`) inside `screen.py` so a second instance immediately exits if one is alive.
  2. Write all result files atomically: write to `results/<id>.json.tmp`, flush, then `os.replace()` to `results/<id>.json`.

### 12. Unlisted YouTube Video vs. Moment "Social Media Post Link" Requirement `[Submission]`
* **Must fix before 17:00:** **YES** (check Moment submission form during Morning Checklist).
* **Why it matters:** `PLAN.md` notes the Moment form asks for `(1) link to social media post (the video goes here)`, while the video section says Can will paste an **unlisted YouTube URL** and skip LinkedIn/X. If Moment validates for a social platform domain (X/LinkedIn/Bluesky) or judges require a public social post for hackathon eligibility/prizes, an unlisted YouTube link could disqualify or penalize the submission.
* **Concrete fix:** Before 17:00, open the Moment submission form (`scientificintelligence.org`) and check the exact field label, URL validator, and rules in `#general`. If a social post is required and Can prefers not to use his personal LinkedIn/X, create a dedicated project X/Bluesky account now or make the YouTube video public.

### 13. Hardcoded CLI Model Names (`gpt-6-astra`, `Gemini 4 Argon`) & Bond MCP Routing `[Orchestration]`
* **Must fix before 17:00:** **YES** (verify in Task 0.3 before 17:00).
* **Why it matters:** `WORKFLOW.md` hardcodes `codex exec -m gpt-6-astra -c model_reasoning_effort=xhigh` and routes Bond queries through both Claude and Codex MCPs. If the CLI rejects the alias string or the Valency MCP token drops/rate-limits on bulk queries, WF1 stalls at 17:30.
* **Concrete fix:** During Task 0.3 (before 17:00), run one live test of the exact `codex exec` command, one `harness.ask` call to Gemini, and one `valency` MCP query from Codex, logging the exact working CLI flags in `CLAUDE.md` / `WORKFLOW.md`. Keep OpenAlex/Crossref script fallback ready if Bond rate-limits.

### 14. Pre-Event `isoshift/` vs. Event `src/isoshift_event/` Auditability `[Submission / Judging]`
* **Must fix before 17:00:** **YES** (tag repo at 17:00).
* **Why it matters:** Organizers require explicit separation of pre-existing vs. hackathon code, and judge strictly on work done *during* the event. Because `isoshift/` already contains MLIP calculators, mass-override phonons, QHA, and `jarvis_h_pairs.csv`, judges inspecting the repo without a hard timestamped boundary may discount the technical implementation as pre-baked.
* **Concrete fix:** At 17:00 sharp, commit all pre-event files and push an immutable git tag (`git tag v0.0-pre-event-baseline`). Ensure all ensemble uncertainty quantification, mode-band decomposition, $\Delta T_{\text{iso}} / \Delta P_{\text{iso}}$ solvers, DFT phonon benchmarking, and the `marimo` app live entirely in `src/isoshift_event/` and `app/`.

### 15. Linearized $\Delta T_{\text{iso}} \approx \Delta\Delta F_{\text{iso}} / \Delta S$ Ambiguity ($\Delta S_H \neq \Delta S_D$) `[Physics / Method]`
* **Must fix before 17:00:** **NO** (resolve in WF1 `mathcheck`).
* **Why it matters:** D modes populate at lower temperatures than H modes ($\omega_D \approx \omega_H / \sqrt{2}$), so $\Delta S_{\text{vib}}^D(T)$ and $\Delta S_{\text{vib}}^H(T)$ can differ significantly between 100 K and 500 K, and $\Delta S(T) \to 0$ as $T \to 0$ (making $\Delta\Delta F_{\text{iso}}/\Delta S$ diverge at low $T$). Using an unguarded single-point derivative produces unphysical giant $\Delta T_{\text{iso}}$ numbers for flat free-energy curves.
* **Concrete fix:** Since `phonopy` outputs $F_{\text{vib}}^H(T)$ and $F_{\text{vib}}^D(T)$ on a 1 K grid ($0\text{–}1000\text{ K}$) for free, solve for the crossing shift **directly by root-finding** $T_c^D - T_c^H$ on the interpolated $\Delta G(T)$ curves (with a minimum slope guard $|\Delta S_{\text{vib}}| \ge 0.01\text{ meV/atom/K}$), and use $\Delta\Delta F_{\text{iso}} / \Delta S_{\text{avg}}$ only as an analytical check.