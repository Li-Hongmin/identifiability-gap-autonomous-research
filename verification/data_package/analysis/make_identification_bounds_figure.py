#!/usr/bin/env python3
"""Create Figure 2: study-specific identified sets and rankability."""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D


ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data" / "derived"
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
        "svg.fonttype": "none",
        "pdf.fonttype": 42,
    }
)

INK = "#263238"
GRID = "#E7EBEF"
POINT = "#315B7D"
PARTIAL = "#8B98A5"
SELECTED = "#D97745"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    capability = read_csv(DERIVED / "capability_identification_bounds.csv")
    rankability = read_csv(DERIVED / "mlreplicate_rankability_bounds.csv")
    edges = read_csv(DERIVED / "mlreplicate_rankability_edges.csv")
    if len(capability) != 9 or len(rankability) != 6 or len(edges) != 15:
        raise ValueError("identification-bound source tables have unexpected row counts")
    if any(row["strict_order_identified"] == "yes" for row in edges):
        raise ValueError("Figure annotation assumes the assumption-free graph has zero edges")

    fig = plt.figure(figsize=(7.205, 3.55))
    gs = fig.add_gridspec(
        1,
        2,
        width_ratios=[1.18, 1],
        left=0.16,
        right=0.985,
        bottom=0.19,
        top=0.78,
        wspace=0.46,
    )

    # Panel a: study-specific finite-design sets. The rows are intentionally
    # not sorted by magnitude because the endpoints are not interchangeable.
    label_order = [
        "MLReplicate aggregate",
        "AI Scientist v1",
        "AI-paper similarity",
        "FAR",
        "Four autonomous research attempts",
        "KOSMOS independent evaluation",
        "Aletheia FirstProof (strict)",
        "Aletheia FirstProof (majority)",
        "Independent AI Scientist evaluation",
    ]
    by_name = {row["short_name"]: row for row in capability}
    rows = [by_name[name] for name in label_order]
    display_names = [
        "MLReplicate\nvalid manuscript",
        "AI Scientist v1\nvalid manuscript",
        "Similarity-check\npass dimension",
        "FAR correct\nresolution",
        "Four attempts\nvalid artifact",
        "KOSMOS clearly\nsupported",
        "Aletheia strict\nvalid proof",
        "Aletheia majority\nvalid proof",
        "Independent eval.\nnumerically sound",
    ]
    ax = fig.add_subplot(gs[0, 0])
    y = np.arange(len(rows))
    for idx, row in enumerate(rows):
        lower = float(row["identified_lower"])
        upper = float(row["identified_upper"])
        is_point = abs(upper - lower) < 1e-12
        color = POINT if is_point else (SELECTED if "selected" in row["endpoint_class"] else PARTIAL)
        if is_point:
            ax.scatter([lower], [idx], s=28, marker="D", color=color, edgecolor="white", linewidth=0.6, zorder=3)
            ax.text(lower + 0.025, idx, f"{lower:.2f}", va="center", fontsize=5.8, color=INK)
        else:
            ax.plot([lower, upper], [idx, idx], color=color, linewidth=4.2, solid_capstyle="round", zorder=2)
            ax.scatter([lower, upper], [idx, idx], s=13, color=color, edgecolor="white", linewidth=0.5, zorder=3)
            ax.text(min(upper + 0.025, 0.96), idx, f"[{lower:.2f}, {upper:.2f}]", va="center", fontsize=5.5, color=INK)
    ax.set_yticks(y, display_names, fontsize=5.8)
    ax.invert_yaxis()
    ax.set_xlim(0, 1)
    ax.set_xticks(np.linspace(0, 1, 6))
    ax.grid(axis="x", color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)
    ax.set_xlabel("Study-specific identified set")
    ax.set_title("Finite-design validity sets are often wide", loc="left", fontweight="bold")
    ax.text(-0.13, 1.06, "a", transform=ax.transAxes, fontsize=9, fontweight="bold", va="top")

    # Panel b: all six systems share the same eight source papers, but only ten
    # automated acceptances receive human scores. Intervals use normalized
    # scores in [0, 1], no-output=0, and leave unreviewed completed scores free.
    system_order = ["AIS1", "AIS2", "AL", "AIR", "CR", "TS"]
    short_labels = {
        "AIS1": "AI Scientist v1",
        "AIS2": "AI Scientist v2",
        "AL": "Agent Laboratory",
        "AIR": "AI Researcher",
        "CR": "CycleResearcher",
        "TS": "Tiny Scientist",
    }
    rank_by_code = {row["system_code"]: row for row in rankability}
    rows = [rank_by_code[code] for code in system_order]
    ax = fig.add_subplot(gs[0, 1])
    y = np.arange(len(rows))
    for idx, row in enumerate(rows):
        lower = float(row["identified_lower"])
        upper = float(row["identified_upper"])
        ax.plot([lower, upper], [idx, idx], color=PARTIAL, linewidth=5, solid_capstyle="round", zorder=2)
        ax.scatter([lower, upper], [idx, idx], s=14, color=PARTIAL, edgecolor="white", linewidth=0.5, zorder=3)
        if row["selected_available_score_mean"]:
            selected_mean = float(row["selected_available_score_mean"])
            ax.scatter([selected_mean], [idx], marker="o", s=28, color=SELECTED, edgecolor="white", linewidth=0.7, zorder=4)
    ax.set_yticks(y, [short_labels[code] for code in system_order], fontsize=6.1)
    ax.invert_yaxis()
    ax.set_xlim(0, 1)
    ax.set_xticks(np.linspace(0, 1, 6))
    ax.grid(axis="x", color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)
    ax.set_xlabel("Mean normalized human score per target")
    ax.set_title("Selected-score order is not rank-identifying", loc="left", fontweight="bold")
    ax.text(-0.17, 1.06, "b", transform=ax.transAxes, fontsize=9, fontweight="bold", va="top")
    ax.text(
        0.03,
        -0.42,
        "Selected means: CR > AL > TS > AIR\nSharp full-attempt graph: 0 / 15 pairwise edges",
        transform=ax.transAxes,
        fontsize=6,
        color=INK,
        va="top",
    )
    ax.legend(
        handles=[
            Line2D([0], [0], color=PARTIAL, linewidth=5, label="sharp full-attempt set"),
            Line2D([0], [0], marker="o", color="none", markerfacecolor=SELECTED, markeredgecolor="white", markersize=5, label="selected-only mean"),
        ],
        loc="lower center",
        bbox_to_anchor=(0.5, -0.43),
        frameon=False,
        ncol=2,
        fontsize=5.7,
        handlelength=1.6,
    )

    fig.suptitle(
        "Denominator recovery turns selected scores into identified sets, not a total leaderboard",
        x=0.07,
        y=0.96,
        ha="left",
        fontsize=9.8,
        fontweight="bold",
        color=INK,
    )
    fig.text(
        0.16,
        0.84,
        "Plug-in finite-design sets; rows in panel a use different endpoints and are not comparable or population estimates",
        ha="left",
        fontsize=6.1,
        color="#54616B",
    )

    OUT.mkdir(parents=True, exist_ok=True)
    for suffix, kwargs in [
        ("svg", {}),
        ("pdf", {}),
        ("tiff", {"dpi": 600, "pil_kwargs": {"compression": "tiff_lzw"}}),
    ]:
        fig.savefig(OUT / f"figure2_identification_bounds.{suffix}", bbox_inches="tight", facecolor="white", **kwargs)
    fig.savefig(OUT / "figure2_identification_bounds_preview.png", dpi=220, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"wrote Figure 2 identification-bound exports to {OUT}")


if __name__ == "__main__":
    main()
