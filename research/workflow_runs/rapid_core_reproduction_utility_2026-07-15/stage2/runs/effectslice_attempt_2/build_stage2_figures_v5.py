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
DEFAULT_V4_SUMMARY = RUN_ROOT / "logs" / "confirmation_v4_summary.json"
DEFAULT_V5_ANALYSIS = RUN_ROOT / "derived" / "confirmation_v5r2" / "analysis.json"
DEFAULT_FIGURE = RUN_ROOT / "figures" / "effectslice_v5_finite_schedule.png"
DEFAULT_REPORT = RUN_ROOT / "figures" / "plot_aggregation_report_v5.json"
V4_SCHEMA = "effectslice-stage2-confirmation-summary.v4"
V5_SCHEMA = "effectslice-confirmation-v5r2-analysis.v1"
FAMILY_ORDER = (
    "snap_mfse",
    "toolformer_negative",
    "toolformer_natural",
    "toolformer_positive",
    "toolformer_identity",
)
SHORT_LABELS = {
    "snap_mfse": "SNAP\nprefix 03",
    "toolformer_negative": "Toolformer\nprefix 01",
    "toolformer_natural": "Toolformer\nprefix 04",
    "toolformer_positive": "Planted\npositive",
    "toolformer_identity": "Identity",
}
CONDITION_COLORS = {"B": "#6B7280", "F": "#007C83", "S": "#D55E00"}


def _sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _load(path: Path, schema: str, label: str) -> tuple[Path, dict[str, Any]]:
    source = Path(path).resolve()
    payload = json.loads(source.read_text(encoding="utf-8"))
    if payload.get("schema_version") != schema:
        raise ValueError(f"unexpected {label} schema")
    return source, payload


def _normalize(
    v4: dict[str, Any], v5: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, list[dict[str, Any]]]]:
    families = {row["family_key"]: row for row in v4["families"]}
    expected_v4 = {
        "snap_mfse",
        "toolformer_negative",
        "toolformer_positive",
        "toolformer_identity",
    }
    if set(families) != expected_v4:
        raise ValueError("the V4 figure family set changed")
    if set(v5["family_summaries"]) != {"toolformer_natural"}:
        raise ValueError("the V5 figure family set changed")
    families["toolformer_natural"] = v5["family_summaries"]["toolformer_natural"]

    blocks: dict[str, list[dict[str, Any]]] = {key: [] for key in FAMILY_ORDER}
    for row in v4["block_scores"]:
        blocks[row["family_key"]].append(
            {"replicate_id": row["replicate_id"], "task_scores": row["task_scores"]}
        )
    for row in v5["blocks"]:
        blocks["toolformer_natural"].append(
            {
                "replicate_id": row["replicate_id"],
                "task_scores": {
                    condition: row["condition_results"][condition]["task_score"]
                    for condition in "BFS"
                },
            }
        )
    return families, blocks


