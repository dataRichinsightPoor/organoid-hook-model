"""Recompute the v0.1.0 reference example. No experimental data are used.

Install:
pip install 'organoid-hook-model @ git+https://github.com/dataRichinsightPoor/organoid-hook-model.git@v0.1.0'
Run: python trace_example.py
"""
from dataclasses import asdict
from pathlib import Path
import csv
import json
import sys
import numpy as np
from organoid_hook import Parameters, simulate, summarize
from organoid_hook.model import geometry, N, I, ligand_inventory

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parent
ROOT.mkdir(parents=True, exist_ok=True)
p = Parameters()
times = np.array([0., 6., 12., 24., 48., 72.])
peak_dose = float(np.logspace(-2, 3, 13)[7])
assert np.isclose(peak_dose, 8.25404185268019)
cases = [
    ("sampled_peak", peak_dose, 3.),
    ("primary_excess", 1000., 3.),
    ("more_secondary", 1000., 100.),
]
volumes, cells, beta, r0, conductance = geometry(p)
weights = cells / cells.sum()
optical = np.linspace(p.optical_core_weight, 1, p.shells)
kd = np.log(2) / p.receptor_half_life_h
kp = np.log(2) / p.payload_half_life_h
kr = np.log(2) / p.protein_recovery_half_life_h
rows, shell_rows, checks = [], [], []
for name, primary, secondary in cases:
    result = simulate(primary, secondary, duration_h=72, order="simultaneous", p=p, times=times)
    summary = summarize(result)
    z = result["states"][3:].reshape(p.shells, N, -1)
    inv_a, inv_s = ligand_inventory(result)
    assert np.allclose(inv_a, inv_a[0], rtol=1e-7, atol=1e-12)
    assert np.allclose(inv_s, inv_s[0], rtol=1e-7, atol=1e-12)
    assert np.allclose(sum(z[:, I[k]] for k in ["L", "E", "D", "X"]), 1, atol=1e-8)
    assert np.all(np.diff(summary["permeability_fluorescence"]) >= -1e-8)
    for ti, time in enumerate(times):
        row = dict(case=name, primary_nm=primary, secondary_nm=secondary, time_h=time)
        row.update({key: float(value[ti]) for key, value in summary.items() if key != "time_h"})
        for state in ["R", "B", "T", "U", "V", "W"]:
            row[f"{state}_copies_per_initial_cell"] = float(np.dot(weights, z[:, I[state], ti] / beta))
        row["surface_receptors_per_initial_cell"] = sum(row[f"{k}_copies_per_initial_cell"] for k in ["R", "B", "T"])
        row["delivery_per_initial_cell_per_h"] = kd * row["W_copies_per_initial_cell"] * p.release_efficiency * p.payload_yield
        row["payload_loss_per_initial_cell_per_h"] = kp * row["payload_copies"]
        row["E_fraction"] = float(np.dot(weights, z[:, I["E"], ti]))
        row["D_fraction"] = float(np.dot(weights, z[:, I["D"], ti]))
        rows.append(row)
        for j in range(p.shells):
            P, Q, L, E, D = [float(z[j, I[k], ti]) for k in ["P", "Q", "L", "E", "D"]]
            damage_in = p.damage_rate_h * P / (p.payload_p50 + P) * (1-Q)
            repair = kr * Q
            hazard = p.death_rate_h * Q**p.hill / (p.damage_half**p.hill + Q**p.hill)
            shell_row = dict(case=name, primary_nm=primary, secondary_nm=secondary, time_h=time, shell=j+1)
            shell_row.update({state: float(z[j, I[state], ti]) for state in I})
            shell_row.update(beta_nm_per_copy=float(beta[j]), initial_cell_weight=float(weights[j]),
                             optical_weight=float(optical[j]), damage_in_per_h=damage_in,
                             repair_per_h=repair, hazard_per_h=hazard,
                             commitment_flux_per_h=hazard*L, permeabilization_flux_per_h=E/p.membrane_delay_h,
                             delivery_per_initial_cell_per_h=kd*z[j,I["W"],ti]/beta[j]*p.release_efficiency*p.payload_yield)
            shell_rows.append(shell_row)
    checks.append({"case": name, "primary_relative_inventory_drift": float(np.max(np.abs(inv_a/inv_a[0]-1))),
                   "secondary_relative_inventory_drift": float(np.max(np.abs(inv_s/inv_s[0]-1)))})
for filename, data in [("trace-summary.csv", rows), ("trace-shells.csv", shell_rows)]:
    with (ROOT / filename).open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(data[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(data)
metadata = {
    "synthetic": True, "calibrated": False, "model_version": "0.1.0",
    "model_url": "https://github.com/dataRichinsightPoor/organoid-hook-model/tree/v0.1.0",
    "parameters": asdict(p), "cases": cases, "times_h": times.tolist(),
    "geometry": {"cells": cells.tolist(), "total_cells": float(cells.sum()),
                 "extracellular_l": volumes.tolist(), "beta_nm_per_copy": beta.tolist(),
                 "initial_surface_receptor_nm": r0.tolist(), "cell_weights": weights.tolist(),
                 "optical_weights": optical.tolist(),
                 "surface_receptor_inventory_well_equivalent_nm": float(np.dot(r0,volumes)/(p.bath_ul*1e-6+volumes.sum()))},
    "derived": {"kdeg_per_h": kd, "payload_loss_per_h": kp, "repair_per_h": kr,
                "initial_endosomal_copies_per_cell": p.kint_free*p.copies_per_cell/(p.krecycle+kd),
                "synthesis_copies_per_cell_per_h": kd*p.kint_free*p.copies_per_cell/(p.krecycle+kd)},
    "checks": checks
}
(ROOT / "trace-parameters.json").write_text(json.dumps(metadata, indent=2)+"\n")
(ROOT / "trace.json").write_text(json.dumps({"metadata": metadata, "rows": rows}, separators=(",", ":"))+"\n")
print(json.dumps(metadata, indent=2))
print("SUMMARY")
for row in rows:
    print(json.dumps(row))
print("RIM AT 24 HOURS")
print(json.dumps(next(r for r in shell_rows if r["case"]=="sampled_peak" and r["time_h"]==24 and r["shell"]==3),indent=2))
print("SHELLS AT 72 HOURS")
for row in shell_rows:
    if row["case"]=="sampled_peak" and row["time_h"]==72:
        print(json.dumps(row))
