"""P12 PIMD module (src/isoshift_event/pimd.py): CPU only, harmonic backend, seeded."""
import json

import numpy as np
import pytest
from ase import Atoms

from isoshift import cache, phonons as Ph
from src.isoshift_event import pimd as M

T = 300.0
M_O = 15.9949146  # 16O (M00 diatomic)
# O mass that main and harmonic_samecell use (natural abundance), so the toy-crystal comparisons share one mass set
M_O_NAT = float(Ph.make_masses(Atoms("O"), {}, default="light")[0])


def _single_atom(nu_thz, P, steps, seed=1, dt=0.25):
    w = 2 * np.pi * nu_thz * 1e-3
    fc = np.zeros((1, 1, 3, 3))
    fc[0, 0] = np.eye(3) * M.M_H * M.AMU_EV * w ** 2
    rp = M.RingPolymer(np.zeros((1, 3)), [M.M_H], P, T, dt, 100.0, M.HarmonicForces(fc, np.zeros((1, 3))),
                       np.random.default_rng(seed), splitting="baoab")
    ks = []
    for s in range(steps):
        rp.step()
        if s >= steps // 5:
            ks.append(rp.kinetic_cv(np.array([True])))
    wk = M.nm_freqs(P, T)
    exact_p = 3 * 0.5 * M.KB_EV * T * np.sum(w ** 2 / (w ** 2 + wk ** 2))
    return np.mean(ks), M.block_error(ks)[0], exact_p


def test_nm_matrix_orthonormal_and_freqs():
    for P in (1, 2, 5, 8):
        C = M.nm_matrix(P)
        assert np.allclose(C.T @ C, np.eye(P))
        assert np.allclose(C[:, 0], 1 / np.sqrt(P))
    wk = M.nm_freqs(8, T)
    assert wk[0] == 0 and np.isclose(wk[4], 2 * 8 * M.KB_EV * T / M.HBAR_EV_FS)


def test_classical_limit_one_bead():
    k, _, ex = _single_atom(30.0, 1, 200)
    assert k == pytest.approx(1.5 * M.KB_EV * T, rel=1e-12) and ex == pytest.approx(k)


def test_1d_oscillator_matches_finite_p_exact():
    """Single H in an isotropic 3D well: <K_cv> equals the closed-form P-bead value within 3 sigma."""
    k, err, ex = _single_atom(60.0, 16, 60000)
    assert abs(k - ex) < 3 * err + 1e-5, (k * 1e3, err * 1e3, ex * 1e3)
    assert err * 1e3 < 1.0


def test_1d_oscillator_h_to_d_within_0p2_meV_of_analytic():
    """P12 section 2, 1D harmonic oscillator: one H on a fixed spring (infinitely heavy anchor, so no centre of
    mass term), isotropic, so the three Cartesian directions are three independent identical 1D oscillators and
    the 1D value is the 3D TI result divided by 3. Frequency 60 THz at m_H, omega proportional to g at fixed
    spring. Compared with the analytic quantum 1D value (P -> infinity) at the production dt."""
    nu, P = 60.0, 64
    w = 2 * np.pi * nu * 1e-3
    fc = np.zeros((1, 1, 3, 3))
    fc[0, 0] = np.eye(3) * M.M_H * M.AMU_EV * w ** 2
    rp = M.RingPolymer(np.zeros((1, 3)), [M.M_H], P, T, 0.25, 100.0, M.HarmonicForces(fc, np.zeros((1, 3))),
                       np.random.default_rng(3), splitting="baoab")
    g, wq = M.ti_nodes(4)
    pts = M.run_points(rp, np.array([True]), g, 60000, 0.2, np.array([M.M_H]))
    df, err = M.ti_integrate(g, wq, [p["K_H_meV"] for p in pts], [p["K_H_err_meV"] for p in pts])
    df1, err1 = df / 3, err / 3
    exact = (M._osc_free_energy(nu * M.G_D, T) - M._osc_free_energy(nu, T)) * 1e3
    exact_p = (M._osc_free_energy(np.array([nu * M.G_D]), T, P).sum()
               - M._osc_free_energy(np.array([nu]), T, P).sum()) * 1e3
    assert abs(df1 - exact) < 0.2, (df1, err1, exact, exact_p)
    assert abs(df1 - exact_p) < 3 * err1, (df1, err1, exact_p)
    assert err1 < 0.1 and all(p["error_converged"] for p in pts)


