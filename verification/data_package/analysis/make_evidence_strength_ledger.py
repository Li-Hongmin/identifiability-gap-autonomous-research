#!/usr/bin/env python3
"""Assign one epistemic evidence class to every ARDA estimand."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "derived" / "estimand_crosswalk.csv"
OUTPUT = ROOT / "data" / "derived" / "evidence_strength_ledger.csv"


EVIDENCE_CLASSES = {
    "A": {
        "label": "controlled or preregistered comparison",
        "ids": {
            "LUO_AGENTLAB_FLIP", "LUO_AISV2_FLIP", "HLER_UNCONSTRAINED_FAILURE",
            "HLER_CONSTRAINED_FAILURE", "DDOS_FULL_SUCCESS", "DDOS_ANY_SUCCESS",
            "DDOS_PERSONA_FULL", "DDOS_AUDIT_FULL", "DDOS_AUDIT_ANY",
            "NEXTLLM_PROSPECTIVE_MITIGATED",
        },
    },
    "B": {
        "label": "all-unit expert or adjudicated scientific validity",
        "ids": {
            "ALETHEIA_SELECTION_MAJ", "ALETHEIA_SELECTION_STRICT", "BEEL_EXECUTION",
            "ALETHEIA_ATTEMPT", "BEEL_NUMERIC_DEFECT", "KOSMOS_NOT_SUPPORTED",
            "SCICOQA_MISSED_REAL",
        },
    },
    "C": {
        "label": "complete-denominator benchmark, funnel, or holdout evidence",
        "ids": {
            "AISCIENTIST_PIPELINE", "MLAGENTBENCH_TASK", "AUTORESEARCH_TARGET", "CAWM_PRIMARY",
            "SCIINTEGRITY_FAILURE", "AISCIENTIST_AUTOREVIEW", "FOURATTEMPTS_FAILURE",
            "PRBENCH_NO_CALLBACK", "AICFD_FINAL_SELECTION", "DEEPSCIENTIST_IMPLEMENT",
            "DEEPSCIENTIST_PROGRESS", "SCIENTISTONE_ALL_ACCEPT", "SCIENTISTONE_BEST_ACCEPT",
            "AUTOMATERIALS_PARENT_GAIN", "AUTOMATERIALS_OUTER_SELECTION",
            "STOPREFUSAL_EPA_COMPLETECASE", "SPATIALBENCH_BEST_FAILURE", "FASTMOVING_F1_COVERAGE",
            "QUADRUPED_WITH_FALSIFIED", "QUADRUPED_WITHOUT_FALSIFIED", "LMRBENCH_UNIT_FAILURE",
            "HARPA_EXECUTION_FAILURE", "HARPA_BASELINE_FAILURE", "NEXTLLM_REVIEWS_MITIGATED",
            "NEXTLLM_DIET_MITIGATED",
        },
    },
    "D": {
        "label": "machine- or study-coded process, artifact, or critique annotation",
        "ids": {
            "CORRAL_UNTESTED", "CORRAL_NONUPTAKE", "CORRAL_FIXED", "AUTORESEARCH_IMPL",
            "AUTORESEARCH_METHOD_CONCL", "AUTORESEARCH_OVERCLAIM", "AUTORESEARCH_UNCORRECTED",
            "IMPLEMENTATION_EXPERIMENTAL_WEAKNESS", "IMPLEMENTATION_METHOD_FLAW",
            "SCRUTINY_PAPER_CRITIQUE", "SCRUTINY_EXECUTION_DEPENDENT",
        },
    },
    "E": {
        "label": "selected, partial, or mechanism-only evidence",
        "ids": {"PLAGIARISM_VERIFIED"},
    },
}


def evidence_class(result_id: str) -> tuple[str, str]:
    matches = [(code, str(spec["label"])) for code, spec in EVIDENCE_CLASSES.items() if result_id in spec["ids"]]
    if len(matches) != 1:
        raise ValueError(f"expected one evidence class for {result_id}, found {matches}")
    return matches[0]


def main() -> None:
    with SOURCE.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    output_rows = []
    for row in rows:
        code, label = evidence_class(row["result_id"])
        output_rows.append(
            {
                "result_id": row["result_id"],
                "study_id": row["study_id"],
                "evidence_class": code,
                "evidence_class_label": label,
                "estimand_family": row["estimand_family"],
                "unit": row["unit"],
                "source_anchor": row["source_anchor"],
                "key_boundary": row["key_boundary"],
            }
        )
    fields = list(output_rows[0])
    with OUTPUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(output_rows)
    counts = {code: sum(row["evidence_class"] == code for row in output_rows) for code in EVIDENCE_CLASSES}
    print(f"wrote evidence classes for {len(output_rows)} ARDA estimands: {counts}")


if __name__ == "__main__":
    main()
