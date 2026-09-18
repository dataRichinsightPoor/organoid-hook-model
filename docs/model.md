# Mathematical specification of the organoid hook model

Version 0.1.0. This document defines the equations actually implemented in `src/organoid_hook/model.py`, a compact analytical reduction in `equilibrium.py`, every state variable, and every configurable parameter. The mathematics is a proposed, uncalibrated model, not an identification of the cause of any experimental observation.

## A compact equation for the assembly hook

Let \(A_0\) be total primary antibody, \(S_0\) total secondary conjugate, \(R_0\) total locally available surface receptor, \(K_A\) the primary–receptor dissociation constant, and \(K_S\) the primary–secondary dissociation constant. All five quantities have concentration units, taken here as nM.

For independent effective 1:1 binding, negligible receptor-mediated depletion of either soluble reagent, uniform exposure, and equilibrium, the soluble primary–secondary complex is

\[
C_{\mathrm{eq}}(A_0,S_0)=
\frac{A_0+S_0+K_S-
\sqrt{(A_0+S_0+K_S)^2-4A_0S_0}}{2}.
\]

The productive surface ternary complex is approximately

\[
\boxed{
T_{\mathrm{eq}}(A_0,S_0;R_0,K_A,K_S)
\simeq
\frac{R_0}{2(K_A+A_0)}
\left[
A_0+S_0+K_S-
\sqrt{(A_0+S_0+K_S)^2-4A_0S_0}
\right].
}
\]

“Productive” here means competent to enter the modeled delivery pathway, not guaranteed to release active payload or kill a cell. The stable numerical implementation evaluates \(C_{\mathrm{eq}}=2A_0S_0/[A_0+S_0+K_S+\sqrt{(A_0+S_0+K_S)^2-4A_0S_0}]\) to avoid subtraction cancellation.

This equation can hook without an imposed bell-shaped response function. At low \(A_0\), \(C_{\mathrm{eq}}\) grows approximately as \(A_0S_0/(K_S+S_0)\); at very high \(A_0\), \(C_{\mathrm{eq}}\to S_0\) while total receptor occupancy competes with excess unconjugated primary, giving

\[
T_{\mathrm{eq}}\sim\frac{R_0S_0}{A_0}\qquad(A_0\to\infty).
\]

The concentration at the maximum, under the same assumptions and for \(S_0>0\), is

\[
\boxed{
A_{\mathrm{peak}}=
\sqrt{K_AK_S}
+S_0\frac{\sqrt{K_A}}{\sqrt{K_A}+\sqrt{K_S}}.
}
\]

Therefore, adding secondary shifts the assembly maximum to a larger total primary concentration in this limiting model. It does not abolish the high-primary asymptote. A hook can disappear from the tested window while remaining in the underlying assembly curve.

### Derivation and limits

Let free primary be \(a\), free secondary \(s\), and free receptor \(r\). At equilibrium, \(C=as/K_S\), \(B=ar/K_A\), and \(T=ars/(K_AK_S)\). With receptor depletion neglected, \(A_0=a+C\); the receptor balance gives \(R_0=r+B+T=r[1+(a+C)/K_A]\), hence \(T=R_0C/(K_A+A_0)\).

The solution balance gives \(A_0=C+K_SC/(S_0-C)\). Differentiating \(C/[K_A+A_0(C)]\) with respect to \(C\) gives the maximum at \(C/(S_0-C)=\sqrt{K_A/K_S}\); substitution yields \(A_{\mathrm{peak}}\) above.

If receptor-mediated ligand depletion matters, retain all three local conservation equations:

\[
A_{\mathrm{tot}}=a+B+C+T,\qquad
S_{\mathrm{tot}}=s+C+T,\qquad
R_{\mathrm{tot}}=r+B+T.
\]

Solve these with the equilibrium relationships rather than using the receptor-dilute approximation. The dynamic finite-bath model below instead conserves each reagent across bath, tissue, internalized complexes, and degradation inventories.

The reduced equation does not predict cell killing, specify a half-maximal lethal concentration, or encode diffusion, preincubation, turnover, multivalency, or signal persistence. These processes must not be disguised as fitted changes in \(K_A\) or \(K_S\).

## Complete dynamical model

The full model has \(3+19n\) states, where \(n\) is the radial-shell count. A three-shell simulation has 60 states. Time is in hours, extracellular and receptor-associated species are nM in the local accessible extracellular volume, payload is model-equivalent copies per initial cell, and cell-state variables are fractions of the initial population.

