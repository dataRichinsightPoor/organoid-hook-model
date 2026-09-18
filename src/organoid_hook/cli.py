import argparse
import csv
import json
from pathlib import Path
from .model import Parameters, simulate, summarize

def main():
    parser=argparse.ArgumentParser(description="Generic no-wash secondary-conjugate simulation. Not calibrated.")
    parser.add_argument("--primary",type=float,default=10)
    parser.add_argument("--secondary",type=float,default=1)
    parser.add_argument("--hours",type=float,default=72)
    parser.add_argument("--delay",type=float,default=6)
    parser.add_argument("--order",choices=["simultaneous","primary_first","secondary_first","precomplexed"],default="simultaneous")
    parser.add_argument("--parameters",type=Path,help="JSON object overriding any Parameters fields")
    parser.add_argument("--output",type=Path,default=Path("simulation.csv"))
    args=parser.parse_args()
    params=Parameters(**json.loads(args.parameters.read_text())) if args.parameters else Parameters()
    result=simulate(args.primary,args.secondary,args.hours,args.order,args.delay,params)
    summary=summarize(result)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open("w",newline="") as f:
        writer=csv.writer(f);writer.writerow(summary)
        writer.writerows(zip(*summary.values()))
    args.output.with_suffix(".json").write_text(json.dumps({"parameters":result["parameters"],"design":result["design"]},indent=2)+"\n")
    print(args.output)
