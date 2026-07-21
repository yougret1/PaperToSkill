from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


RUN_ROOT = Path(__file__).resolve().parent
DEFAULT_SUMMARY = RUN_ROOT / "logs" / "confirmation_v4_summary.json"
DEFAULT_FIGURE = RUN_ROOT / "figures" / "effectslice_v4_finite_schedule.png"
DEFAULT_REPORT = RUN_ROOT / "figures" / "plot_aggregation_report_v4.json"
SUMMARY_SCHEMA = "effectslice-stage2-confirmation-summary.v4"
FAMILY_ORDER = (
    "snap_mfse",
    "toolformer_negative",
    "toolformer_positive",
    "toolformer_identity",
)
SHORT_LABELS = {
    "snap_mfse": "SNAP\nreal",
    "toolformer_negative": "Toolformer\nreal",
    "toolformer_positive": "Planted\npositive",
    "toolformer_identity": "Identity",
}
COLORS = {"B": "#6B7280", "F": "#007C83", "S": "#D55E00"}


def _sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _load(path: Path) -> tuple[Path, dict[str, Any]]:
    source = Path(path).resolve()
    payload = json.loads(source.read_text(encoding="utf-8"))
    if payload.get("schema_version") != SUMMARY_SCHEMA:
        raise ValueError("unexpected confirmation V4 summary schema")
    if payload.get("registered_blocks") != 60:
        raise ValueError("the V4 figure requires all 60 blocks")
    return source, payload


