**Pick F2, narrowly—but only after imposing a hard baseline gate.** It offers the cleanest route to a result an adversarial judge can independently verify. F1 has stronger materials relevance, but its most exciting headline depends on resolving energy differences your proposed validation cannot reliably establish.

These are **subjective planning probabilities**, conditional on competent solo execution—not measured forecasts. The competing field is unknown. I have not verified the supplied literature searches; neither “no inorganic screen” nor “no record since 2012” establishes novelty.

### 1. Judge’s assessment

“Positive headline” below means a defensible substantive finding, beyond merely building the pipeline.

| Rank | Finalist | Scientific soundness and first attack | Positive headline in 34 h | First place |
|---|---|---|---:|---:|
| **1** | **F2: PackEvolve** | Sound optimization problem. First attack: **Does it beat the correct reference envelope, including phase-separated packings, and is feasibility certified?** Materials relevance needs substance. | **3–10%** | **2–7%** |
| **2** | **F1: IsoSwitch** | Mass substitution is sound within the harmonic approximation. First attack: **Your predicted stability reversal is smaller than your model error.** | **5–15%** for credible new switching candidates; confirmed switching much lower | **2–5%** |
| **3** | **F5: DataDoctor** | Sound if corrections have traceable evidence. First attack: **Without original references, how do you distinguish errors from legitimate experimental variation?** | **25–45%** | **1–4%** |
| **4** | **F3: GNoME audit** | Useful bibliometrics, but reported compounds do not automatically validate predicted structures or thermodynamic stability. First attack: **Your denominator, discovery dates, and detection recall are biased.** | **15–30%** | **<2%** |
| **5** | **F4: Na conductors** | MD transport screening is valid in principle. First attack: **Did you observe enough independent diffusion events, and does either potential describe this chemistry?** Two models can share errors. | **3–10%** | **<2%** |

F4’s approximately 2,000 compounds are an inappropriate starting scope for this hardware and deadline. Conductivity additionally requires care with correlations, temperature extrapolation, and phase stability.

### 2. F1: real physics, fragile discovery claim

**Yes, isotope effects can reverse sufficiently close free-energy orderings.** But the large absolute H/D ZPE change is not the relevant quantity: you need its **difference between polymorphs**.

For an approximately H-dominated mode,

\[
\omega_D\approx\omega_H/\sqrt2,\qquad
E_{\mathrm{ZPE},D}-E_{\mathrm{ZPE},H}\approx-0.146\,\hbar\omega_H.
\]

A 3,000 cm⁻¹ stretching mode therefore loses approximately **54 meV** of ZPE on deuteration. However, if two polymorphs differ by only **100 cm⁻¹** in that mode, their isotope-induced *relative* shift is only approximately **1.8 meV per mode**. Several modes can accumulate meaningful shifts; cancellation is also common. Keep **per formula unit versus per atom** explicit.

**A universal MLIP is not automatically accurate enough.** Phonons test second derivatives; hydrogen bonding, proton transfer, soft modes, and unfamiliar coordination can defeat otherwise reasonable energy predictions. Relative isotope shifts may cancel some errors, but that is a hypothesis requiring validation. Agreement between two potentials is insufficient.

Relevant established examples include **KH₂PO₄/KD₂PO₄**, with strongly different ferroelectric transition temperatures; isotope-dependent ordering in **ammonium halides**; and proton/deuteron ordering phenomena in **ice**. These establish physical plausibility. They do **not** automatically validate harmonic polymorph screening: anharmonicity, tunnelling, configurational disorder, isotope-induced geometry changes, and kinetics can govern the observed behaviour.

A generic PhononDB comparison is useful only where chemistry and modes match your targets. Quasi-harmonic calculations do not repair proton-transfer anharmonicity.

**Defensible claim:** “Validated isotope sensitivity identifies near-degenerate candidates for targeted investigation.”  
**Currently indefensible claim:** “We discovered deuteration-controlled polymorph switches.”

### 3. F2: credible headline, low record probability

My estimate for beating a **genuine best-known binary density represented by the 2012 diagram** in 34 hours is **1–5%**. Matching several structures is substantially more realistic. Larger cells create opportunities and vastly harder optimization.

Critical traps:

- A composition-specific packing can lose to **coexistence of other packings**.
- An unreported parameter point is not automatically a meaningful record.
- Floating-point non-overlap checks are not “exact.” Use conservative certification, including periodic images and numerical uncertainty.
- Ternary novelty claims require their own literature baseline.
- “AI found it” requires attribution: compare evolved generators against random search and conventional optimization under matched budgets.

Sphere packing connects to materials, but **maximum density does not establish experimental assembly or energetic stability**. Present geometric structural hypotheses accordingly.

### 4. Sharpened winner and internal fallback

**PackEvolve: an auditable discovery engine for periodic binary packings.** Fix a narrow radius-ratio region with a verified reference envelope; reproduce known structures before searching larger cells. Save every candidate, independently certify feasible density, publish reconstructible coordinates, and measure whether program evolution improves search efficiency. Spend the first **six hours** on baseline reproduction and certification; failure there ends record hunting. The same pipeline’s fallback is a validated packing benchmark and search tool, demonstrating reproducible recovery and quantified efficiency gains. That fallback is credible but unlikely to win without exceptional execution. **Choose F2 for verification strength; recognize that first place still requires a discovery or a striking, measured algorithmic improvement.**