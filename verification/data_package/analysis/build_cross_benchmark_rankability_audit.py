#!/usr/bin/env python3
"""Build the cross-benchmark rankability audit from source-bounded inputs.

The outputs compare each evaluation's displayed strict pair claims with the
strict relations supported for its all-initiated-unit target. They are finite-
design identification results, not confidence statements or field prevalence.
"""

from __future__ import annotations

import csv
import itertools
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data" / "derived"
INPUT = DERIVED / "rankability_audit_inputs.csv"
SCREENING = DERIVED / "rankability_audit_screening.csv"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"refusing to write empty table: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def f6(value: float | None) -> str:
    return "" if value is None else f"{value:.6f}"


def parse_float(value: str) -> float | None:
    return None if value == "" else float(value)


def resolve_interval(
    row: dict[str, str], prefix: str
) -> tuple[float | None, float | None, str]:
    numerator = row[f"{prefix}_numerator"]
    denominator = row[f"{prefix}_denominator"]
    lower = parse_float(row[f"{prefix}_lower"])
    upper = parse_float(row[f"{prefix}_upper"])
    if numerator or denominator:
        if not numerator or not denominator:
            raise ValueError(f"incomplete {prefix} count for {row['audit_id']} {row['system_code']}")
        n = int(numerator)
        d = int(denominator)
        if not 0 <= n <= d or d <= 0:
            raise ValueError(f"invalid {prefix} count for {row['audit_id']} {row['system_code']}")
        value = n / d
        return value, value, f"{n}/{d}"
    if lower is None and upper is None:
        return None, None, ""
    if lower is None or upper is None or not 0 <= lower <= upper <= 1:
        raise ValueError(f"invalid {prefix} interval for {row['audit_id']} {row['system_code']}")
    return lower, upper, "source interval"


def strict_relation(
    i: dict[str, object], j: dict[str, object], prefix: str
) -> str:
    il = i[f"{prefix}_lower"]
    iu = i[f"{prefix}_upper"]
    jl = j[f"{prefix}_lower"]
    ju = j[f"{prefix}_upper"]
    if il is None or iu is None or jl is None or ju is None:
        return "no_display" if prefix == "display" else "unresolved"
    if float(il) > float(ju):
        return f"{i['system_code']}>{j['system_code']}"
    if float(jl) > float(iu):
        return f"{j['system_code']}>{i['system_code']}"
    return "unresolved"


def direction(relation: str) -> tuple[str, str] | None:
    if ">" not in relation:
        return None
    return tuple(relation.split(">", 1))  # type: ignore[return-value]


