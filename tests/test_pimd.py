"""P12 PIMD module (src/isoshift_event/pimd.py): CPU only, harmonic backend, seeded."""
import json

import numpy as np
import pytest

from isoshift import cache, phonons as Ph
from src.isoshift_event import pimd as M

T = 300.0
M_O = 15.9949146


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
    """Relative coordinate: three oscillators with the reduced mass; plus the free 3D centre of mass."""
    mu = M_O * m_h / (M_O + m_h)
    nu = np.sqrt(ks / (mu * M.AMU_EV)) / (2 * np.pi * 1e-3)
    return M._osc_free_energy(nu, T, P).sum() + M.com_free_energy(M_O + m_h, T)


def test_oh_diatomic_within_0p2_meV_of_analytic():
    """P12 section 2: isolated O-H diatomic (finite O mass, M00 reduced mass), H to D within 0.2 meV of the
    analytic quantum value, at the production time step 0.25 fs. P = 128 keeps the bead error near 0.1 meV."""
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
    assert err < 0.15


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


def test_samecell_reference_matches_supercell_diagonalization():
    ph = _toy_phonopy()
    s = ph.supercell
    fc = ph.force_constants
    n = len(s.positions)
    out = {}
    for iso, mh in (("H", M.M_H), ("D", M.M_D)):
        m = np.where(np.array(list(s.symbols)) == "H", mh, M_O)
        phi = fc.transpose(0, 2, 1, 3).reshape(3 * n, 3 * n)
        isq = 1 / np.sqrt(np.repeat(m, 3) * M.AMU_EV)
        ev = np.linalg.eigvalsh(isq[:, None] * phi * isq[None, :])
        nu = np.sqrt(np.clip(ev, 0, None)) / (2 * np.pi * 1e-3)
        nu = np.sort(nu)[3:]
        out[iso] = M._osc_free_energy(nu, T).sum() + M.com_free_energy(m.sum(), T)
    ref = M.harmonic_samecell(ph, [2, 2, 2], T, P=16)
    assert ref["n_dropped_H"] == 3 and not ref["has_imaginary"]
    assert ref["dF_eV"] == pytest.approx(out["D"] - out["H"], rel=1e-5)  # phonopy vs CODATA unit constants
    assert ref["dF_P_eV"] > ref["dF_eV"]  # finite P under-counts the zero-point term


def test_periodic_toy_pimd_matches_samecell_harmonic():
    ph = _toy_phonopy()
    s = ph.supercell
    x0 = s.positions
    mask = np.array(list(s.symbols)) == "H"
    base = np.where(mask, M.M_H, M_O)
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

def _fake_tree(tmp_path, n_copies=1, sc=(2, 2, 2), struct="toy-1"):
    ph = _toy_phonopy()
    meta = {"supercell": list(sc), "natoms_cell": 2, "natoms_supercell": 16, "energy_eV": -10.123456,
            "volume_A3": 64.0}
    root = tmp_path / "cache"
    for i in range(n_copies):
        cache.save_fc(ph, f"h{i:019d}__{M.CALC_ID}__sc2x2x2__d0.01__sym", meta, root=root)
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
              "dF_PIMD_err_meV_H", "dF_harm_samecell_meV_H", "delta_anh_meV_H", "harmonic_samecell"):
        assert k in d2, k
    for p in d2["points"]:
        for k in ("g", "mass_H_u", "weight", "K_H_meV", "K_H_err_meV", "steps_used", "block_curve_meV", "wall_s"):
            assert k in p, k
    assert d2["supercell"] == [2, 2, 2] and d2["n_H"] == 8 and d2["dF_PIMD_meV_H"] < 0
    assert d2["delta_anh_meV_H"] == pytest.approx(d2["dF_PIMD_meV_H"] - d2["dF_harm_samecell_meV_H"])
    with pytest.raises(ValueError, match="different arguments"):
        M.main([a if a != "300" else "301" for a in args])
