import csv
import json

import pytest

from src.isoshift_event import benchmark as bm


def test_dft_dzpe_positive_and_equal_masses_zero():
    if not (bm.ROOT / "data/isoshift/dft_phonons/mdr_phonondb/index.json").exists():
        pytest.skip("prefetched MDR DFT phonon data is gitignored and not in a fresh clone")
    entry = bm.entries(limit=1)[0]
    q, ctx = bm.dft_record(entry)
    assert q["dzpe_meV"] > 0
    assert q["dF300_meV"] > 0
    assert q["zpe_H_meV"] > q["zpe_D_meV"]
    assert q["stretch_cm1"] > 500
    fc = bm.full_force_constants(ctx["ph"])
    z = bm.isotope_quantities(ctx["atoms"], ctx["supercell"], fc, ctx["mesh"], sub_h="H")
    assert z["dzpe_meV"] == 0.0
    assert z["dF300_meV"] == 0.0


def _rec(entry, model, setting, dft, mlip, imag=False):
    base = {"n_H": 1, "zpe_H_meV": 0, "zpe_D_meV": 0, "min_freq_THz": 0.0, "has_imaginary": False}
    d = dict(base, dzpe_meV=dft[0], dF300_meV=dft[1], stretch_cm1=dft[2])
    m = dict(base, dzpe_meV=mlip[0], dF300_meV=mlip[1], stretch_cm1=mlip[2], has_imaginary=imag)
    return {"entry": entry, "model": model, "setting": setting, "formula": "X", "n_atoms_cell": 2,
            "supercell": [2, 2, 2], "mesh": [4, 4, 4], "dft": d, "mlip": m}


def test_collect_mae(tmp_path):
    raw, out = tmp_path / "raw", tmp_path / "out"
    raw.mkdir()
    recs = [_rec("mp-1", "mace", "a_dftstruct", (100, 10, 3000), (110, 12, 2950)),
            _rec("mp-2", "mace", "a_dftstruct", (100, 10, 3000), (95, 9, 3100), imag=True)]
    for i, r in enumerate(recs):
        (raw / f"{i}.json").write_text(json.dumps(r))
    (raw / "mp-3__mace__error.json").write_text(json.dumps({"error": "x"}))
    bm.collect(raw, out)
    rows = list(csv.DictReader(open(out / "isotope_benchmark.csv")))
    assert len(rows) == 2
    s = list(csv.DictReader(open(out / "summary.csv")))
    assert len(s) == 1
    s = s[0]
    assert s["n"] == "2" and s["n_imag_mlip"] == "1"
    assert float(s["dzpe_MAE_meV"]) == pytest.approx(7.5)
    assert float(s["dzpe_bias_meV"]) == pytest.approx(2.5)
    assert float(s["dF300_MAE_meV"]) == pytest.approx(1.5)
    assert float(s["stretch_MAE_cm1"]) == pytest.approx(75.0)
    assert float(s["stretch_bias_cm1"]) == pytest.approx(25.0)