def build_figure(summary_path: Path, output_path: Path, report_path: Path) -> dict[str, str]:
    source, summary = _load(summary_path)
    families = {row["family_key"]: row for row in summary["families"]}
    if set(families) != set(FAMILY_ORDER):
        raise ValueError("the V4 figure family set changed")

    fig = plt.figure(figsize=(11.2, 3.65), constrained_layout=True)
    grid = fig.add_gridspec(1, 3, width_ratios=(1.25, 1.2, 1.35))

    ax1 = fig.add_subplot(grid[0, 0])
    x = np.arange(len(FAMILY_ORDER), dtype=float)
    width = 0.23
    for offset, condition in zip((-width, 0.0, width), "BFS"):
        fractions = [
            families[key]["operational_success_counts"][condition]
            / families[key]["registered_blocks"]
            for key in FAMILY_ORDER
        ]
        bars = ax1.bar(
            x + offset,
            fractions,
            width,
            label=condition,
            color=COLORS[condition],
            edgecolor="white",
            linewidth=0.6,
        )
        for bar, key in zip(bars, FAMILY_ORDER):
            count = families[key]["operational_success_counts"][condition]
            total = families[key]["registered_blocks"]
            ax1.text(
                bar.get_x() + bar.get_width() / 2,
                min(1.04, bar.get_height() + 0.025),
                f"{count}/{total}",
                ha="center",
                va="bottom",
                fontsize=6.5,
                rotation=90,
            )
    ax1.plot(
        [-0.48, 2.48],
        [16 / 18, 16 / 18],
        color="#222222",
        linestyle="--",
        linewidth=0.9,
    )
    ax1.set_ylim(0, 1.16)
    ax1.set_ylabel("Operational success fraction")
    ax1.set_xticks(x, [SHORT_LABELS[key] for key in FAMILY_ORDER])
    ax1.legend(frameon=False, ncol=3, loc="upper left")
    ax1.set_title("(a) Registered condition outcomes", loc="left", fontsize=10)
    ax1.spines[["top", "right"]].set_visible(False)

    ax2 = fig.add_subplot(grid[0, 1])
    offsets = np.linspace(-0.18, 0.18, 18)
    marker_by_key = {
        "snap_mfse": "o",
        "toolformer_negative": "s",
        "toolformer_positive": "^",
        "toolformer_identity": "D",
    }
    color_by_key = {
        "snap_mfse": "#007C83",
        "toolformer_negative": "#CC79A7",
        "toolformer_positive": "#009E73",
        "toolformer_identity": "#E69F00",
    }
    blocks_by_family: dict[str, list[dict[str, Any]]] = {key: [] for key in FAMILY_ORDER}
    for row in summary["block_scores"]:
        blocks_by_family[row["family_key"]].append(row)
    for index, key in enumerate(FAMILY_ORDER):
        rows = sorted(blocks_by_family[key], key=lambda row: row["replicate_id"])
        local_offsets = offsets if len(rows) == 18 else np.linspace(-0.12, 0.12, len(rows))
        deltas = [row["task_scores"]["S"] - row["task_scores"]["F"] for row in rows]
        ax2.scatter(
            index + local_offsets,
            deltas,
            s=30,
            marker=marker_by_key[key],
            color=color_by_key[key],
            edgecolor="white",
            linewidth=0.45,
            alpha=0.88,
        )
        ax2.plot(
            [index - 0.22, index + 0.22],
            [float(np.mean(deltas)), float(np.mean(deltas))],
            color="#111111",
            linewidth=1.5,
        )
    ax2.axhline(0, color="#555555", linestyle="--", linewidth=0.9)
    ax2.set_xticks(x, [SHORT_LABELS[key] for key in FAMILY_ORDER])
    ax2.set_ylabel("Registered score difference, S - F")
    ax2.set_ylim(-1.08, 1.08)
    ax2.set_title("(b) Registered S-F private-score differences", loc="left", fontsize=10)
    ax2.spines[["top", "right"]].set_visible(False)

    ax3 = fig.add_subplot(grid[0, 2])
    decision_keys = FAMILY_ORDER[:3]
    check_keys = ("baseline_ceiling", "full_sufficiency", "slice_sufficiency", "slice_shortfall")
    matrix = np.array(
        [
            [int(bool(families[key]["admission_decision"]["checks"][check])) for check in check_keys]
            + [int(bool(families[key]["admission_decision"]["passed"]))]
            for key in decision_keys
        ],
        dtype=int,
    )
    cmap = matplotlib.colors.ListedColormap(["#C44E52", "#55A868"])
    ax3.imshow(matrix, cmap=cmap, vmin=0, vmax=1, aspect="auto")
    for row in range(matrix.shape[0]):
        for column in range(matrix.shape[1]):
            ax3.text(
                column,
                row,
                "Pass" if matrix[row, column] else "Fail",
                ha="center",
                va="center",
                color="white",
                fontsize=7.2,
                fontweight="bold",
            )
    ax3.set_xticks(
        range(5),
        ["B <= 2", "F >= 16", "S >= 16", "F-S <= 2*", "Admit"],
        rotation=35,
        ha="right",
    )
    ax3.set_yticks(range(3), [SHORT_LABELS[key].replace("\n", " ") for key in decision_keys])
    identity = families["toolformer_identity"]["identity_instrumentation"]
    ax3.set_xlabel(
        f"Identity instrumentation: {identity['full_slice_success_matches']}/6 matches, "
        f"count gap {identity['full_slice_success_count_gap']} (Pass)",
        fontsize=7.5,
    )
    ax3.set_title("(c) Frozen engineering SLA", loc="left", fontsize=10)
    ax3.tick_params(length=0)
    for spine in ax3.spines.values():
        spine.set_visible(False)

    destination = Path(output_path).resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(destination, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)

    report = {
        "schema_version": "effectslice-plot-aggregation-report.v4",
        "source": {"path": source.as_posix(), "sha256": _sha256(source)},
        "figure": {"path": destination.as_posix(), "sha256": _sha256(destination)},
        "panels": {
            "a": "B/F/S operational success fractions with exact count annotations",
            "b": "all registered per-block private-score differences between S and F",
            "c": (
                "pre-registered finite-schedule SLA fields and identity instrumentation; "
                "the starred F-S field is implied by S >= 16 at n = 18"
            ),
        },
        "invented_values": False,
        "population_inference_shown": False,
    }
    report_destination = Path(report_path).resolve()
    report_destination.parent.mkdir(parents=True, exist_ok=True)
    report_destination.write_text(
        json.dumps(report, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return {"figure": destination.as_posix(), "report": report_destination.as_posix()}


def main() -> int:
    parser = argparse.ArgumentParser(description="Build final V4 manuscript figure")
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument("--output", type=Path, default=DEFAULT_FIGURE)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()
    print(json.dumps(build_figure(args.summary, args.output, args.report), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
