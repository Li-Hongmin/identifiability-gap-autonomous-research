#!/usr/bin/env python3
"""Build finite-design identification sets and a selected-score rankability case.

The outputs deliberately separate three objects:

1. whether each frozen ARDA estimand can inform the target reliability estimand;
2. study-specific bounds on an adjudicated valid-artifact endpoint; and
3. a common-design rankability analysis for MLReplicate's selected human scores.

The bounds are plug-in identified sets for the released finite designs. They are
not confidence intervals and do not transport to an unspecified task population.
"""

from __future__ import annotations

import csv
import itertools
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data" / "derived"
CROSSWALK = DERIVED / "estimand_crosswalk.csv"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"refusing to write empty table: {path}")
    fields = list(rows[0])
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def write_mlreplicate_rankability_certificate(
    bounds: list[dict[str, object]], edges: list[dict[str, object]]
) -> None:
    """Write the paper's proposed comparative-evaluation output for one public case."""
    certificate = {
        "schema": "rankability-certificate/0.1",
        "study": "MLReplicate",
        "source_anchor": "arXiv:2605.16616v1 Figures 2--3",
        "target": {
            "task_frame": "the same eight source papers for each of six configured systems",
            "endpoint": "mean normalized external-human overall score per targeted attempt",
            "score_range": [0, 1],
            "policy_budget_compatibility": "systems target the same papers and endpoint, but models, implementations, and resource use differ; comparisons concern evaluated configurations only",
        },
        "observation_process": {
            "initiated_units": 48,
            "initiated_units_per_system": 8,
            "failure_and_no_output_rule": "failed experiments receive score zero; completed but unreviewed manuscripts remain in [0,1]",
            "selection_rule": "minimum-page screen followed by three-model automated acceptance",
            "evaluation_rule": "three external human scores only for the ten automated acceptances",
            "evaluation_probability": "not a probability sample; inclusion depends on the selection pipeline",
            "validator_calibration": "not identified for latent scientific truth; certificate targets the reported human-review endpoint",
        },
        "selected_only_order": {
            "systems_with_selected_human_observations": ["CR", "AL", "TS", "AIR"],
            "order": ["CR", "AL", "TS", "AIR"],
            "missing_score_sensitivity": "the single missing AL score cannot change this selected-only order",
        },
        "identified_sets": [
            {
                "system_code": row["system_code"],
                "system": row["system"],
                "lower": float(row["identified_lower"]),
                "upper": float(row["identified_upper"]),
            }
            for row in bounds
        ],
        "pairwise_relations": edges,
        "certified_directed_edges": [
            row["relation"] for row in edges if row["strict_order_identified"] == "yes"
        ],
        "summary": {
            "possible_unordered_pairs": len(edges),
            "identified_strict_orders": sum(
                row["strict_order_identified"] == "yes" for row in edges
            ),
            "leaderboard_status": "unsupported as a total order under assumption-free missing-score bounds",
            "certification_qualification": "complete-run retention is an algebraic control rather than independent evidence of scientific validity; certified orders hold only for the realized endpoint (which may be a proxy); finite-sample strict orders may be practically small or statistically uncertain",
        },
        "certification_qualification": "complete-run retention is an algebraic control rather than independent evidence of scientific validity; certified orders hold only for the realized endpoint (which may be a proxy); finite-sample strict orders may be practically small or statistically uncertain",
    }
    path = DERIVED / "mlreplicate_rankability_certificate.json"
    path.write_text(json.dumps(certificate, indent=2) + "\n", encoding="utf-8")


def f6(value: float | None) -> str:
    return "" if value is None else f"{value:.6f}"


