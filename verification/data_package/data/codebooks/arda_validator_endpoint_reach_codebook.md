# ARDA validator independence and endpoint reach: construct stress test

## Purpose

The original four-requirement coding permits a narrow endpoint to count as scientific validity when the paper explicitly targets that endpoint. This stress test asks a stricter question: does the measurement validate the paper's primary autonomous-research output claim without redefining the target after seeing the available evaluation?

Apply this codebook only to the eight source-adjudicated joint-positive designs. It is a construct-sensitivity analysis, not a replacement for the first, blind-second, or adjudicated matrices.

## A. Validator separation

Code one level:

- `institutionally_external`: the decisive validity judgment or reference outcome is produced by people, laboratories, data holders, or institutions outside both the generator developers and the evaluating paper's author team.
- `procedurally_separated`: the author team constructs or commissions the reference, but generation cannot adapt to it and the decisive evaluator is blinded, held out, independently reproduced, or otherwise separated by a prespecified procedure.
- `author_internal_or_unclear`: the decisive reference is produced or interpreted by the same author team without adequate blinding, holdout, independent reproduction, or documented separation.

Do not infer institutional externality merely from the word “expert,” “human,” “ground truth,” or “independent.”

## B. Endpoint reach

First state the paper's `primary_output_claim` using the abstract, introduction, or primary results—not the evaluation metric alone. Then code one level:

- `claim_complete`: the reference procedure directly tests the correctness or empirical support of the primary produced proof, hypothesis, mechanism, intervention claim, or research conclusion, including its central failure conditions.
- `claim_dimension`: the procedure directly tests a necessary and scientifically meaningful dimension of the primary output, but leaves another central part untested (for example, reproduction without substantive conclusion validity, one hypothesis among a broader report, or predictive transfer without the claimed explanation).
- `task_proxy`: the endpoint is chiefly benchmark score, rubric performance, component execution, similarity, compilation, selector agreement, or another task outcome that does not validate the primary scientific claim.

The coder must not turn a benchmark metric into a `claim_complete` endpoint by restating the paper's target as “performance on this metric.” The primary output claim is fixed before endpoint classification.

## Stress-test conjunctions

- `procedural_claim_identification=yes` iff original R1 and R2 remain `yes`, validator separation is either `institutionally_external` or `procedurally_separated`, and endpoint reach is `claim_complete`.
- `external_claim_identification=yes` iff original R1 and R2 remain `yes`, validator separation is `institutionally_external`, and endpoint reach is `claim_complete`.

Report both. Neither count is field prevalence, and neither may replace the three original coding matrices without showing all results together.

## Required output

- `paper_id`, `short_name`
- `primary_output_claim`
- `validator_separation`, `validator_anchor`, `validator_rationale`
- `endpoint_reach`, `endpoint_anchor`, `endpoint_rationale`
- `coder`
