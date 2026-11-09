#!/usr/bin/env python3
"""Create the main-text Figure 1 from the cross-benchmark rankability audit."""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "derived" / "rankability_audit_summary.csv"
OUT = ROOT / "figures"

mpl.rcParams.update(
    {
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans", "sans-serif"],
        "font.size": 7,
        "axes.titlesize": 8,
        "axes.labelsize": 7,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "legend.frameon": False,
        "svg.fonttype": "none",
        "pdf.fonttype": 42,
    }
)

CERTIFIED = "#3775BA"
REVERSED = "#B64342"
UNRESOLVED = "#8B98A5"
INK = "#263238"
MUTED = "#5F6B73"
GRID = "#E7EBEF"

ORDER = [
    "MLREPLICATE",
    "SCIENTISTONE",
    "SCIENCEAGENTBENCH",
    "BADSCIENTIST_RATE",
    "DELTAML_4X6H",
    "MLAGENTBENCH",
    "SPATIALBENCH",
    "SCIINTEGRITY",
    "CORRAL_TASK",
    "LABLOOP_46",
    "DISCOVERYWORLD",
    "HLER_ABLATION",
    "INQUITREE",
    "LMRBENCH",
    "DDOS_AGENT",
]

LABELS = {
    "MLREPLICATE": "MLReplicate",
    "SCIENCEAGENTBENCH": "ScienceAgentBench",
    "SCIENTISTONE": "ScientistOne",
    "BADSCIENTIST_RATE": "BadScientist",
    "DELTAML_4X6H": "DeltaML 4@6h",
    "MLAGENTBENCH": "MLAgentBench",
    "SPATIALBENCH": "SpatialBench-Long",
    "SCIINTEGRITY": "SciIntegrity-Bench",
    "CORRAL_TASK": "Corral",
    "LABLOOP_46": "Lab-in-the-loop",
    "DISCOVERYWORLD": "DiscoveryWorld",
    "HLER_ABLATION": "HLER ablation",
    "INQUITREE": "InquiTree",
    "LMRBENCH": "LMR-Bench",
    "DDOS_AGENT": "Distributed Denial of Science",
}


def read_rows() -> list[dict[str, str]]:
    with SOURCE.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    by_id = {row["audit_id"]: row for row in rows}
    if len(rows) != 15 or set(by_id) != set(ORDER):
        raise ValueError("Figure 1 source does not contain the expected 15 audits")
    return [by_id[audit_id] for audit_id in ORDER]


def main() -> None:
    rows = read_rows()
    fig, ax = plt.subplots(figsize=(7.205, 4.75))
    fig.subplots_adjust(left=0.255, right=0.94, bottom=0.17, top=0.82)

    y = np.arange(len(rows))
    certified_share = []
    reversed_share = []
    unresolved_share = []
    for row in rows:
        displayed = int(row["displayed_strict_pairs_n"])
        if displayed <= 0:
            raise ValueError(f"{row['audit_id']} has no displayed strict pair")
        certified_share.append(int(row["certified_displayed_pairs_n"]) / displayed)
        reversed_share.append(int(row["reversed_displayed_pairs_n"]) / displayed)
        unresolved_share.append(int(row["unresolved_displayed_pairs_n"]) / displayed)

    ax.barh(y, certified_share, color=CERTIFIED, edgecolor="white", linewidth=0.5, height=0.66)
    ax.barh(
        y,
        reversed_share,
        left=certified_share,
        color=REVERSED,
        edgecolor="white",
        linewidth=0.5,
        height=0.66,
        hatch="////",
    )
    second_left = np.asarray(certified_share) + np.asarray(reversed_share)
    ax.barh(
        y,
        unresolved_share,
        left=second_left,
        color=UNRESOLVED,
        edgecolor="white",
        linewidth=0.5,
        height=0.66,
        hatch="...",
    )

    ax.set_yticks(y, [LABELS[row["audit_id"]] for row in rows], fontsize=6.4)
    ax.invert_yaxis()
    ax.set_xlim(0, 1.18)
    ax.set_xticks(np.linspace(0, 1, 6), ["0", "20", "40", "60", "80", "100"])
    ax.set_xlabel("Displayed strict pairwise claims supported after denominator recovery (%)")
    ax.grid(axis="x", color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0)

    for idx, row in enumerate(rows):
        certified = int(row["certified_displayed_pairs_n"])
        displayed = int(row["displayed_strict_pairs_n"])
        rho = float(row["rankability_ratio"])
        ax.text(1.045, idx, f"{certified}/{displayed}", va="center", ha="center", fontsize=5.9, color=INK)
        ax.text(1.145, idx, f"{rho:.2f}", va="center", ha="center", fontsize=5.9, color=MUTED)

    ax.text(1.045, -1.0, "support", va="bottom", ha="center", fontsize=5.8, color=MUTED, fontweight="bold")
    ax.text(1.145, -1.0, r"$\rho$", va="bottom", ha="center", fontsize=5.8, color=MUTED, fontweight="bold")

    divider = 3.5
    ax.axhline(divider, color="#C8D0D6", linewidth=0.8)
    ax.text(
        -0.225,
        1.5,
        "selected or\nmissing output",
        transform=ax.get_yaxis_transform(),
        ha="right",
        va="center",
        fontsize=5.8,
        color=MUTED,
    )
    ax.text(
        -0.225,
        9.5,
        "all-run or\nnear-complete",
        transform=ax.get_yaxis_transform(),
        ha="right",
        va="center",
        fontsize=5.8,
        color=MUTED,
    )

    fig.suptitle(
        "Rankability loss is concentrated in particular observation designs",
        x=0.07,
        y=0.965,
        ha="left",
        fontsize=9.8,
        fontweight="bold",
        color=INK,
    )
    fig.text(
        0.07,
        0.885,
        "Fifteen endpoint-specific audits from a 45-paper screen; ρ is the fraction of all unordered pairs with an identified strict order",
        ha="left",
        fontsize=6.2,
        color=MUTED,
    )
    ax.legend(
        handles=[
            Patch(facecolor=CERTIFIED, edgecolor="white", label="same-direction certified"),
            Patch(facecolor=REVERSED, edgecolor="white", hatch="////", label="reversed"),
            Patch(facecolor=UNRESOLVED, edgecolor="white", hatch="...", label="unresolved"),
        ],
        loc="upper center",
        bbox_to_anchor=(0.47, -0.14),
        ncol=3,
        fontsize=6,
        handlelength=1.5,
    )

    fig.text(
        0.94,
        0.012,
        "Pair counts are dependent and endpoint-specific; this is not field prevalence.",
        ha="right",
        fontsize=5.6,
        color=MUTED,
    )

    OUT.mkdir(parents=True, exist_ok=True)
    for suffix, kwargs in [
        ("svg", {}),
        ("pdf", {}),
        ("tiff", {"dpi": 600, "pil_kwargs": {"compression": "tiff_lzw"}}),
    ]:
        fig.savefig(OUT / f"figure1_rankability_audit.{suffix}", bbox_inches="tight", facecolor="white", **kwargs)
    fig.savefig(OUT / "figure1_rankability_audit_preview.png", dpi=240, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"wrote Figure 1 rankability-audit exports to {OUT}")


if __name__ == "__main__":
    main()
