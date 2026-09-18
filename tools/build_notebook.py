"""Generate an executable notebook without requiring notebook tooling."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
cells=[]
def md(text):cells.append({"cell_type":"markdown","metadata":{},"source":text.splitlines(keepends=True)})
def code(text):cells.append({"cell_type":"code","execution_count":None,"metadata":{},"outputs":[],"source":text.splitlines(keepends=True)})
md("""# Organoid Hook Model: run, change, test

Data-Rich, Insight-Poor · v0.1.0 · All results synthetic and uncalibrated.

This notebook downloads the public, version-pinned repository and installs its dependencies in the notebook runtime. No account credentials or experimental data are required. Run the cells in order; then edit the parameter block and rerun the plots. The static explorer uses precomputed results; this notebook runs the actual equations.
""")
code("""from pathlib import Path
import subprocess, sys
repo = Path("organoid-hook-model")
if not repo.exists():
    subprocess.run(["git", "clone", "--depth", "1", "--branch", "v0.1.0",
                    "https://github.com/dataRichinsightPoor/organoid-hook-model.git",
                    str(repo)], check=True)
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-e", str(repo.resolve())+"[dev,fast]"], check=True)
""")
md("## Verify the implementation\nThe test suite checks specified mathematical/software behavior, not empirical biological validity.")
code("""subprocess.run([sys.executable, "-m", "pytest", "-q"], cwd=repo, check=True)
subprocess.run([sys.executable, "tools/verify_atlas.py"], cwd=repo, check=True)
""")
md("## Choose the assumptions\nEvery parameter in `Parameters` can be changed. Doses below are secondary-conjugate molecule concentrations, not payload-equivalent concentrations.")
code("""from dataclasses import replace, asdict
import json
import numpy as np
import matplotlib.pyplot as plt
from organoid_hook import Parameters, simulate, summarize, hook_metrics
from organoid_hook.equilibrium import ternary_equilibrium, peak_primary_nm

p = replace(Parameters(),
    copies_per_cell=100_000,
    core_copy_ratio=1.0,
    radius_um=150,
    diffusion_um2_s=3.0,
    kint_primary=0.12,
    kint_ternary=0.12,
    krecycle=0.06,
    receptor_half_life_h=12,
    protein_recovery_half_life_h=24,
    reporter_loss_h=0.0,
)
primary_doses = np.logspace(-2, 3, 25)
secondary_doses = [0.1, 3.0, 100.0]
order = "simultaneous"  # also primary_first, secondary_first, precomplexed
delay_h = 6
endpoint_h = 72  # clock starts at first addition
print(json.dumps(asdict(p), indent=2))
""")
code("""fig, axs = plt.subplots(1, 2, figsize=(12, 4), layout="constrained")
records = []
for secondary in secondary_doses:
    outputs = [summarize(simulate(float(a), secondary, duration_h=endpoint_h,
                 order=order, delay_h=delay_h, p=p, times=[endpoint_h]))
               for a in primary_doses]
    fluorescence = [s["permeability_fluorescence"][0] for s in outputs]
    committed = [s["committed_fraction"][0] for s in outputs]
    axs[0].semilogx(primary_doses, fluorescence, label=f"{secondary:g} nM secondary")
    axs[1].semilogx(primary_doses, committed, label=f"{secondary:g} nM secondary")
    print(secondary, hook_metrics(primary_doses, fluorescence))
    for a, f, d in zip(primary_doses, fluorescence, committed):
        records.append({"primary_nm": float(a), "secondary_nm": secondary,
                        "fluorescence": float(f), "committed": float(d)})
for ax, title in zip(axs, ["Permeability reporter", "Committed to death"]):
    ax.set(title=title, xlabel="Primary antibody (nM)", ylabel="Normalized state / signal", ylim=(0, 1.05))
    ax.legend()
fig.suptitle("Synthetic, uncalibrated model outputs")
plt.show()
Path("custom-results.json").write_text(json.dumps({"parameters":asdict(p),
    "order":order,"delay_h":delay_h,"endpoint_h":endpoint_h,"results":records},indent=2))
""")
md("""## Test the compact equilibrium equation

The receptor-dilute equilibrium approximation is not the dynamic killing model. It provides an analytically testable assembly maximum under narrower assumptions.
""")
code("""fig, ax = plt.subplots()
for secondary in secondary_doses:
    y = ternary_equilibrium(primary_doses, secondary, receptor_nm=0.001)
    ax.semilogx(primary_doses, y, label=f"{secondary:g} nM secondary")
    print("Analytic peak primary concentration:", peak_primary_nm(secondary), "nM")
ax.set(xlabel="Primary antibody (nM)", ylabel="Surface ternary complex (nM)",
       title="Receptor-dilute equilibrium approximation")
ax.legend()
plt.show()
""")
md("""## Inspect the limits before interpreting

The model omits multivalent cross-linking, nonspecific toxicity, bystander transport, growth, and death-dependent receptor loss. The slow-transport lab scenario is not spatially converged. A generic protein-recovery state is not a named toxin's biochemical mechanism; normalized reporter equations are not commercial-kit calibrations.

Read `docs/model.md` for the complete equations, parameter dictionary, initial/boundary conditions, and inventory balances. Change one assumption at a time and compare the latent biological state with the reporter output.
""")
out={"cells":cells,"metadata":{"kernelspec":{"display_name":"Python 3","language":"python","name":"python3"},"language_info":{"name":"python","version":"3.12"}},"nbformat":4,"nbformat_minor":5}
(ROOT/"examples/quickstart.ipynb").write_text(json.dumps(out,indent=1)+"\n")
print("Built examples/quickstart.ipynb")
