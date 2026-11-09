#!/usr/bin/env python3
"""Validate the manuscript-facing public-evidence data package."""

from __future__ import annotations

import csv
import itertools
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data" / "derived"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def unique(rows: list[dict[str, str]], field: str, label: str) -> set[str]:
    values = [row[field] for row in rows]
    require(all(values), f"{label}: empty {field}")
    require(len(values) == len(set(values)), f"{label}: duplicate {field}")
    return set(values)


def main() -> None:
    studies = read_csv(DERIVED / "studies.csv")
    matrix = read_csv(DERIVED / "study_identifiability_matrix.csv")
    second = read_csv(DERIVED / "arda_identification_secondcode_44.csv")
    disagreements = read_csv(DERIVED / "arda_identification_secondcode_disagreements.csv")
    adjudicated = read_csv(DERIVED / "arda_identification_adjudicated_44.csv")
    sensitivity = read_csv(DERIVED / "arda_identification_coding_sensitivity.csv")
    endpoint_reach = read_csv(DERIVED / "arda_validator_endpoint_reach_8.csv")
    endpoint_reach_summary = read_csv(DERIVED / "arda_validator_endpoint_reach_summary.csv")
    crosswalk = read_csv(DERIVED / "estimand_crosswalk.csv")
    intervals = read_csv(DERIVED / "proportion_intervals.csv")
    evidence_strength = read_csv(DERIVED / "evidence_strength_ledger.csv")
    headline = read_csv(DERIVED / "headline_quantitative_answers.csv")
    computability = read_csv(DERIVED / "estimand_bound_computability.csv")
    capability_bounds = read_csv(DERIVED / "capability_identification_bounds.csv")
    selected_scores = read_csv(DERIVED / "mlreplicate_selected_human_scores.csv")
    rankability_bounds = read_csv(DERIVED / "mlreplicate_rankability_bounds.csv")
    rankability_edges = read_csv(DERIVED / "mlreplicate_rankability_edges.csv")
    rankability_certificate = json.loads(
        (DERIVED / "mlreplicate_rankability_certificate.json").read_text(encoding="utf-8")
    )
    audit_screening = read_csv(DERIVED / "rankability_audit_screening.csv")
    audit_inputs = read_csv(DERIVED / "rankability_audit_inputs.csv")
    audit_systems = read_csv(DERIVED / "rankability_audit_systems.csv")
    audit_pairs = read_csv(DERIVED / "rankability_audit_pairs.csv")
    audit_summary = read_csv(DERIVED / "rankability_audit_summary.csv")
    audit_groups = read_csv(DERIVED / "rankability_audit_group_summary.csv")
    audit_certificate = json.loads(
        (DERIVED / "cross_benchmark_rankability_certificate.json").read_text(encoding="utf-8")
    )
    claim_map = read_csv(DERIVED / "manuscript_claim_evidence_map.csv")
    screening = read_csv(DERIVED / "autonomous_research_evaluation_screening_merged.csv")
    flow = read_csv(DERIVED / "screening_flow.csv")
    inventory = read_csv(ROOT / "data" / "data_inventory.csv")

    study_ids = unique(studies, "study_id", "studies")
    paper_ids = unique(matrix, "paper_id", "identifiability matrix")
    second_ids = unique(second, "paper_id", "blind second-code matrix")
    adjudicated_ids = unique(adjudicated, "paper_id", "adjudicated matrix")
    result_ids = unique(crosswalk, "result_id", "estimand crosswalk")
    interval_ids = unique(intervals, "result_id", "proportion intervals")
    evidence_ids = unique(evidence_strength, "result_id", "evidence-strength ledger")
    headline_ids = unique(headline, "result_id", "headline answers")
    computability_ids = unique(computability, "result_id", "bound computability")
    target_ids = unique(capability_bounds, "target_id", "capability bounds")
    rank_systems = unique(rankability_bounds, "system_code", "rankability bounds")
    unique(claim_map, "claim_id", "manuscript claim map")
    theory_records = json.loads((DERIVED / "paper_lib_identification_theory_records.json").read_text(encoding="utf-8"))

    require(len(studies) == 45, f"expected 45 study rows, found {len(studies)}")
    require(len(matrix) == 44, f"expected 44 paper rows, found {len(matrix)}")
    require(len(second) == 44, f"expected 44 blind second-code rows, found {len(second)}")
    require(len(adjudicated) == 44, f"expected 44 adjudicated rows, found {len(adjudicated)}")
    require(second_ids == paper_ids == adjudicated_ids, "identification-coding paper coverage differs")
    require(len(disagreements) == 62, f"expected 62 criterion disagreements, found {len(disagreements)}")
    disagreement_keys = [(row["paper_id"], row["criterion"]) for row in disagreements]
    require(len(disagreement_keys) == len(set(disagreement_keys)), "duplicate criterion disagreement")
    require({row["paper_id"] for row in disagreements} <= paper_ids, "disagreement contains unknown paper")
    require(len(endpoint_reach) == 8 and len({row["paper_id"] for row in endpoint_reach}) == 8, "expected eight unique endpoint-reach papers")
    require({row["paper_id"] for row in studies} == paper_ids, "study and matrix paper IDs differ")
    require({row["study_id"] for row in crosswalk} <= study_ids, "crosswalk contains an unknown study ID")
    require(interval_ids <= result_ids, "interval table contains an unknown result ID")
    require(evidence_ids == result_ids, "evidence-strength ledger must classify all estimands")
    require(headline_ids <= result_ids, "headline table contains an unknown result ID")
    require(computability_ids == result_ids, "bound-computability ledger must classify all estimands")
    evidence_by_id = {row["result_id"]: row for row in evidence_strength}
    require(
        all(row["evidence_class"] == evidence_by_id[row["result_id"]]["evidence_class"] for row in headline),
        "headline and full-ledger evidence classes disagree",
    )
    require(len(intervals) == 35, f"expected 35 interval rows, found {len(intervals)}")
    require(len(headline) == 30, f"expected 30 headline rows, found {len(headline)}")
    require(len(capability_bounds) == 9 and len(target_ids) == 9, "expected nine unique study-target identified sets")
    require(len(selected_scores) == 30, "expected 30 planned MLReplicate human-score slots")
    require(sum(row["score_status"] == "observed" for row in selected_scores) == 29, "expected 29 observed MLReplicate human scores")
    require(sum(row["score_status"] != "observed" for row in selected_scores) == 1, "expected one missing MLReplicate human score")
    require(len(rankability_bounds) == 6 and len(rank_systems) == 6, "expected six MLReplicate system bounds")
    require(len(rankability_edges) == 15, "expected all 15 unordered MLReplicate system pairs")
    require(len(theory_records) == 6, "expected six cached identification-theory references")
    require(len(claim_map) == 31, "expected 31 current manuscript claims")
    require(all(row["evidence_anchor"] and row["scope_boundary"] for row in claim_map), "claim map provenance or scope boundary missing")
    claim_by_id = {row["claim_id"]: row for row in claim_map}
    require(
        {"C21", "C23", "C24", "C25", "C26", "C27", "C28", "C29", "C30", "C31"}
        <= set(claim_by_id),
        "claim map missing coding, score-sensitivity, or cross-evaluation rankability claims",
    )
    require("3 7 and 8" in claim_by_id["C21"]["atomic_claim"] and "35 2267 and 2287" in claim_by_id["C21"]["atomic_claim"], "three-matrix claim mapping is stale")
    require("1930" in claim_by_id["C23"]["atomic_claim"], "procedural-claim mapping is stale")
    require("eight adjudicated positives" in claim_by_id["C24"]["atomic_claim"], "external-claim scope mapping is stale")
    require("0.240 to 0.307" in claim_by_id["C25"]["atomic_claim"], "missing-score sensitivity mapping is stale")
    require("no directed edge among 15 system pairs" in claim_by_id["C26"]["atomic_claim"], "rankability-certificate mapping is stale")
    require("45 paper-level screening records 15 admitted evaluations 100 configurations and 376" in claim_by_id["C27"]["atomic_claim"], "cross-evaluation frame mapping is stale")
    require("119 of 134" in claim_by_id["C28"]["atomic_claim"] and "six reverse and nine" in claim_by_id["C28"]["atomic_claim"], "selected-output rankability mapping is stale")
    require("all 214" in claim_by_id["C29"]["atomic_claim"], "all-run rankability mapping is stale")
    require(len({row["answer_group"] for row in headline}) == 11, "expected 11 non-pooled answer groups")
    require({row["evidence_class"] for row in headline} == {"A", "B", "C", "D", "E"}, "headline evidence classes must cover A-E")
    require(all(row["evidence_class_label"] for row in headline), "headline evidence-class label missing")
    require(all(row["source_anchor"] and row["key_boundary"] for row in crosswalk), "crosswalk source or boundary missing")
    require(all(row["source_anchor"] and row["reason_for_joint_status"] for row in matrix), "matrix source or joint-status reason missing")

    allowed = {"yes", "partial", "no"}
    first_fields = [
        "complete_initial_denominator",
        "all_or_probability_sample_same_standard_validation",
        "external_or_independent_validator",
        "validation_targets_scientific_validity",
    ]
    second_fields = [
        "complete_initial_denominator",
        "same_standard_validation",
        "independent_validator",
        "scientific_validity_endpoint",
    ]
    for row in second:
        require(all(row[field] in allowed for field in second_fields), f"invalid blind second code for {row['paper_id']}")
        expected = "yes" if all(row[field] == "yes" for field in second_fields) else "no"
        require(row["joint_identification"] == expected, f"blind second-code conjunction mismatch for {row['paper_id']}")
        require(bool(row["validated_initial_units_n"]) == (expected == "yes"), f"blind second-code unit mismatch for {row['paper_id']}")
    for row in adjudicated:
        require(all(row[field] in allowed for field in first_fields), f"invalid adjudicated code for {row['paper_id']}")
        expected = "yes" if all(row[field] == "yes" for field in first_fields) else "no"
        require(row["joint_identification"] == expected, f"adjudicated conjunction mismatch for {row['paper_id']}")
        require(row["units_require_source_resolution"] == "no", f"unresolved joint-positive units for {row['paper_id']}")
        require(bool(row["validated_initial_units_n"]) == (expected == "yes"), f"adjudicated unit mismatch for {row['paper_id']}")
    adjudicated_joint_ids = {row["paper_id"] for row in adjudicated if row["joint_identification"] == "yes"}
    require({row["paper_id"] for row in endpoint_reach} == adjudicated_joint_ids, "endpoint-reach coverage differs from adjudicated positives")
    require(
        all(row["validator_separation"] in {"institutionally_external", "procedurally_separated", "author_internal_or_unclear"} for row in endpoint_reach),
        "invalid validator-separation label",
    )
    require(all(row["endpoint_reach"] in {"claim_complete", "claim_dimension", "task_proxy"} for row in endpoint_reach), "invalid endpoint-reach label")
    require(sum(row["procedural_claim_identification"] == "yes" for row in endpoint_reach) == 4, "procedural-claim sensitivity changed")
    require(sum(int(row["validated_initial_units_n"]) for row in endpoint_reach if row["procedural_claim_identification"] == "yes") == 1930, "procedural-claim unit count changed")
    require(sum(row["external_claim_identification"] == "yes" for row in endpoint_reach) == 0, "external-claim sensitivity changed")

    for row in capability_bounds:
        lower = float(row["identified_lower"])
        upper = float(row["identified_upper"])
        width = float(row["identified_width"])
        require(0 <= lower <= upper <= 1, f"invalid identified set for {row['target_id']}")
        require(abs(width - (upper - lower)) < 2e-6, f"identified-set width mismatch for {row['target_id']}")
        require(row["source_anchor"] and row["key_boundary"], f"bound provenance missing for {row['target_id']}")

    require(sum(int(row["generated_manuscripts_n"]) for row in rankability_bounds) == 45, "MLReplicate generated count changed")
    require(sum(int(row["failed_experiments_n"]) for row in rankability_bounds) == 3, "MLReplicate failed-experiment count changed")
    require(sum(int(row["human_reviewed_selected_papers_n"]) for row in rankability_bounds) == 10, "MLReplicate selected-review count changed")
    require(sum(int(row["observed_selected_scores_n"]) for row in rankability_bounds) == 29, "MLReplicate observed-score count changed")
    rank_by_code = {row["system_code"]: row for row in rankability_bounds}
    require(rank_by_code["AL"]["unknown_selected_scores_n"] == "1", "expected one missing selected Agent Laboratory score")
    require(abs(float(rank_by_code["AL"]["selected_complete_score_mean_lower"]) - 0.24) < 1e-6, "Agent Laboratory selected lower sensitivity changed")
    require(abs(float(rank_by_code["AL"]["selected_complete_score_mean_upper"]) - 4.6 / 15) < 2e-6, "Agent Laboratory selected upper sensitivity changed")
    require(
        float(rank_by_code["CR"]["selected_complete_score_mean_lower"])
        > float(rank_by_code["AL"]["selected_complete_score_mean_upper"])
        > float(rank_by_code["TS"]["selected_complete_score_mean_upper"])
        > float(rank_by_code["AIR"]["selected_complete_score_mean_upper"]),
        "selected-score total order is not robust to the missing Agent Laboratory score",
    )
    expected_pairs = {tuple(sorted(pair)) for pair in itertools.combinations(rank_systems, 2)}
    observed_pairs = {tuple(sorted((row["system_i"], row["system_j"]))) for row in rankability_edges}
    require(observed_pairs == expected_pairs, "MLReplicate rankability pair coverage changed")
    require(all(row["strict_order_identified"] == "no" and row["relation"] == "incomparable" for row in rankability_edges), "assumption-free MLReplicate graph is no longer empty")
    require(rankability_certificate["schema"] == "rankability-certificate/0.1", "rankability-certificate schema changed")
    require(len(rankability_certificate["identified_sets"]) == 6, "rankability certificate lost a system")
    require(len(rankability_certificate["pairwise_relations"]) == 15, "rankability certificate lost a system pair")
    require(rankability_certificate["certified_directed_edges"] == [], "rankability certificate should expose no identified edge")
    require(rankability_certificate["summary"]["identified_strict_orders"] == 0, "rankability certificate summary changed")

    require(len(audit_screening) == 45, "expected 45 paper-level rankability screening records")
    require(len({row["paper_id"] for row in audit_screening}) == 45, "rankability screening paper IDs are not unique")
    admitted_ids = {row["candidate_id"] for row in audit_screening if row["decision"] == "include"}
    excluded = [row for row in audit_screening if row["decision"] != "include"]
    require(len(admitted_ids) == 15 and len(excluded) == 30, "rankability screening inclusion counts changed")
    require(all(row["decision_reason"] for row in audit_screening), "rankability screening reason missing")
    require(len(audit_inputs) == 100 and len(audit_systems) == 100, "rankability audit must contain 100 configurations")
    input_keys = {(row["audit_id"], row["system_code"]) for row in audit_inputs}
    system_keys = {(row["audit_id"], row["system_code"]) for row in audit_systems}
    require(len(input_keys) == 100 and input_keys == system_keys, "rankability system coverage differs from inputs")
    require(len(audit_pairs) == 376, "rankability audit must contain 376 unordered pairs")
    pair_keys = {
        (row["audit_id"], *sorted((row["system_i"], row["system_j"])))
        for row in audit_pairs
    }
    require(len(pair_keys) == 376, "rankability audit contains duplicate system pairs")
    require(len(audit_summary) == 15, "rankability audit must contain 15 evaluation summaries")
    audit_ids = {row["audit_id"] for row in audit_summary}
    require(audit_ids == admitted_ids, "rankability screening and evaluation summaries differ")
    group_by_id = {row["audit_group"]: row for row in audit_groups}
    require(set(group_by_id) == {"selected_output", "all_unit_control", "all_audits"}, "rankability group coverage changed")
    selected_group = group_by_id["selected_output"]
    require(
        selected_group["displayed_strict_pairs_n"] == "134"
        and selected_group["certified_displayed_pairs_n"] == "119"
        and selected_group["reversed_displayed_pairs_n"] == "6"
        and selected_group["unresolved_displayed_pairs_n"] == "9",
        "selected-output rankability headline changed",
    )
    all_run_group = group_by_id["all_unit_control"]
    require(
        all_run_group["displayed_strict_pairs_n"] == "214"
        and all_run_group["certified_displayed_pairs_n"] == "214"
        and all_run_group["reversed_displayed_pairs_n"] == "0"
        and all_run_group["unresolved_displayed_pairs_n"] == "0",
        "all-run rankability headline changed",
    )
    all_audits_group = group_by_id["all_audits"]
    require(
        all_audits_group["possible_pairs_n"] == "376"
        and all_audits_group["displayed_strict_pairs_n"] == "348"
        and all_audits_group["certified_displayed_pairs_n"] == "333",
        "all-audit rankability totals changed",
    )
    require(audit_certificate["schema"] == "cross-benchmark-rankability-audit/0.2", "cross-evaluation certificate schema changed")
    require(audit_certificate["headline"]["screened_papers"] == 45, "cross-evaluation certificate frame changed")
    require(audit_certificate["headline"]["mlreplicate_possible_pairs_identified"] == "0/15", "MLReplicate cross-evaluation headline changed")

    for row in intervals:
        numerator = int(row["events_n"])
        denominator = int(row["denominator_n"])
        require(0 <= numerator <= denominator, f"invalid binary counts for {row['result_id']}")
        require(abs(float(row["estimate"]) - numerator / denominator) < 1e-6, f"estimate mismatch for {row['result_id']}")
        require(0 <= float(row["wilson95_low"]) <= float(row["estimate"]) <= float(row["wilson95_high"]) <= 1, f"interval mismatch for {row['result_id']}")

    require(len(screening) == 453, f"expected 453 screening records, found {len(screening)}")
    flow_counts = {(row["stage"], row["category"]): int(row["n"]) for row in flow}
    require(flow_counts[("retrieval", "unique_query_hits")] == 446, "query-hit count changed")
    require(flow_counts[("retrieval", "citation_chain_additions")] == 7, "citation-addition count changed")
    require(446 + 7 == len(screening), "screening frame does not equal query hits plus citation additions")

    inventory_by_id = {row["dataset_id"]: row for row in inventory}
    for dataset_id, actual in {
        "PROPORTION_INTERVALS": len(intervals),
        "STUDY_IDENTIFIABILITY": len(matrix),
        "ARDA_IDENTIFICATION_SECOND_CODE": len(second),
        "ARDA_IDENTIFICATION_ADJUDICATION": len(adjudicated),
        "ARDA_IDENTIFICATION_SENSITIVITY": len(sensitivity),
        "ARDA_VALIDATOR_ENDPOINT_REACH": len(endpoint_reach),
        "ARDA_VALIDATOR_ENDPOINT_REACH_SUMMARY": len(endpoint_reach_summary),
        "EVALUATION_SCREENING_MERGED": len(screening),
        "HEADLINE_QUANTITATIVE_ANSWERS": len(headline),
        "EVIDENCE_STRENGTH_LEDGER": len(evidence_strength),
        "ESTIMAND_BOUND_COMPUTABILITY": len(computability),
        "CAPABILITY_IDENTIFICATION_BOUNDS": len(capability_bounds),
        "MLREPLICATE_SELECTED_HUMAN_SCORES": len(selected_scores),
        "MLREPLICATE_RANKABILITY_BOUNDS": len(rankability_bounds),
        "MLREPLICATE_RANKABILITY_EDGES": len(rankability_edges),
        "RANKABILITY_AUDIT_CODEBOOK": 1,
        "RANKABILITY_AUDIT_SCREENING": len(audit_screening),
        "RANKABILITY_AUDIT_INPUTS": len(audit_inputs),
        "RANKABILITY_AUDIT_SYSTEMS": len(audit_systems),
        "RANKABILITY_AUDIT_PAIRS": len(audit_pairs),
        "RANKABILITY_AUDIT_SUMMARY": len(audit_summary),
        "RANKABILITY_AUDIT_GROUP_SUMMARY": len(audit_groups),
        "CROSS_BENCHMARK_RANKABILITY_CERTIFICATE": 1,
        "IDENTIFICATION_THEORY_RECORDS": len(theory_records),
        "MANUSCRIPT_CLAIM_MAP": len(claim_map),
        "FIGURE2_SOURCE": len(capability_bounds) + len(rankability_bounds),
        "FIGURE1_RANKABILITY_SOURCE": len(audit_summary),
    }.items():
        require(dataset_id in inventory_by_id, f"inventory missing {dataset_id}")
        require(int(inventory_by_id[dataset_id]["rows_or_files"]) == actual, f"inventory count stale for {dataset_id}")

    joint = [row for row in matrix if row["joint_denominator_and_independent_scientific_validation"] == "yes"]
    validated_units = sum(int(row["validated_initial_units_n"]) for row in joint)
    require(len(joint) == 3 and validated_units == 35, "joint-identifiability headline changed")
    second_joint = [row for row in second if row["joint_identification"] == "yes"]
    second_units = sum(int(row["validated_initial_units_n"]) for row in second_joint)
    require(len(second_joint) == 7 and second_units == 2267, "blind second-code sensitivity changed")
    adjudicated_joint = [row for row in adjudicated if row["joint_identification"] == "yes"]
    adjudicated_units = sum(int(row["validated_initial_units_n"]) for row in adjudicated_joint)
    require(len(adjudicated_joint) == 8 and adjudicated_units == 2287, "adjudicated sensitivity changed")
    sensitivity_by_key = {(row["matrix"], row["statistic"]): row for row in sensitivity}
    require(len(sensitivity) == 18 and len(sensitivity_by_key) == 18, "expected 18 unique sensitivity rows")
    for matrix_name, papers, units in [
        ("first", 3, 35),
        ("blind_second", 7, 2267),
        ("adjudicated", 8, 2287),
    ]:
        require(int(sensitivity_by_key[(matrix_name, "strict_joint_papers")]["value"]) == papers, f"{matrix_name} joint-paper sensitivity mismatch")
        require(int(sensitivity_by_key[(matrix_name, "strict_joint_initial_units")]["value"]) == units, f"{matrix_name} unit sensitivity mismatch")

    print(
        "validated public data package: "
        f"44 papers, 45 study rows, 54 estimands, 54-row computability ledger, "
        f"9 identified sets, 6-system/15-pair rankability graph, 35 intervals, "
        f"15-evaluation/100-configuration/376-pair cross audit, "
        f"30 headline answers, 453 screening records, strict-joint sensitivity="
        f"3/35 first, 7/2267 blind-second, 8/2287 adjudicated"
    )


if __name__ == "__main__":
    main()