### Geometry and unit conversion

Let \(a\) now denote organoid radius; the free-primary symbol \(a\) used only in the preceding equilibrium derivation is not used in the dynamical equations. Let \(n_o\) be organoid count, \(\epsilon\) extracellular volume fraction, \(\rho\) cells per tissue \(\mu\mathrm{m}^3\), \(b_j=ja/n\) shell boundaries, and \(c_j=(b_j+b_{j-1})/2\) shell centers.

\[
\mathcal V_j=\frac{4\pi n_o}{3}(b_j^3-b_{j-1}^3),\quad
v_j=\epsilon\mathcal V_j\,10^{-15}\ {\rm L},\quad
N_j=\rho\mathcal V_j,\quad
\beta_j=\frac{10^9N_j}{N_{\rm Av}v_j}.
\]

\(N_{\rm Av}=6.02214076\times10^{23}\ \mathrm{mol}^{-1}\). Thus \(\beta_j\) converts one molecule per initial cell into nM in the shell's accessible extracellular volume. \(v_b=10^{-6}V_{\rm bath}\) L when `bath_ul` is specified in µL.

For \(n>1\), surface receptor copies vary linearly between core and rim:

\[
q_j=q_{\rm rim}\left[q_{\rm ratio}+
(1-q_{\rm ratio})\frac{j-1}{n-1}\right],\qquad
R_{0j}=\beta_jq_j.
\]

For \(n=1\), the implementation uses \(q_1=q_{\rm rim}q_{\rm ratio}\). The default ratio is 1.

The finite-volume conductance through each shell's outer interface is

\[
G_j=D_{\rm eff}\,3600\,
\frac{4\pi n_ob_j^2\epsilon}{\delta_j}\,10^{-15}\quad({\rm L/h}),
\]

where \(\delta_j=c_{j+1}-c_j\) internally and \(\delta_n=a-c_n\) at the outer boundary. For species \(Z\in\{A,S,C\}\), define \(d_A=d_S=1,\ d_C=\chi_C\), and \(Z_{n+1}=Z_b\).

\[
\Phi_{Zj}=d_ZG_j(Z_{j+1}-Z_j),\quad
\mathcal D_{Zj}=\frac{\Phi_{Zj}-\Phi_{Z,j-1}}{v_j},\quad
\Phi_{Z0}=0.
\]

The sphere center is no-flux. The well-mixed finite bath loses exactly the amount entering the outer shell, so diffusion conserves reagent amounts. \(D_{\rm eff}\) is a lumped effective diffusivity; matrix binding and tortuosity are not estimated separately.

### Reaction network and fluxes

\[
A+S\rightleftharpoons C,\qquad
A+R\rightleftharpoons B,\qquad
S+B\rightleftharpoons T,\qquad
C+R\rightleftharpoons T.
\]

\[
f_{0j}=k^+_SA_jS_j-k^-_SC_j,\quad
f_{1j}=k^+_AA_jR_j-k^-_AB_j,
\]
\[
f_{2j}=k^+_SS_jB_j-k^-_ST_j,\quad
f_{3j}=k^+_AC_jR_j-k^-_AT_j.
\]

\(k^-_A=k^+_AK_A\), \(k^-_S=k^+_SK_S\). On-rates have units nM\(^{-1}\)h\(^{-1}\); off-rates have units h\(^{-1}\). Equal affinities for corresponding edges impose independent binding and close the thermodynamic cycle; this version has no cooperativity parameter.

The optional `solution_binding=False` ablation sets only the association part of \(f_0\) to zero, while preserving soluble-complex dissociation. It is a deliberately nonequilibrium counterfactual for causal isolation, not an alternative physical equilibrium chemistry.

### Extracellular and bath equations

\[
\dot A_j=\mathcal D_{Aj}-f_{0j}-f_{1j},\quad
\dot S_j=\mathcal D_{Sj}-f_{0j}-f_{2j},\quad
\dot C_j=\mathcal D_{Cj}+f_{0j}-f_{3j}.
\]

Between addition events:

\[
\dot A_b=-f_{0b}-\Phi_{An}/v_b,\quad
\dot S_b=-f_{0b}-\Phi_{Sn}/v_b,\quad
\dot C_b=+f_{0b}-\Phi_{Cn}/v_b,
\]

with \(f_{0b}=k^+_SA_bS_b-k^-_SC_b\). The accumulation format retains added reagents; no medium replacement, reagent removal, or nonspecific extracellular conjugate clearance is applied.