def test_ti_quadrature_exact_integrand():
    """4-point Gauss-Legendre with the exact harmonic <K_H(g)> reproduces F_D - F_H (omega proportional to g)."""
    nu_h = np.array([100.0, 35.0, 35.0])
    g, w = M.ti_nodes(4)
    assert g[0] > g[-1] and np.isclose(w.sum(), 1 - M.G_D)
    kT = M.KB_EV * T
    k = [np.sum(M.HBAR_EV_FS * (2 * np.pi * nu_h * gi * 1e-3) / 4
                / np.tanh(M.HBAR_EV_FS * 2 * np.pi * nu_h * gi * 1e-3 / (2 * kT))) for gi in g]
    exact = M._osc_free_energy(nu_h * M.G_D, T).sum() - M._osc_free_energy(nu_h, T).sum()
    assert abs(M.ti_integrate(g, w, k) - exact) * 1e3 < 0.01
    assert M.ti_integrate(g, w, k) < 0


def test_equal_masses_give_zero():
    g, w = M.ti_nodes(4, g_lo=1.0)
    assert np.allclose(w, 0) and M.ti_integrate(g, w, np.full(4, 0.3)) == 0


def test_estimator_ignores_non_h_atoms():
    fc = np.zeros((2, 2, 3, 3))
    fc[0, 0] = fc[1, 1] = np.eye(3) * 20.0
    rp = M.RingPolymer(np.zeros((2, 3)), [M_O, M.M_H], 8, T, 0.25, 100.0,
                       M.HarmonicForces(fc, np.zeros((2, 3))), np.random.default_rng(0), splitting="baoab")
    for _ in range(50):
        rp.step()
    mask = np.array([False, True])
    k = rp.kinetic_cv(mask)
    rp.f[:, 0] += 123.0
    rp.q[:, 0] += 0.3 * np.random.default_rng(1).standard_normal((8, 3))
    assert rp.kinetic_cv(mask) == k


# ---- isolated O-H diatomic, the P12 acceptance check

NU_OH = np.array([108.0, 40.0, 40.0])  # stretch along x and two perpendicular relative modes, THz, for O-H


def _diatomic_fc():
    mu_h = M_O * M.M_H / (M_O + M.M_H)
    ks = mu_h * M.AMU_EV * (2 * np.pi * NU_OH * 1e-3) ** 2
    K = np.diag(ks)
    fc = np.zeros((2, 2, 3, 3))
    fc[0, 0] = fc[1, 1] = K
    fc[0, 1] = fc[1, 0] = -K
    return fc, ks


def _diatomic_exact(m_h, ks, P=None):
    """Exact F of the model below: 6 degrees of freedom = 3 relative harmonic modes with the reduced mass
    mu = m_O m / (m_O + m) + the free 3D centre of mass with M = m_O + m. No rotations: the two perpendicular
    relative directions are bound by springs (a harmonic model of the molecule, not a free rotor)."""
    mu = M_O * m_h / (M_O + m_h)
    nu = np.sqrt(ks / (mu * M.AMU_EV)) / (2 * np.pi * 1e-3)
    return M._osc_free_energy(nu, T, P).sum() + M.com_free_energy(M_O + m_h, T)


def test_oh_diatomic_com_term_is_the_free_translation():
    """The H to D shift of the free centre of mass is -(3/2) kT ln[(m_O + m_D)/(m_O + m_H)], about -2.23 meV at
    300 K. It is part of the analytic reference below, because the ring polymer of two free atoms contains it;
    without it the stretch-only reference would be off by far more than the 0.2 meV tolerance."""
    _, ks = _diatomic_fc()
    com = (M.com_free_energy(M_O + M.M_D, T) - M.com_free_energy(M_O + M.M_H, T)) * 1e3
    assert com == pytest.approx(-1.5 * M.KB_EV * T * np.log((M_O + M.M_D) / (M_O + M.M_H)) * 1e3, rel=1e-12)
    assert -2.3 < com < -2.2
    full = (_diatomic_exact(M.M_D, ks) - _diatomic_exact(M.M_H, ks)) * 1e3
    rel_only = full - com
    assert abs(full - rel_only) > 1.0