def main() -> None:
    inputs = read_csv(INPUT)
    if len(inputs) != 100:
        raise ValueError(f"expected 100 system configurations, found {len(inputs)}")
    keys = [(row["audit_id"], row["system_code"]) for row in inputs]
    if len(keys) != len(set(keys)):
        raise ValueError("duplicate audit-system input")

    systems: list[dict[str, object]] = []
    by_audit: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in inputs:
        dl, du, draw = resolve_interval(row, "display")
        tl, tu, traw = resolve_interval(row, "target")
        if tl is None or tu is None:
            raise ValueError(f"target interval missing for {row['audit_id']} {row['system_code']}")
        resolved: dict[str, object] = {
            "audit_id": row["audit_id"],
            "evaluation": row["evaluation"],
            "paper_id": row["paper_id"],
            "audit_group": row["audit_group"],
            "system_code": row["system_code"],
            "system": row["system"],
            "initial_units_n": int(row["initial_units_n"]),
            "selected_units_n": int(row["selected_units_n"]),
            "display_lower": dl,
            "display_upper": du,
            "display_raw": draw,
            "target_lower": tl,
            "target_upper": tu,
            "target_raw": traw,
            "budget_scope": row["budget_scope"],
            "endpoint": row["endpoint"],
            "source_anchor": row["source_anchor"],
            "key_boundary": row["key_boundary"],
        }
        by_audit[row["audit_id"]].append(resolved)
        systems.append(resolved)

    expected_sizes = {
        "MLREPLICATE": 6,
        "SCIENCEAGENTBENCH": 15,
        "SCIENTISTONE": 5,
        "DELTAML_4X6H": 4,
        "MLAGENTBENCH": 7,
        "SPATIALBENCH": 15,
        "BADSCIENTIST_RATE": 6,
        "SCIINTEGRITY": 7,
        "CORRAL_TASK": 6,
        "LABLOOP_46": 6,
        "DISCOVERYWORLD": 3,
        "HLER_ABLATION": 4,
        "INQUITREE": 7,
        "LMRBENCH": 6,
        "DDOS_AGENT": 3,
    }
    if {key: len(value) for key, value in by_audit.items()} != expected_sizes:
        raise ValueError("audit configuration coverage changed")

    screening = read_csv(SCREENING)
    screening_ids = [row["paper_id"] for row in screening]
    if len(screening) != 45 or len(set(screening_ids)) != 45:
        raise ValueError("rankability screen must contain 45 unique paper records")
    included_ids = {row["candidate_id"] for row in screening if row["decision"] == "include"}
    if included_ids != set(expected_sizes):
        raise ValueError("included screening records and quantitative audits differ")

    pair_rows: list[dict[str, object]] = []
    summaries: list[dict[str, object]] = []
    for audit_id, rows in by_audit.items():
        audit_pairs: list[dict[str, object]] = []
        for i, j in itertools.combinations(rows, 2):
            displayed = strict_relation(i, j, "display")
            target = strict_relation(i, j, "target")
            displayed_dir = direction(displayed)
            target_dir = direction(target)
            if displayed == "no_display":
                status = "no_display"
            elif displayed_dir is None:
                status = "displayed_not_strict"
            elif target_dir == displayed_dir:
                status = "certified"
            elif target_dir is None:
                status = "unresolved"
            else:
                status = "reversed"
            pair = {
                "audit_id": audit_id,
                "evaluation": i["evaluation"],
                "audit_group": i["audit_group"],
                "system_i": i["system_code"],
                "system_i_name": i["system"],
                "system_j": j["system_code"],
                "system_j_name": j["system"],
                "display_relation": displayed,
                "target_relation": target,
                "display_claim_status": status,
                "source_anchor": i["source_anchor"],
            }
            audit_pairs.append(pair)
            pair_rows.append(pair)

        possible = len(audit_pairs)
        target_strict = sum(direction(str(row["target_relation"])) is not None for row in audit_pairs)
        displayed_strict = sum(direction(str(row["display_relation"])) is not None for row in audit_pairs)
        certified = sum(row["display_claim_status"] == "certified" for row in audit_pairs)
        reversed_count = sum(row["display_claim_status"] == "reversed" for row in audit_pairs)
        unresolved = sum(row["display_claim_status"] == "unresolved" for row in audit_pairs)
        summaries.append(
            {
                "audit_id": audit_id,
                "evaluation": rows[0]["evaluation"],
                "audit_group": rows[0]["audit_group"],
                "systems_n": len(rows),
                "possible_pairs_n": possible,
                "identified_strict_orders_n": target_strict,
                "rankability_ratio": f6(target_strict / possible),
                "displayed_strict_pairs_n": displayed_strict,
                "certified_displayed_pairs_n": certified,
                "reversed_displayed_pairs_n": reversed_count,
                "unresolved_displayed_pairs_n": unresolved,
                "rankability_gap": f6(1 - certified / displayed_strict) if displayed_strict else "",
                "endpoint": rows[0]["endpoint"],
                "source_anchor": rows[0]["source_anchor"],
                "scope_boundary": rows[0]["key_boundary"],
            }
        )

    def group_summary(label: str, subset: list[dict[str, object]]) -> dict[str, object]:
        possible = sum(int(row["possible_pairs_n"]) for row in subset)
        identified = sum(int(row["identified_strict_orders_n"]) for row in subset)
        displayed = sum(int(row["displayed_strict_pairs_n"]) for row in subset)
        certified = sum(int(row["certified_displayed_pairs_n"]) for row in subset)
        reversed_count = sum(int(row["reversed_displayed_pairs_n"]) for row in subset)
        unresolved = sum(int(row["unresolved_displayed_pairs_n"]) for row in subset)
        return {
            "audit_group": label,
            "evaluations_n": len(subset),
            "systems_n": sum(int(row["systems_n"]) for row in subset),
            "possible_pairs_n": possible,
            "identified_strict_orders_n": identified,
            "pair_weighted_rankability_ratio": f6(identified / possible),
            "displayed_strict_pairs_n": displayed,
            "certified_displayed_pairs_n": certified,
            "reversed_displayed_pairs_n": reversed_count,
            "unresolved_displayed_pairs_n": unresolved,
            "pair_weighted_rankability_gap": f6(1 - certified / displayed),
            "interpretation": "descriptive coverage of the admitted audits; pairs are dependent and this is not field prevalence; complete-run retention is an algebraic control rather than independent evidence of scientific validity, certified orders hold only for the realized endpoint (which may be a proxy), and finite-sample strict orders may be practically small or statistically uncertain",
        }

    selected = [row for row in summaries if row["audit_group"] == "selected_output"]
    controls = [row for row in summaries if row["audit_group"] == "all_unit_control"]
    group_rows = [
        group_summary("selected_output", selected),
        group_summary("all_unit_control", controls),
        group_summary("all_audits", summaries),
    ]

    # Decision-changing headline checks.
    summary_by_id = {str(row["audit_id"]): row for row in summaries}
    if summary_by_id["MLREPLICATE"]["identified_strict_orders_n"] != 0:
        raise ValueError("MLReplicate no longer has an empty six-system graph")
    if summary_by_id["MLREPLICATE"]["displayed_strict_pairs_n"] != 6:
        raise ValueError("MLReplicate should expose six strict selected-score claims among four reviewed systems")
    if summary_by_id["SCIENCEAGENTBENCH"]["certified_displayed_pairs_n"] != 95:
        raise ValueError("ScienceAgentBench pair support changed")
    if summary_by_id["SCIENCEAGENTBENCH"]["reversed_displayed_pairs_n"] != 6:
        raise ValueError("ScienceAgentBench reversal count changed")
    if summary_by_id["SCIENTISTONE"]["certified_displayed_pairs_n"] != 9:
        raise ValueError("ScientistOne pair support changed")
    expected_strict = {
        "BADSCIENTIST_RATE": 15,
        "SCIINTEGRITY": 21,
        "CORRAL_TASK": 15,
        "LABLOOP_46": 15,
        "DISCOVERYWORLD": 3,
        "HLER_ABLATION": 6,
        "INQUITREE": 21,
        "LMRBENCH": 14,
        "DDOS_AGENT": 3,
    }
    for audit_id, expected in expected_strict.items():
        row = summary_by_id[audit_id]
        if row["identified_strict_orders_n"] != expected:
            raise ValueError(f"{audit_id} identified strict-order count changed")
        if row["certified_displayed_pairs_n"] != expected:
            raise ValueError(f"{audit_id} displayed-edge support changed")
    selected_group = group_rows[0]
    if (
        selected_group["displayed_strict_pairs_n"] != 134
        or selected_group["certified_displayed_pairs_n"] != 119
        or selected_group["reversed_displayed_pairs_n"] != 6
        or selected_group["unresolved_displayed_pairs_n"] != 9
    ):
        raise ValueError("selected-output audit headline changed")
    if (
        group_rows[1]["displayed_strict_pairs_n"] != 214
        or group_rows[1]["certified_displayed_pairs_n"] != 214
    ):
        raise ValueError("a complete-run control has an unsupported displayed edge")

    system_output = []
    for row in systems:
        out = dict(row)
        for field in ["display_lower", "display_upper", "target_lower", "target_upper"]:
            out[field] = f6(out[field] if isinstance(out[field], float) else None)
        system_output.append(out)
    write_csv(DERIVED / "rankability_audit_systems.csv", system_output)
    write_csv(DERIVED / "rankability_audit_pairs.csv", pair_rows)
    write_csv(DERIVED / "rankability_audit_summary.csv", summaries)
    write_csv(DERIVED / "rankability_audit_group_summary.csv", group_rows)

    certificate = {
        "schema": "cross-benchmark-rankability-audit/0.2",
        "search_date": "2026-08-26",
        "formulas": {
            "rankability_ratio": "identified strict target orders / all unordered system pairs",
            "rankability_gap": "1 - same-direction certified displayed strict edges / displayed strict edges",
        },
        "evaluations": summaries,
        "groups": group_rows,
        "headline": {
            "screened_papers": 45,
            "admitted_evaluations": 15,
            "configurations": 100,
            "selected_output_displayed_strict_pairs": 134,
            "selected_output_certified_pairs": 119,
            "selected_output_reversed_pairs": 6,
            "selected_output_unresolved_pairs": 9,
            "selected_output_rankability_gap": 15 / 134,
            "mlreplicate_possible_pairs_identified": "0/15",
        },
        "certification_qualification": "complete-run retention is an algebraic control rather than independent evidence of scientific validity; certified orders hold only for the realized endpoint (which may be a proxy); finite-sample strict orders may be practically small or statistically uncertain",
        "boundary": "census screen of the 44-paper ARDA primary frame plus one targeted current update; endpoint- and configuration-level audit with no pooled capability score or field prevalence claim; complete-run retention is an algebraic control, certified orders hold only for the realized endpoint, and finite-sample orders may be practically small or statistically uncertain",
    }
    (DERIVED / "cross_benchmark_rankability_certificate.json").write_text(
        json.dumps(certificate, indent=2) + "\n", encoding="utf-8"
    )

    print(
        "Built 15-evaluation rankability audit: "
        f"{len(systems)} configurations, {len(pair_rows)} pairs; "
        "selected-output displayed edges 119/134 certified, 6 reversed, 9 unresolved."
    )


if __name__ == "__main__":
    main()