### Surface receptor, endosomal recycling, and receptor turnover

Let \(k_R,k_B,k_T\) be internalization rates for unoccupied receptor, primary-bound receptor, and ternary complex; \(k_{\rm rec}\) the intact recycling rate; and \(k_{\rm deg}\) the common endosomal degradation rate. The endosomal species \(U,V,W\) correspond to internalized \(R,B,T\).

\[
\dot R_j=\sigma_j-f_{1j}-f_{3j}-k_RR_j+k_{\rm rec}U_j,
\]
\[
\dot B_j=f_{1j}-f_{2j}-k_BB_j+k_{\rm rec}V_j,\quad
\dot T_j=f_{2j}+f_{3j}-k_TT_j+k_{\rm rec}W_j,
\]
\[
\dot U_j=k_RR_j-(k_{\rm rec}+k_{\rm deg})U_j,\quad
\dot V_j=k_BB_j-(k_{\rm rec}+k_{\rm deg})V_j,\quad
\dot W_j=k_TT_j-(k_{\rm rec}+k_{\rm deg})W_j.
\]

\[
k_{\rm deg}=\ln 2/\tau_R,\qquad
U_{0j}=\frac{k_RR_{0j}}{k_{\rm rec}+k_{\rm deg}},\qquad
\sigma_j=k_{\rm deg}U_{0j}.
\]

This construction starts untreated receptor pools at steady state. Synthesis is constant per initial-cell scaffold after dosing; it is not a fitted transcriptional feedback response.

The parameter \(\tau_R\), named `receptor_half_life_h` in code, is the half-time for degradation of a retained endosomal receptor if recycling were absent. It is **not the measured half-life of the whole cellular receptor pool**. For the unliganded baseline, the pool-normalized degradation flux is

\[
k_{\rm turn,baseline}=
\frac{k_{\rm deg}k_R}{k_{\rm rec}+k_{\rm deg}+k_R}.
\]

\(\ln2/k_{\rm turn,baseline}\) is a flux-derived effective turnover timescale, not generally the single-exponential half-life of a pulse-chase trace. Changing \(\tau_R\) also changes the baseline synthesis rate needed to hold initial surface copies fixed.

### Productive delivery and downstream protein recovery

\[
j_{Pj}=\eta\,d\,k_{\rm deg}W_j/\beta_j,\qquad
\dot P_j=j_{Pj}-k_PP_j,\qquad
\dot J_j=j_{Pj},\qquad
k_P=\ln2/\tau_P.
\]

Here \(d\) is effective payload yield per secondary conjugate, \(\eta\) the fraction becoming productive intracellular payload, \(P\) current productive payload, and \(J\) cumulative productive delivery. Payload-equivalent dose is not confused with conjugate-molecule dose.

\[
\dot Q_j=k_{\rm dam}
\frac{P_j}{P_{50}+P_j}(1-Q_j)-k_{\rm rep}Q_j,\qquad
k_{\rm rep}=\ln2/\tau_Q.
\]

\(Q\in[0,1]\) is generic recoverable damage or functional-protein deficit. \(\tau_Q\) is a downstream protein-recovery half-time, not receptor turnover. This phenomenological module can represent recovery by protein replacement or repair, but it does not claim a named payload's molecular mechanism. Payload mechanism-specific models should replace it rather than merely rename its parameters.

### Cell-state equations and reporter persistence

\[
h_j=h_{\max}\frac{Q_j^m}{Q_{50}^m+Q_j^m},\qquad
\dot L_j=-h_jL_j,\qquad
\dot E_j=h_jL_j-E_j/\tau_m,
\]
\[
\dot D_j=E_j/\tau_m-k_FD_j,\qquad
\dot X_j=k_FD_j,\qquad
\dot H_j=E_j/\tau_m-k_HH_j.
\]

\(L\) is not yet irreversibly committed to death; \(E\) is committed but not yet membrane-permeable; \(D\) is permeabilized, reporter-accessible material; \(X\) is permeabilized material no longer visible to this reporter. \(H\) is a separate release-and-decay reporter proxy. \(L+E+D+X=1\); \(1-L\) is cumulative death commitment and \(D+X\) is cumulative membrane permeabilization.

\(\tau_m\) is a mean waiting time for membrane permeabilization, not a half-life. Default \(k_F=0\): retained reporter-accessible material accumulates monotonically in time. Nonzero \(k_F\) represents optional loss of reportable material; no claim is made that a particular commercial dye has this behavior. Fluorescence saturation alone is monotone and cannot turn a monotone reporter population into a hook.