def build_estimand_computability(crosswalk: list[dict[str, str]]) -> list[dict[str, object]]:
    roles: dict[str, tuple[str, str, str, str]] = {
        "ALETHEIA_SELECTION_MAJ": (
            "selection-amplification component",
            "companion all-attempt outcome required",
            "ALETHEIA_MAJORITY_VALID_PROOF",
            "The attributable fraction is not itself per-attempt reliability; ALETHEIA_ATTEMPT supplies the all-attempt expert endpoint.",
        ),
        "ALETHEIA_SELECTION_STRICT": (
            "selection-amplification component",
            "companion all-attempt outcome required",
            "ALETHEIA_STRICT_VALID_PROOF",
            "This sensitivity definition changes the validity rule but is not itself a reliability rate.",
        ),
        "ALETHEIA_ATTEMPT": (
            "direct all-attempt adjudicated validity",
            "point identified on the realized challenge set",
            "ALETHEIA_MAJORITY_VALID_PROOF;ALETHEIA_STRICT_VALID_PROOF",
            "All 20 attempts, including no-output states, receive the stated expert validity rule.",
        ),
        "AISCIENTIST_PIPELINE": (
            "artifact-completion upper-bound component",
            "partial: completion only",
            "AISCIENTIST_VALID_COMPILABLE_ARTIFACT",
            "A non-compilable attempt cannot produce the target artifact, but completed papers lack all-unit independent scientific validity labels.",
        ),
        "BEEL_EXECUTION": (
            "artifact-completion component",
            "point identified with companion validity row",
            "BEEL_NUMERICALLY_SOUND_MANUSCRIPT",
            "Seven of 12 initiated ideas produce manuscripts; BEEL_NUMERIC_DEFECT supplies the nested all-manuscript validity count.",
        ),
        "BEEL_NUMERIC_DEFECT": (
            "completed-artifact adjudicated validity component",
            "point identified with companion completion row",
            "BEEL_NUMERICALLY_SOUND_MANUSCRIPT",
            "All seven generated manuscripts receive the independent numerical-validity check.",
        ),
        "KOSMOS_NOT_SUPPORTED": (
            "direct all-unit adjudicated validity",
            "point identified on the three stated problems",
            "KOSMOS_CLEARLY_SUPPORTED_HYPOTHESIS",
            "All three stated evaluation problems receive the same independent empirical audit.",
        ),
        "FOURATTEMPTS_FAILURE": (
            "artifact-completion upper-bound component",
            "partial: selected external review only",
            "FOURATTEMPTS_VALID_ARTIFACT",
            "Only the one completed manuscript reaches external review; failure states have no qualifying artifact.",
        ),
        "PLAGIARISM_VERIFIED": (
            "selected validity-dimension component",
            "partial: 18 of 50 source-author rated",
            "AI_PAPER_PASSES_SIMILARITY_CHECK",
            "The 32 documents without source-author ratings retain unknown outcomes under the same standard.",
        ),
        "SCICOQA_MISSED_REAL": (
            "validator sensitivity component",
            "insufficient for truth correction",
            "",
            "The 43/92 recall identifies sensitivity on ascertained positives, not specificity or transport to autonomous-research artifacts.",
        ),
    }

    output: list[dict[str, object]] = []
    for row in crosswalk:
        result_id = row["result_id"]
        if result_id in roles:
            role, status, target_id, reason = roles[result_id]
        else:
            role = "distinct mechanism, proxy, or intervention estimand"
            status = "not a per-attempt scientific-reliability bound"
            target_id = ""
            reason = (
                "This row answers its source-bounded estimand but does not jointly expose completion, "
                "selection, and adjudicated scientific validity for a common initiated-attempt target."
            )
        output.append(
            {
                "result_id": result_id,
                "study_id": row["study_id"],
                "estimand_family": row["estimand_family"],
                "theta_role": role,
                "bound_computability": status,
                "derived_target_id": target_id,
                "source_anchor": row["source_anchor"],
                "reason": reason,
            }
        )
    if len(output) != 54 or len({row["result_id"] for row in output}) != 54:
        raise ValueError("computability ledger must classify all 54 frozen ARDA estimands exactly once")
    return output


