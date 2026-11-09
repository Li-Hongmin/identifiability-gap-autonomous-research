# Cross-benchmark rankability audit codebook

Version: 2026-08-26. Search boundary: autonomous-research and scientific-agent comparative evaluations available by 26 August 2026. This is an endpoint-specific, purposive design audit, not a probability sample of leaderboards.

## Frame and chronology

The paper-level census frame contains all 44 unique primary papers already admitted to the Autonomous Research Denominator Atlas (ARDA), plus one separately flagged current-update paper, DeltaML-Bench. Thus `data/derived/rankability_audit_screening.csv` contains 45 unique paper records: 15 inclusions and 30 exclusions with a paper-specific reason.

The chronology matters. ARDA and its 44-paper frame were constructed before the cross-benchmark rankability extension. Every ARDA paper was then screened under the rules below. DeltaML-Bench was added by one targeted current-update search because it supplies a fixed-budget complete-run comparison; it is not silently treated as part of the original ARDA frame. For each admitted evaluation, the endpoint, common configuration panel, source display, and denominator-aware target were recorded in `rankability_audit_inputs.csv` before the aggregation script computed pair statuses. The audit was not preregistered, so its totals remain descriptive.

## Decision target and eligibility

The audit asks whether a strict pairwise order displayed by a source evaluation is supported for the corresponding single-attempt or all-initiated-unit endpoint. It does not compare endpoint magnitudes across evaluations.

An evaluation enters the quantitative audit only when it has:

1. at least three configured systems evaluated on a common task frame;
2. a common bounded scalar endpoint and a recoverable displayed system comparison;
3. a recoverable initiated denominator; and
4. either all-initiated-unit outcomes or enough information to form a sharp missing-outcome set under the stated endpoint model.

When a paper reported several candidate endpoints, selection followed this hierarchy: use the source's explicit common scalar system comparison on the widest compatible task panel; when the source contrasted a selected or best-of-*k* display with disclosed all-run outcomes, retain that contrast; otherwise use the narrowest bounded endpoint that is exactly recoverable for all configurations. No endpoint is relabelled as latent scientific truth. Exclusions include fewer than three configurations, incompatible task frames, selected corpora without an initiated denominator, and tables whose all-run comparison is not computable.

## Objects and decision rules

For system $i$, the source-displayed score has interval $D_i=[d_i^L,d_i^U]$, and the denominator-aware target has identified set $I_i=[L_i,U_i]$. Count-derived rates are exact finite-design proportions. Closed intervals propagate source rounding or missing bounded outcomes; they are identified sets, not confidence intervals.

For $m$ configurations, define the directed strict-edge sets

\[
E_D=\{(i,j):d_i^L>d_j^U\},\qquad
E_I=\{(i,j):L_i>U_j\}.
\]

A displayed strict edge is:

- `certified` when $E_I$ contains the same directed edge;
- `reversed` when $E_I$ contains the opposite directed edge;
- `unresolved` when the target sets overlap;
- `displayed_not_strict` when the displayed intervals tie or overlap; or
- `no_display` when at least one configuration lacks a selected display.

The **rankability ratio** is

\[
\rho=\frac{|E_I|}{\binom m2},
\]

the fraction of all unordered configuration pairs for which the denominator-aware endpoint identifies a strict order. Ties remain unordered.

The **rankability gap** is defined only over strict claims the display makes:

\[
G_R=1-\frac{|E_D\cap E_I|}{|E_D|},
\]

where the intersection requires the same direction. Thus reversals and unresolved displayed edges both contribute to the gap. $G_R$ is undefined when $E_D$ is empty.

## Observation-design groups

The 15 admitted evaluations contain 100 configurations and 376 unordered within-evaluation pairs.

- `selected_output`: MLReplicate, ScienceAgentBench, ScientistOne, and BadScientist rate-matched review. Their displayed score selects runs or leaves bounded initiated outcomes missing. BadScientist has one unknown initiated outcome for each of two strategies; those outcomes remain in $[0,1]$.
- `all_unit_control`: DeltaML-Bench `4@6h`, MLAgentBench, SpatialBench-Long, SciIntegrity-Bench, Corral, Lab-in-the-loop Sonnet 4.6, DiscoveryWorld, HLER ablation, InquiTree, LMR-Bench, and Distributed Denial of Science. These are positive controls: for a complete-run evaluation, display and target intervals coincide and strict-edge retention follows by construction. Corral is the sole near-complete case: GPT-OSS/ReAct has 89 successes among 1,722 released records from 1,725 intended trials, so its target is $[89/1725,92/1725]$.

The selected/missing-output group contains 145 possible pairs. It identifies 127 strict target relations; among 134 displayed strict relations, 119 are certified in the same direction, six reverse, and nine are unresolved, giving the pair-weighted descriptive gap 15/134 = 11.2%. The all-run/near-complete group contains 231 possible pairs; all 214 displayed strict relations are certified, while 17 tied or rounding-overlapping pairs remain non-strict. Across all audits, 333 of 348 displayed strict relations are certified, six reverse, and nine remain unresolved. These totals are pair-weighted coverage summaries, not independent observations or field prevalence.

## Evaluation-specific boundaries

- MLReplicate targets mean normalized external-human overall score per source-configured attempt. Its six systems share eight target papers but not fixed compute; all 15 denominator-aware pair orders are unresolved, while the selected observations make six strict claims among four reviewed systems.
- ScienceAgentBench compares the selected lexicographic best of three runs in Table 3 with the all-run mean disclosed in Appendix E.1. Framework costs differ, so this is a source-configuration comparison.
- ScientistOne uses ScholarPeer paper scores. One-decimal values on the 1--10 scale are represented by closed half-unit-in-the-last-reported-digit intervals after normalization.
- DeltaML-Bench is restricted to the common four-runs-at-six-hours allocation on one H100.
- MLAgentBench, SpatialBench-Long, DiscoveryWorld, LMR-Bench, and Corral use executable benchmark or task-evaluator endpoints, not complete scientific validity.
- SciIntegrity-Bench uses the exact non-`Fail` rate. `Flawed` outcomes count as passing this deliberately narrow endpoint.
- BadScientist and Distributed Denial of Science use adversarial susceptibility endpoints; a larger value is not greater scientific capability.
- HLER configurations include different human gates and therefore are policy configurations, not autonomous-model comparisons.
- Lab-in-the-loop, ScientistOne, and InquiTree propagate published rounding intervals rather than inventing unreported precision.

Every result is configuration-, endpoint-, and budget-specific. Pair decisions within an evaluation share systems and tasks and are statistically dependent. The pair-weighted summaries are useful for comparing admitted observation designs, but they do not estimate how often rankability fails in the field.
