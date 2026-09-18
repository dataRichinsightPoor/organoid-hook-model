"""Deterministic browser atlas, computed with the SAME Python ODE as the CLI."""
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict, replace
from pathlib import Path
import itertools
import json
import platform
import time
import numpy as np
import scipy
from organoid_hook import Parameters, simulate, summarize

ROOT=Path(__file__).resolve().parents[1]
TRAFFIC={
 "slow":dict(kint_free=.01,kint_primary=.02,kint_ternary=.02,krecycle=.02),
 "recycling":dict(kint_free=.08,kint_primary=.4,kint_ternary=.4,krecycle=.5),
 "retained":dict(kint_free=.04,kint_primary=.2,kint_ternary=.2,krecycle=.02),
}
DOSES=np.logspace(-2,3,13)
SECONDARY=[.1,3.,100.]
TIMES=[24.,48.,72.]
ORDERS=["simultaneous","primary_first","secondary_first","precomplexed"]
FIELDS=["permeability_fluorescence","committed_fraction","membrane_compromised_cumulative",
 "atp_proxy","caspase_proxy","ldh_proxy","surface_complex_copies","internalized_complex_copies",
 "payload_copies","delivered_payload_cumulative","core_committed","rim_committed"]

def one(task):
    order,copies,traffic,half,secondary=task
    p=replace(Parameters(),copies_per_cell=copies,receptor_half_life_h=half,**TRAFFIC[traffic])
    values=[]
    for a in DOSES:
        s=summarize(simulate(float(a),secondary,order=order,p=p,times=TIMES))
        values.append([[round(float(s[f][i]),8) for f in FIELDS] for i in range(len(TIMES))])
    return {"order":order,"copies":copies,"traffic":traffic,"half_life":half,"secondary":secondary,"values":values}

def main():
    tasks=list(itertools.product(ORDERS,[1e4,1e5,1e6],TRAFFIC,[4.,24.,96.],SECONDARY))
    rows=[]
    start=time.time()
    with ProcessPoolExecutor(max_workers=2) as pool:
        for i,row in enumerate(pool.map(one,tasks),1):
            rows.append(row)
            if i%20==0: print(f"{i}/{len(tasks)} curves, {time.time()-start:.1f}s",flush=True)
    out={"schema_version":1,"model_version":"0.1.0","synthetic":True,
         "calibration":"none","doses_nm":DOSES.tolist(),"secondary_nm":SECONDARY,"times_h":TIMES,
         "fields":FIELDS,"base_parameters":asdict(Parameters()),"traffic_presets":TRAFFIC,
         "curve_count":len(rows),"simulation_count":len(rows)*len(DOSES),
         "runtime_versions":{"python":platform.python_version(),"numpy":np.__version__,"scipy":scipy.__version__},
         "curves":rows}
    (ROOT/"viewer").mkdir(exist_ok=True)
    (ROOT/"viewer/atlas.json").write_text(json.dumps(out,separators=(",",":"))+"\n")
    print("Saved viewer/atlas.json",len(rows)*len(DOSES),"simulations",flush=True)

if __name__=="__main__":main()