def test_oh_diatomic_within_0p2_meV_of_analytic():
    """P12 section 2: isolated O-H diatomic (finite O mass, M00 reduced mass), H to D within 0.2 meV of the
    analytic quantum value, at the production time step 0.25 fs (this also bounds the PILE-L time-step bias of
    the harmonic O-H stretch at 108 THz). Degrees of freedom as in _diatomic_exact: the TI over the H mass with
    two free atoms includes the centre-of-mass translation, and so does the reference. P = 128 keeps the bead
    error near 0.1 meV."""
    fc, ks = _diatomic_fc()
    x0 = np.array([[0.0, 0, 0], [0.97, 0, 0]])
    P = 128
    rp = M.RingPolymer(x0, [M_O, M.M_H], P, T, 0.25, 100.0, M.HarmonicForces(fc, x0), np.random.default_rng(12),
                       splitting="baoab")
    g, w = M.ti_nodes(4)
    pts = M.run_points(rp, np.array([False, True]), g, 250000, 0.2, np.array([M_O, M.M_H]))
    df, err = M.ti_integrate(g, w, [p["K_H_meV"] for p in pts], [p["K_H_err_meV"] for p in pts])
    exact = (_diatomic_exact(M.M_D, ks) - _diatomic_exact(M.M_H, ks)) * 1e3
    exact_p = (_diatomic_exact(M.M_D, ks, P) - _diatomic_exact(M.M_H, ks, P)) * 1e3
    assert abs(df - exact) < 0.2, (df, err, exact, exact_p)
    assert abs(df - exact_p) < 3 * err, (df, err, exact_p)
    assert err < 0.15 and all(p["error_converged"] for p in pts)


# ---- periodic toy crystal

def _toy_phonopy(sc=(2, 2, 2)):
    """Cubic cell a = 4 A with O at 0 and H at (1, 0, 0) A; isotropic springs O-H (intra) and O-O, H-H (nn).
    Force constants are built directly on the phonopy supercell (exact acoustic sum rule)."""
    from phonopy import Phonopy

    uc = Ph._pa(["O", "H"], np.eye(3) * 4.0, [[0, 0, 0], [0.25, 0, 0]], [M_O, M.M_H])
    ph = Phonopy(uc, supercell_matrix=np.diag(sc), primitive_matrix="P", log_level=0)
    s = ph.supercell
    pos, cell, sym = s.positions, s.cell, list(s.symbols)
    n = len(pos)
    mu = M_O * M.M_H / (M_O + M.M_H) * M.AMU_EV
    k_oh = mu * (2 * np.pi * 70e-3) ** 2
    k_nn = 2.0
    fc = np.zeros((n, n, 3, 3))
    shifts = np.array([[i, j, k] for i in (-1, 0, 1) for j in (-1, 0, 1) for k in (-1, 0, 1)]) @ cell
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            d = np.linalg.norm(pos[j] + shifts - pos[i], axis=1)
            kk = 0.0
            if sym[i] != sym[j]:
                kk = k_oh * np.sum(np.isclose(d, 1.0))
            else:
                kk = k_nn * np.sum(np.isclose(d, 4.0))
            fc[i, j] = -kk * np.eye(3)
    for i in range(n):
        fc[i, i] = -fc[i].sum(axis=0)
    ph.force_constants = fc
    return ph


def test_samecell_reference_matches_supercell_hessian():
    """Interpolated commensurate-q reference vs the supercell's own finite-difference Hessian (the check that
    main runs when the PIMD q-points are not commensurate with the force-constant supercell)."""
    ph = _toy_phonopy()
    s = ph.supercell
    x0 = s.positions
    mask = np.array(list(s.symbols)) == "H"
    phi = M.fd_hessian(M.HarmonicForces(ph.force_constants, x0), x0, chunk=7)
    n = len(x0)
    assert np.allclose(phi, ph.force_constants.transpose(0, 2, 1, 3).reshape(3 * n, 3 * n), atol=1e-9)
    direct = M.hessian_samecell(phi, np.where(mask, M.M_H, M_O_NAT), mask, T, P=16)
    ref = M.harmonic_samecell(ph, [2, 2, 2], T, P=16)
    for r in (ref, direct):
        assert r["valid"] and r["translations_verified"] and not r["has_imaginary"]
    assert ref["qpoints_exact"] and ref["fc_asr_max_eV_A2"] < 1e-12
    assert ref["dF_eV"] == pytest.approx(direct["dF_eV"], rel=1e-5)  # phonopy vs CODATA unit constants
    assert ref["dF_P_eV"] == pytest.approx(direct["dF_P_eV"], rel=1e-5)
    assert ref["dF_com_eV"] == pytest.approx(-1.5 * M.KB_EV * T * np.log(
        (8 * (M_O_NAT + M.M_D)) / (8 * (M_O_NAT + M.M_H))), rel=1e-12)
    assert ref["dF_P_eV"] > ref["dF_eV"]  # finite P under-counts the zero-point term