### Observation equations

Define initial-cell weights \(w_j=N_j/\sum N_j\), optical weights \(o_j\) linearly spaced from \(o_{\rm core}\) to 1, and \(\langle Z\rangle=\sum_jw_jZ_j\). For a one-shell model the optical weight is \(o_{\rm core}\).

\[
u_F(t)=\frac{\sum_jw_jo_jD_j(t)}{\sum_jw_jo_j},\qquad
\boxed{F_{\rm norm}(t)=\frac{(1+\kappa)u_F(t)}{1+\kappa u_F(t)}}.
\]

This normalizes the hypothetical fully permeabilized initial population to 1 with the same optical weighting. Raw instrument units would additionally require empirical background \(F_{\rm bg}\) and gain \(g_F\): \(F_{\rm raw}=F_{\rm bg}+g_FF_{\rm norm}\). Neither background nor gain is estimated or configurable in this version.

\[
Y_{\rm ATP}=\langle(L+E)(1-\zeta Q)\rangle,\quad
Y_{\rm caspase}=\langle E\rangle,\quad
Y_{\rm LDH}=\langle H\rangle.
\]

These are deliberately distinct observation operators. The ATP proxy assumes committed but not yet permeabilized cells retain some metabolic signal; the caspase proxy is a committed-state signal, not a calibrated protease reaction.

\[
Y_{\rm surface}=\langle T/\beta\rangle,\quad
Y_{\rm endosome}=\langle W/\beta\rangle,\quad
Y_{\rm payload}=\langle P\rangle,\quad
Y_{\rm delivered}=\langle J\rangle.
\]

