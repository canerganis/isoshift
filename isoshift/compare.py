"""Compare polymorph free energies for H and D variants: crossings, isotope shifts, ensembles."""
from __future__ import annotations

import numpy as np


def delta_G(T, G_a, G_b):
    """Delta G(T) = G_a - G_b on a common T grid (arrays interpolated onto the shorter grid)."""
    T = np.asarray(T, float)
    return np.asarray(G_a, float) - np.asarray(G_b, float)


def crossing_temperatures(T, dG) -> list[float]:
    """All temperatures where dG(T) changes sign (linear interpolation). Exact zeros count."""
    T = np.asarray(T, float)
    dG = np.asarray(dG, float)
    out = []
    for i in range(len(T) - 1):
        a, b = dG[i], dG[i + 1]
        if a == 0.0:
            out.append(float(T[i]))
        elif a * b < 0:
            out.append(float(T[i] - a * (T[i + 1] - T[i]) / (b - a)))
    if len(T) and dG[-1] == 0.0 and (not out or out[-1] != float(T[-1])):
        out.append(float(T[-1]))
    return out


def isotope_shift(T, G_a_H, G_b_H, G_a_D, G_b_D, ref_T: float | None = None) -> dict:
    """Polymorph a vs b. dG_H, dG_D, ddG_iso(T) = dG_D - dG_H, crossings and T shift.

    dT_iso = T_cross(D) - T_cross(H) using the crossing in each curve nearest to ref_T
    (or the first crossing); D crossing is the one nearest to the H crossing. None when either variant has no crossing in range.
    """
    T = np.asarray(T, float)
    dG_H = delta_G(T, G_a_H, G_b_H)
    dG_D = delta_G(T, G_a_D, G_b_D)
    ddG = dG_D - dG_H
    cH = crossing_temperatures(T, dG_H)
    cD = crossing_temperatures(T, dG_D)

    def pick(c):
        if not c:
            return None
        return c[0] if ref_T is None else min(c, key=lambda x: abs(x - ref_T))

    tH = pick(cH)
    tD = min(cD, key=lambda x: abs(x - tH)) if (tH is not None and cD) else None
    dT = None if (tH is None or tD is None) else tD - tH
    return {"T": T, "dG_H": dG_H, "dG_D": dG_D, "ddG_iso": ddG, "cross_H": cH, "cross_D": cD,
            "T_cross_H": tH, "T_cross_D": tD, "dT_iso": dT}


def ddF_iso_at(T_grid, T, F_a_H, F_a_D, F_b_H, F_b_D) -> float:
    """Delta Delta F_iso at fixed T: (F_a(D)-F_a(H)) - (F_b(D)-F_b(H)). Inputs are curves on T_grid."""
    f = lambda y: float(np.interp(T, T_grid, y))
    return (f(F_a_D) - f(F_a_H)) - (f(F_b_D) - f(F_b_H))


def dT_from_ddF(ddF: float, dS: float) -> float:
    """First order estimate dT_iso ~ ddF / dS (dS = S_a - S_b, same energy unit per K)."""
    return ddF / dS


def ensemble(values: dict) -> dict:
    """values: calculator name -> scalar (e.g. ddF in meV/atom). Mean, std (sample), min, max,
    and sign agreement (fraction of members sharing the majority sign, 1.0 = unanimous)."""
    v = np.array([x for x in values.values() if x is not None and np.isfinite(x)], float)
    if len(v) == 0:
        return {"n": 0, "mean": None, "std": None, "sign_agreement": None, "all_same_sign": None,
                "exceeds_spread": None}
    pos = int((v > 0).sum())
    neg = int((v < 0).sum())
    agree = max(pos, neg) / len(v)
    std = float(v.std(ddof=1)) if len(v) > 1 else 0.0
    mean = float(v.mean())
    return {"n": len(v), "mean": mean, "std": std, "min": float(v.min()), "max": float(v.max()),
            "sign_agreement": agree, "all_same_sign": agree == 1.0, "exceeds_spread": abs(mean) > std}
