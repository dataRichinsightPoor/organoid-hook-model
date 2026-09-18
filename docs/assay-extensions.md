# Extending the hook model to other assays

An assay extension changes either the biological state equations, the observation equation, or both. Reusing a bell-shaped curve and changing its axis label is not a mechanistic extension.

## Implemented observation operators

- **Membrane-integrity fluorescence:** optically weighted reporter-accessible permeabilized material. Default signal persistence is infinite; loss and monotonic saturation are explicit optional parameters. This is not a calibrated commercial kit model.
- **ATP-like signal:** metabolically weighted intact-cell states, including committed but not yet permeable cells. It can decline before the permeability readout rises, by construction. Growth, extraction efficiency, and cell-size-dependent ATP content are omitted.
- **Committed-state / caspase proxy:** the transient pre-permeabilization committed state. It is not enzyme abundance, luminescence kinetics, or proof that all modeled death is apoptotic.
- **LDH-like signal:** release at membrane permeabilization followed by first-order reporter loss. It does not include basal secretion, matrix partitioning, enzymatic saturation, or maximum-lysis calibration.
- **Surface/internalized antibody readouts:** surface ternary or internalized ternary copies per initial cell. Direct labeling, acid sensitivity, fluorophore ratio, and recycling of free label need separate models before interpreting these as particular internalization assays.
- **Payload exposure:** current and cumulative productive payload, available independently of all reporters. These states are model outputs, not an assertion that an assay directly measures cytosolic payload.

Different viability methods interrogate distinct cellular properties, rather than being universally interchangeable estimates of a single latent “viability” variable ([methodological review](https://pmc.ncbi.nlm.nih.gov/articles/PMC11719996/)). A published indirect internalization assay also explicitly distinguishes acidified-compartment detection from verified lysosomal delivery ([internalization study](https://pmc.ncbi.nlm.nih.gov/articles/PMC4708616/)).

## Biological extensions not implemented in version 0.1.0

| Application | Change required | Critical distinction |
|---|---|---|
| Direct antibody–drug conjugate killing | Replace primary/secondary assembly with directly conjugated antibody binding; specify payload loading, cleavage, and transport | The secondary-sequestration hook disappears as a mechanism; a direct conjugate need not reproduce the indirect assay ranking |
| Multivalent secondary conjugates | Explicit valency, cross-linked receptor states, avidity, and complex-dependent diffusion/internalization | Concentration ratio can alter the biological object rather than merely its abundance |
| Bystander killing | Add extracellular free payload, release, diffusion, cell entry, and receptor-negative populations sharing the same bath | Zero-target controls may become nonzero for a mechanistically valid reason |
| Target degradation / bifunctional ligands | Replace payload/damage module with induced target degradation, synthesis, and catalytic turnover | Linker-mediated equilibrium hooks motivate a possible analogy, not transferable potency or kinetics |
| Immune-cell cytotoxicity | Add effector cells, contact formation, serial killing, activation/exhaustion, and ratio effects | Killing is not a receptor-internalization flux |
| Sandwich or homogeneous binding assays | Remove cellular trafficking and death modules; replace receptor with capture partner and observation with labeled ternary complex | A binding-complex hook need not imply a biological loss of efficacy |
| Mixed organoid populations | Shared-bath multi-population geometry and population-specific receptor, repair, and transport states | Averaging separately simulated wells cannot reproduce competition in one well |
| Long-term organoid growth assays | Add proliferation, cytostasis, evolving geometry, nutrients, and changing target inventories | Growth inhibition is not identical to death commitment |

The general linker-hook analogy is supported by [published cooperative-binding analysis](https://pmc.ncbi.nlm.nih.gov/articles/PMC5556679/); the specific extensions above are proposals, not implemented or empirically validated modules.

## Measurements that discriminate explanations

Use independent, appropriately controlled measurements to constrain each step rather than fitting every parameter to a single endpoint. Surface receptor abundance, occupied-receptor internalization, recycling/degradation, productive intracellular payload, irreversible cell-state change, and reporter behavior provide different constraints.

A two-dimensional reagent matrix should be interpreted with target-negative, primary-only, and secondary-only controls. A dose-dependent secondary-only signal is outside this version's zero-nonspecific-uptake assumptions; it should trigger a model extension, not be silently absorbed into a receptor-affinity parameter.

Separate the effect of order from the effect of total exposure time. Compare both a common time from first addition and a common time after the second reagent becomes available; retain raw, background-corrected, and normalized readouts so normalization cannot hide a change in the controls.

Optical or reporter explanations require independent reporter-stability, dynamic-range, accessibility, and cell-state checks. A modeled reporter-loss counterexample is a reason to measure persistence, not evidence that persistence failed.