Endosomal complex copies are not themselves a pH-sensitive fluorescence calibration or proof of lysosomal drug release. The distinction between endosomal detection and lysosomal delivery is explicitly discussed in the [published internalization-assay study](https://pmc.ncbi.nlm.nih.gov/articles/PMC4708616/).

### Dosing events and incubation order

Let \(A_{\rm dose},S_{\rm dose}\) be nominal final-well concentrations and \(v_{\rm tot}=v_b+\sum v_j\). Adding \(A\) changes bath concentration by \(A_{\rm dose}v_{\rm tot}/v_b\); adding \(S\) changes it by \(S_{\rm dose}v_{\rm tot}/v_b\). Injection volume is assumed negligible. Soluble concentrations in organoid shells initially equal zero.

Simultaneous addition applies both jumps at \(t=0\). Primary-first applies \(A\) at 0 and \(S\) at \(\Delta\); secondary-first does the reverse. The event is applied without resetting any prior state. Zero delay is exactly simultaneous addition.

For equilibrium-precomplexed addition, compute \(C_0\) with the solution quadratic using the bath doses, then set \((A_b,S_b,C_b)=(A_{\rm bath}-C_0,S_{\rm bath}-C_0,C_0)\) at \(t=0\). This is the equilibrium preincubation limit, not a finite-time precomplexing model. It assumes solution complex can subsequently bind target with the same primary affinity.

All other initial states are zero except \(R=R_0,\ U=U_0,\ L=1\). The browser uses \(\Delta=6\) h and endpoints 24, 48, 72 h from first addition. Python accepts other delays and durations, and `results/sensitivity.json` compares both clocks: fixed endpoint from first addition and fixed combined-reagent exposure after second addition.

## Complete state-variable dictionary

| Code | Symbol | Meaning | Unit |
|---|---|---|---|
| first 3 states | \(A_b,S_b,C_b\) | Free primary, free secondary conjugate, soluble complex in bath | nM |
| `A,S,C` | \(A_j,S_j,C_j\) | Corresponding soluble species in shell \(j\) | nM |
| `R` | \(R_j\) | Unoccupied surface receptor | nM |
| `B` | \(B_j\) | Surface primary–receptor complex | nM |
| `T` | \(T_j\) | Surface primary–secondary–receptor complex | nM |
| `U,V,W` | \(U_j,V_j,W_j\) | Internalized unoccupied, primary-bound, and ternary receptor | nM |
| `P` | \(P_j\) | Current productive intracellular payload | model-equivalent copies/cell |
| `Q` | \(Q_j\) | Recoverable damage / functional-protein deficit | fraction |
| `L` | \(L_j\) | Not irreversibly committed | fraction |
| `E` | \(E_j\) | Committed, not yet permeabilized | fraction |
| `D` | \(D_j\) | Permeabilized and reporter-accessible | fraction |
| `X` | \(X_j\) | Permeabilized but no longer reporter-accessible | fraction |
| `LA` | \(\Lambda_{Aj}\) | Cumulative degraded primary inventory | nM equivalent |
| `LS` | \(\Lambda_{Sj}\) | Cumulative degraded secondary inventory | nM equivalent |
| `J` | \(J_j\) | Cumulative productive payload delivered | model-equivalent copies/cell |
| `H` | \(H_j\) | Release-and-decay / LDH-like reporter | normalized units |

\[
\dot\Lambda_{Aj}=k_{\rm deg}(V_j+W_j),\qquad
\dot\Lambda_{Sj}=k_{\rm deg}W_j.
\]

These two bookkeeping states do not generate biological effects; they close antibody inventory balances.

## Complete parameter dictionary

Every numerical default below is an illustrative assumption. Literature motivates the existence of the process, not the assigned default. Browser trafficking presets and lab overrides are recorded alongside the data.

| Code parameter | Symbol | Default | Unit / interpretation |
|---|---|---:|---|
| `shells` | \(n\) | 3 | Radial shells |
| `radius_um` | \(a\) | 150 | µm |
| `organoids` | \(n_o\) | 20 | Identical spheres in shared bath |
| `bath_ul` | \(V_{\rm bath}\) | 100 | µL |
| `extracellular_fraction` | \(\epsilon\) | 0.2 | Accessible extracellular fraction |
| `cells_per_tissue_um3` | \(\rho\) | 0.0005 | Initial cells/µm³ |
| `copies_per_cell` | \(q_{\rm rim}\) | 100000 | Initial surface copies per rim cell |
| `core_copy_ratio` | \(q_{\rm ratio}\) | 1 | Core/rim copy ratio |
| `diffusion_um2_s` | \(D_{\rm eff}\) | 3 | µm²/s |
| `complex_diffusion_ratio` | \(\chi_C\) | 0.65 | Complex / free-conjugate diffusivity |
| `kon_a` | \(k^+_A\) | 0.36 | nM⁻¹h⁻¹ |
| `kd_a_nm` | \(K_A\) | 1 | nM |
| `kon_s` | \(k^+_S\) | 0.36 | nM⁻¹h⁻¹ |
| `kd_s_nm` | \(K_S\) | 0.3 | nM |
| `solution_binding` | association switch | true | Disables only solution association if false |
| `kint_free` | \(k_R\) | 0.04 | h⁻¹ |
| `kint_primary` | \(k_B\) | 0.12 | h⁻¹ |
| `kint_ternary` | \(k_T\) | 0.12 | h⁻¹ |
| `krecycle` | \(k_{\rm rec}\) | 0.06 | h⁻¹ |
| `receptor_half_life_h` | \(\tau_R\) | 12 | Conditional endosomal degradation half-time, h |
| `payload_yield` | \(d\) | 1 | Model-equivalent payload units per secondary |
| `release_efficiency` | \(\eta\) | 0.2 | Productive release fraction |
| `payload_half_life_h` | \(\tau_P\) | 12 | Intracellular productive payload half-life, h |
| `payload_p50` | \(P_{50}\) | 1000 | Payload copies/cell at half-maximal damage induction |
| `damage_rate_h` | \(k_{\rm dam}\) | 0.15 | h⁻¹ |
| `protein_recovery_half_life_h` | \(\tau_Q\) | 24 | Generic downstream protein-recovery half-time, h |
| `death_rate_h` | \(h_{\max}\) | 0.12 | Maximum commitment hazard, h⁻¹ |
| `damage_half` | \(Q_{50}\) | 0.45 | Half-maximal hazard damage fraction |
| `hill` | \(m\) | 3 | Hazard Hill exponent |
| `membrane_delay_h` | \(\tau_m\) | 6 | Mean commitment-to-permeabilization delay, h |
| `reporter_loss_h` | \(k_F\) | 0 | Loss of accessible reporter material, h⁻¹ |
| `ldh_loss_h` | \(k_H\) | 0.03 | Release-reporter decay, h⁻¹ |
| `optical_core_weight` | \(o_{\rm core}\) | 0.7 | Relative core optical weight |
| `fluorescence_saturation` | \(\kappa\) | 0 | Dimensionless monotonic observation saturation |
| `atp_suppression` | \(\zeta\) | 0.35 | Damage-associated ATP-proxy suppression |

The dosing/API arguments are `primary_nm` (\(A_{\rm dose}\), default 10 nM), `secondary_nm` (\(S_{\rm dose}\), default 1 nM), `duration_h` (\(t_{\rm end}\), default 72 h), `order` (default simultaneous), `delay_h` (\(\Delta\), default 6 h), `p` (parameter object), and `times` (strictly increasing observation times, default 145 equally spaced samples). Numerical solver settings are `rtol=2e-6`, `atol=1e-9`, and LSODA integration with exact restarts at addition events. Absolute tolerance applies to mixed state units and is a numerical control, not an experimental uncertainty.

The browser atlas scans \(q_{\rm rim}=10^4,10^5,10^6\); \(\tau_R=4,24,96\) h; \(S_{\rm dose}=0.1,3,100\) nM; and 13 log-spaced primary doses from 0.01 to 1000 nM. “Slow” trafficking uses \((k_R,k_B,k_T,k_{\rm rec})=(0.01,0.02,0.02,0.02)\) h⁻¹; “recycling” uses \((0.08,0.4,0.4,0.5)\); “retained” uses \((0.04,0.2,0.2,0.02)\). The atlas initial selection is not the package-default kinetic parameter set; the mechanism lab's reference scenario is.

## Inventory, hook definition, and numerical verification

Total primary amount in nM·L is

\[
M_A=v_b(A_b+C_b)+
\sum_jv_j(A_j+C_j+B_j+T_j+V_j+W_j+\Lambda_{Aj}),
\]

and total secondary is

\[
M_S=v_b(S_b+C_b)+
\sum_jv_j(S_j+C_j+T_j+W_j+\Lambda_{Sj}).
\]

Both remain constant between addition events. The tests also check nonnegative states within numerical tolerance, \(L+E+D+X=1\), zero-primary / zero-secondary / zero-target / zero-release controls, zero-delay order equivalence, and tighter solver tolerances.

For a nonnegative response \(Y\) on an increasing primary-dose grid, the descriptive hook depth is

\[
H_{\rm hook}=\max\left(0,1-\frac{Y(A_{\max})}{\max_iY(A_i)}\right).
\]

A normalized-response flag requires an interior sampled peak, peak response at least 0.05, and decline at least 0.10. These are analyst-selected descriptive thresholds, not a significance test or universal assay acceptance criterion. Multiple local extrema can occur; the summary is not a curve fit, EC50, or mechanistic diagnosis. Raw molecule-count outputs and ATP-like viability are not assigned the same normalized hook flag in the browser.

`results/sensitivity.json` records numerical ablation, delay, and spatial-resolution checks. At 10 nM primary / 3 nM secondary / 72 h, the reference fluorescence is approximately 0.9851, 0.9854, and 0.9855 for 3, 6, and 12 shells. In the large/slow-transport stress case the corresponding values are 0.291, 0.389, and 0.260: **that stress case is not spatially converged and must not be used for quantitative transport inference**. The default atlas is an exploratory coarse model; reference-case agreement does not validate every parameter combination.

## Structural uncertainty and empirical calibration

This model can reproduce a hook and a shift with secondary concentration. It cannot establish that either event in a real assay has the same cause. Secondary rescue can reflect altered assembly, availability, uptake, toxicity, or reporter behavior; several combinations can produce similar output curves.

Finite effective 1:1:1 stoichiometry omits real secondary valency, cross-linking, avidity, aggregate-size distributions, and concentration-dependent trafficking. There is no nonspecific conjugate uptake, extracellular cleavage, free-payload killing, bystander transport, growth, changing organoid geometry, or cell-cycle dependence. The receptor/delivery subsystem remains active on a fixed initial-cell scaffold after death commitment; this is a serious late-time limitation, not a claim about dead-cell trafficking.

The minimum identification strategy separates surface copies, unoccupied versus liganded internalization, recycling versus degradation, intracellular productive payload, direct cell-state change, and reporter response. Target-negative and secondary-only observations are particularly important because this version predicts exactly zero target-independent toxicity by construction. A mismatch requires extending the model, not changing the experimental result.

The geometric and turnover mechanisms are motivated by [published spheroid-penetration experiments](https://pmc.ncbi.nlm.nih.gov/articles/PMC2831054/); the assembly mechanism has a direct homogeneous-format precedent in [cell-surface antibody detection](https://pmc.ncbi.nlm.nih.gov/articles/PMC5842027/) and [homogeneous internalization assays](https://pmc.ncbi.nlm.nih.gov/articles/PMC4708616/). These studies do not supply a calibrated parameter set for this simulator.
