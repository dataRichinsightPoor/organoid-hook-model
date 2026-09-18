"""Independent numerical checks for the editorial review; does not edit the model."""
import json
from dataclasses import replace
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares
from organoid_hook.equilibrium import ternary_equilibrium, peak_primary_nm
from organoid_hook.model import Parameters, geometry, simulate, summarize


def full_equilibrium(A, S, R, ka=1., ks=.3):
    """Solve all three mass balances, independently of the dilute formula."""
    def species(x):
        a, s = np.exp(x)
        r = R / (1 + a/ka + a*s/(ka*ks))
        b, c, t = a*r/ka, a*s/ks, a*s*r/(ka*ks)
        return a, s, r, b, c, t
    def residual(x):
        a, s, r, b, c, t = species(x)
        return [(a+b+c+t-A)/A, (s+c+t-S)/S]
    result = least_squares(
        residual, np.log([A*ks/(S+ks), S]),
        xtol=1e-13, ftol=1e-13, gtol=1e-13, max_nfev=1000)
    assert np.max(np.abs(result.fun)) < 1e-8
    a, s, r, b, c, t = species(result.x)
    return {"loaded_fraction": t/R, "free_primary_nm": a,
            "free_secondary_nm": s, "max_relative_balance_error": float(np.max(np.abs(result.fun)))}


p = Parameters()
v, cells, beta, r0, _ = geometry(p)
well_r = float(np.dot(v, r0)/(p.bath_ul*1e-6+v.sum()))
out = {
    "scope": "Synthetic checks, not assay validation; default dynamic model unchanged.",
    "default_geometry": {
        "initial_cells": float(cells.sum()),
        "local_surface_receptor_equivalent_nm": r0.tolist(),
        "initial_surface_receptor_equivalent_per_total_accessible_well_nm": well_r,
    },
    "tenfold_example": {},
    "finite_receptor_equilibria": [],
    "peak_checks": {},
    "dynamic_examples": [],
}
fractions = ternary_equilibrium(np.array([1.,10.]),1000.,.001)/.001
out["tenfold_example"] = {"loaded_fractions": fractions.tolist(),
                         "fold_change": float(fractions[1]/fractions[0]),
                         "peak_primary_nm": float(peak_primary_nm(1000.))}
for R in (.001, well_r, float(r0[0])):
    out["finite_receptor_equilibria"].append({
        "receptor_nm": R, "interpretation": "Uniform closed compartment, fixed surface receptor; not a dynamic organoid.",
        "primary_1": full_equilibrium(1., 1000., R),
        "primary_10": full_equilibrium(10., 1000., R),
    })
rng = np.random.default_rng(4921)
max_err = 0.
for _ in range(100):
    S, ka, ks = 10**rng.uniform(-3,3,3)
    peak = peak_primary_nm(S,ka,ks)
    doses = np.geomspace(peak/2,peak*2,10001)
    numerical = doses[np.argmax(ternary_equilibrium(doses,S,.001,ka,ks))]
    max_err = max(max_err, abs(numerical/peak-1))
out["peak_checks"] = {"random_parameter_sets":100, "max_relative_grid_peak_error":max_err}
for A in (1., 10.):
    res = simulate(A,1000.,p=p,times=np.array([24.,72.]))
    summary = summarize(res)
    out["dynamic_examples"].append({
        "primary_nm": A, "secondary_nm":1000., "note":"New review-only simulations, outside the committed atlas grid.",
        **{k: summary[k].tolist() for k in ("time_h","surface_complex_copies",
             "delivered_payload_cumulative","payload_copies","permeability_fluorescence")}
    })
base = summarize(simulate(8.254,3.,p=p))
scaled = summarize(simulate(8.254,3.,p=replace(
    p,release_efficiency=.4,payload_p50=2000.)))
out["payload_scale_nonidentifiability"] = {
    "change": "Double release efficiency and P50 together; all other parameters fixed.",
    "max_absolute_fluorescence_difference": float(np.max(np.abs(
        base["permeability_fluorescence"]-scaled["permeability_fluorescence"]))),
    "delivery_at_72h": [float(base["delivered_payload_cumulative"][-1]),
                       float(scaled["delivered_payload_cumulative"][-1])],
    "fluorescence_at_72h": [float(base["permeability_fluorescence"][-1]),
                           float(scaled["permeability_fluorescence"][-1])],
}
high_base = summarize(simulate(1000.,100.,p=p))
high_scaled = summarize(simulate(1000.,100.,p=replace(
    p,release_efficiency=.4,payload_p50=2000.)))
out["payload_scale_nonidentifiability"]["relative_delivery_reduction"] = [
    float(1-high_base["delivered_payload_cumulative"][-1] /
          base["delivered_payload_cumulative"][-1]),
    float(1-high_scaled["delivered_payload_cumulative"][-1] /
          scaled["delivered_payload_cumulative"][-1]),
]
assert np.isclose(*out["payload_scale_nonidentifiability"]["relative_delivery_reduction"],
                  atol=2e-6,rtol=0)
(Path(__file__).resolve().parents[1] / "results/review-checks.json").write_text(
    json.dumps(out,indent=2) + "\n")
print(json.dumps(out,indent=2))
