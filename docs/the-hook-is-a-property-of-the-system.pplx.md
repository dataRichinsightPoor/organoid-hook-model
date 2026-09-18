# The Hook Is a Property of the System

Data-Rich, Insight-Poor

An antibody curve can turn downward precisely where receptor occupancy ought to be least in doubt. In a no-wash assay, the cell is not the only place where antibodies meet: excess primary antibody can occupy the target while another fraction recruits the secondary reagent in solution, a competition documented in homogeneous cell-binding and internalization assays ([cell-binding study](https://pmc.ncbi.nlm.nih.gov/articles/PMC5842027/); [internalization study](https://pmc.ncbi.nlm.nih.gov/articles/PMC4708616/)). The downward turn is therefore not necessarily a statement about the antibody's affinity. It may be a statement about the assay's inventory.

That distinction becomes more consequential when the secondary reagent carries a cytotoxic payload rather than a fluorophore. Binding must then be followed by entry, productive processing, sufficient intracellular exposure, damage that outlasts recovery, and a death-associated change the readout can detect; internalization alone does not establish successful drug delivery ([trafficking analysis](https://pmc.ncbi.nlm.nih.gov/articles/PMC3564878/)). Increasing secondary concentration perturbs the beginning of that sequence. There is no reason to expect it to repair every later step.

The accompanying Organoid Hook Model makes this argument executable. Its 5,304 simulations are synthetic, its parameters are illustrative, and none is fitted to an experimental dataset. Readers can open the [browser explorer](https://datarichinsightpoor.github.io/organoid-hook-model/), change the receptor and assay assumptions, inspect exact values, download the results, and rerun the Python implementation. The purpose is not to manufacture a persuasive explanation for a particular curve. It is to show which explanations the curve cannot distinguish.

## The missing partner

In the simplest representation, a primary antibody binds both a receptor and a secondary conjugate. Four reversible associations connect the possible states: primary with receptor, primary with secondary in solution, secondary with receptor-bound primary, and soluble primary–secondary complex with receptor. The last route is essential. A complex in solution is not automatically useless; declaring it so would make the desired hook easier to obtain by making the chemistry less faithful.

With limited secondary, increasing primary eventually distributes that secondary across an expanding population of primary molecules while unconjugated primary competes for receptor. This is the relevant intuition behind the hook, consistent with the more general mathematics of linker-mediated complex formation ([cooperative-binding analysis](https://pmc.ncbi.nlm.nih.gov/articles/PMC5556679/)). It is not the claim that the secondary has vanished. The question is where it is, what it is bound to, and whether that state can reach the next step.

The reduced equilibrium equation makes the competition explicit. Productive surface complex is proportional to soluble primary–secondary complex divided by the sum of primary concentration and the primary–receptor dissociation constant. At high primary concentration, soluble complex approaches a ceiling set by the finite secondary supply, while the competing primary population continues to increase. Productive surface complex consequently falls approximately in inverse proportion to primary concentration. The [mathematical specification](https://datarichinsightpoor.github.io/organoid-hook-model/equations.html) gives the closed-form equation, its derivation, the predicted peak location, and the assumptions under which that approximation is valid.

More secondary shifts that peak to a higher primary concentration in the reduced model. A hook can therefore leave the sampled concentration window without disappearing from the underlying assembly mechanism. The assay has become less visibly nonmonotonic, not necessarily more informative.

In the full synthetic reference example, the normalized permeability signal at the highest tested primary concentration rises from approximately 0.020 with 3 nM secondary to 0.980 with 100 nM secondary at 72 hours. The decline from the sampled maximum falls from approximately 98% to 1.5%. These are model outputs, not reagent recommendations, and the nearly saturated response deserves as much scrutiny as the original hook: a downstream ceiling can conceal differences in delivery that remain large upstream.

## Receptors have a traffic history

A surface copy number is an initial condition, not a delivery rate. The relevant flux depends on how much productive complex is present, how quickly it enters the cell, what fraction recycles, and what fraction is processed in a compartment capable of releasing active payload; published work explicitly distinguishes these steps ([trafficking analysis](https://pmc.ncbi.nlm.nih.gov/articles/PMC3564878/)). A busy receptor can be a poor courier if most of its journeys return the cargo unopened.

The model therefore separates free-receptor, primary-bound, and ternary-complex internalization. Internalized receptor can recycle intact or be degraded. Surface copies begin at a defined steady state, maintained by a synthesis term, so a high-copy target and a rapidly replenished target are not treated as interchangeable.

Even “receptor half-life” requires a compartment. The explorer varies the degradation half-time of retained endosomal receptor, not an experimentally measured whole-cell protein half-life. Recycling competes with that degradation, and changing the degradation rate changes the synthesis flux required to maintain the same starting surface abundance. A pulse-chase experiment and a surface-binding measurement would constrain different parts of this model.

There is a second turnover process downstream. The simulator includes a generic recoverable protein deficit or damage state, separate from receptor degradation and payload clearance. In one synthetic counterexample, shortening the recovery half-time from 24 hours to 2 hours leaves a substantial hook even at 100 nM secondary: the top-dose permeability signal is approximately 0.226, compared with a sampled maximum of approximately 0.710. Residual differences in delivered payload are no longer hidden by near-complete killing. Increasing secondary improves the assembly problem but does not make the downstream recovery timescale irrelevant.

This is a conditional result, not a claim that protein turnover explains every failed rescue. A nearly flat low curve can instead arise because productive release is inadequate. Calling that flatness a repaired hook would confuse the absence of shape with the presence of useful signal.

![Six synthetic mechanism comparisons showing how secondary concentration, transport, productive release, protein recovery, and optional reporter loss change the dose-response curve.](../figures/mechanism-map.png)

Figure 1. Synthetic no-wash examples at 72 hours, generated from the committed model outputs. The transport panel is a deliberately coarse, non-mesh-converged stress test; its numerical values should not be interpreted as transport predictions.

## An organoid is not a stirred well

Antibody binding, diffusion, antigen abundance, and antigen turnover jointly influence penetration into tumor spheroids; direct experiments have tested the prediction that high expression and rapid turnover can impede access to deeper regions ([spheroid-penetration study](https://pmc.ncbi.nlm.nih.gov/articles/PMC2831054/)). More target can therefore increase the local binding sink while reducing the fraction of tissue reached. The surface of an organoid and its center do not necessarily experience the nominal concentration written on the plate map.

The simulator uses a finite bath coupled to concentric tissue shells. Free primary, free secondary, and soluble complex diffuse separately, with the complex assigned a lower effective diffusivity. Ligand binding depletes local soluble material, and every intercompartmental transfer is balanced by an equal loss elsewhere. A target-poor core can be specified independently of the rim.

This geometry is intentionally modest. Three shells are enough to make a spatial assumption visible, not enough to declare it resolved. In the reference scenario, increasing the shell count from three to twelve changes the modeled endpoint fluorescence only slightly. In the deliberately difficult large-organoid, slow-transport case, it changes substantially and nonmonotonically. That scenario is visibly labeled as not spatially converged; its purpose is qualitative stress testing, not quantitative prediction of penetration depth. A numerical model should report where its own measurement becomes inadequate.

The timing comparison carries a similar accounting requirement. Reading all wells 72 hours after the first addition gives a delayed-secondary condition less combined-reagent exposure than simultaneous addition. The repository also calculates endpoints aligned to the second addition. In the synthetic secondary-first example, much of the apparent delay effect disappears when the combined-exposure clock is matched. Order of addition and duration of joint exposure are different experimental variables, even when a single endpoint makes them look like one.

## The reporter arrives last

A membrane-impermeant DNA-binding readout measures an event associated with loss of membrane integrity, not the preceding molecular delivery sequence; viability methods based on metabolism, membrane integrity, and other cellular properties interrogate different aspects of cell state ([viability-methods review](https://pmc.ncbi.nlm.nih.gov/articles/PMC11719996/)). This is not a defect of a particular reagent. It is the ordinary consequence of measuring one event downstream of several others.

The model keeps death commitment, membrane permeabilization, and reporter-accessible material separate. With reporter loss disabled, accessible material accumulates through time after cells become permeable. An optional stress test allows reportable material to disappear after that event, representing a hypothetical loss of accessibility or persistence rather than an asserted property of a commercial dye.

That distinction produces a useful counterexample. At 100 nM secondary, the synthetic reporter-loss scenario shows approximately 99% cumulative death commitment at the highest primary concentration but only approximately 9% normalized endpoint fluorescence. Earlier, stronger killing has had more time to lose its reportable material. The fluorescence curve can turn down while the cumulative biological response remains close to its ceiling.

The model does not need this assumption to generate the assembly hook. Reporter loss is off by default, and the stress test is not evidence that it occurs in a real organoid assay. It specifies an alternative that must be measured before being invoked. A saturating detector alone is not the same alternative: a monotonic saturation function can flatten a monotonic input, but it cannot reverse its direction.

![Synthetic curves separating cumulative death commitment, cumulative membrane loss, and fluorescence, with reporter loss disabled or enabled.](../figures/readout-separation.png)

Figure 2. The same modeled biological response observed with persistent or transient reporter accessibility. Only the observation-persistence assumption changes; the reporter-loss scenario is not a claim about a commercial assay.

The same caution applies to indirect internalization measurements. A published homogeneous assay study explicitly notes that acidified endosomal detection does not uniquely quantify lysosomal routing and that recycling can inflate apparent delivery ([internalization study](https://pmc.ncbi.nlm.nih.gov/articles/PMC4708616/)). The useful distinction is not between a good assay and a bad assay. It is between the event observed and the event inferred.

## A model worth disagreeing with

The browser offers permeability fluorescence, an ATP-like signal, a committed-state/caspase proxy, an LDH-like release reporter, surface ternary complex, endosomal complex, intracellular payload, and cumulative productive delivery. These are different observation equations applied to a shared latent system, not interchangeable versions of “percent killing.” They are also generic proxies; replacing one with a named assay would require its own calibration, extraction efficiency, background, persistence, and biological controls.

The most useful comparison is therefore not simply a better-looking concentration curve. It is a set of measurements that separates assembly from uptake, uptake from productive processing, and biological response from the observation process. Two-dimensional primary-by-secondary titrations can test the predicted movement of an assembly maximum. Surface and intracellular measurements can test whether that movement survives trafficking. Target-negative and secondary-only controls can expose toxicity absent from the model by construction. A time course and an independent cell-state measurement can test whether endpoint fluorescence records accumulated death faithfully.

The implementation also contains limitations that cannot be fixed by collecting a denser concentration series. Binding is effectively 1:1:1, not a full account of multivalent secondary cross-linking. There is no explicit aggregate distribution, bystander payload transport, extracellular cleavage, cell growth, or changing tissue geometry. Receptor trafficking continues on a fixed initial-cell scaffold after modeled death commitment, which can overestimate late delivery. Those are structural assumptions, not inconvenient parameters waiting for a fit.

An ablation provides a small example of why the distinction matters. Removing solution-phase association greatly attenuates the modeled hook, but does not completely remove it: competition involving receptor binding by pre-existing soluble complexes remains. The result is retained in the repository rather than rewritten to make the explanation cleaner. A simulation earns its place in an argument when it is allowed to disagree with the argument.

The hook is not an instruction to discard a curve, nor a diagnosis supplied by the curve itself. It is a demand to account for the reagent, the receptor, the route, and the reporter. Increasing secondary can make that demand less visible. Making the accounting executable is what makes the interpretation testable.

## Read, inspect, reproduce

The [Organoid Hook Model explorer](https://datarichinsightpoor.github.io/organoid-hook-model/) runs without installation and includes exact-value tables, CSV export, and complete parameter export. The [versioned repository](https://github.com/dataRichinsightPoor/organoid-hook-model) contains the equations, public-source provenance, synthetic outputs, original figures, and tests; changing a continuous parameter or replacing an observation equation requires the documented Python workflow.

The literature establishes the cited assay and transport principles. The simulations, numerical examples, and proposed mechanistic interpretations are independent illustrative constructions, not reported findings from those papers and not a substitute for experimental calibration.