def capability_row(
    *,
    target_id: str,
    paper_id: str,
    short_name: str,
    endpoint: str,
    endpoint_class: str,
    initial_n: int,
    completed_n: int,
    selected_n: int | None,
    adjudicated_valid_n: int | None,
    lower: float,
    upper: float,
    label_as_truth_lower: float | None,
    status: str,
    validator_status: str,
    source_anchor: str,
    key_boundary: str,
) -> dict[str, object]:
    if not (0 <= completed_n <= initial_n and 0 <= lower <= upper <= 1):
        raise ValueError(f"invalid identification row: {target_id}")
    c = completed_n / initial_n
    s = None if selected_n is None or completed_n == 0 else selected_n / completed_n
    v_s = None if adjudicated_valid_n is None or not selected_n else adjudicated_valid_n / selected_n
    return {
        "target_id": target_id,
        "paper_id": paper_id,
        "short_name": short_name,
        "endpoint": endpoint,
        "endpoint_class": endpoint_class,
        "initial_n": initial_n,
        "completed_or_outcome_accounted_n": completed_n,
        "selected_same_standard_n": "" if selected_n is None else selected_n,
        "adjudicated_valid_n": "" if adjudicated_valid_n is None else adjudicated_valid_n,
        "c": f6(c),
        "s": f6(s),
        "v_s": f6(v_s),
        "identified_lower": f6(lower),
        "identified_upper": f6(upper),
        "identified_width": f6(upper - lower),
        "label_as_truth_lower": f6(label_as_truth_lower),
        "identification_status": status,
        "validator_status": validator_status,
        "population_transport": "not identified beyond the stated finite or curated study target",
        "comparison_stratum": target_id,
        "source_anchor": source_anchor,
        "key_boundary": key_boundary,
    }


