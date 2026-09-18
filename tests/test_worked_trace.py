"""The browser worked example must remain tied to the actual model."""
from pathlib import Path
import csv
import json
import numpy as np
import pytest
from organoid_hook import Parameters, simulate, summarize

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "viewer/trace/trace.json").read_text())

@pytest.mark.parametrize("case", ["sampled_peak", "primary_excess", "more_secondary"])
def test_trace_recomputes(case):
    rows = [row for row in DATA["rows"] if row["case"] == case]
    assert len(rows) == 6
    result = summarize(simulate(rows[0]["primary_nm"], rows[0]["secondary_nm"],
                               p=Parameters(**DATA["metadata"]["parameters"]),
                               times=[row["time_h"] for row in rows]))
    for field, values in result.items():
        assert np.allclose([row[field] for row in rows], values, rtol=3e-5, atol=1e-8), field

def test_trace_downloads_and_bookkeeping():
    with (ROOT / "viewer/trace/trace-summary.csv").open() as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 18
    for expected, row in zip(DATA["rows"], rows):
        assert row["case"] == expected["case"]
        for field in expected:
            if field != "case":
                assert np.isclose(float(row[field]), expected[field])
        assert np.isclose(expected["delivery_per_initial_cell_per_h"],
                          .2*np.log(2)/12*expected["internalized_complex_copies"])
        assert np.isclose(expected["payload_loss_per_initial_cell_per_h"],
                          np.log(2)/12*expected["payload_copies"])
        assert np.isclose(expected["committed_fraction"], expected["E_fraction"]+expected["D_fraction"])
    assert (ROOT/"examples/trace_example.py").read_bytes() == (ROOT/"viewer/trace/trace_example.py").read_bytes()

def test_trace_agrees_with_published_lab():
    lab = json.loads((ROOT / "viewer/lab.json").read_text())
    for row in DATA["rows"]:
        if row["time_h"] not in lab["times_h"]:
            continue
        curve = next(c for c in lab["curves"] if c["case"]=="reference" and
                     c["order"]=="simultaneous" and c["secondary"]==row["secondary_nm"])
        dose = int(np.argmin(np.abs(np.array(lab["doses_nm"])-row["primary_nm"])))
        time = lab["times_h"].index(row["time_h"])
        for field, value in zip(lab["fields"], curve["values"][dose][time]):
            assert np.isclose(row[field], value, rtol=3e-5, atol=1e-8), field