def test_qpoints_commensurate_flag():
    assert M.qpoints_commensurate_with(M.commensurate_qpoints([2, 2, 2]), np.diag([2, 2, 2]))
    assert M.qpoints_commensurate_with(M.commensurate_qpoints([2, 1, 2]), np.diag([4, 2, 2]))
    assert not M.qpoints_commensurate_with(M.commensurate_qpoints([3, 3, 3]), np.diag([2, 2, 2]))
    assert not M.qpoints_commensurate_with(M.commensurate_qpoints([4, 4, 4]), np.diag([2, 2, 2]))


def _two_atom_hessian(nu_stretch, nu_perp, nu_trans):
    """Isolated O-H Hessian (6x6) with a stretch along x, perpendicular relative springs, and a spurious
    restoring term acting only on the mass-weighted translations (a broken acoustic sum rule), which puts the
    three translations at nu_trans without moving the internal modes."""
    m = np.array([M_O, M.M_H])
    mu = M_O * M.M_H / (M_O + M.M_H) * M.AMU_EV
    k = mu * (2 * np.pi * 1e-3 * np.array([nu_stretch, nu_perp, nu_perp])) ** 2 * np.sign([1, nu_perp, nu_perp])
    K = np.diag(k)
    phi = np.block([[K, -K], [-K, K]])
    sm = np.sqrt(np.repeat(m, 3) * M.AMU_EV)
    t = np.zeros((6, 3))
    for a in range(3):
        t[a::3, a] = np.sqrt(m)
    t /= np.linalg.norm(t, axis=0)
    phi += (2 * np.pi * 1e-3 * nu_trans) ** 2 * (sm[:, None] * (t @ t.T) * sm[None, :])
    return phi, m


def test_translations_found_by_eigenvector_not_smallest_frequency():
    """Soft optical modes at 0.02 THz below translations shifted to 0.05 THz by a broken sum rule: the three
    smallest |nu| would be two physical modes and one translation. classify_modes removes the three
    translations and keeps the soft modes, and F_H equals the analytic diatomic value."""
    phi, m = _two_atom_hessian(100.0, 0.02, 0.05)
    isq = 1 / np.sqrt(np.repeat(m, 3) * M.AMU_EV)
    ev, vec = np.linalg.eigh(isq[:, None] * phi * isq[None, :])
    nu = np.sign(ev) * np.sqrt(np.abs(ev)) / (2 * np.pi * 1e-3)
    keep, trans, info = M.classify_modes(nu[None], vec, m)
    assert info["translations_verified"] and info["n_soft_kept"] == 2
    assert np.allclose(nu[trans[0]], 0.05) and np.allclose(np.sort(nu[keep[0]])[:2], 0.02)
    assert set(np.argsort(np.abs(nu))[:3]) != set(np.flatnonzero(trans[0]))
    mu = M_O * M.M_H / (M_O + M.M_H) * M.AMU_EV
    ks = mu * (2 * np.pi * 1e-3 * np.array([100.0, 0.02, 0.02])) ** 2
    assert M._isotope_free_energy(nu[None], keep, m.sum(), T) == pytest.approx(_diatomic_exact(M.M_H, ks), abs=1e-9)
    # The spurious term is not a pure translation shift at the D masses: there it mixes the translations with
    # the soft modes. That is detected (overlap < 0.99) and invalidates the reference instead of guessing.
    r = M.hessian_samecell(phi, m, np.array([False, True]), T)
    assert r["translations_verified_H"] and not r["translations_verified_D"] and not r["valid"]
    # With the sum rule intact both isotopes verify and dF is the analytic diatomic value.
    r0 = M.hessian_samecell(_two_atom_hessian(100.0, 0.02, 0.0)[0], m, np.array([False, True]), T)
    assert r0["valid"] and r0["n_soft_kept_H"] == 2 and r0["n_soft_kept_D"] == 2
    assert r0["dF_eV"] == pytest.approx(_diatomic_exact(M.M_D, ks) - _diatomic_exact(M.M_H, ks), abs=1e-9)