def build_capability_bounds(crosswalk: list[dict[str, str]]) -> list[dict[str, object]]:
    by_id = {row["result_id"]: row for row in crosswalk}
    assert int(by_id["AISCIENTIST_PIPELINE"]["denominator_n"]) == 616
    assert int(by_id["AISCIENTIST_PIPELINE"]["numerator_n"]) == 326
    assert int(by_id["BEEL_EXECUTION"]["numerator_n"]) == 5
    assert int(by_id["BEEL_NUMERIC_DEFECT"]["numerator_n"]) == 4
    assert int(by_id["ALETHEIA_ATTEMPT"]["numerator_n"]) == 11
    assert int(by_id["KOSMOS_NOT_SUPPORTED"]["numerator_n"]) == 2
    assert int(by_id["FOURATTEMPTS_FAILURE"]["numerator_n"]) == 3
    assert int(by_id["PLAGIARISM_VERIFIED"]["numerator_n"]) == 12

    return [
        capability_row(
            target_id="AISCIENTIST_VALID_COMPILABLE_ARTIFACT",
            paper_id="arXiv:2408.06292v3",
            short_name="AI Scientist v1",
            endpoint="independently valid compilable manuscript per generated idea",
            endpoint_class="scientific-validity upper bound from completion",
            initial_n=616,
            completed_n=290,
            selected_n=None,
            adjudicated_valid_n=None,
            lower=0,
            upper=290 / 616,
            label_as_truth_lower=None,
            status="completion-only partial identification",
            validator_status="no all-paper independent scientific validity assessment",
            source_anchor="arXiv:2408.06292v3 Tables 3--5",
            key_boundary="Paper completion is necessary but not sufficient for scientific validity.",
        ),
        capability_row(
            target_id="BEEL_NUMERICALLY_SOUND_MANUSCRIPT",
            paper_id="arXiv:2502.14297v3",
            short_name="Independent AI Scientist evaluation",
            endpoint="executable manuscript without an incorrect or hallucinated numerical result per planned idea",
            endpoint_class="independently adjudicated validity dimension",
            initial_n=12,
            completed_n=7,
            selected_n=7,
            adjudicated_valid_n=3,
            lower=3 / 12,
            upper=3 / 12,
            label_as_truth_lower=3 / 12,
            status="point identified on the realized 12-idea set",
            validator_status="independent evaluator team; all completed manuscripts inspected",
            source_anchor="arXiv:2502.14297v3 Sections 2.3--2.5",
            key_boundary="The endpoint is numerical soundness, not every dimension of scientific quality.",
        ),
        capability_row(
            target_id="ALETHEIA_MAJORITY_VALID_PROOF",
            paper_id="arXiv:2602.21201v3",
            short_name="Aletheia FirstProof (majority)",
            endpoint="majority-valid proof per problem-agent attempt, with no-output retained",
            endpoint_class="expert-adjudicated scientific validity",
            initial_n=20,
            completed_n=20,
            selected_n=20,
            adjudicated_valid_n=9,
            lower=9 / 20,
            upper=9 / 20,
            label_as_truth_lower=9 / 20,
            status="point identified on the current 20-attempt matrix",
            validator_status="expert panel including external specialists",
            source_anchor="arXiv:2602.21201v3 Tables 1--3",
            key_boundary="Three Agent-B outputs are post-deadline ablations; ten problems are not a population sample.",
        ),
        capability_row(
            target_id="ALETHEIA_STRICT_VALID_PROOF",
            paper_id="arXiv:2602.21201v3",
            short_name="Aletheia FirstProof (strict)",
            endpoint="strict-valid proof per problem-agent attempt, with disputed problem 8 treated invalid",
            endpoint_class="expert-adjudicated sensitivity endpoint",
            initial_n=20,
            completed_n=20,
            selected_n=20,
            adjudicated_valid_n=8,
            lower=8 / 20,
            upper=8 / 20,
            label_as_truth_lower=8 / 20,
            status="point identified under the strict rule on the current matrix",
            validator_status="strict sensitivity rule over the expert table",
            source_anchor="arXiv:2602.21201v3 Tables 1--3",
            key_boundary="This is a definition sensitivity, not an additional independent sample.",
        ),
        capability_row(
            target_id="KOSMOS_CLEARLY_SUPPORTED_HYPOTHESIS",
            paper_id="arXiv:2511.13825v1",
            short_name="KOSMOS independent evaluation",
            endpoint="clearly supported hypothesis per stated radiobiology problem",
            endpoint_class="independently adjudicated scientific validity",
            initial_n=3,
            completed_n=3,
            selected_n=3,
            adjudicated_valid_n=1,
            lower=1 / 3,
            upper=1 / 3,
            label_as_truth_lower=1 / 3,
            status="point identified on the three stated problems",
            validator_status="independent evaluator authors using empirical null models",
            source_anchor="arXiv:2511.13825v1 Abstract and Sections 2--5",
            key_boundary="The three retrospective problems are narrow and not sampled from a declared task distribution.",
        ),
        capability_row(
            target_id="FOURATTEMPTS_VALID_ARTIFACT",
            paper_id="arXiv:2601.03315v1",
            short_name="Four autonomous research attempts",
            endpoint="scientifically valid completed artifact per full-pipeline idea",
            endpoint_class="scientific-validity upper bound from completion",
            initial_n=4,
            completed_n=1,
            selected_n=1,
            adjudicated_valid_n=None,
            lower=0,
            upper=1 / 4,
            label_as_truth_lower=None,
            status="partial: one completed artifact, no same-standard terminal validity for all ideas",
            validator_status="external review covers only the completed and submitted manuscript",
            source_anchor="arXiv:2601.03315v1 Table 1; Sections 3 and 6",
            key_boundary="The four ideas were themselves selected after feasibility review; publication is a proxy for truth.",
        ),
        capability_row(
            target_id="FAR_CORRECT_RESOLUTION",
            paper_id="arXiv:2608.16977v1",
            short_name="FAR",
            endpoint="correct resolution per attempted conjecture",
            endpoint_class="selected author-label plus completion upper bound",
            initial_n=4717,
            completed_n=1050,
            selected_n=15,
            adjudicated_valid_n=15,
            lower=0,
            upper=1050 / 4717,
            label_as_truth_lower=15 / 4717,
            status="partial: unselected resolutions unknown and author validator uncalibrated",
            validator_status="15 author-interest-selected artifacts reviewed by the author team",
            source_anchor="arXiv:2608.16977v1 Sections 4--5; Figure 3",
            key_boundary="Treating all 15 author labels as truth raises only the lower endpoint to 15/4717; it does not validate the other 1,035 claimed resolutions.",
        ),
        capability_row(
            target_id="MLREPLICATE_VALID_MANUSCRIPT",
            paper_id="arXiv:2605.16616v1",
            short_name="MLReplicate aggregate",
            endpoint="scientifically valid manuscript per targeted system-paper attempt",
            endpoint_class="scientific-validity upper bound from generation",
            initial_n=48,
            completed_n=45,
            selected_n=10,
            adjudicated_valid_n=None,
            lower=0,
            upper=45 / 48,
            label_as_truth_lower=None,
            status="partial: external human review is automated-acceptance selected",
            validator_status="10 automated acceptances receive human review; experiments are not independently validated",
            source_anchor="arXiv:2605.16616v1 Figures 2--4",
            key_boundary="Human scores are selected paper-quality outcomes, not binary scientific ground truth for all 48 attempts.",
        ),
        capability_row(
            target_id="AI_PAPER_PASSES_SIMILARITY_CHECK",
            paper_id="arXiv:2502.16487v3",
            short_name="AI-paper similarity",
            endpoint="document not rated high-similarity by a source-paper author",
            endpoint_class="selected adjudicated validity dimension",
            initial_n=50,
            completed_n=50,
            selected_n=18,
            adjudicated_valid_n=6,
            lower=6 / 50,
            upper=(6 + 32) / 50,
            label_as_truth_lower=6 / 50,
            status="sharp worst-case bounds for one validity dimension",
            validator_status="source-paper author ratings for a non-probability subset",
            source_anchor="arXiv:2502.16487v3 Sections 3 and 5; public workbook",
            key_boundary="Passing this similarity check is not full scientific validity; 32 documents lack the same-standard rating.",
        ),
    ]


