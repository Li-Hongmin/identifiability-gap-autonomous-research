#!/usr/bin/env python3
"""Merge the eight-paper construct stress test and compute nested coverage."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/derived"
PARTS = [DATA / f"arda_validator_endpoint_reach_part_{part}.csv" for part in "abc"]
ADJUDICATED = DATA / "arda_identification_adjudicated_44.csv"
OUTPUT = DATA / "arda_validator_endpoint_reach_8.csv"
SUMMARY = DATA / "arda_validator_endpoint_reach_summary.csv"

SEPARATION = {"institutionally_external", "procedurally_separated", "author_internal_or_unclear"}
REACH = {"claim_complete", "claim_dimension", "task_proxy"}
EXPECTED_CODERS = {"arda_reach_a", "arda_reach_b", "arda_reach_c"}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    source = read(ADJUDICATED)
    joint = {row["paper_id"]: row for row in source if row["joint_identification"] == "yes"}
    rows = [row for path in PARTS for row in read(path)]
    if len(rows) != 8 or len({row["paper_id"] for row in rows}) != 8 or set(joint) != {row["paper_id"] for row in rows}:
        raise ValueError("stress test must cover exactly the eight adjudicated joint-positive papers")
    if {row["coder"] for row in rows} != EXPECTED_CODERS:
        raise ValueError("unexpected stress-test coder coverage")
    for row in rows:
        if row["validator_separation"] not in SEPARATION or row["endpoint_reach"] not in REACH:
            raise ValueError(f"invalid stress-test label for {row['paper_id']}")
        for field in ["primary_output_claim", "validator_anchor", "validator_rationale", "endpoint_anchor", "endpoint_rationale"]:
            if not row[field].strip():
                raise ValueError(f"missing {field} for {row['paper_id']}")
        row["validated_initial_units_n"] = joint[row["paper_id"]]["validated_initial_units_n"]
        row["procedural_claim_identification"] = (
            "yes" if row["validator_separation"] in {"institutionally_external", "procedurally_separated"}
            and row["endpoint_reach"] == "claim_complete" else "no"
        )
        row["external_claim_identification"] = (
            "yes" if row["validator_separation"] == "institutionally_external"
            and row["endpoint_reach"] == "claim_complete" else "no"
        )
    rows.sort(key=lambda row: row["paper_id"])
    with OUTPUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)

    summary = []
    for dimension, labels in [("validator_separation", sorted(SEPARATION)), ("endpoint_reach", sorted(REACH))]:
        counts = Counter(row[dimension] for row in rows)
        for label in labels:
            summary.append({"analysis": dimension, "category": label, "papers_n": counts[label], "initial_units_n": sum(int(row["validated_initial_units_n"]) for row in rows if row[dimension] == label), "papers": ";".join(row["paper_id"] for row in rows if row[dimension] == label)})
    for field in ["procedural_claim_identification", "external_claim_identification"]:
        selected = [row for row in rows if row[field] == "yes"]
        summary.append({"analysis": "nested_conjunction", "category": field, "papers_n": len(selected), "initial_units_n": sum(int(row["validated_initial_units_n"]) for row in selected), "papers": ";".join(row["paper_id"] for row in selected)})
    with SUMMARY.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(summary[0]))
        writer.writeheader(); writer.writerows(summary)
    print(f"stress-tested 8 joint-positive papers; procedural-claim={sum(row['procedural_claim_identification']=='yes' for row in rows)}; external-claim={sum(row['external_claim_identification']=='yes' for row in rows)}")


if __name__ == "__main__":
    main()