def test_unverified_translations_and_imaginary_modes_invalidate():
    phi, m = _two_atom_hessian(100.0, 30.0, 0.3)  # translations at 0.3 THz: sum rule broken beyond tolerance
    r = M.hessian_samecell(phi, m, np.array([False, True]), T)
    assert not r["translations_verified"] and not r["valid"]
    phi, m = _two_atom_hessian(100.0, -5.0, 0.0)  # imaginary perpendicular modes, never folded to +5 THz
    r = M.hessian_samecell(phi, m, np.array([False, True]), T)
    assert r["translations_verified"] and not r["valid"] and r["has_imaginary"]
    assert r["n_nonpositive_nontranslation_H"] == 2 and r["min_freq_THz_nontranslation_H"] < -4.9


def test_periodic_toy_pimd_matches_samecell_harmonic():
    ph = _toy_phonopy()
    s = ph.supercell
    x0 = s.positions
    mask = np.array(list(s.symbols)) == "H"
    base = np.where(mask, M.M_H, M_O_NAT)
    P = 16
    rp = M.RingPolymer(x0, base, P, T, 0.25, 100.0, M.HarmonicForces(ph.force_constants, x0),
                       np.random.default_rng(5), splitting="baoab")
    g, w = M.ti_nodes(4)
    pts = M.run_points(rp, mask, g, 12000, 0.2, base)
    df, err = M.ti_integrate(g, w, [p["K_H_meV"] for p in pts], [p["K_H_err_meV"] for p in pts])
    ref = M.harmonic_samecell(ph, [2, 2, 2], T, P=P)
    ref_p = ref["dF_P_eV"] * 1e3 / mask.sum()
    assert abs(df - ref_p) < 3 * err + 0.02, (df, err, ref_p)
    assert err < 0.3


# ---- cache matching, CLI, JSON schema, resume

def _fake_tree(tmp_path, n_copies=1, sc=(2, 2, 2), struct="toy-1", decoys=()):
    """decoys: (volume_A3, n_displacements) of extra entries with the same energy, natoms_cell and supercell."""
    ph = _toy_phonopy()
    meta = {"supercell": list(sc), "natoms_cell": 2, "natoms_supercell": 16, "energy_eV": -10.123456,
            "volume_A3": 64.0, "n_displacements": 2}
    root = tmp_path / "cache"
    for i in range(n_copies):
        cache.save_fc(ph, f"h{i:019d}__{M.CALC_ID}__sc2x2x2__d0.01__sym", meta, root=root)
    for i, (v, nd) in enumerate(decoys):
        cache.save_fc(ph, f"x{i:019d}__{M.CALC_ID}__sc2x2x2__d0.01__sym", dict(meta, volume_A3=v, n_displacements=nd),
                      root=root)
    raw = tmp_path / "raw"
    raw.mkdir()
    (raw / f"{struct}.json").write_text(json.dumps({"fc_meta": dict(meta, supercell=[2, 2, 2])}))
    return raw, root


def test_find_cache_unique_missing_ambiguous(tmp_path):
    raw, root = _fake_tree(tmp_path / "a")
    assert M.find_cache("toy-1", raw, root).name.startswith("h0")
    raw2, root2 = _fake_tree(tmp_path / "b", n_copies=2)
    with pytest.raises(LookupError, match="2 cache matches"):
        M.find_cache("toy-1", raw2, root2)
    raw3, root3 = _fake_tree(tmp_path / "c", sc=(3, 3, 3))
    with pytest.raises(LookupError, match="0 cache matches"):
        M.find_cache("toy-1", raw3, root3)
    # the real mp-625054 / mp-626497 case: same energy, natoms and supercell, different volume or n_displacements
    raw4, root4 = _fake_tree(tmp_path / "d", decoys=[(64.0 - 5.5e-4, 2), (64.0, 4)])
    assert M.find_cache("toy-1", raw4, root4).name.startswith("h0")