MLREPLICATE_SCORES = [
    # Figure 2 contains one explicitly missing third human score for AL-P2.
    ("AL", "P5", 3, 2, 2),
    ("AL", "P4", 1, 2, 2),
    ("AL", "P2", 3, 4, None),
    ("AL", "P6", 1, 2, 3),
    ("AL", "P3", 3, 1, 3),
    ("AIR", "P5", 1, 1, 1),
    ("CR", "P3", 4, 3, 4),
    ("CR", "P7", 3, 3, 3),
    ("TS", "P8", 1, 1, 2),
    ("TS", "P1", 1, 1, 3),
]

MLREPLICATE_SYSTEMS = {
    "AIS1": ("AI Scientist v1", 8, 0),
    "AIS2": ("AI Scientist v2", 8, 0),
    "AL": ("Agent Laboratory", 7, 5),
    "AIR": ("AI Researcher", 7, 1),
    "CR": ("CycleResearcher", 7, 2),
    "TS": ("Tiny Scientist", 8, 2),
}


def build_mlreplicate_scores() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for system_code, paper_code, *scores in MLREPLICATE_SCORES:
        for reviewer_index, score in enumerate(scores, start=1):
            rows.append(
                {
                    "system_code": system_code,
                    "system": MLREPLICATE_SYSTEMS[system_code][0],
                    "paper_code": paper_code,
                    "reviewer": f"R{reviewer_index}",
                    "score_1_to_6": "" if score is None else score,
                    "normalized_score_0_to_1": "" if score is None else f6((score - 1) / 5),
                    "score_status": "missing in source figure" if score is None else "observed",
                    "source_anchor": "arXiv:2605.16616v1 Figure 2",
                }
            )
    if len(rows) != 30 or sum(row["score_status"] == "observed" for row in rows) != 29:
        raise ValueError("expected 29 observed and one missing MLReplicate human score")
    return rows


