"""Generate mechanistic counterexamples and publication figures."""
from dataclasses import asdict, replace
from pathlib import Path
import csv
import json
import numpy as np
from organoid_hook import Parameters,simulate,summarize,hook_metrics
from build_atlas import DOSES,SECONDARY,TIMES,ORDERS,FIELDS

ROOT=Path(__file__).resolve().parents[1]
CASES={
 "reference":("Reference",{}),
 "transport":("Large / slow transport",{"radius_um":250,"diffusion_um2_s":.1}),
 "core_low":("Target-poor core",{"core_copy_ratio":.03}),
 "fast_repair":("Fast protein recovery",{"protein_recovery_half_life_h":2}),
 "slow_repair":("Slow protein recovery",{"protein_recovery_half_life_h":96}),
 "reporter_loss":("Reporter persistence stress test",{"reporter_loss_h":.08}),
 "poor_release":("Poor productive release",{"release_efficiency":.001}),
}

def main():
    rows=[]; metrics=[]
    for key,(name,changes) in CASES.items():
        p=replace(Parameters(),**changes)
        for order in ORDERS:
            for s in SECONDARY:
                values=[]
                for a in DOSES:
                    summary=summarize(simulate(float(a),s,order=order,p=p,times=TIMES))
                    values.append([[round(float(summary[f][i]),8) for f in FIELDS] for i in range(len(TIMES))])
                rows.append({"case":key,"order":order,"secondary":s,"values":values})
                if order=="simultaneous":
                    y=np.array(values)[:,-1,FIELDS.index("permeability_fluorescence")]
                    death=np.array(values)[:,-1,FIELDS.index("committed_fraction")]
                    metrics.append({"case":key,"secondary_nm":s,**hook_metrics(DOSES,y),"committed_at_top":float(death[-1])})
        print("Built",key,flush=True)
    lab={"schema_version":1,"synthetic":True,"model_version":"0.1.0","calibration":"none",
         "doses_nm":DOSES.tolist(),"secondary_nm":SECONDARY,"times_h":TIMES,"fields":FIELDS,
         "base_parameters":asdict(Parameters()),"cases":{k:{"name":n,"overrides":c} for k,(n,c) in CASES.items()},
         "curves":rows,"simulation_count":len(rows)*len(DOSES)}
    (ROOT/"viewer/lab.json").write_text(json.dumps(lab,separators=(",",":"))+"\n")
    (ROOT/"results").mkdir(exist_ok=True)
    (ROOT/"results/lab_metrics.json").write_text(json.dumps(metrics,indent=2)+"\n")
    with (ROOT/"results/mechanism_lab.csv").open("w",newline="") as f:
        w=csv.writer(f); w.writerow(["case","order","secondary_nm","primary_nm","time_h"]+FIELDS)
        for row in rows:
            for a,values in zip(DOSES,row["values"]):
                for t,v in zip(TIMES,values):w.writerow([row["case"],row["order"],row["secondary"],a,t]+v)
    # Ablation, spatial resolution, delay and exposure-clock sensitivity.
    sensitivity={"ablation":{},"mesh":[],"delay":[]}
    for flag in (True,False):
        p=replace(Parameters(),solution_binding=flag)
        values=[float(summarize(simulate(float(a),1,p=p,times=[72]))["permeability_fluorescence"][0]) for a in DOSES]
        sensitivity["ablation"][str(flag)]={"doses_nm":DOSES.tolist(),"response":values,"metrics":hook_metrics(DOSES,values)}
    for shells in (3,6,12):
        for case in ("reference","transport"):
            p=replace(Parameters(),shells=shells,**CASES[case][1])
            s=summarize(simulate(10,3,p=p,times=[72]))
            sensitivity["mesh"].append({"shells":shells,"case":case,"fluorescence":float(s["permeability_fluorescence"][0]),"committed":float(s["committed_fraction"][0])})
    for order in ("primary_first","secondary_first"):
        for delay in (0,2,6,24):
            for clock in ("first_addition","second_addition"):
                end=72 if clock=="first_addition" else 72+delay
                s=summarize(simulate(30,3,order=order,delay_h=delay,duration_h=end,times=[end]))
                sensitivity["delay"].append({"order":order,"delay_h":delay,"clock":clock,
                    "endpoint_h":end,"fluorescence":float(s["permeability_fluorescence"][0]),
                    "committed":float(s["committed_fraction"][0])})
    (ROOT/"results/sensitivity.json").write_text(json.dumps(sensitivity,indent=2)+"\n")
    print("Saved lab, CSV, metrics and sensitivity results.")
    figures(lab,sensitivity)