def build_figure(
    v4_summary_path: Path,
    v5_analysis_path: Path,
    output_path: Path,
    report_path: Path,
) -> dict[str, str]:
    v4_source, v4 = _load(v4_summary_path, V4_SCHEMA, "V4 summary")
    v5_source, v5 = _load(v5_analysis_path, V5_SCHEMA, "V5 analysis")
    families, blocks = _normalize(v4, v5)

    fig = plt.figure(figsize=(11.3, 3.9), constrained_layout=True)
    grid = fig.add_gridspec(1, 3, width_ratios=(1.4, 1.25, 1.35))
    x = np.arange(len(FAMILY_ORDER), dtype=float)

    ax1 = fig.add_subplot(grid[0, 0])
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
            color=CONDITION_COLORS[condition],
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
                fontsize=6.1,
                rotation=90,
            )
    ax1.plot(
        [-0.48, 3.48],
        [16 / 18, 16 / 18],
        color="#222222",
        linestyle="--",
        linewidth=0.9,
    )
    ax1.set_ylim(0, 1.16)
    ax1.set_ylabel("Operational success fraction")
    ax1.set_xticks(x, [SHORT_LABELS[key] for key in FAMILY_ORDER], fontsize=7.2)
    ax1.legend(frameon=False, ncol=3, loc="upper left")
    ax1.set_title("(a) Registered condition outcomes", loc="left", fontsize=10)
    ax1.spines[["top", "right"]].set_visible(False)

    ax2 = fig.add_subplot(grid[0, 1])
    markers = dict(
        zip(FAMILY_ORDER, ("o", "s", "P", "^", "D"))
    )
    colors = dict(
        zip(FAMILY_ORDER, ("#007C83", "#CC79A7", "#2F6B3C", "#E69F00", "#4C78A8"))
    )
    for index, key in enumerate(FAMILY_ORDER):
        rows = sorted(blocks[key], key=lambda row: row["replicate_id"])
        offsets = np.linspace(-0.18, 0.18, len(rows))
        deltas = [row["task_scores"]["S"] - row["task_scores"]["F"] for row in rows]
        ax2.scatter(
            index + offsets,
            deltas,
            s=27,
            marker=markers[key],
            color=colors[key],
            edgecolor="white",
            linewidth=0.45,
            alpha=0.88,
        )
        mean = float(np.mean(deltas))
        ax2.plot(
            [index - 0.22, index + 0.22],
            [mean, mean],
            color="#111111",
            linewidth=1.5,
        )
    ax2.axhline(0, color="#555555", linestyle="--", linewidth=0.9)
    ax2.set_xticks(x, [SHORT_LABELS[key] for key in FAMILY_ORDER], fontsize=7.2)
    ax2.set_ylabel("Registered score difference, S - F")
    ax2.set_ylim(-1.08, 1.08)
    ax2.set_title("(b) S-F private-score differences", loc="left", fontsize=10)
    ax2.spines[["top", "right"]].set_visible(False)

    ax3 = fig.add_subplot(grid[0, 2])
    decision_keys = FAMILY_ORDER[:4]
    check_keys = (
        "baseline_ceiling",
        "full_sufficiency",
        "slice_sufficiency",
        "slice_shortfall",
    )
    matrix = np.array(
        [
            [
                int(bool(families[key]["admission_decision"]["checks"][check]))
                for check in check_keys
            ]
            + [int(bool(families[key]["admission_decision"]["passed"]))]
            for key in decision_keys
        ],
        dtype=int,
    )
    cmap = matplotlib.colors.ListedColormap(["#C44E52", "#55A868"])
    ax3.imshow(matrix, cmap=cmap, vmin=0, vmax=1, aspect="auto")
    for row in range(matrix.shape[0]):
        for column in range(matrix.shape[1]):
            if column < matrix.shape[1] - 1:
                label = "Pass" if matrix[row, column] else "Fail"
            elif decision_keys[row] == "toolformer_positive":
                label = "Pass" if matrix[row, column] else "Fail"
            else:
                label = "Admit" if matrix[row, column] else "Reject"
            ax3.text(
                column,
                row,
                label,
                ha="center",
                va="center",
                color="white",
                fontsize=7.0,
                fontweight="bold",
            )
    ax3.set_xticks(
        range(5),
        ["B <= 2", "F >= 16", "S >= 16", "F-S <= 2*", "Status"],
        rotation=35,
        ha="right",
    )
    ax3.set_yticks(
        range(4),
        [SHORT_LABELS[key].replace("\n", " ") for key in decision_keys],
        fontsize=7.2,
    )
    identity = families["toolformer_identity"]["identity_instrumentation"]
    ax3.set_xlabel(
        f"Identity: {identity['full_slice_success_matches']}/6 matches, "
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
        "schema_version": "effectslice-plot-aggregation-report.v5",
        "sources": {
            "v4_summary": {"path": v4_source.as_posix(), "sha256": _sha256(v4_source)},
            "v5_analysis": {"path": v5_source.as_posix(), "sha256": _sha256(v5_source)},
        },
        "figure": {"path": destination.as_posix(), "sha256": _sha256(destination)},
        "panels": {
            "a": "B/F/S success fractions for V4 families and the later V5 candidate",
            "b": "all registered per-block S-F private-score differences",
            "c": (
                "finite-schedule SLA fields and candidate/control status; V4 and V5 were separately registered, "
                "and the starred F-S field is implied by S >= 16 at n = 18"
            ),
        },
        "invented_values": False,
        "population_inference_shown": False,
        "v5_selected_after_v4_disclosed": True,
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
    parser = argparse.ArgumentParser(description="Build final V4+V5 manuscript figure")
    parser.add_argument("--v4-summary", type=Path, default=DEFAULT_V4_SUMMARY)
    parser.add_argument("--v5-analysis", type=Path, default=DEFAULT_V5_ANALYSIS)
    parser.add_argument("--output", type=Path, default=DEFAULT_FIGURE)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()
    print(
        json.dumps(
            build_figure(
                args.v4_summary,
                args.v5_analysis,
                args.output,
                args.report,
            ),
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
