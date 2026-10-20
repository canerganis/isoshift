### 1. Finalist Red-Team Audit

* **F1. IsoSwitch (H/D Polymorph Switching)**
  * **Soundness:** Physically sound for the *differential isotope shift* $\Delta\Delta F_{\text{iso}} = (\Delta F_{\text{D}} - \Delta F_{\text{H}})^{\alpha\to\beta}$, because Born–Oppenheimer force constants are mass-independent and static $\Delta E_{\text{elec}}$ errors cancel in the shift itself. Unsound if claiming definitive phase flips when $\Delta E_{\text{elec}}$ is taken from PBE/MLIP without dispersion/hybrid validation.
  * **First expert attack:** *"Famous H/D phase shifts (KDP, ice) are governed by anharmonic double-well potentials and proton tunneling, where harmonic phonons give imaginary modes. Meanwhile, PBE/MLIP polymorph rankings have $\sim 10\text{–}20\text{ meV/atom}$ errors—5$\times$ larger than your isotope shift."*
  * **34 h positive result:** **80%** | **1st Place probability:** **35%**

* **F2. PackEvolve (LLM-Evolved Binary/Ternary Sphere Packings)**
  * **Soundness:** Mathematically bulletproof. Hard-sphere non-overlap and packing fraction $\phi$ are exact, zero-noise, deterministically verifiable ground truths.
  * **First expert attack:** *"Two critiques: (1) Did the LLM actually discover anything, or did `scipy.optimize` do all the work on random seeds? (2) Hard spheres aren't real chemistry—why should materials scientists care?"* Both are fatal if unaddressed, and lethal weapons in your favor if preempted.
  * **34 h positive result:** **75%** | **1st Place probability:** **50%**

* **F3. GNoME Literature Reality Check**
  * **Soundness:** Flawed experimental design. Solid-state synthesis takes years, novel phases hide in CIF tables rather than abstracts, and chemical formula normalization across doped experimental reports is notoriously noisy.
  * **First expert attack:** *"Absence of abstract mentions in 24 months is not evidence of non-synthesizability; your recall on quaternaries is uncalibrated."*
  * **34 h positive result:** **20%** | **1st Place probability:** **<3%**

* **F4. Fast Na-Ion Conductors via MLIP-MD**
  * **Soundness:** Standard workflow, severe compute bottleneck. Accurate room-temperature diffusivity requires long nanosecond trajectories across multiple temperatures; 50 ps high-$T$ bursts on an RTX 4060 yield massive Arrhenius extrapolation error bars.
  * **First expert attack:** *"This is a 2023 workflow on a smaller budget. Short high-$T$ MLIP-MD melts or overestimates $\sigma_{300\text{K}}$ by orders of magnitude."*
  * **34 h positive result:** **50%** | **1st Place probability:** **10%**

* **F5. DataDoctor (Benchmark Auditing)**
  * **Soundness:** Rock-solid data engineering, zero scientific discovery.
  * **First expert attack:** *"Useful janitorial service, but the prompt asked if a real discovery is possible in two days."*
  * **34 h positive result:** **95%** | **1st Place probability:** **5%**

---

### 2. Deep Dive: F1 (IsoSwitch)

* **Is H/D ZPE large enough to flip realistic inorganic polymorphs?**
  **Yes, for nearly degenerate polymorphs.** A single H atom contributes $\sim 150\text{–}250\text{ meV}$ to total ZPE ($\frac{1}{2}\sum \hbar\omega_i$). Deuteration scales pure H-modes by $1/\sqrt{2}$, reducing total ZPE by **$\sim 45\text{–}70\text{ meV per H}$**. However, polymorph switching depends on the *difference* in ZPE between polymorphs $\alpha$ and $\beta$:
  $$\Delta\Delta E_{\text{ZPE}} \approx \left(1 - \frac{1}{\sqrt{2}}\right)\left(\text{ZPE}_{\text{H}}^{\alpha} - \text{ZPE}_{\text{H}}^{\beta}\right) \approx 0.293\,\Delta\text{ZPE}_{\text{H}}$$
  Between distinct coordination or H-bonding geometries, $\Delta\text{ZPE}_{\text{H}}$ is typically $5\text{–}25\text{ meV/H}$, yielding a net isotope switch of **$1.5\text{–}7.5\text{ meV per H atom}$** ($\sim 0.5\text{–}3\text{ meV/atom}$). Around $10\text{–}15\%$ of H-containing polymorph pairs in Materials Project lie within $<3\text{ meV/atom}$.