def test_cli_schema_and_resume(tmp_path):
    raw, root = _fake_tree(tmp_path)
    out = tmp_path / "res" / "toy-1_P4.json"
    args = ["--struct", "toy-1", "--beads", "4", "--steps", "300", "--backend", "harmonic", "--out", str(out),
            "--raw-root", str(raw), "--cache-root", str(root), "--state-root", str(tmp_path / "state")]
    d1 = M.main(args + ["--stop-after", "2"])
    assert d1["status"] == "partial" and len(d1["points"]) == 2 and "dF_PIMD_meV_H" not in d1
    d2 = M.main(args)
    assert d2["status"] == "complete" and len(d2["points"]) == 4
    assert d2["points"][:2] == d1["points"]
    for k in ("struct_id", "cache_key", "supercell", "natoms", "n_H", "P", "dt_fs", "T_K", "tau0_fs", "seed",
              "model", "git", "initial_max_abs_F_eV_A", "gpu_peak_GB", "splitting", "dF_PIMD_meV_H",
              "dF_PIMD_err_meV_H", "dF_harm_samecell_meV_H", "delta_anh_meV_H", "harmonic_samecell",
              "harmonic_valid", "fc_interpolation_verified", "hessian_check", "error_converged", "unverified",
              "harmonic_bead_error_meV_H", "delta_anh_beadcorr_meV_H", "finite_size", "zero_modes"):
        assert k in d2, k
    for p in d2["points"]:
        for k in ("g", "mass_H_u", "weight", "K_H_meV", "K_H_err_meV", "error_converged", "K_H_err_block_meV",
                  "K_H_err_acf_meV", "tau_int_steps", "n_eff", "steps_used", "block_curve_meV", "wall_s"):
            assert k in p, k
    # 300 steps per point cannot resolve the error: the run says so instead of quoting a small block error.
    assert not d2["error_converged"] and any(u.startswith("statistical_error") for u in d2["unverified"])
    assert any(u.startswith("time_step") for u in d2["unverified"])
    assert any(u.startswith("beads") for u in d2["unverified"])
    assert "finite_size_anharmonic" in d2["unverified"]
    assert d2["harmonic_samecell"]["qpoints_exact"] and d2["hessian_check"] is None and d2["fc_interpolation_verified"]
    assert d2["supercell"] == [2, 2, 2] and d2["n_H"] == 8 and d2["dF_PIMD_meV_H"] < 0
    assert d2["delta_anh_meV_H"] == pytest.approx(d2["dF_PIMD_meV_H"] - d2["dF_harm_samecell_meV_H"])
    with pytest.raises(ValueError, match="different arguments"):
        M.main([a if a != "300" else "301" for a in args])


def test_cli_hessian_check_on(tmp_path):
    raw, root = _fake_tree(tmp_path)
    out = tmp_path / "res" / "toy-1_P4.json"
    d = M.main(["--struct", "toy-1", "--beads", "4", "--steps", "40", "--backend", "harmonic", "--out", str(out),
                "--raw-root", str(raw), "--cache-root", str(root), "--state-root", str(tmp_path / "state"),
                "--hessian-check", "on"])
    h = d["hessian_check"]
    assert h["passed"] and abs(h["diff_meV_H"]) < 1e-3 and h["direct_valid"]


# ---- statistical error: plateau and autocorrelation

def _ar1(phi, n, seed):
    rng = np.random.default_rng(seed)
    e = rng.standard_normal(n)
    x = np.empty(n)
    x[0] = e[0] / np.sqrt(1 - phi ** 2)
    for i in range(1, n):
        x[i] = phi * x[i - 1] + e[i]
    return x


