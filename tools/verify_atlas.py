"""Validate atlas dimensions and recompute representative rows."""
import json
from dataclasses import replace
from pathlib import Path
import numpy as np
from organoid_hook import Parameters,simulate,summarize

root=Path(__file__).resolve().parents[1]
d=json.loads((root/"viewer/atlas.json").read_text())
assert d["synthetic"] and d["calibration"]=="none"
assert len(d["curves"])==d["curve_count"]==324
assert d["simulation_count"]==4212
for row in d["curves"]:
    arr=np.array(row["values"])
    assert arr.shape==(13,3,len(d["fields"]))
    assert np.all(np.isfinite(arr)) and arr.min()>-1e-5
for idx in (0,161,323):
    row=d["curves"][idx]
    p=replace(Parameters(**d["base_parameters"]),copies_per_cell=row["copies"],
              receptor_half_life_h=row["half_life"],**d["traffic_presets"][row["traffic"]])
    for dose_idx in (2,9,12):
        s=summarize(simulate(d["doses_nm"][dose_idx],row["secondary"],order=row["order"],p=p,times=d["times_h"]))
        expected=np.array([[s[f][i] for f in d["fields"]] for i in range(3)])
        assert np.allclose(expected,row["values"][dose_idx],rtol=1e-4,atol=2e-5)
print("Atlas structure and nine independent reference recomputations passed.")
lab=json.loads((root/"viewer/lab.json").read_text())
assert len(lab["curves"])==84 and lab["simulation_count"]==1092
for row in lab["curves"]:
    arr=np.asarray(row["values"])
    assert arr.shape==(13,3,len(lab["fields"])) and np.all(np.isfinite(arr)) and arr.min()>-1e-5
for idx in (0,43,83):
    row=lab["curves"][idx]
    p=replace(Parameters(**lab["base_parameters"]),**lab["cases"][row["case"]]["overrides"])
    s=summarize(simulate(lab["doses_nm"][7],row["secondary"],order=row["order"],p=p,times=lab["times_h"]))
    expected=np.array([[s[f][i] for f in lab["fields"]] for i in range(3)])
    assert np.allclose(expected,row["values"][7],rtol=1e-4,atol=2e-5)
print("Mechanism lab structure and three reference recomputations passed.")
