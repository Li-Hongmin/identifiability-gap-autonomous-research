#!/usr/bin/env python3
"""Compare blind ARDA requirement coding with the first 44-paper matrix."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/derived"
FIRST = DATA / "study_identifiability_matrix.csv"
PARTS = [DATA / f"arda_identification_secondcode_part_{part}.csv" for part in "abc"]
SECOND = DATA / "arda_identification_secondcode_44.csv"
AGREEMENT = DATA / "arda_identification_secondcode_agreement.csv"
DISAGREEMENTS = DATA / "arda_identification_secondcode_disagreements.csv"

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


def kappa(left: list[str], right: list[str]) -> float:
    n = len(left)
    observed = sum(a == b for a, b in zip(left, right)) / n
    lc, rc = Counter(left), Counter(right)
    expected = sum(lc[label] / n * rc[label] / n for label in ALLOWED)
    return (observed - expected) / (1 - expected) if expected < 1 else 1.0


def main() -> None:
    first = read(FIRST)
    second = [row for path in PARTS for row in read(path)]
    if len(first) != 44 or len(second) != 44:
        raise ValueError(f"expected 44+44 papers, found {len(first)}+{len(second)}")
    first_by = {row["paper_id"]: row for row in first}
    second_by = {row["paper_id"]: row for row in second}
    if len(first_by) != 44 or set(first_by) != set(second_by):
        raise ValueError("paper coverage differs between first and second coding")

    for row in second:
        for second_field in CRITERIA.values():
            if row[second_field] not in ALLOWED:
                raise ValueError(f"invalid {second_field}: {row['paper_id']}")
        expected_joint = "yes" if all(row[field] == "yes" for field in CRITERIA.values()) else "no"
        if row["joint_identification"] != expected_joint:
            raise ValueError(f"second-code joint mismatch: {row['paper_id']}")
        if expected_joint == "yes" and not row["validated_initial_units_n"]:
            raise ValueError(f"joint positive without unit count: {row['paper_id']}")
        if expected_joint == "no" and row["validated_initial_units_n"]:
            raise ValueError(f"joint negative with unit count: {row['paper_id']}")

    second_fields = list(second[0])
    with SECOND.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=second_fields)
        writer.writeheader()
        writer.writerows(sorted(second, key=lambda row: row["paper_id"]))

    agreement_rows = []
    disagreements = []
    for first_field, second_field in CRITERIA.items():
        left = [first_by[key][first_field] for key in sorted(first_by)]
        right = [second_by[key][second_field] for key in sorted(first_by)]
        agreed = sum(a == b for a, b in zip(left, right))
        agreement_rows.append({
            "criterion": first_field,
            "agreed": agreed,
            "total": 44,
            "agreement_rate": f"{agreed / 44:.6f}",
            "cohen_kappa": f"{kappa(left, right):.6f}",
            "first_yes": sum(value == "yes" for value in left),
            "second_yes": sum(value == "yes" for value in right),
        })
        for paper_id in sorted(first_by):
            a, b = first_by[paper_id], second_by[paper_id]
            if a[first_field] == b[second_field]:
                continue
            disagreements.append({
                "paper_id": paper_id,
                "short_name": a["short_name"],
                "criterion": first_field,
                "first_label": a[first_field],
                "second_label": b[second_field],
                "first_anchor": a["source_anchor"],
                "first_rationale": a["reason_for_joint_status"],
                "second_anchor": b[f"{second_field}_anchor"],
                "second_rationale": b[f"{second_field}_rationale"],
                "second_coder": b["coder"],
            })

    joint_left = [first_by[key]["joint_denominator_and_independent_scientific_validation"] for key in sorted(first_by)]
    joint_right = [second_by[key]["joint_identification"] for key in sorted(first_by)]
    joint_agreed = sum(a == b for a, b in zip(joint_left, joint_right))
    agreement_rows.append({
        "criterion": "strict_joint_identification",
        "agreed": joint_agreed,
        "total": 44,
        "agreement_rate": f"{joint_agreed / 44:.6f}",
        "cohen_kappa": "",
        "first_yes": sum(value == "yes" for value in joint_left),
        "second_yes": sum(value == "yes" for value in joint_right),
    })

    with AGREEMENT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(agreement_rows[0]))
        writer.writeheader()
        writer.writerows(agreement_rows)
    with DISAGREEMENTS.open("w", newline="", encoding="utf-8") as handle:
        fields = ["paper_id", "short_name", "criterion", "first_label", "second_label", "first_anchor", "first_rationale", "second_anchor", "second_rationale", "second_coder"]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(disagreements)

    second_joint_units = sum(int(row["validated_initial_units_n"] or 0) for row in second)
    print(
        f"compared 44 papers x 4 criteria; disagreements={len(disagreements)}; "
        f"joint agreement={joint_agreed}/44; second joint={sum(v == 'yes' for v in joint_right)} papers/{second_joint_units} units"
    )


if __name__ == "__main__":
    main()