* **Are universal MLIPs accurate enough?**
  PBE-trained MLIPs (MACE-MP-0, ORB) soften O–H/N–H stretches by $5\text{–}10\%$ and omit LO–TO splitting, **but** systematic errors largely cancel in $\Delta\Delta F_{\text{iso}}(T)$. Avoid proton-disordered H-bonds with imaginary harmonic modes; focus on **metal hydrides, borohydrides ($\text{MBH}_4$), alanates, and ordered hydroxides** where modes are well-behaved.
* **Known inorganic examples:** Ice polymorph boundaries ($\text{H}_2\text{O}/\text{D}_2\text{O}$ VI/VII/VIII, Ih/XI), $\text{PdH}_x/\text{PdD}_x$, $\text{VH}_2/\text{VD}_2$ phase transitions, $\text{LiBH}_4/\text{LiBD}_4$, high-pressure $\delta\text{-AlOOH}/\text{AlOOD}$ and $\varepsilon\text{-FeOOH}$, $\text{NH}_4\text{Cl}/\text{ND}_4\text{Cl}$, and $\text{KH}_2\text{PO}_4$ (KDP).

---

### 3. Deep Dive: F2 (PackEvolve)

* **Realistic chance to beat a 2012 record in 34 h:**
  * **At $N \le 12$ on exact Hopkins–Stillinger–Torquato (HST 2012) grid points:** Low ($\sim 20\%$), as Torquato–Jiao’s Adaptive Shrinking Cell (ASC) searched small cells thoroughly.
  * **At $N = 13\text{–}36$ using symmetry-aware (Wyckoff/space-group) generator programs, between grid points, or in ternary packings:** **High ($>75\%$)**. HST-2012 was bottlenecked by free-coordinate dimensionality at $N > 12$; a program synthesis loop that proposes *crystallographic motif rules* (chains, icosahedral clusters, layered nets, space-group Wyckoff placements) collapses a $3N$-dimensional search into a $2\text{–}5$ parameter search that L-BFGS-B/FIRE + JAX can polish on your RTX 4060 at thousands of cells per minute.
* **Credibility & Relevance to Materials Judges:**
  * **Credibility is 100%:** Unlike MLIP predictions that a skeptical DFT judge can dismiss as artifacts, a packing with $\phi_{\text{new}} > \phi_{\text{HST}} + 10^{-4}$ verified in exact rational/float64 geometry is an **irrefutable mathematical discovery made in 34 hours**.
  * **Materials relevance requires one extra step:** Map every discovered $(\alpha, x)$ or $(\alpha, \beta, x, y)$ packing to real **ionic radius ratios (Shannon radii), metallic glass compositions, and colloidal nanocrystal superlattices**, then decorate the top packings with real elements and relax with MACE to show they form low-energy crystal prototypes.

---

### 4. Final Ranking & Winning Execution Plan

**Rank for 1st Place:** **1. F2 (PackEvolve)** $\succ$ **2. F1 (IsoSwitch)** $\succ\succ$ **3. F4** $\succ$ **4. F5** $\succ$ **5. F3**

*Why F2 edges out F1:* When the organizer asks *"is two days to a real discovery possible?"*, F1 gives a *plausible candidate subject to DFT/anharmonicity error bars*, whereas F2 delivers a **provable, zero-dispute mathematical and crystallographic discovery** plus maximum "AlphaEvolve for Crystal Prototypes" excitement.

#### Sharpened Winner: **SymPackEvolve (F2)**
Build a closed-loop **LLM Crystallographic Program Synthesizer + JAX GPU Batch Optimizer** that evolves Python functions generating *symmetry-constrained and motif-based* periodic sphere packings (using `pyxtal`/Wyckoff positions, cluster-packing templates, and laminated lattices rather than raw coordinates). Run a vectorized JAX repulsion + cell-compression solver on the RTX 4060 to polish 1,000 candidate cells in parallel, paired with an exact zero-overlap verifier and an ablation curve proving LLM-evolved symmetry generators beat random/ASC baselines at $N = 13\text{–}32$. Target three high-value zones: (1) binary stability gaps in HST-2012 at $N = 13\text{–}24$, (2) **ternary hard-sphere packings** aligned with common Shannon ionic radius ratios ($\text{ABO}_3$, Heusler, Laves-derivative ratios), and (3) MACE-MP-0 relaxation of the newly discovered packings decorated with real ions/alloys to propose novel crystal structure prototypes. **Built-in Fallback:** Even if HST-2012 binary records at $N \le 12$ hold firm, the exact same pipeline guarantees **(a)** the first systematic dense ternary packing atlas across realistic Shannon radius ratios and **(b)** novel denser binary structures at $12 < N \le 32$ and non-tabulated $\alpha$ ratios.
