import numpy as np
import pytest
from ase import Atoms
from ase.build import bulk
from ase.calculators.lj import LennardJones

from isoshift import cache, compare, phonons as P


class CountingLJ(LennardJones):
    n = 0

    def calculate(self, *a, **k):
        CountingLJ.n += 1
        super().calculate(*a, **k)


def fcc_ar():
    a = bulk("Ar", "fcc", a=5.26, cubic=True)
    return a


def toy_rocksalt():
    a = bulk("NaCl", "rocksalt", a=4.0, cubic=True)
    a.set_chemical_symbols(["H", "X" if False else "He", "H", "He", "H", "He", "H", "He"])
    return a


def test_supercell_min_length():
    a = bulk("Cu", "fcc", a=3.6, cubic=True)
    sc = np.diag(P.supercell_for_min_length(a, 10.0))
    assert all(sc * 3.6 >= 10.0) and all(sc * 3.6 < 10.0 + 3.6)


def test_make_masses():
    a = Atoms("LiH", positions=[[0, 0, 0], [2, 0, 0]], cell=[5, 5, 5])
    m = P.make_masses(a, {"H": "D", "Li": "6Li"})
    assert m[0] == pytest.approx(6.0151228) and m[1] == pytest.approx(2.01410178)


def test_monatomic_freq_scales_inverse_sqrt_mass_without_recompute():
    a = fcc_ar()
    calc = CountingLJ(sigma=3.4, epsilon=0.0104, rc=8.0, smooth=False)
    ph, meta = P.compute_force_constants(a, calc, supercell=np.diag([2, 2, 2]))
    n_before = CountingLJ.n
    m0 = P.mesh_frequencies(ph, np.full(len(a), 40.0), mesh=(6, 6, 6))
    m4 = P.mesh_frequencies(ph, np.full(len(a), 160.0), mesh=(6, 6, 6))
    assert CountingLJ.n == n_before  # no force recomputation
    mask = m0.freqs > 0.2
    np.testing.assert_allclose(m4.freqs[mask] / m0.freqs[mask], 0.5, rtol=1e-6)
    assert m4.zpe() == pytest.approx(0.5 * m0.zpe(), rel=1e-6)


def test_light_atom_optical_scaling_with_heavy_partner():
    """Rocksalt-like LJ crystal: with an effectively infinite heavy partner the optical
    frequencies scale as 1/sqrt(m_light)."""
    a = bulk("NaCl", "rocksalt", a=4.6, cubic=True)
    calc = LennardJones(sigma=3.0, epsilon=0.01, rc=7.0, smooth=False)
    ph, _ = P.compute_force_constants(a, calc, supercell=np.diag([2, 2, 2]))
    idx_light = [i for i, s in enumerate(a.get_chemical_symbols()) if s == "Na"]
    def masses(ml):
        m = np.full(len(a), 1e9)
        m[idx_light] = ml
        return m
    f1 = P.mesh_frequencies(ph, masses(1.0), mesh=(4, 4, 4)).freqs
    f4 = P.mesh_frequencies(ph, masses(4.0), mesh=(4, 4, 4)).freqs
    top1, top4 = f1.max(), f4.max()
    assert top4 / top1 == pytest.approx(0.5, rel=1e-4)


def test_free_energy_limits():
    f = np.array([[5.0, 10.0]])
    mf = P.MeshFreqs(f, np.array([1.0]), 1)
    zpe = 0.5 * P.H_EV_THZ * 15.0
    assert mf.zpe() == pytest.approx(zpe)
    F = mf.helmholtz_free_energy([0.0, 1e-3, 3000.0])
    assert F[0] == pytest.approx(zpe) and F[1] == pytest.approx(zpe, rel=1e-6)
    assert F[2] < 0  # classical limit: free energy turns negative


def test_imaginary_flag():
    mf = P.MeshFreqs(np.array([[-1.0, 2.0], [0.0, 3.0]]), np.array([1.0, 3.0]), 1)
    assert mf.has_imaginary() and mf.n_imaginary == 1 and mf.min_freq == -1.0


def test_crossing_math():
    T = np.linspace(0, 100, 101)
    dG = T - 40.0
    assert compare.crossing_temperatures(T, dG) == pytest.approx([40.0])
    assert compare.crossing_temperatures(T, T + 1) == []
    r = compare.isotope_shift(T, T * 0 + 0.0, T * 0 + 40 - T, T * 0, T * 0 + 45 - T)
    # dG_H = T-40, dG_D = T-45 => crossings 40 and 45, shift +5
    assert r["T_cross_H"] == pytest.approx(40.0) and r["dT_iso"] == pytest.approx(5.0)
    assert r["ddG_iso"][0] == pytest.approx(-5.0)


def test_ddF_and_ensemble():
    T = np.array([0, 300, 600.0])
    v = compare.ddF_iso_at(T, 300, [0, 1, 2], [0, 3, 6], [0, 1, 2], [0, 2, 4])
    assert v == pytest.approx(1.0)
    e = compare.ensemble({"a": 1.0, "b": 2.0, "c": 3.0})
    assert e["mean"] == 2.0 and e["all_same_sign"] and e["sign_agreement"] == 1.0
    e = compare.ensemble({"a": 1.0, "b": -2.0, "c": 3.0})
    assert e["sign_agreement"] == pytest.approx(2 / 3)
    assert compare.dT_from_ddF(0.002, 0.0005) == pytest.approx(4.0)


def test_cache_roundtrip(tmp_path):
    a = fcc_ar()
    calc = LennardJones(sigma=3.4, epsilon=0.0104, rc=8.0, smooth=False)
    sc = np.diag([2, 2, 2])
    ph, meta, hit = P.get_force_constants(a, calc, "lj-test", supercell=sc, cache_root=tmp_path)
    assert not hit
    ph2, meta2, hit2 = P.get_force_constants(a, calc, "lj-test", supercell=sc, cache_root=tmp_path)
    assert hit2 and meta2["supercell"] == [2, 2, 2]
    m = np.full(len(a), 40.0)
    np.testing.assert_allclose(P.mesh_frequencies(ph, m, (4, 4, 4)).freqs,
                               P.mesh_frequencies(ph2, m, (4, 4, 4)).freqs, atol=1e-6)
    # other calc id or perturbed structure give different keys
    assert cache.cache_key(a, "lj-test", sc) != cache.cache_key(a, "other", sc)
    b = a.copy(); b.rattle(0.05, seed=1)
    assert cache.structure_hash(a) != cache.structure_hash(b)
    assert cache.structure_hash(a) == cache.structure_hash(a.copy())
