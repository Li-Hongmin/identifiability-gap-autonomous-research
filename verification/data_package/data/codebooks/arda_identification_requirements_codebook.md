# ARDA joint-identification requirements: blind second-coding manual

## Purpose and unit

The unit is one paper-level empirical design and its primary quantitative target as listed in the blind task. Code only what the paper and directly linked public artifacts establish. Do not infer a positive label from system reputation, paper conclusions, or the existence of a final artifact.

The four requirements are separately coded `yes`, `partial`, or `no`. `partial` never satisfies the strict conjunction. Record a concise source-grounded rationale and an exact section, table, figure, appendix, or public-artifact anchor for every requirement.

## R1. Complete initial denominator

Question: Is the full number of initiated units for the target design known, with failed, stopped, no-output, and excluded units accounted for?

- `yes`: all initiated units are enumerated or their total is exactly reconstructable; exclusions and no-output/failure states remain accounted for.
- `partial`: the planned denominator or a major subgroup denominator is known, but realized initiation, exclusions, retries, seeds, or failures are incompletely reconciled.
- `no`: only selected successes, completed outputs, recommendations, or an otherwise outcome-conditioned subset is visible; the initial denominator cannot be recovered.

Do not require a probability sample here. A complete purposive finite design can receive `yes`.

## R2. Same-standard all-unit or probability-sample validation

Question: Is the target endpoint measured under the same stated reference procedure for every initiated unit, or for a prespecified probability sample with known inclusion?

- `yes`: every initiated unit receives the same endpoint rule, including prespecified values for no-output/failure, or a genuine probability sample is assessed under one rule.
- `partial`: assessment covers a large or structured subset but conditions on completion/valid output, changes standards across units, leaves some initiated units without endpoint accounting, or uses a non-probability subset whose missing outcomes remain material.
- `no`: validation is limited to selected, recommended, interesting, successful, or showcased artifacts without probability sampling.

Automated assessment may satisfy coverage even if it fails R3 or R4.

## R3. External or sufficiently independent validator

Question: Is the reference procedure institutionally or procedurally separated from generation and selection enough to serve as an independent validity measurement for the target?

- `yes`: external evaluators, independent expert teams, held-out real-world adjudication, or a prespecified reference process not produced or tuned by the generator/selector assesses the units; the relevant endpoint is not merely the system's own score.
- `partial`: human or expert checking exists but is author-selected, available only for a subset, lacks clear blinding/separation, or combines independent and internal components.
- `no`: validity is assigned only by the generating system, its internal agents, author-designed proxy/judge without independent calibration, or the same downstream signal used for search/selection.

Executable tests can be independent for a narrow task endpoint, but an author-built simulated benchmark is not automatically independent scientific adjudication.

## R4. Scientific-validity endpoint

Question: Does the measured endpoint target whether the produced research claim, proof, mechanism, empirical result, or scientific artifact is substantively valid?

- `yes`: proof correctness, independent empirical support, correct scientific mechanism, executable manuscript with sound reported results, or another explicit scientific-validity endpoint.
- `partial`: one important validity dimension is measured (for example numerical soundness, paper-code consistency, similarity/non-copying, or support of one hypothesis) but not the full claimed scientific result, or proxy and validity components are mixed.
- `no`: the endpoint is task score, compilation, completion, automated acceptance, selector agreement, benchmark integrity behavior, stylistic quality, or another proxy that does not establish scientific validity.

An endpoint may be narrow and still receive `yes` if the target is explicitly that narrow scientific claim. Explain the boundary.

## Strict joint status and validated units

`joint_identification=yes` if and only if R1=R2=R3=R4=`yes`; otherwise `no`.

For a joint-positive paper, record `validated_initial_units_n`: the number of initiated units receiving the jointly identifying design. Leave it blank for joint-negative papers. Do not sum repeated evaluations when the empirical unit is the initiated research problem or idea.

## Required output columns

- `paper_id`, `short_name`
- `complete_initial_denominator`, `complete_initial_denominator_rationale`, `complete_initial_denominator_anchor`
- `same_standard_validation`, `same_standard_validation_rationale`, `same_standard_validation_anchor`
- `independent_validator`, `independent_validator_rationale`, `independent_validator_anchor`
- `scientific_validity_endpoint`, `scientific_validity_endpoint_rationale`, `scientific_validity_endpoint_anchor`
- `joint_identification`, `validated_initial_units_n`
- `coder`

## Independence rule

The blind task files omit first-round labels and joint-status rationales. Coders must not open `data/derived/study_identifiability_matrix.csv`, `data/derived/identifiability_summary.csv`, the manuscript's ARDA coverage counts, or another coder's output until their partition is complete.
