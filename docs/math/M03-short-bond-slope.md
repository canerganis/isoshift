# M03: an analytic estimate of the short-bond slope

Status: derived twice, independently (GPT-6 Astra xhigh, Claude Opus high), numerically cross-checked and accepted by the `mathcheck` workflow (run `wf_125a7256-90c`, 23 Oct 2026). Written after submission; it does not change any frozen number. Check script: `docs/math/M03_check.py` (both derivations as functions plus the cross-check output).

## Question

F01 finds that the harmonic isotope double difference per H between two polymorphs, ddF_iso = [F_D(b) - F_H(b)] - [F_D(a) - F_H(a)], grows with the difference in mean O-H length: 0.11 to 0.13 meV per H per mÅ over all rows, 0.13 to 0.15 in the strong hydrogen-bond regime, with a stretch-only slope of 0.25 to 0.31 and bend and libration cancelling 49 to 56% of it. F01 states this as a fit. This note asks whether the size and sign follow from harmonic physics plus one empirical input.

## One harmonic mode

For a mode of frequency omega_H, F(omega, T) = kT ln[2 sinh(hbar omega / 2kT)], including the zero-point energy. The isotope ratio is rho = omega_H/omega_D = sqrt(mu_D/mu_H) with mu = m_O m_X/(m_O + m_X). With 16O, H and D masses, mu_H = 0.948087 u, mu_D = 1.788824 u, rho = 1.373607 and 1/rho = 0.728010. Using 1/sqrt(2) instead overstates every shift by 7%.

    dF_mode(T) = F_D - F_H = kT ln[ sinh(x/2rho) / sinh(x/2) ],   x = hbar omega_H / kT

At 0 K this is -(hbar omega_H/2)(1 - 1/rho), minus the zero-point difference. At high T it is -kT ln rho + (hbar^2 omega_H^2 / 24kT)(1/rho^2 - 1); the first term depends on mass only and cancels between polymorphs, and the second, summed over the modes of an H site, is the Wigner-Kirkwood term (hbar^2/24kT)(1/m_D - 1/m_H) Tr Phi_HH.

Test case: nu_H = 3400 cm^-1 gives a zero-point difference of 57.328 meV per mode; the 300 K value differs by 2e-4 meV.

## Stretch slope

Let s = -d nu_stretch / d r_OH (cm^-1 per mÅ), the empirical softening of the stretch as the O-H bond lengthens. Linearising,

    S_str = d ddF / d(d_b - d_a) = s (hc/2) [ coth(x/2) - (1/rho) coth(x/2rho) ]

which at 0 and 300 K is S_str = (hc/2)(1 - 1/rho) s = 0.016861 s meV per H per mÅ, independent of nu between 3000 and 3600 cm^-1 to better than 5e-5. Values: s = 10, 15, 20, 25 gives 0.169, 0.253, 0.337, 0.422.

Sign: a longer O-H bond (stronger hydrogen bond) softens the stretch, so F_D - F_H is less negative, ddF > 0 for d_b > d_a, and from the stretch alone deuteration favours the polymorph with the shorter O-H bond. This is the direction of the short-bond rule.

The empirical input. From the screen's own phonons (`results/stretch_check.csv`, rows with stretch weight above 0.5, mean O-H 0.96 to 1.05 Å), the model stretch frequencies fall by 19.0 to 19.5 cm^-1 per mÅ (MACE 19.0, ORB 19.3, MatterSim 19.5; r = -0.99 to -1.00; 17 to 21 cm^-1 per mÅ over narrower windows). An experimental value for d nu / d r_OH was not checked against a primary source in this note and is not used.

With s = 19 to 19.5, S_str = 0.32 to 0.33 meV per H per mÅ. The mode-resolved stretch slope in F01 is 0.25 to 0.31, so the one-mode estimate is 5 to 30% high. Two likely reasons, not tested here: the F01 regressor is the mean O-H length of all H in the cell while s is fitted per donor, and the stretch is not a pure mode (the screen's stretch weights are below 1, so part of the shift sits in mixed modes counted as bend).

## Bends and librations

Each H has two bending modes (in plane and out of plane), and in hydroxides and hydrates librations play the same role. They harden as the hydrogen bond strengthens, so with s_b = +d nu_b / d r_OH > 0 and n_b = 2,

    S_bend = -n_b s_b (hc/2) [ coth(x_b/2) - (1/rho_b) coth(x_b/2rho_b) ]
    compensation f = -S_bend / S_str

At 0 K with rho_b close to rho_s, f = n_b s_b / s, so the screen's f of about 0.5 corresponds to s_b of about s/4, roughly 5 cm^-1 per mÅ per bend for s = 19. Omitting the factor 2 for the two bends would double the inferred s_b. The bend slope was not measured separately in this note; s_b here is what the observed compensation implies.

## Temperature

Bend and libration terms lose weight with temperature faster than the stretch: relative to 0 K the stretch weight is 1.000 at 300 K and 0.988 at 600 K, a 1600 cm^-1 bend 0.983 and 0.813, a 1200 cm^-1 bend 0.941 and 0.687, a 900 cm^-1 libration 0.858 and 0.556. With s = 18, s_b = 4.5 and nu_b = 1400 cm^-1, f falls from 0.50 (0 K) to 0.48 (300 K) and 0.38 (600 K), and the net slope rises from 0.15 to 0.16 and 0.19. At high T the sign is set by one monotone quantity, the H force-constant trace, while at 0 K bend and libration cancel half of the stretch and small errors can flip signs. This agrees in direction with F09 (sign rule right in 153, 185 and 210 of 212 evaluations at 0, 300 and 600 K). The size of the 0 to 300 K jump is larger than bend weights alone give and needs librations and lattice modes below about 900 cm^-1 and rows near zero; that part is a plausibility argument, not a derivation of the counts.

## What this changes about the claim

The direction of the rule and the size of the stretch slope follow from harmonic physics plus one empirical relation, d nu / d r_OH. The high-temperature direction is the textbook force-constant argument already noted in decision 08. What the screen adds is the outcome of the stretch against bend and libration competition at room temperature across real polymorph pairs, its net slope, where it fails (weak hydrogen bonds; the Al(OH)3 structure where bend and libration cancel 95 to 132% of the stretch) and the AlOOH prediction. The rule is therefore best described as a physically expected effect, quantified and bounded for polymorph stability, not as an unexplained correlation.

## Assumptions

Harmonic modes; isolated O-H stretch with reduced mass of O and H (the crystal environment changes rho by less than 0.1%, while anharmonicity lowers the measured O-H/O-D ratio to about 1.33 to 1.36 and is outside this note); linear dependence of frequencies on O-H length over the range used; bends treated as two modes of one frequency; one H per site counted per H.
