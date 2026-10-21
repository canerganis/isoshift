import importlib.util
import json
from pathlib import Path

import numpy as np
import pandas as pd

APP = Path(__file__).resolve().parents[1] / "app" / "isoshift_app.py"


def _load():
    spec = importlib.util.spec_from_file_location("isoshift_app", APP)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _build(root):
    (root / "results" / "validation").mkdir(parents=True)
    (root / "data" / "isoshift").mkdir(parents=True)
    T = np.arange(0, 1001, 5, dtype=float)
    # a flat; b rises 0.01 meV/atom/K; D(b) is 1 meV higher. dE = -2.
    fa_h = np.zeros_like(T)
    fb_h = 0.01 * T
    curves = {"A": (fa_h, fa_h), "B": (fb_h, fb_h + 1.0)}
    pd.DataFrame([dict(struct_id=s, model="mace", status="ok",
                       F_H_meV_atom_json=json.dumps(h.tolist()),
                       F_D_meV_atom_json=json.dumps(d.tolist()))
                  for s, (h, d) in curves.items()]).to_csv(root / "results" / "screen_structures.csv", index=False)
    pd.DataFrame([dict(pair_id="A__B", struct_a="A", struct_b="B", model="mace",
                       dE_static_meV_atom=-2.0, ddF_iso_300K_meV_atom=1.0, flags="x")]
                 ).to_csv(root / "results" / "screen_pairs.csv", index=False)
    pd.DataFrame([dict(pair_id="A__B", formula="XH", struct_a="A", struct_b="B")]
                 ).to_csv(root / "data" / "isoshift" / "pairs.csv", index=False)
    pd.DataFrame([dict(struct_id="A", spg=1), dict(struct_id="B", spg=2)]
                 ).to_csv(root / "data" / "isoshift" / "structures.csv", index=False)
    pd.DataFrame([dict(case="c", model="mace", T_K=0, VIE_pct=0.3, exp_VIE_pct=None)]
                 ).to_csv(root / "results" / "validation" / "volume_isotope.csv", index=False)


def test_loader_and_crossing(tmp_path):
    m = _load()
    _build(tmp_path)
    d = m.load_data(tmp_path)
    assert len(d["pairs"]) == 1 and len(d["validation"]) == 1
    fa = m.structure_curves(d, "A", "mace")
    fb = m.structure_curves(d, "B", "mace")
    gh, gd = m.dG_curves(-2.0, fa, fb)
    (th, dirn), = m.crossings(m.TEMPS, gh)
    assert abs(th - 200.0) < 1e-9 and dirn == "-+"
    (td, _), = m.crossings(m.TEMPS, gd)
    assert abs(td - 100.0) < 1e-9
    assert np.allclose(m.ddF_curve(fa, fb), 1.0)
    tab = m.candidate_table(d["pairs"], d["meta_pairs"], d["meta_structs"])
    assert tab.iloc[0]["sign_agree"] == "1/1" and tab.iloc[0]["formula"] == "XH"
    assert "XH" in m.pair_label(d["meta_pairs"], d["meta_structs"], "A__B")


def test_data_root_prefers_demo(tmp_path):
    m = _load()
    (tmp_path / "demo_data").mkdir()
    assert m.data_root(tmp_path, Path("/nonexistent")) == tmp_path / "demo_data"
