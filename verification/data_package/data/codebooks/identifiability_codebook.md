# Identifiability coding rules

Version: 2026-08-26. Unit: one paper, using one prespecified primary quantitative target per paper. The target is the earliest or broadest target that bears directly on autonomous-research reliability, selection, or scientific validity; a favorable secondary target cannot replace it after outcomes are known.

## Allowed values

Criterion cells use `yes`, `partial`, or `no`. `Partial` is not counted in strict coverage. Missing evidence is coded `no`, not inferred from silence. Every row must contain a source anchor and a prose reason for its joint status.

## C1. Complete initial denominator

- `yes`: the paper or a version-matched public artifact reports every unit entering the named target before outcome-dependent filtering, including no-output and execution-failure states.
- `partial`: an upstream count exists but cannot be linked to the target population, or the public and paper versions differ such that completeness cannot be established.
- `no`: only selected, successful, recommended, interesting, or completed units are enumerated.

The denominator can be a curated benchmark; completeness does not imply population representativeness.

## C2. Same-standard evaluation of all units or a probability sample

- `yes`: every initial unit receives the same stated outcome rule, or a prespecified probability sample receives that rule with known inclusion probabilities.
- `partial`: the rule covers a selected subset, mixes incomparable rules without a common endpoint, or covers a calibration subset only.
- `no`: final or expert evaluation is restricted to recommended, successful, interesting, available, or otherwise outcome-selected units.

Automatic task metrics can satisfy C2 even when they do not establish scientific validity; that distinction is coded in C4.

## C3. External or independent validator

- `yes`: the decisive outcome is assigned by evaluators institutionally independent of the system-producing team, or by an external physical/formal reference process not constructed from the system's own judgments.
- `partial`: a mixed internal/external panel is used, external validation covers only a subset, or independence is unclear.
- `no`: the generating team, its model judge, its benchmark stack, or its automated reviewer supplies the decisive outcome.

An executable author-designed task metric is reproducible but not independent under this rule. Formal proof checking or direct physical measurement may qualify when the checker/measurement is external to the generated claim and determines the outcome without author judgment.

## C4. Validation targets scientific validity rather than a proxy

- `yes`: the outcome asks whether the scientific or mathematical claim, result, mechanism, numerical conclusion, novelty, or integrity property is valid.
- `partial`: the outcome measures a scientific-reasoning process or one component of validity but not the final claim.
- `no`: the outcome is paper completion, formatting, reviewer score, benchmark improvement, task completion, or another proxy that can succeed while the scientific claim remains invalid.

## C5. Joint identification

`yes` if and only if C1=C2=C3=C4=`yes`; otherwise `no`. `Partial` is never promoted in the strict joint count.

`validated_initial_units_n` is recorded only for C5=`yes` and equals the number of initial units receiving the joint all-unit independent scientific-validity assessment. It is not the number of validators, votes, stages, or selected outputs.

## Borderline examples frozen before evidence-set expansion

- A complete benchmark with host metrics: C1=`yes`, C2=`yes`, C3=`no`, C4=`no` if the metric is a task proxy.
- Full-corpus machine process annotations calibrated on a human subset: C1=`yes`, C2=`yes`, C3=`no`, C4=`partial`.
- Expert review of author-interest-selected recommendations: C1=`no`, C2=`no`, C3=`partial`, C4=`yes`.
- Independent reproduction team attempts every planned idea and inspects every executable paper: all four criteria can be `yes`.
- Expert panel judges every generated proof attempt, including no-output states: all four criteria can be `yes`; post-deadline generation must still be disclosed as a temporal boundary.

## Expansion rule

Newly included studies are appended and coded under these frozen rules. Existing cell values may change only if a source error is found or a rule is explicitly versioned; they must not change merely to preserve the current `2/12` result.
