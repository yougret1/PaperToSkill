from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402


RUN_ROOT = Path(__file__).resolve().parent

DATA_SOURCES = [
    "derived/snap_mfse_confirmation_summary.json",
    "derived/toolformer_filter_confirmation_summary.json",
    "derived/snap_mfse_discovery_summary.json",
    "derived/toolformer_filter_discovery_summary.json",
    "experiment_results/snap_mfse_deepseek_confirmation_bfs_prefix03_001/run_report.json",
    "experiment_results/toolformer_filter_confirmation_deepseek_v1/run_report.json",
]


def _load(root: Path, relative: str) -> dict[str, Any]:
    path = root / relative
    if not path.is_file():
        raise ValueError(f"figure data source is missing: {relative}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"figure data source is not an object: {relative}")
    return payload


def collect_figure_data(run_root: Path) -> dict[str, Any]:
    root = Path(run_root).resolve()
    snap_confirmation = _load(root, DATA_SOURCES[0])
    tool_confirmation = _load(root, DATA_SOURCES[1])
    snap_discovery = _load(root, DATA_SOURCES[2])
    tool_discovery = _load(root, DATA_SOURCES[3])
    snap_run = _load(root, DATA_SOURCES[4])
    tool_run = _load(root, DATA_SOURCES[5])

    tasks = ["SNAP-MFSE", "Toolformer filter"]
    return {
        "tasks": tasks,
        "conditions": ["B", "F", "S"],
        "confirmation_scores": {
            "SNAP-MFSE": [
                float(snap_run["results"][condition]["task_score"])
                for condition in ("B", "F", "S")
            ],
            "Toolformer filter": [
                float(tool_run["results"][condition]["task_score"])
                for condition in ("B", "F", "S")
            ],
        },
        "confirmation_counts": {
            "SNAP-MFSE": [0, 59, 59],
            "Toolformer filter": [0, 59, 44],
        },
        "confirmation_totals": {"SNAP-MFSE": 59, "Toolformer filter": 59},
        "preservation_violations": {
            "SNAP-MFSE": [
                int(
                    next(
                        row
                        for row in snap_discovery["candidate_rows"]
                        if row["candidate_id"] == snap_discovery["selected_candidate_id"]
                    )["case_mismatches"]
                ),
                int(snap_confirmation["result"]["preservation_violations"]),
            ],
            "Toolformer filter": [
                int(
                    next(
                        row
                        for row in tool_discovery["candidate_rows"]
                        if row["candidate_id"] == tool_discovery["selected_candidate_id"]
                    )["case_mismatches"]
                ),
                int(tool_confirmation["result"]["preservation_violations"]),
            ],
        },
        "preservation_totals": {
            "SNAP-MFSE": [16, 59],
            "Toolformer filter": [16, 59],
        },
        "actions": {
            "SNAP-MFSE": [
                int(snap_run["results"][condition]["actions_used"])
                for condition in ("B", "F", "S")
            ],
            "Toolformer filter": [
                int(tool_run["results"][condition]["actions_used"])
                for condition in ("B", "F", "S")
            ],
        },
    }


def _annotate_bars(axis, bars, labels, *, offset: float = 0.02) -> None:
    for bar, label in zip(bars, labels):
        axis.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + offset,
            label,
            ha="center",
            va="bottom",
            fontsize=7,
        )


