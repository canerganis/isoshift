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


def test_f01_banner_frozen_and_posthoc_collapsed():
    src = APP.read_text(encoding="utf-8")
    assert "oh_unfiltered_strong" in src and "unique_pair_majority" in src
    assert "123 of 130" not in src and "mo.ui.dropdown(options=_pops" not in src  # no population toggle
    assert "Post hoc sensitivity (not the result)" in src
    head = src.split("Post hoc sensitivity (not the result)")[0]
    assert "177" not in head  # post hoc figure only inside the expander
    cv = json.loads((APP.parents[1] / "results" / "F01_cv.json").read_text(encoding="utf-8"))["oh_unfiltered_strong"]
    pm = cv["unique_pair_majority"]
    assert (cv["right"], cv["n"], pm["right"], pm["tie"], pm["wrong"]) == (185, 212, 74, 0, 10)


def _repo_data():
    m = _load()
    return m, m.load_data(m.REPO)


def test_check_a_pair_default_is_diaspore_delta():
    m, d = _repo_data()
    opts = m.pair_options(d)
    assert m.DEFAULT_PAIR in opts.values() and any("AlHO2" in k for k in opts)
    rep = m.pair_report(d, m.DEFAULT_PAIR)
    t = rep["models"].set_index("model")
    assert list(t.index) == m.MODELS and rep["formula"] == "AlHO2"
    assert (t["regime"] == "strong").all()  # both members have mean O-H above 0.99 A
    assert (t["rule call"] == "+").all() and (t["model sign"] == "+").all() and (t["agree"] == "yes").all()
    assert abs(t.loc["mace", "ddF_iso 300 K (meV/atom)"] - 0.768484) < 1e-5
    assert abs(t.loc["mace", "ddF_iso 300 K (meV/H)"] - 3.073935) < 1e-5
    assert abs(t.loc["mace", "d(X-H) b minus a (mA)"] - 32.36) < 0.1
    assert abs(t.loc["mace", "stretch (meV/atom)"] - 2.1048) < 1e-3 and t.loc["mace", "bend/libration (meV/atom)"] < 0
    assert rep["a"]["struct_id"] == "mp-625152" and rep["b"]["struct_id"] == "mp-23807"
    assert rep["a"]["experimental"] == "True" and rep["b"]["experimental"] == "True"
    assert (APP.parents[1] / "docs" / "findings" / "CARD-AlOOH.md").exists()


def test_check_a_pair_synthetic_regime_and_missing(tmp_path):
    m = _load()
    _build(tmp_path)
    pd.DataFrame([dict(pair_id="A__B", model="mace", struct_a="A", struct_b="B", flags="x",
                       ddF_iso_300K_meV_atom=-1.0, ddF_iso_300K_meV_H=-2.0)]
                 ).to_csv(tmp_path / "results" / "screen_pairs_refined.csv", index=False)
    pd.DataFrame([dict(model="mace", struct_id=s, XH_mean_A=x, covalent_XH=True) for s, x in (("A", 0.97), ("B", 0.985))]
                 ).to_csv(tmp_path / "results" / "decompose_structures.csv", index=False)
    d = m.load_data(tmp_path)
    r = m.pair_report(d, "A__B")["models"].iloc[0]
    assert r["regime"] == "weak" and r["rule call"] == "+" and r["model sign"] == "-" and r["agree"] == "no"
    assert m.pair_report(d, "nope") is None


def test_how_we_know_brucite_trace():
    m, d = _repo_data()
    tr = m.brucite_trace(d)
    assert tr["n_log"] == len((APP.parents[1] / "logs" / "bond_queries.jsonl").read_text(encoding="utf-8").splitlines())
    assert tr["n_sweep"] + tr["n_agent"] + tr["n_other"] == tr["n_log"]
    assert len(tr["agent_rows"]) + len(tr["sweep_rows"]) >= 5 and len(tr["sweep_rows"]) >= 1
    assert tr["lit"].iloc[0]["doi"] == "10.2138/am.2013.4202" and "0.31% larger volume" in tr["lit"].iloc[0]["quote"]
    assert len(tr["vie"]) == 16 and (tr["vie"].VIE_pct > 0).all()
    assert len(tr["gate"]) == 2 and "Tier B under P12 passes" in tr["gate"][0]
    audit = (APP.parents[1] / "docs" / "story" / "agent_extraction_audit.md").read_text(encoding="utf-8")
    a = m.AUDIT
    assert f"of {a['sweep_items']} sweep items, {a['ok_single_pass']} returned \"ok\", but only {a['survived']}" in audit
    assert len(m.BRUCITE_STEPS) == 5