def build_mlreplicate_rankability(
    score_rows: list[dict[str, object]],
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    bounds: list[dict[str, object]] = []
    for system_code, (system, generated_n, selected_papers_n) in MLREPLICATE_SYSTEMS.items():
        observed = [
            float(row["normalized_score_0_to_1"])
            for row in score_rows
            if row["system_code"] == system_code and row["score_status"] == "observed"
        ]
        expected_reviews_n = 8 * 3
        completed_review_slots_n = generated_n * 3
        unknown_completed_reviews_n = completed_review_slots_n - len(observed)
        if unknown_completed_reviews_n < 0:
            raise ValueError(f"more observed scores than completed slots for {system_code}")
        observed_sum = sum(observed)
        lower = observed_sum / expected_reviews_n
        upper = (observed_sum + unknown_completed_reviews_n) / expected_reviews_n
        selected_mean = None if not observed else observed_sum / len(observed)
        selected_slots_n = selected_papers_n * 3
        unknown_selected_scores_n = selected_slots_n - len(observed)
        if unknown_selected_scores_n < 0:
            raise ValueError(f"more observed scores than selected slots for {system_code}")
        selected_complete_lower = None if selected_slots_n == 0 else observed_sum / selected_slots_n
        selected_complete_upper = None if selected_slots_n == 0 else (observed_sum + unknown_selected_scores_n) / selected_slots_n
        bounds.append(
            {
                "system_code": system_code,
                "system": system,
                "targeted_attempts_n": 8,
                "generated_manuscripts_n": generated_n,
                "failed_experiments_n": 8 - generated_n,
                "human_reviewed_selected_papers_n": selected_papers_n,
                "planned_human_scores_n": expected_reviews_n,
                "observed_selected_scores_n": len(observed),
                "unknown_completed_scores_n": unknown_completed_reviews_n,
                "observed_normalized_score_sum": f6(observed_sum),
                "selected_available_score_mean": f6(selected_mean),
                "unknown_selected_scores_n": unknown_selected_scores_n,
                "selected_complete_score_mean_lower": f6(selected_complete_lower),
                "selected_complete_score_mean_upper": f6(selected_complete_upper),
                "identified_lower": f6(lower),
                "identified_upper": f6(upper),
                "identified_width": f6(upper - lower),
                "endpoint": "mean normalized human overall score per targeted attempt; failed experiment score fixed at zero",
                "source_anchor": "arXiv:2605.16616v1 Figures 2--3",
                "key_boundary": "Unreviewed generated manuscripts retain scores in [0,1]; bounds concern human review score, not latent scientific truth.",
            }
        )

    if sum(int(row["generated_manuscripts_n"]) for row in bounds) != 45:
        raise ValueError("MLReplicate generated-manuscript total must equal 45")
    if sum(int(row["failed_experiments_n"]) for row in bounds) != 3:
        raise ValueError("MLReplicate failed-experiment total must equal 3")
    if sum(int(row["human_reviewed_selected_papers_n"]) for row in bounds) != 10:
        raise ValueError("MLReplicate selected human-review total must equal 10")

    edges: list[dict[str, object]] = []
    for left, right in itertools.combinations(bounds, 2):
        left_l, left_u = float(left["identified_lower"]), float(left["identified_upper"])
        right_l, right_u = float(right["identified_lower"]), float(right["identified_upper"])
        if left_l > right_u:
            relation = f"{left['system_code']}>{right['system_code']}"
            identified = "yes"
        elif right_l > left_u:
            relation = f"{right['system_code']}>{left['system_code']}"
            identified = "yes"
        else:
            relation = "incomparable"
            identified = "no"
        edges.append(
            {
                "system_i": left["system_code"],
                "system_j": right["system_code"],
                "L_i": left["identified_lower"],
                "U_i": left["identified_upper"],
                "L_j": right["identified_lower"],
                "U_j": right["identified_upper"],
                "strict_order_identified": identified,
                "relation": relation,
            }
        )
    if len(edges) != 15 or any(row["strict_order_identified"] == "yes" for row in edges):
        raise ValueError("expected an empty six-system assumption-free rankability graph")
    return bounds, edges


def main() -> None:
    crosswalk = read_csv(CROSSWALK)
    computability = build_estimand_computability(crosswalk)
    capability = build_capability_bounds(crosswalk)
    score_rows = build_mlreplicate_scores()
    rankability, edges = build_mlreplicate_rankability(score_rows)

    write_csv(DERIVED / "estimand_bound_computability.csv", computability)
    write_csv(DERIVED / "capability_identification_bounds.csv", capability)
    write_csv(DERIVED / "mlreplicate_selected_human_scores.csv", score_rows)
    write_csv(DERIVED / "mlreplicate_rankability_bounds.csv", rankability)
    write_csv(DERIVED / "mlreplicate_rankability_edges.csv", edges)
    write_mlreplicate_rankability_certificate(rankability, edges)

    relevant = sum(row["derived_target_id"] != "" for row in computability)
    print(
        f"wrote 54-row computability ledger ({relevant} component rows), "
        f"{len(capability)} study-target bounds, 29/30 observed selected human scores, "
        f"and an assumption-free rankability graph with 0/{len(edges)} identified pairwise orders"
    )


if __name__ == "__main__":
    main()