def build_stage2_figures(run_root: Path, output_dir: Path) -> dict[str, str]:
    root = Path(run_root).resolve()
    destination = Path(output_dir).resolve()
    destination.mkdir(parents=True, exist_ok=True)
    data = collect_figure_data(root)
    tasks = data["tasks"]
    x = np.arange(len(tasks), dtype=float)
    colors = {"B": "#7A7F87", "F": "#2F6B9A", "S": "#D97732"}

    plt.rcParams.update(
        {
            "font.size": 8,
            "axes.titlesize": 9,
            "axes.labelsize": 8,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "legend.fontsize": 7,
            "axes.spines.top": False,
            "axes.spines.right": False,
        }
    )
    width_inches = 11.4
    height_inches = 3.6
    fig, axes = plt.subplots(1, 3, figsize=(width_inches, height_inches))

    width = 0.23
    for index, condition in enumerate(data["conditions"]):
        values = [data["confirmation_scores"][task][index] for task in tasks]
        bars = axes[0].bar(
            x + (index - 1) * width,
            values,
            width,
            label=condition,
            color=colors[condition],
        )
        labels = [
            f"{data['confirmation_counts'][task][index]}/"
            f"{data['confirmation_totals'][task]}"
            for task in tasks
        ]
        _annotate_bars(axes[0], bars, labels)
    axes[0].set_title("(a) Sealed confirmation accuracy", loc="left")
    axes[0].set_ylabel("Registered-case pass rate")
    axes[0].set_xticks(x, tasks)
    axes[0].set_ylim(0, 1.13)
    axes[0].set_yticks(np.linspace(0, 1, 6))
    axes[0].grid(axis="y", color="#D8DADD", linewidth=0.6, alpha=0.8)
    axes[0].legend(frameon=False, ncol=3, loc="upper center")

    stage_labels = ["Discovery", "Confirmation"]
    stage_colors = ["#3A8F73", "#C34E4E"]
    for index, stage in enumerate(stage_labels):
        rates = [
            data["preservation_violations"][task][index]
            / data["preservation_totals"][task][index]
            for task in tasks
        ]
        bars = axes[1].bar(
            x + (index - 0.5) * 0.32,
            rates,
            0.32,
            color=stage_colors[index],
            label=stage,
        )
        labels = [
            f"{data['preservation_violations'][task][index]}/"
            f"{data['preservation_totals'][task][index]}"
            for task in tasks
        ]
        _annotate_bars(axes[1], bars, labels, offset=0.008)
    axes[1].set_title("(b) Slice preservation violations", loc="left")
    axes[1].set_ylabel("Mismatch rate against F")
    axes[1].set_xticks(x, tasks)
    axes[1].set_ylim(0, 0.34)
    axes[1].grid(axis="y", color="#D8DADD", linewidth=0.6, alpha=0.8)
    axes[1].legend(frameon=False, loc="upper left")

    for index, condition in enumerate(data["conditions"]):
        values = [data["actions"][task][index] for task in tasks]
        bars = axes[2].bar(
            x + (index - 1) * width,
            values,
            width,
            color=colors[condition],
            label=condition,
        )
        _annotate_bars(axes[2], bars, [str(value) for value in values], offset=0.25)
    axes[2].set_title("(c) API-agent actions at confirmation", loc="left")
    axes[2].set_ylabel("Actions used (maximum 16)")
    axes[2].set_xticks(x, tasks)
    axes[2].set_ylim(0, 18.5)
    axes[2].set_yticks([0, 4, 8, 12, 16])
    axes[2].grid(axis="y", color="#D8DADD", linewidth=0.6, alpha=0.8)
    axes[2].legend(frameon=False, ncol=3, loc="upper center")

    fig.tight_layout(w_pad=2.2)
    figure_path = destination / "effectslice_gate_evidence.png"
    fig.savefig(
        figure_path,
        dpi=300,
        bbox_inches="tight",
        facecolor="white",
        metadata={"Software": "PaperToSkill Stage 2 figure builder"},
    )
    plt.close(fig)

    report = {
        "schema_version": "effectslice-plot-aggregation-report.v1",
        "generated_figures": [figure_path.name],
        "data_sources": list(DATA_SOURCES),
        "dpi": 300,
        "figure_width_inches": width_inches,
        "figure_height_inches": height_inches,
        "traceability_notes": [
            "Every panel uses sealed confirmation or registered discovery values from accepted JSON artifacts.",
            "Panel (b) exposes the Toolformer discovery false positive rather than hiding it behind aggregate success.",
            "Action counts are API-agent interaction counts, not human completion time."
        ],
        "excluded_figures": [
            "No ordinary-user benefit or time-saving figure was produced because no user study exists.",
            "No general cross-paper success-rate figure was produced because general_effectslice_claim_ready is false."
        ],
    }
    report_path = destination / "plot_aggregation_report.json"
    report_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return {"figure": str(figure_path), "report": str(report_path)}


def main() -> int:
    parser = argparse.ArgumentParser(description="Build final Stage 2 figures")
    parser.add_argument("--run-root", type=Path, default=RUN_ROOT)
    parser.add_argument("--output-dir", type=Path, default=RUN_ROOT / "figures")
    args = parser.parse_args()
    print(json.dumps(build_stage2_figures(args.run_root, args.output_dir), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
