# Organoid Hook Model: Scientific Challenge and Literature Audit

September 18, 2026. Article: The Hook Is a Property of the System, Data-Rich, Insight-Poor — CCXXIV. Numerical model: v0.1.0, synthetic and uncalibrated.

This audit separates mathematical verification, literature support, and biological validation. The first two can strengthen the article; neither substitutes for matched experimental measurements.

## Independent challenge and disposition

Claude Fable 5 independently challenged the manuscript and numerical implementation against baseline commit `3d6e2ec`. A separately selectable Fable 5.1 was not available. This was an AI-assisted adversarial technical review, not formal peer review or experimental validation. Its verdict was “accept with required revisions.” The final manuscript was revised by the coordinating editor; the reviewer did not independently re-review the final version.

The review reproduced the equilibrium reduction, peak formula, high-primary asymptote, and principal dynamic results. Its substantive objections were independently checked rather than accepted on authority:

- **Equilibrium versus dynamic inventories:** Accepted. The prior 50,000/91,000 receptor-copy illustration was removed. The text now gives approximately 0.50/0.91 as dilute-equilibrium fractions and separately reports approximately 12,600/35,200 surface complexes per initial cell in the dynamic model at 72 hours.
- **Payload-scale symmetry:** Accepted and strengthened. The calibration section now states the joint release/susceptibility rescaling and demonstrates invariant fluorescence with doubled payload. The opening comparison labels its assigned scale. The 63% relative deficit survives this shared rescaling; it is not thereby experimentally identified or robust to every other parameter change.
- **Nominal secondary excess:** Accepted with a correction to the review's generalization. The large-secondary limit is not a universal finite-secondary statement. The exact finite condition is `S₀ > KA + √(KA KS)` for the dilute assembly peak to occur below equimolar primary. The equations page and regression test state that boundary explicitly; the article uses the illustrative 647 nM peak at 1,000 nM secondary.
- **Closer literature precedent:** Accepted. Quadros 2010 is now the first reference, but is not characterized as definitive proof of a tumor-organoid CellTox hook.
- **Default geometry versus analytical reduction:** Clarified. The reduced expression is a valid idealized limiting case, but is not a substitute for default finite-bath dynamics. The mathematical specification now gives both local and whole-well receptor-equivalent concentrations and warns against interchanging their volume bases.
- **Cooperativity citation:** Re-fetched and verified. The theoretical analysis explicitly retains a hook while positive cooperativity delays and mitigates it; the article now states that direction precisely ([Dutta Roy et al.](https://pmc.ncbi.nlm.nih.gov/articles/PMC5556679/)).

An optional reviewer suggestion to choose affinities that reproduce the Quadros optimum was not included. An adjustable peak can demonstrate compatibility but would add no independent calibration or mechanism identification. Likewise, the review's suggestion that the relative delivery ratio is “identified” was narrowed to invariance under the specific scale transformation.

## Literature coverage

The expanded search used nineteen focused queries and returned 88 hits representing 83 distinct URLs before relevance screening. It covered secondary-toxin competition, secondary-labeled hook effects, ternary assembly, multivalency, receptor trafficking and turnover, productive payload access, three-dimensional transport, membrane-integrity fluorescence, and alternative assay interpretation. Previously retrieved primary records were reused and promising or contradictory new records were read in full or through targeted full-text extraction.

The revised article cites fifteen peer-reviewed publications and separately identifies manufacturer documentation. This is a targeted literature challenge, not a preregistered systematic review or a guarantee that all relevant publications have been captured. Records with inadequate disclosure coverage were not promoted to core references.

## Evidence that changed the argument

The closest added cytotoxicity precedent is the secondary-saporin study by [Quadros and colleagues](https://pmc.ncbi.nlm.nih.gov/articles/PMC2978776/). Specific primary and normal mouse IgG competition reduced growth inhibition, while increasing secondary from 10 to 40 nM at 2.5 nM primary did not further increase death ([Quadros et al.](https://pmc.ncbi.nlm.nih.gov/articles/PMC2978776/)). These results establish relevant competition and a limit to endpoint improvement, not the complete mechanism of a tumor-organoid CellTox hook. The text does not promote the reported optimal concentration into a figure-verified full hook curve.

Cross-linking can change the delivery route, rather than simply increasing the number of loaded receptors: [Moody and colleagues](https://pmc.ncbi.nlm.nih.gov/articles/PMC4700114/) redirected receptor complexes toward lysosomes using a biotin–streptavidin system. This is adjacent mechanistic evidence, not a secondary-toxin hook study. The revised article explicitly states that fixed-rate trafficking presets cannot generate concentration-dependent cross-linking effects.

Processing can be dissociated from cytotoxicity: a protein-immunotoxin itinerary that generated more cleaved active fragment was less cytotoxic and showed faster degradation in the study by [Tortorella and colleagues](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0047320). The model's common endosomal degradation/processing rate is therefore described as a simplifying assumption, not a transferable biological law. Toxin destruction and productive access would need separate routes where the experimental system requires them.

CellTox-specific evidence tempers the optional reporter-loss narrative. [Chiaraviglio and Kirby](https://pmc.ncbi.nlm.nih.gov/articles/PMC4026211/) found sustained assay separation during a three-day evaluation in J774 cells, whereas the marker-loss precedent cited from [Forcina and colleagues](https://pmc.ncbi.nlm.nih.gov/articles/PMC5509363/) concerned SYTOX-positive object counts. Neither provides a CellTox loss constant in organoids. The article now foregrounds this distinction and identifies the optional loss simulation as an unvalidated stress test.

The [CellTox Green technical manual](https://www.promega.de/-/media/files/resources/protocols/technical-manuals/101/celltox-green-cytotoxicity-assay-protocol.pdf) identifies autofluorescence, quenching, competition by DNA-intercalating compounds, and matrix-associated DNA as potential interference. These are measurement checks, not evidence that any one occurred in the user's assay.

## Mathematical checks

The receptor-dilute secondary-excess example was recalculated with secondary 1,000 nM, primary 1 and 10 nM, primary–receptor dissociation constant 1 nM, and primary–secondary dissociation constant 0.3 nM. The loaded fractions are 0.499849895 and 0.908815511, a 1.818176858-fold increase. The article now rounds these to 0.50, 0.91, and about 1.8-fold and removes the earlier receptor-copy conversion to avoid confusing the fixed-pool calculation with dynamic inventories.

An independent closed-compartment calculation retained receptor-mediated ligand depletion and solved the primary, secondary, and receptor mass balances. At the default geometry's initial whole-well receptor equivalent of 0.234620505 nM, the loaded fractions become 0.470631317 and 0.907022078. This is not a dynamic organoid prediction; it demonstrates why receptor copies must be accompanied by cell number and accessible volume before the dilute approximation is adopted.

Review-only dynamic simulations at secondary 1,000 nM gave 72-hour fluorescence values of 0.921420809 and 0.992131899 for primary 1 and 10 nM. Their surface ternary inventories were approximately 12,641 and 35,221 copies per initial cell, not 50,000 and 91,000. This does not contradict the static calculation: trafficking, replacement, spatial transport, and changing receptor pools are present only in the dynamic case. These trajectories remain outside the browser's precomputed grid and were not silently added to its 5,304 scenarios.

The analytical peak expression was checked against a dense neighboring dose grid for 100 randomly selected positive affinity/secondary parameter sets. Because each grid was centered on the analytical peak, this is a local maximum sanity check, not an independent symbolic derivation or a proof of all possible regimes.

## Structural nonidentifiability

The most consequential added numerical test changes productive-release efficiency from 0.2 to 0.4 and the payload response scale from 1,000 to 2,000, with all other parameters fixed. Productive payload and cumulative delivery double, while the ratio governing damage production remains unchanged. Consequently, death and fluorescence trajectories are invariant apart from solver error.

At primary 8.254 nM and secondary 3 nM, cumulative delivery at 72 hours changes from 9,724.409 to 19,448.819 equivalents per initial cell. Endpoint fluorescence is 0.985057977 versus 0.985057959; the largest absolute fluorescence difference across the trajectory is approximately 0.000000106.

This is a structural ambiguity in the stated model. More observations of the same fluorescence response cannot identify an absolute payload scale that the observation equations make interchangeable with susceptibility. Calibration requires a constraint that breaks that equivalence, such as an independently measured payload inventory or response scale.

## Reproduction and limits

Run `python tools/review_checks.py` from the repository root after installing the package dependencies. The resulting calculations are recorded in `results/review-checks.json`. The automated regression `test_payload_scale_nonidentifiability` checks preservation of fluorescence and doubling of productive inventories; the full suite contains 44 passing tests at this revision.

The numerical solver, reference parameters, atlas grid, and model version are unchanged. Tests verify the implementation's stated mathematical behavior, not empirical predictive accuracy. The three-shell transport stress case is not spatially converged; post-commitment trafficking continues on a fixed initial-cell scaffold; growth, nonspecific uptake, aggregate distributions, and concentration-dependent cross-linking remain outside the model.

Source screening inspected retrieved affiliations, support, acknowledgments, and disclosures. No explicitly excluded affiliation was identified in the newly included records; industry support and patent interests were retained in the provenance record rather than suppressed. This bounded publication-record screen cannot establish the absence of undisclosed or historical relationships and provides no legal clearance.
