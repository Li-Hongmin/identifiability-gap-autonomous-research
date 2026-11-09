#!/usr/bin/env python3
"""Validate identifiability coding and recompute strict coverage counts."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "data" / "derived" / "study_identifiability_matrix.csv"
SUMMARY = ROOT / "data" / "derived" / "identifiability_summary.csv"
CRITERIA = [
    "complete_initial_denominator",
    "all_or_probability_sample_same_standard_validation",
    "external_or_independent_validator",
    "validation_targets_scientific_validity",
]


def main() -> None:
    with MATRIX.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if len({row["paper_id"] for row in rows}) != len(rows):
        raise ValueError("paper_id must be unique")
    allowed = {"yes", "partial", "no"}
    for row in rows:
        for criterion in CRITERIA:
            if row[criterion] not in allowed:
                raise ValueError(f"invalid {criterion} for {row['paper_id']}: {row[criterion]}")
        expected_joint = "yes" if all(row[key] == "yes" for key in CRITERIA) else "no"
        if row["joint_denominator_and_independent_scientific_validation"] != expected_joint:
            raise ValueError(f"joint logic mismatch for {row['paper_id']}")
        if expected_joint == "yes" and not row["validated_initial_units_n"]:
            raise ValueError(f"joint-positive row lacks validated unit count: {row['paper_id']}")
        if expected_joint == "no" and row["validated_initial_units_n"]:
            raise ValueError(f"joint-negative row has validated unit count: {row['paper_id']}")
        if not row["reason_for_joint_status"] or not row["source_anchor"]:
            raise ValueError(f"missing audit text for {row['paper_id']}")

    counts = {criterion: sum(row[criterion] == "yes" for row in rows) for criterion in CRITERIA}
    joint = sum(row["joint_denominator_and_independent_scientific_validation"] == "yes" for row in rows)
    units = sum(int(row["validated_initial_units_n"] or 0) for row in rows)
    expected = {
        "complete_initial_denominator": counts["complete_initial_denominator"],
        "all_or_probability_sample_same_standard_validation": counts["all_or_probability_sample_same_standard_validation"],
        "external_or_independent_validator": counts["external_or_independent_validator"],
        "validation_targets_scientific_validity": counts["validation_targets_scientific_validity"],
        "joint_denominator_and_independent_scientific_validation": joint,
        "initial_units_in_jointly_identifying_papers": joint,
    }
    with SUMMARY.open(newline="", encoding="utf-8") as handle:
        summary = {row["criterion"]: int(row["papers_yes_n"]) for row in csv.DictReader(handle)}
    if summary != expected:
        raise ValueError(f"summary mismatch: observed={summary}, expected={expected}")
    print(f"validated {len(rows)} papers; joint={joint}; validated_initial_units={units}")


if __name__ == "__main__":
    main()
