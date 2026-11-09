#!/usr/bin/env python3
"""Merge source-based ARDA adjudications and report three-matrix sensitivity."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/derived"
FIRST = DATA / "study_identifiability_matrix.csv"
SECOND = DATA / "arda_identification_secondcode_44.csv"
DISAGREEMENTS = DATA / "arda_identification_secondcode_disagreements.csv"
ADJ_PARTS = [DATA / f"arda_identification_adjudication_part_{part}.csv" for part in "abc"]
OUTPUT = DATA / "arda_identification_adjudicated_44.csv"
SUMMARY = DATA / "arda_identification_coding_sensitivity.csv"

CRITERIA = {
    "complete_initial_denominator": "complete_initial_denominator",
    "all_or_probability_sample_same_standard_validation": "same_standard_validation",
    "external_or_independent_validator": "independent_validator",
    "validation_targets_scientific_validity": "scientific_validity_endpoint",
}
ALLOWED = {"yes", "partial", "no"}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    first = read(FIRST)
    second = read(SECOND)
    disagreements = read(DISAGREEMENTS)
    adjudications = [row for path in ADJ_PARTS for row in read(path)]
    expected_keys = {(row["paper_id"], row["criterion"]) for row in disagreements}
    adjudicated = {(row["paper_id"], row["criterion"]): row for row in adjudications}
    if len(adjudications) != len(adjudicated) or set(adjudicated) != expected_keys:
        raise ValueError("adjudications must cover each disagreement exactly once")
    for row in adjudications:
        if row["adjudicated_label"] not in ALLOWED:
            raise ValueError(f"invalid adjudication label: {row}")
        if not row["adjudication_anchor"].strip() or not row["adjudication_rationale"].strip():
            raise ValueError(f"missing adjudication evidence: {row}")

    first_by = {row["paper_id"]: row for row in first}
    second_by = {row["paper_id"]: row for row in second}
    output_rows = []
    for paper_id in sorted(first_by):
        a, b = first_by[paper_id], second_by[paper_id]
        out = {"paper_id": paper_id, "short_name": a["short_name"]}
        for first_field, second_field in CRITERIA.items():
            key = (paper_id, first_field)
            if key in adjudicated:
                decision = adjudicated[key]
                out[first_field] = decision["adjudicated_label"]
                out[f"{first_field}_anchor"] = decision["adjudication_anchor"]
                out[f"{first_field}_rationale"] = decision["adjudication_rationale"]
                out[f"{first_field}_adjudicator"] = decision["adjudicator"]
            else:
                if a[first_field] != b[second_field]:
                    raise ValueError(f"uncovered disagreement: {key}")
                out[first_field] = a[first_field]
                out[f"{first_field}_anchor"] = b[f"{second_field}_anchor"]
                out[f"{first_field}_rationale"] = "First and blind-second coders agreed; no adjudication required."
                out[f"{first_field}_adjudicator"] = "not_required"
        out["joint_identification"] = (
            "yes" if all(out[field] == "yes" for field in CRITERIA) else "no"
        )
        # Unit counts are admitted only when already source-anchored by either coding.
        units = b["validated_initial_units_n"].strip()
        if not units and a["joint_denominator_and_independent_scientific_validation"] == "yes":
            units = a["validated_initial_units_n"].strip()
        out["validated_initial_units_n"] = units if out["joint_identification"] == "yes" else ""
        out["units_require_source_resolution"] = (
            "yes" if out["joint_identification"] == "yes" and not units else "no"
        )
        output_rows.append(out)

    with OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(output_rows[0]))
        writer.writeheader()
        writer.writerows(output_rows)

    summary_rows = []
    matrices = {
        "first": (first_by, list(CRITERIA), "joint_denominator_and_independent_scientific_validation"),
        "blind_second": (second_by, list(CRITERIA.values()), "joint_identification"),
        "adjudicated": ({row["paper_id"]: row for row in output_rows}, list(CRITERIA), "joint_identification"),
    }
    for matrix, (rows_by, fields, joint_field) in matrices.items():
        joint_papers = sorted(pid for pid, row in rows_by.items() if row[joint_field] == "yes")
        for field in fields:
            summary_rows.append({
                "matrix": matrix, "statistic": f"yes_count:{field}",
                "value": sum(row[field] == "yes" for row in rows_by.values()), "papers": "",
            })
        summary_rows.append({
            "matrix": matrix, "statistic": "strict_joint_papers", "value": len(joint_papers),
            "papers": ";".join(joint_papers),
        })
        unit_field = "validated_initial_units_n"
        units = sum(int(rows_by[pid].get(unit_field, "") or 0) for pid in joint_papers)
        summary_rows.append({
            "matrix": matrix, "statistic": "strict_joint_initial_units", "value": units,
            "papers": ";".join(joint_papers),
        })
    with SUMMARY.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(summary_rows[0]))
        writer.writeheader()
        writer.writerows(summary_rows)

    unresolved = [row["paper_id"] for row in output_rows if row["units_require_source_resolution"] == "yes"]
    print(
        f"adjudicated {len(adjudications)} disagreements; "
        f"joint={sum(row['joint_identification'] == 'yes' for row in output_rows)}/44; "
        f"unresolved units={unresolved or 'none'}"
    )


if __name__ == "__main__":
    main()
