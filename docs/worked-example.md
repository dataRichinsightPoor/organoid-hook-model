# From Receptor Copies to Fluorescence

A worked example from the Organoid Hook Model

This is a numerical walkthrough of the published [v0.1.0 implementation](https://github.com/dataRichinsightPoor/organoid-hook-model/tree/v0.1.0), not an experimental result or a fit to a particular reagent. The biological parameters remain fixed while three dose conditions reveal the assembly hook and its downstream consequences. All molecule counts below are model-equivalent counts per initial cell, not measurements per surviving cell.

## The chosen system

Use **Mechanism lab → Reference**, not the separate receptor-atlas default, in the [public explorer](https://datarichinsightpoor.github.io/organoid-hook-model/). Choose simultaneous addition, 72 hours, accumulation, and permeability fluorescence; compare the 3 nM and 100 nM secondary curves.

The main trajectory uses 8.254 nM primary and 3 nM secondary. The primary dose is the highest-fluorescence point on the published 13-dose reference grid at 72 hours, not a continuously optimized peak and not the analytical equilibrium peak.

| Component | Fixed assumption |
|---|---|
| Organoids | 20 spheres, each 150 µm in radius, divided into three radial shells |
| Cells | One cell per 2,000 µm³ of tissue; approximately 141,372 initial cells per well |
| Initial surface target | 100,000 receptors per cell, identical initial copy number in every shell |
| Accessible extracellular fraction | 0.20 |
| Bath | 100 µL, finite and well mixed |
| Effective diffusion | 3 µm²/s for free reagents; 1.95 µm²/s for soluble primary–secondary complex |
| Binding | \(K_A=1\) nM; \(K_S=0.3\) nM; both on-rates \(0.36\) nM\(^{-1}\)h\(^{-1}\) |
| Internalization | \(k_R=0.04\), \(k_B=k_T=0.12\) h\(^{-1}\) |
| Intact recycling | \(k_{\mathrm{rec}}=0.06\) h\(^{-1}\) |
| Endosomal receptor degradation | Conditional half-time 12 h; \(k_{\mathrm{deg}}=0.05776\) h\(^{-1}\) |
| Productive payload | Yield \(d=1\) equivalent per conjugate; productive fraction \(\eta=0.20\) |
| Payload loss | Half-time 12 h; \(k_P=0.05776\) h\(^{-1}\) |
| Damage | \(k_{\mathrm{dam}}=0.15\) h\(^{-1}\); \(P_{50}=1,000\) equivalents/cell |
| Recovery | Half-time 24 h; \(k_{\mathrm{rep}}=0.02888\) h\(^{-1}\) |
| Death commitment | \(h_{\max}=0.12\) h\(^{-1}\); \(Q_{50}=0.45\); Hill exponent \(m=3\) |
| Membrane permeabilization | Mean waiting time 6 h after commitment |
| Fluorescence | Persistent reporter, no saturation; optical weights 0.70, 0.85, 1.00 from core to rim |

These are illustrative assumptions. The endosomal degradation half-time is not the whole-cell receptor half-life; downstream recovery is a separate process. The accompanying parameter JSON retains every configurable parameter, including parameters for alternative readouts that do not affect this fluorescence example.

## Converting receptor copies to local concentration

The model uses local nM for binding species and copies per initial cell for productive payload. With cell density \(\rho=1/2000\) cells/µm³ and accessible extracellular fraction \(\epsilon=0.20\), the conversion factor is

\[
\beta=\frac{10^9\rho}{N_{\mathrm{Av}}\epsilon\,10^{-15}}
=0.00415135\ \frac{\mathrm{nM}}{\mathrm{copy/cell}},
\]

where \(N_{\mathrm{Av}}=6.02214076\times10^{23}\) mol\(^{-1}\). Thus

\[
R_{0j}=\beta(100{,}000)=415.13\ \mathrm{nM}
\]

in each shell \(j\). This is a local receptor-equivalent concentration referenced to a very small extracellular tissue volume, not 415 nM receptor throughout the well. The total initial surface-receptor inventory distributed over bath plus accessible tissue volume is only 0.2346 nM equivalent.

To begin at untreated receptor steady state, the model also initializes approximately 33,967 unoccupied endosomal receptors per cell and a constant synthesis flux of 1,962 receptors per initial cell per hour:

\[
u_0=\frac{k_Rq_0}{k_{\mathrm{rec}}+k_{\mathrm{deg}}},
\qquad
\sigma_{\mathrm{copies}}=k_{\mathrm{deg}}u_0.
\]

Here \(q_0=100{,}000\) is initial surface copies/cell and \(u_0\) is initial endosomal copies/cell. The total surface pool is allowed to change after dosing; 100,000 is an initial condition, not a permanently clamped value.

## Binding creates a deliverable complex

The primary \(A\) can bind receptor \(R\) to form \(B\), or bind secondary conjugate \(S\) in solution to form \(C\). Productive surface assembly \(T\) can occur by either route:

\[
A+S\rightleftharpoons C,\qquad
A+R\rightleftharpoons B,\qquad
S+B\rightleftharpoons T,\qquad
C+R\rightleftharpoons T.
\]

The model does not declare all soluble complexes nonproductive. It permits them to bind target, while excess unconjugated primary competes for receptor and the finite secondary inventory is distributed across the primary population.

At 24 h, the outer shell of the chosen trajectory contains:

\[
A=4.370,\ S=0.1467,\ C=2.135,\ R=33.50,\ B=130.28,\ T=63.08
\quad\mathrm{nM}.
\]

These are local state concentrations, not the nominal dosing concentrations. Converting the ternary complex gives

\[
n_T=\frac{T}{\beta}
=\frac{63.0815}{0.00415135}
\simeq15{,}195\ \mathrm{surface\ ternary\ complexes/cell}.
\]

At the same time, the outer-shell endosomal ternary state is \(W=63.8327\) nM, or \(n_W=W/\beta\simeq15{,}376\) complexes/cell. The symbols \(n_T,n_W\) denote molecular counts; \(T,W\) denote concentrations.

## Endosomal complexes become productive payload

Internalized ternary complex \(W_j\) competes between intact recycling and degradation:

\[
\dot W_j=0.12T_j-(0.06+0.05776)W_j.
\]

Only the modeled productive fraction of processed conjugate contributes to intracellular payload. In copies per initial cell,

\[
j_{Pj}=\eta d k_{\mathrm{deg}}\frac{W_j}{\beta},
\qquad
\dot P_j=j_{Pj}-k_PP_j,
\qquad
\dot J_j=j_{Pj}.
\]

Here \(j_P\) is productive delivery rate, \(P\) is currently present productive payload, and \(J\) is cumulative productive delivery. For the outer shell at 24 h:

\[
j_P=0.20(1)(0.05776)(15{,}376.39)
\simeq177.64\ \mathrm{equivalents/cell/h}.
\]

The current payload is \(P=1{,}806.17\) equivalents/cell. Its loss rate is \(0.05776P=104.33\) equivalents/cell/h, so

\[
\dot P=177.64-104.33=73.31\ \mathrm{equivalents/cell/h}.
\]

Payload is still accumulating at this point. It is not correct to multiply the 24 h delivery rate by 24 and call that the accumulated payload, because both delivery and loss vary over time.

## Payload produces damage that competes with recovery

For each shell, generic recoverable damage \(Q\), bounded between zero and one, obeys

\[
\dot Q
=0.15\frac{P}{1000+P}(1-Q)-0.02888Q.
\]

At the same outer-shell 24 h snapshot, \(P=1{,}806.17\) and \(Q=0.61175\):

\[
\dot Q
=0.15\frac{1806.17}{2806.17}(1-0.61175)
-0.02888(0.61175)
\]
\[
=0.03748-0.01767
=0.01982\ \mathrm{h}^{-1}.
\]

This is a phenomenological damage/recovery calculation, not a named toxin's molecular mechanism. \(P_{50}=1,000\) determines half-maximal payload drive at fixed \(Q\); it is not a hard lethal threshold.

The commitment hazard is

\[
h(Q)=0.12\frac{Q^3}{0.45^3+Q^3}.
\]

At \(Q=0.61175\), \(h=0.08584\) h\(^{-1}\). Because the uncommitted fraction in this shell is \(L=0.49846\), the instantaneous commitment flux is \(hL=0.04279\) of the initial population per hour. The hazard is a rate among the remaining uncommitted cells, not the percentage already killed.

## Death commitment becomes fluorescence after a delay

With \(E\) committed but not yet membrane-permeable and \(D\) permeabilized and reporter-accessible,

\[
\dot L=-hL,\qquad
\dot E=hL-\frac{E}{6},\qquad
\dot D=\frac{E}{6}.
\]

At 24 h in the outer shell, \(L=0.49846,\ E=0.23039,\ D=0.27115\). About 50.15% are committed, but only 27.12% are already reporter-accessible; the instantaneous permeabilization flux is \(E/6=0.03840\) per hour. Reporter persistence does not eliminate this biological delay.

The instrument proxy averages shells using both initial-cell counts and optical accessibility:

\[
F_{\mathrm{norm}}
=\frac{\sum_j w_jo_jD_j}{\sum_j w_jo_j}.
\]

Here \(w_j\) is the initial-cell fraction in shell \(j\), and \(o_j\) is its optical weight. Equal radial thicknesses give unequal cell fractions: \(w_j=(1,7,19)/27\).

At 72 h, the reporter-accessible fractions from core to rim are \(0.94338,\ 0.97637,\ 0.98931\). Therefore,

\[
F_{\mathrm{norm}}
=\frac{(1)(0.70)(0.94338)+(7)(0.85)(0.97637)+(19)(1)(0.98931)}
{(1)(0.70)+(7)(0.85)+(19)(1)}
=0.98506.
\]

That is 98.51% of the model's hypothetical fully permeabilized reference signal, not a calibrated CellTox Green RFU and not exactly 98.51% cell death. The cell-weighted membrane-permeable fraction is 98.43%, and cumulative commitment is 99.35%.

Raw fluorescence would require experimentally determined background and gain, \(F_{\mathrm{raw}}=F_{\mathrm{bg}}+g_FF_{\mathrm{norm}}\). Neither is supplied by the simulation.

## Following the same trajectory over time

The following are initial-cell-weighted averages across the three shells. Nonlinear reactions are calculated separately within each shell before averaging; the average damage is not inserted into the hazard equation as a substitute for the spatial model.

| Time | Surface ternary complexes/cell | Current payload/cell | Cumulative delivered payload/cell | Committed | Normalized fluorescence |
|---|---:|---:|---:|---:|---:|
| 0 h | 0 | 0 | 0 | 0% | 0 |
| 6 h | 13,283 | 107 | 117 | 0.00155% | 0.00000120 |
| 12 h | 14,954 | 513 | 624 | 1.43% | 0.00268 |
| 24 h | 14,660 | 1,510 | 2,330 | 39.47% | 0.21337 |
| 48 h | 12,607 | 2,464 | 6,211 | 92.82% | 0.85471 |
| 72 h | 11,418 | 2,494 | 9,724 | 99.35% | 0.98506 |

Surface assembly has already declined by the time fluorescence approaches its maximum. At 72 h the mean payload is also decreasing slightly, with delivery about 138.84 and loss about 144.03 equivalents/cell/h, while fluorescence continues to accumulate. An endpoint reporter therefore cannot be interpreted as an instantaneous measure of receptor engagement or productive payload.

## Where the hook appears, and what more secondary restores

Keep every biological parameter fixed and change only the reagent concentrations:

| Quantity at 72 h | Sampled peak: A 8.254 / S 3 nM | Primary excess: A 1,000 / S 3 nM | More secondary: A 1,000 / S 100 nM |
|---|---:|---:|---:|
| Initial surface receptors/cell | 100,000 | 100,000 | 100,000 |
| Remaining surface receptors/cell | 41,277 | 36,208 | 36,208 |
| Surface ternary complexes/cell | 11,418 | 108 | 3,613 |
| Endosomal ternary complexes/cell | 12,018 | 114 | 3,798 |
| Current productive payload/cell | 2,494 | 24 | 810 |
| Cumulative productive delivery/cell | 9,724 | 107 | 3,584 |
| Mean damage \(Q\) | 0.787 | 0.095 | 0.700 |
| Cumulative commitment | 99.35% | 2.56% | 99.11% |
| Normalized fluorescence | 0.98506 | 0.01985 | 0.97988 |

At excess primary and 3 nM secondary, approximately 99.88% of the remaining surface receptors are antibody-occupied, counting both \(B\) and \(T\). Yet only about 108 complexes per initial cell carry secondary, compared with 11,418 in the peak-dose condition. High primary occupancy is therefore compatible with poor productive assembly, little intracellular payload, and a strong fluorescence hook.

Raising secondary to 100 nM restores fluorescence to 0.97988, close to 0.98506, without restoring surface ternary complexes or current payload to their peak-dose values. Current payload reaches only 810 rather than 2,494 equivalents/cell, but persistent damage and time-integrated commitment are sufficient for near-maximal membrane-permeability signal under these assumptions. A recovered endpoint does not establish recovered delivery.

This is one parameter set in which more secondary restores the endpoint. It does not establish that secondary rescue must occur with another recovery rate, productive-release efficiency, trafficking scheme, tissue geometry, or reporter model.

## Reproduce and interpret responsibly

The accompanying `trace_example.py` reruns the three trajectories, writes the complete parameter JSON, exports the aggregate CSV, and exports all 19 shell states plus selected rate calculations. It checks antibody inventories, cell-state conservation, and monotonic accumulation of the persistent reporter. The endpoint fluorescence values were also recomputed with 100-fold tighter relative solver tolerance; the largest absolute change was less than \(1.4\times10^{-7}\).

No hypothesis test or confidence interval is appropriate here: these are deterministic model evaluations, not experimental replicates. Rounding is for readability, not a statement of biological precision.

The most consequential limitation is that v0.1.0 retains a fixed initial-cell receptor scaffold after death commitment. Its late trafficking and payload counts can therefore be overestimated; they must not be described as payload measured in living cells. The three-shell geometry and all illustrative parameters remain uncalibrated. Full reaction equations, state definitions, assumptions, and boundary conditions are available in the [complete mathematical specification](https://datarichinsightpoor.github.io/organoid-hook-model/equations.html).