def test_stat_error_converges_on_long_ar1():
    """AR(1) with phi = 0.9: tau_int = (1 + phi) / (2 (1 - phi)) = 9.5 samples, var = 1/(1 - phi^2)."""
    phi, n = 0.9, 2 ** 17
    se = M.stat_error(_ar1(phi, n, 4))
    exact = np.sqrt(1 / (1 - phi ** 2) * 2 * 9.5 / n)
    assert se["converged"] and se["plateau_block_size"] is not None
    assert se["tau_int_steps"] == pytest.approx(9.5, rel=0.15)
    assert se["err"] == pytest.approx(exact, rel=0.25)


def test_stat_error_flags_short_correlated_series():
    """phi = 0.995 (tau about 200 samples) with 3000 samples: the block curve is still rising. The old
    maximum-over-blocks value underestimates the true error; stat_error does not call it converged."""
    phi, n = 0.995, 3000
    x = _ar1(phi, n, 5)
    se = M.stat_error(x)
    exact = np.sqrt(1 / (1 - phi ** 2) * (1 + phi) / (1 - phi) / n)
    assert not se["converged"]
    assert M.block_error(x)[0] < exact


# ---- systematic checks between runs (P vs 2P, dt vs dt/2)

def _run_doc(P=32, dt=0.25, df=-60.0, err=0.05, hb=0.4, conv=True):
    return {"struct_id": "toy-1", "status": "complete", "P": P, "dF_PIMD_meV_H": df, "dF_PIMD_err_meV_H": err,
            "error_converged": conv, "harmonic_bead_error_meV_H": hb,
            "run_args": {"beads": P, "steps": 1000, "dt": dt, "T": 300.0, "seed": 12}}


def test_compare_runs_uses_the_error_of_the_difference():
    # observed difference 0.1 meV < 0.3, but each run has 0.3 meV error: the difference is not resolved
    r = M.compare_runs(_run_doc(32, err=0.3), _run_doc(64, df=-59.9, err=0.3, hb=0.1))
    assert r["varied"] == "beads" and r["diff_err_meV_H"] == pytest.approx(0.3 * np.sqrt(2))
    assert not r["converged"]
    r = M.compare_runs(_run_doc(32, err=0.02), _run_doc(64, df=-59.9, err=0.02, hb=0.1))
    assert r["converged"] and r["transfer_P"] == 64 and r["transfer_reference_meV_H"] == 0.1
    assert M.bead_transfer_ok(r, _run_doc(64, hb=0.08))
    assert not M.bead_transfer_ok(r, _run_doc(64, hb=0.2))  # stiffer spectrum: bead error unknown
    assert not M.bead_transfer_ok(r, _run_doc(32, hb=0.05))
    r = M.compare_runs(_run_doc(32, err=0.02, conv=False), _run_doc(64, df=-59.9, err=0.02))
    assert not r["converged"]


def test_compare_runs_time_step_and_bad_pairs(tmp_path):
    a, b = _run_doc(dt=0.25, err=0.03), _run_doc(dt=0.125, df=-60.05, err=0.03)
    pa, pb = tmp_path / "a.json", tmp_path / "b.json"
    pa.write_text(json.dumps(a))
    pb.write_text(json.dumps(b))
    r = M.main(["--compare", str(pa), str(pb)])
    assert r["varied"] == "dt" and r["converged"]
    with pytest.raises(ValueError, match="differ in"):
        M.compare_runs(_run_doc(32, dt=0.25), _run_doc(64, dt=0.125))
    with pytest.raises(ValueError, match="factor 2"):  # P = 32 vs 33 can agree and both be far from P -> inf
        M.compare_runs(_run_doc(32), _run_doc(33))
    with pytest.raises(ValueError, match="not complete"):
        M.compare_runs(dict(a, status="partial"), b)


def test_step_resonance_instability_detected():
    """Reviewer case: 300 K, dt 0.25 fs, 108 THz O-H stretch. P = 256 resonates at k = 55 (spectral radius
    1.0000009), P <= 128 is stable; the check stops the unstable combination."""
    r, k = M.step_spectral_radius(256, 300.0, 0.25, 108.0)
    assert r > 1 + 1e-7 and k == 55
    for P in (32, 64, 128):
        assert M.step_spectral_radius(P, 300.0, 0.25, 108.0)[0] < 1
    assert M.check_step_stable(64, 300.0, 0.25, 110.0)["stable"]
    with pytest.raises(ValueError, match="unstable ring-polymer step"):
        M.check_step_stable(256, 300.0, 0.25, 108.0)