def figures(lab,sensitivity):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.family":"DejaVu Sans","font.size":11,"axes.spines.top":False,
                        "axes.spines.right":False,"svg.hashsalt":"organoid-hook-v0.1.0"})
    fig,axs=plt.subplots(2,3,figsize=(15,9),layout="constrained")
    colors=["#737F8A","#006D77","#B05B36"]
    labels=["0.1 nM secondary","3 nM secondary","100 nM secondary"]
    styles=[":","--","-"]
    cases=["reference","poor_release","reporter_loss","transport","fast_repair","slow_repair"]
    titles=["Assembly: more secondary shifts the hook","A delivery bottleneck is not a hook diagnosis",
            "Reporter persistence changes the endpoint","Transport stress test (not mesh-converged)",
            "Fast recovery can limit the response","Slow recovery accumulates more damage"]
    for ax,case,title in zip(axs.flat,cases,titles):
        for s,c,label,style in zip(SECONDARY,colors,labels,styles):
            row=next(r for r in lab["curves"] if r["case"]==case and r["order"]=="simultaneous" and r["secondary"]==s)
            vals=np.array(row["values"])
            ax.semilogx(DOSES,vals[:,-1,0],color=c,ls=style,label=label,lw=2)
        ax.set(title=title,xlabel="Primary antibody (nM)",ylabel="Permeability reporter (normalized)",ylim=(-.02,1.03))
        ax.grid(axis="y",alpha=.13)
    axs[0,0].legend(frameon=False,fontsize=9,loc="upper left")
    fig.suptitle("The Hook Is a Property of the System\nSynthetic accumulation-format simulations at 72 h; illustrative parameters, not experimental estimates",fontsize=17)
    (ROOT/"figures").mkdir(exist_ok=True)
    fig.savefig(ROOT/"figures/mechanism-map.png",dpi=180)
    fig.savefig(ROOT/"figures/mechanism-map.svg",metadata={"Date":None})
    plt.close(fig)
    fig,axs=plt.subplots(1,2,figsize=(12,4.8),layout="constrained")
    for ax,case,title in zip(axs,["reference","reporter_loss"],["Persistent reporter","Reporter-loss stress test"]):
        row=next(r for r in lab["curves"] if r["case"]==case and r["order"]=="simultaneous" and r["secondary"]==100)
        vals=np.array(row["values"])
        for idx,label,c,style in [(1,"Committed to death","#B05B36","--"),(2,"Cumulative membrane loss","#667580",":"),(0,"Permeability fluorescence","#006D77","-")]:
            ax.semilogx(DOSES,vals[:,-1,idx],label=label,color=c,ls=style,lw=2)
        ax.set(title=title,xlabel="Primary antibody (nM)",ylabel="Normalized population / signal",ylim=(-.02,1.03))
        ax.grid(axis="y",alpha=.13)
    axs[0].legend(frameon=False,fontsize=10)
    fig.suptitle("Accumulated death and endpoint fluorescence are different model variables\nSynthetic 72 h example; reporter loss is an optional hypothesis, not a claim about a commercial assay",fontsize=14)
    fig.savefig(ROOT/"figures/readout-separation.png",dpi=180)
    fig.savefig(ROOT/"figures/readout-separation.svg",metadata={"Date":None})
    plt.close(fig)
    for name in ("mechanism-map.svg","readout-separation.svg"):
        path=ROOT/"figures"/name
        path.write_text("\n".join(line.rstrip() for line in path.read_text().splitlines())+"\n")

if __name__=="__main__":
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--figures-only",action="store_true",
                        help="Render committed simulation data without rerunning the model.")
    args=parser.parse_args()
    if args.figures_only:
        figures(json.loads((ROOT/"viewer/lab.json").read_text()),
                json.loads((ROOT/"results/sensitivity.json").read_text()))
    else:
        main()
