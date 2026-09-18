# Organoid Hook Model

A no-install, accumulation-format secondary-conjugate assay explorer for Data-Rich, Insight-Poor — CCXXIV. A mechanistic Python model separates reagent assembly, receptor trafficking, finite-bath transport, productive payload delivery, recoverable damage, and the observation process.

**All results are synthetic. All default parameters are illustrative assumptions. This is an uncalibrated hypothesis generator, not a predictor of a specific antibody, receptor, toxin, organoid, or commercial assay.**

## Model, code, and mathematics

- **Interactive model:** [Open the public Organoid Hook Model](https://datarichinsightpoor.github.io/organoid-hook-model/).
- **Source code:** [Browse the Python package](https://github.com/dataRichinsightPoor/organoid-hook-model/tree/main/src/organoid_hook), including the [dynamic solver](https://github.com/dataRichinsightPoor/organoid-hook-model/blob/main/src/organoid_hook/model.py) and [analytical equilibrium model](https://github.com/dataRichinsightPoor/organoid-hook-model/blob/main/src/organoid_hook/equilibrium.py).
- **Mathematics:** [Read all equations, variables, units, and parameters on GitHub](https://github.com/dataRichinsightPoor/organoid-hook-model/blob/main/docs/model.md), or open the [typeset browser version](https://datarichinsightpoor.github.io/organoid-hook-model/equations.html).
- **Illustrated article:** [Read the article with figures](https://datarichinsightpoor.github.io/organoid-hook-model/article.html), or open the [GitHub manuscript](docs/the-hook-is-a-property-of-the-system.md).

The [public-source provenance](docs/provenance.md) and [scientific challenge and literature audit](docs/scientific-challenge.md) document the evidence boundaries and revisions.

## Start here

No coding or GitHub experience is needed to explore the model.

1. **Open the [interactive explorer](https://datarichinsightpoor.github.io/organoid-hook-model/).** Keep the default settings initially and compare the three secondary-concentration curves. The plotted values are synthetic simulations, not experimental measurements.
2. **[Follow one simulation](https://datarichinsightpoor.github.io/organoid-hook-model/#follow-one-simulation).** Trace receptor copies through surface assembly, productive payload, and fluorescence before changing the larger parameter set.
3. **Compare what the assay reports with what was delivered.** Return to the explorer and change the vertical-axis measurement from fluorescence to cumulative payload delivery. Then change one available receptor, trafficking, or timing setting at a time.
4. **Inspect or extend the model.** Read the [illustrated article](https://datarichinsightpoor.github.io/organoid-hook-model/article.html) for interpretation and the [equations and parameter definitions](https://datarichinsightpoor.github.io/organoid-hook-model/equations.html) for the mathematics. To run new parameter combinations, use the [Colab notebook](https://colab.research.google.com/github/dataRichinsightPoor/organoid-hook-model/blob/main/examples/quickstart.ipynb) or follow **Run locally** below.

The browser displays precomputed scenarios; it does not fit your data or solve arbitrary new settings. The model is uncalibrated, so use it to examine assumptions and competing explanations, not to predict your assay's potency.

[Run and modify the actual model in Colab](https://colab.research.google.com/github/dataRichinsightPoor/organoid-hook-model/blob/main/examples/quickstart.ipynb). The notebook downloads the version-pinned public release, runs the tests, and lets you change continuous parameters without a local Python installation; it executes in a third-party notebook runtime.

[Follow one simulation](https://datarichinsightpoor.github.io/organoid-hook-model/#follow-one-simulation): step through six computed time points from receptor copies to fluorescence, compare three dose conditions, and inspect the substituted equations in the [complete worked example](https://datarichinsightpoor.github.io/organoid-hook-model/worked-example.html). This fixed Reference example is independent of the atlas controls and uses the unchanged v0.1.0 model. Its downloadable script, parameters, shell states, and aggregate trajectories are included.

The explorer and reading pages open in dark mode, with a manual light-mode option. The expanded article includes fifteen peer-reviewed references and separately identified manufacturer documentation. Its [publication cover](figures/cover-hook-system.png) uses actual viewer captures; `tools/build_cover.py` reproduces the composition from committed screenshots.

The [LinkedIn and Substack publication kit](publication/README.md) contains the illustrated manuscript, portable inline notation, five typeset equation images in light and dark versions, and the cover and six scientific figures.

## What you can explore

- **Receptor atlas:** 4,212 simulations across 10,000 / 100,000 / 1,000,000 initial surface copies per cell, three trafficking archetypes, three endosomal receptor degradation half-times, four orders of addition, and two-dimensional primary / secondary concentration combinations.
- **Mechanism lab:** 1,092 additional simulations isolating transport geometry, target-poor cores, downstream protein-recovery kinetics, productive release, and optional reporter loss.
- **Accumulation format:** simultaneous addition, primary first, secondary first, and equilibrium-precomplexed addition. Delayed additions are 6 h apart in the browser atlas. No medium or reagent is removed.
- **Time-resolved comparisons:** 24, 48, and 72 h from first addition, with both biological state and reporter output. Exposure-clock sensitivity is provided separately.
- **Assay extensions:** permeability-dye fluorescence, ATP-like metabolic signal, committed-state/caspase proxy, LDH-like reporter, surface ternary complex, endosomal complex, and payload delivery. These are generic observation models, not fitted kit calibrations.
- **Downloadable evidence:** browser CSV, JSON parameter exports, complete atlas JSON, documented equations, reproducible figures, unit tests, citation metadata, and a versioned release.

The browser filters committed Python outputs; it does not silently substitute a simplified live model. There is no interpolation between parameter combinations and no hidden data collection.

## Run locally

```bash
python -m pip install -e '.[dev,fast]'
python -m pytest -q
organoid-hook --primary 30 --secondary 3 --order primary_first --delay 6 --hours 72 --output example.csv
organoid-hook --parameters examples/custom-parameters.json --primary 30 --secondary 3 --output custom.csv
python tools/build_atlas.py
python tools/build_mechanism_lab.py
python tools/build_trace.py
python tools/build_reading_pages.py
python tools/verify_atlas.py
```

The optional `fast` extra accelerates the same ODE with Numba. The package also runs with NumPy and SciPy alone. Generated CSVs have matching JSON sidecars recording all model parameters and dose timing.

For a fully custom sweep:

```python
from dataclasses import replace
from organoid_hook import Parameters, simulate, summarize

p = replace(Parameters(), copies_per_cell=2e5, radius_um=200,
            receptor_half_life_h=36, protein_recovery_half_life_h=8,
            kint_primary=0.2, kint_ternary=0.1, krecycle=0.3)
result = simulate(primary_nm=30, secondary_nm=3, duration_h=96,
                  order="secondary_first", delay_h=12, p=p)
trace = summarize(result)
```

For mixtures of distinct organoids, run each population separately and aggregate with initial-cell-count weights. This does not reproduce competition between mixed populations in one shared bath; that would require a multi-population common-bath extension.

## Interpretation boundaries

A high-dose decline can arise from competing assembly routes. More secondary can shift that decline beyond the tested window without eliminating it at all possible primary concentrations. A flat low response is not a successfully repaired assay, and a delivery bottleneck does not automatically generate a hook.

The model explicitly includes a primary-bound soluble complex that can still bind receptor. It does not assume every soluble complex is permanently nonproductive. Effective binding is 1:1:1; multivalent cross-linking, concentration-dependent aggregation, Fc-receptor uptake, free-payload toxicity, bystander diffusion, growth, evolving tissue geometry, and death-dependent receptor loss are not modeled.

The receptor module runs on a fixed initial-cell scaffold, even after modeled death commitment. This preserves explicit ligand bookkeeping but can overestimate late delivery. Three radial shells are an exploratory approximation, not a spatially converged organoid reconstruction. See the [resolution checks and structural limitations](docs/model.md).

No confidential measurements, internal protocols, nonpublic target identities, or proprietary reagent parameters are included. Public literature is used for mechanisms, not to disguise guessed numbers as fitted values. The source screen is bounded to retrieved publication records and disclosures; it is not a legal clearance or a guarantee about all past and present affiliations.

## Project map

```text
src/organoid_hook/      Python ODE, validation, readouts, CLI
tests/                 controls, inventories, event timing, solver checks
tools/                 deterministic atlas, figures, verification
viewer/                static browser explorer and computed JSON
results/               machine-readable mechanism and sensitivity outputs
figures/               original figures generated from synthetic outputs
docs/                  article, equations, source audit, extensions
examples/              editable parameter files
```

MIT licensed. Citation metadata is in `CITATION.cff`. Version 0.1.0 denotes an initial, uncalibrated research-software release; code verification is not biological validation.
