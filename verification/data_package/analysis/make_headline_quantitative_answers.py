#!/usr/bin/env python3
"""Build the direct quantitative answer table without pooling estimands."""

from __future__ import annotations

import csv
from pathlib import Path

from make_evidence_strength_ledger import evidence_class


ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data" / "derived"
OUT_CSV = DERIVED / "headline_quantitative_answers.csv"
OUT_MD = DERIVED / "headline_quantitative_answers.md"


GROUPS: list[tuple[str, str, list[str]]] = [
    ("manipulated_post_selection", "Causal loss of correct selection under manipulated test information", ["LUO_AGENTLAB_FLIP", "LUO_AISV2_FLIP"]),
    ("transparent_best_of_k", "Descriptive contribution of disclosed best-of-2 selection", ["ALETHEIA_SELECTION_STRICT", "ALETHEIA_SELECTION_MAJ"]),
    ("selected_effect_nontransfer_retrospective", "Retrospectively selected known-null effects that fail on the next model", ["NEXTLLM_DIET_MITIGATED", "NEXTLLM_REVIEWS_MITIGATED"]),
    ("selected_effect_nontransfer_prospective", "Preregistered selected effects that fail on the first eligible future model", ["NEXTLLM_PROSPECTIVE_MITIGATED"]),
    ("pipeline_or_task_attrition", "Initiated units that fail a study-specific pipeline or task endpoint", ["BEEL_EXECUTION", "AISCIENTIST_PIPELINE", "AUTORESEARCH_TARGET", "MLAGENTBENCH_TASK"]),
    ("scientific_or_artifact_invalidity", "Completed or evaluated units failing a validity criterion", ["CAWM_PRIMARY", "PLAGIARISM_VERIFIED", "ALETHEIA_ATTEMPT", "BEEL_NUMERIC_DEFECT"]),
    ("process_failure", "Trace labels showing failures to test, absorb, correct, or act on evidence", ["CORRAL_UNTESTED", "CORRAL_NONUPTAKE", "CORRAL_FIXED", "AUTORESEARCH_IMPL", "AUTORESEARCH_METHOD_CONCL", "AUTORESEARCH_OVERCLAIM", "AUTORESEARCH_UNCORRECTED"]),
    ("evidence_provenance_failure_baseline", "Full or partial poisoning success with complete baseline run denominators", ["DDOS_FULL_SUCCESS", "DDOS_ANY_SUCCESS"]),
    ("evidence_provenance_failure_mitigation", "Residual poisoning success after persona or provenance-audit safeguards", ["DDOS_PERSONA_FULL", "DDOS_AUDIT_FULL", "DDOS_AUDIT_ANY"]),
    ("validator_false_negative", "Known real discrepancies missed by the best tested validator", ["SCICOQA_MISSED_REAL"]),
    ("healthy_falsification", "Hypotheses rejected by an experiment loop; scientific updating, not system failure", ["QUADRUPED_WITHOUT_FALSIFIED", "QUADRUPED_WITH_FALSIFIED"]),
]

def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    crosswalk = {row["result_id"]: row for row in read_csv(DERIVED / "estimand_crosswalk.csv")}
    intervals = {row["result_id"]: row for row in read_csv(DERIVED / "proportion_intervals.csv")}
    rows: list[dict[str, str]] = []

    for group, question_answered, result_ids in GROUPS:
        for result_id in result_ids:
            if result_id not in crosswalk:
                raise ValueError(f"unknown result_id: {result_id}")
            source = crosswalk[result_id]
            interval = intervals.get(result_id, {})
            estimate = float(source["estimate"])
            class_code, class_label = evidence_class(result_id)
            rows.append(
                {
                    "answer_group": group,
                    "question_answered": question_answered,
                    "result_id": result_id,
                    "study_id": source["study_id"],
                    "unit": source["unit"],
                    "events_n": source["numerator_n"],
                    "denominator_n": source["denominator_n"],
                    "estimate": source["estimate"],
                    "estimate_percent": f"{100 * estimate:.1f}",
                    "wilson95_low": interval.get("wilson95_low", ""),
                    "wilson95_high": interval.get("wilson95_high", ""),
                    "estimate_label": source["estimate_label"],
                    "evidence_class": class_code,
                    "evidence_class_label": class_label,
                    "source_anchor": source["source_anchor"],
                    "key_boundary": source["key_boundary"],
                }
            )

    fields = list(rows[0])
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    lines = [
        "# Direct quantitative answers",
        "",
        "These are design-specific quantities selected from ARDA's frozen estimand crosswalk. The spans below are descriptive minima and maxima, not pooled estimates, confidence bounds, or field prevalence.",
        "",
        "| Question | Observed design-specific quantities | What it does not estimate |",
        "|---|---:|---|",
    ]
    for group, question_answered, result_ids in GROUPS:
        group_rows = [row for row in rows if row["answer_group"] == group]
        values = [float(row["estimate_percent"]) for row in group_rows]
        display = f"{values[0]:.1f}%" if len(values) == 1 else f"{min(values):.1f}%–{max(values):.1f}%"
        if group == "healthy_falsification":
            boundary = "Not an AI failure rate; rejection can be the correct scientific outcome."
        elif group == "validator_false_negative":
            boundary = "Not discrepancy prevalence among papers."
        elif group == "process_failure":
            boundary = "Labels overlap and are not additive or independently human-validated prevalence."
        else:
            boundary = "Not a global fraction of AI research capability that is false or illusory."
        lines.append(f"| {question_answered} | {display} | {boundary} |")
    lines.extend(
        [
            "",
            "Evidence classes: **A**, controlled or preregistered comparison; **B**, all-unit expert or adjudicated scientific validity; **C**, complete-denominator benchmark or holdout evidence; **D**, machine-coded process annotation; **E**, selected or partial mechanism evidence. Classes express epistemic design strength and do not authorize pooling.",
            "",
            "The row-level CSV retains every numerator, denominator, unit, source anchor, Wilson interval when identified, and interpretation boundary. Transparent best-of-2 attribution has no integer event numerator because it is a decomposition of selected success under two validity rules.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {len(rows)} design-specific answers across {len(GROUPS)} non-pooled groups")


if __name__ == "__main__":
    main()
