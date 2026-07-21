from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402


RUN_ROOT = Path(__file__).resolve().parent
DATA_SOURCES = ["logs/ablation_summary.json", "logs/research_summary.json"]
CONDITIONS = ("B", "F", "S")
INDICATOR_FIELDS = ("full_benefit", "slice_preservation", "slice_benefit")
CALIBRATION_LABELS = ("positive", "negative", "identity")


def _load(root: Path, relative: str) -> dict[str, Any]:
    path = root / relative
    if not path.is_file():
        raise ValueError(f"figure data source is missing: {relative}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"figure data source must be a JSON object: {relative}")
    return payload


def collect_figure_data(run_root: Path) -> dict[str, Any]:
    root = Path(run_root).resolve()
    ablation = _load(root, DATA_SOURCES[0])
    research = _load(root, DATA_SOURCES[1])
    if ablation.get("schema_version") != "effectslice-stage2-ablation-summary.v3":
        raise ValueError("figure requires the v3 ablation summary")
    if research.get("schema_version") != "effectslice-stage2-research-summary.v3":
        raise ValueError("figure requires the v3 research summary")
    if (
        ablation.get("statistical_unit") != "independent_agent_run"
        or research.get("statistical_unit") != "independent_agent_run"
    ):
        raise ValueError("real-task figure inputs must use independent_agent_run")

    ablation_rows = {
        row["task_key"]: row for row in ablation.get("task_rows", [])
    }
    research_rows = {
        row["task_key"]: row for row in research.get("task_rows", [])
    }
    tasks = list(ablation_rows)
    if not tasks or set(tasks) != set(research_rows):
        raise ValueError("figure summaries must contain the same task keys")
    denominator = int(ablation["replicate_denominator_per_task"])
    condition_successes: dict[str, list[int]] = {}
    indicator_successes: dict[str, list[int]] = {}
    cp_lowers: dict[str, list[float]] = {}
    thresholds: dict[str, list[float]] = {}
    for task in tasks:
        condition_counts = ablation_rows[task]["condition_successes"]
        condition_successes[task] = [
            int(condition_counts[condition]) for condition in CONDITIONS
        ]
        indicator_successes[task] = [
            int(research_rows[task][field]["successes"])
            for field in INDICATOR_FIELDS
        ]
        cp_lowers[task] = [
            float(research_rows[task][field]["one_sided_cp_lower"])
            for field in INDICATOR_FIELDS
        ]
        thresholds[task] = [
            float(research_rows[task][field]["minimum_prevalence"])
            for field in INDICATOR_FIELDS
        ]
        if any(
            int(research_rows[task][field]["total"]) != denominator
            for field in INDICATOR_FIELDS
        ):
            raise ValueError("indicator denominator does not match ablation summary")

    research_calibration = research.get("calibration_replication")
    ablation_calibration = ablation.get("calibration_replication")
    if research_calibration != ablation_calibration:
        raise ValueError("calibration summaries differ across figure inputs")
    if not isinstance(research_calibration, dict):
        raise ValueError("v3 summaries are missing the calibration replication")
    calibration_rows = {
        row["label"]: row for row in research_calibration.get("label_rows", [])
    }
    if set(calibration_rows) != set(CALIBRATION_LABELS):
        raise ValueError("calibration labels are incomplete")
    if research_calibration.get("full_integrity_passed") is not True:
        raise ValueError("calibration figure requires full integrity")

    return {
        "tasks": tasks,
        "conditions": list(CONDITIONS),
        "indicator_labels": ["Full benefit", "Slice preservation", "Slice benefit"],
        "replicate_denominator": denominator,
        "clustered_hidden_checks_per_run": int(
            ablation["clustered_hidden_checks_per_run"]
        ),
        "condition_successes": condition_successes,
        "indicator_successes": indicator_successes,
        "cp_lowers": cp_lowers,
        "thresholds": thresholds,
        "calibration": {
            "labels": list(CALIBRATION_LABELS),
            "event_counts": [
                int(calibration_rows[label]["primary_event_count"])
                for label in CALIBRATION_LABELS
            ],
            "denominators": [
                int(calibration_rows[label]["registered_blocks"])
                for label in CALIBRATION_LABELS
            ],
            "instrument_passed": bool(
                research_calibration["instrument_passed"]
            ),
            "positive_requirement_passed": bool(
                research_calibration["positive_requirement_passed"]
            ),
            "negative_requirement_passed": bool(
                research_calibration["negative_requirement_passed"]
            ),
            "independence_verified": bool(
                research_calibration["independence_verified"]
            ),
            "preregistration_sha256": research_calibration[
                "preregistration_sha256"
            ],
        },
    }


def _display_task(task_key: str) -> str:
    return {
        "snap_mfse": "SNAP-MFSE",
        "toolformer_filter": "Toolformer filter",
    }.get(task_key, task_key.replace("_", " ").title())


def _annotate(axis, bars, labels, *, offset: float = 0.018) -> None:
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
    denominator = data["replicate_denominator"]
    tasks = data["tasks"]
    task_labels = [_display_task(task) for task in tasks]
    figure_data_sha256 = hashlib.sha256(
        json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()

    plt.rcParams.update(
        {
            "font.size": 8,
            "axes.titlesize": 8.5,
            "axes.labelsize": 8,
            "xtick.labelsize": 7.5,
            "ytick.labelsize": 7.5,
            "legend.fontsize": 6.8,
            "axes.spines.top": False,
            "axes.spines.right": False,
        }
    )
    colors = {"B": "#6B7280", "F": "#277DA1", "S": "#43AA8B"}
    figure, axes = plt.subplots(1, 3, figsize=(7.2, 3.15))

    x_tasks = np.arange(len(tasks), dtype=float)
    width = 0.23
    for index, condition in enumerate(CONDITIONS):
        counts = [data["condition_successes"][task][index] for task in tasks]
        rates = [count / denominator for count in counts]
        bars = axes[0].bar(
            x_tasks + (index - 1) * width,
            rates,
            width,
            color=colors[condition],
            label=condition,
        )
        _annotate(
            axes[0],
            bars,
            [f"{count}/{denominator}" for count in counts],
        )
    axes[0].set_title("(a) Fresh-run condition success", loc="left")
    axes[0].set_ylabel("Observed rate")
    axes[0].set_xticks(x_tasks, task_labels, rotation=10, ha="right")
    axes[0].set_ylim(0, 1.14)
    axes[0].set_yticks(np.linspace(0, 1, 6))
    axes[0].grid(axis="y", color="#D1D5DB", linewidth=0.6, alpha=0.8)
    axes[0].legend(frameon=False, ncol=3, loc="upper center")

    indicator_labels = data["indicator_labels"]
    x_indicators = np.arange(len(indicator_labels), dtype=float)
    task_width = 0.32
    task_colors = ["#277DA1", "#F8961E", "#9C6644", "#577590"]
    for task_index, task in enumerate(tasks):
        offset = (task_index - (len(tasks) - 1) / 2) * task_width
        counts = data["indicator_successes"][task]
        rates = [count / denominator for count in counts]
        bars = axes[1].bar(
            x_indicators + offset,
            rates,
            task_width,
            color=task_colors[task_index % len(task_colors)],
            alpha=0.8,
            label=_display_task(task),
        )
        axes[1].scatter(
            x_indicators + offset,
            data["cp_lowers"][task],
            marker="D",
            s=20,
            color="#111827",
            zorder=3,
        )
        _annotate(
            axes[1],
            bars,
            [f"{count}/{denominator}" for count in counts],
        )
    thresholds = {
        threshold for values in data["thresholds"].values() for threshold in values
    }
    if len(thresholds) != 1:
        raise ValueError("figure requires a shared prevalence threshold")
    threshold = thresholds.pop()
    axes[1].axhline(
        threshold,
        color="#B91C1C",
        linewidth=1.0,
        linestyle="--",
    )
    axes[1].text(
        2.48,
        threshold + 0.012,
        f"{threshold:.1f} gate",
        color="#B91C1C",
        ha="right",
        va="bottom",
        fontsize=6.8,
    )
    axes[1].set_title("(b) Registered paired indicators", loc="left")
    axes[1].set_ylabel("Rate; diamond = CP lower")
    axes[1].set_xticks(x_indicators, ["Full\nbenefit", "Slice\npreservation", "Slice\nbenefit"])
    axes[1].set_ylim(0, 1.14)
    axes[1].set_yticks(np.linspace(0, 1, 6))
    axes[1].grid(axis="y", color="#D1D5DB", linewidth=0.6, alpha=0.8)
    axes[1].legend(frameon=False, loc="upper right")

    calibration = data["calibration"]
    calibration_x = np.arange(3, dtype=float)
    calibration_rates = [
        count / total
        for count, total in zip(
            calibration["event_counts"], calibration["denominators"]
        )
    ]
    calibration_bars = axes[2].bar(
        calibration_x,
        calibration_rates,
        0.58,
        color=["#43AA8B", "#C44536", "#6B7280"],
    )
    _annotate(
        axes[2],
        calibration_bars,
        [
            f"{count}/{total}"
            for count, total in zip(
                calibration["event_counts"], calibration["denominators"]
            )
        ],
        offset=0.012,
    )
    axes[2].hlines(
        1.0,
        calibration_x[0] - 0.29,
        calibration_x[0] + 0.29,
        color="#B91C1C",
        linewidth=1.4,
        zorder=4,
    )
    axes[2].text(
        calibration_x[0],
        1.035,
        "18/18 req.",
        color="#B91C1C",
        ha="center",
        va="bottom",
        fontsize=6.8,
    )
    axes[2].set_title("(c) Interleaved diagnostic calibration", loc="left")
    axes[2].set_ylabel("Event rate (fixed schedule)")
    axes[2].set_xticks(
        calibration_x,
        ["Planted\npositive", "Real\nnegative", "Identity"],
    )
    axes[2].set_ylim(0, 1.14)
    axes[2].set_yticks(np.linspace(0, 1, 6))
    axes[2].grid(axis="y", color="#D1D5DB", linewidth=0.6, alpha=0.8)

    figure.tight_layout(w_pad=1.4)
    figure_path = destination / "effectslice_run_level_evidence.png"
    figure.savefig(
        figure_path,
        dpi=300,
        bbox_inches="tight",
        facecolor="white",
        metadata={"Software": "EffectSlice Stage 2 v3 figure builder"},
    )
    plt.close(figure)

    report = {
        "schema_version": "effectslice-plot-aggregation-report.v3",
        "generated_figures": [figure_path.name],
        "data_sources": list(DATA_SOURCES),
        "figure_data_sha256": figure_data_sha256,
        "real_task_statistical_unit": "independent_agent_run",
        "calibration_analysis_unit": "registered_interleaved_BFS_block",
        "replicate_denominator_per_task": denominator,
        "clustered_hidden_checks_per_run": data[
            "clustered_hidden_checks_per_run"
        ],
        "calibration_preregistration_sha256": calibration[
            "preregistration_sha256"
        ],
        "calibration_instrument_passed": calibration["instrument_passed"],
        "dpi": 300,
        "traceability_notes": [
            "All empirical values are loaded from v3 Stage 2 JSON summaries.",
            "Panels (a) and (b) use independent fresh agent runs; hidden cases are clustered within-run checks.",
            "Panel (c) reports the complete fixed interleaved calibration schedule without IID or population inference.",
            "The open marker at 18/18 is the preregistered planted-positive requirement; 17/18 does not pass it.",
        ],
        "excluded_figures": [
            "Contaminated case-level confirmation plots are excluded.",
            "The non-interleaved exploratory V3 calibration is excluded from the main empirical figure.",
            "No user-benefit or cross-paper success figure is produced because those claims are untested.",
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
    parser = argparse.ArgumentParser(
        description="Build final V3 EffectSlice evidence figure"
    )
    parser.add_argument("--run-root", type=Path, default=RUN_ROOT)
    parser.add_argument("--output-dir", type=Path, default=RUN_ROOT / "figures")
    args = parser.parse_args()
    print(json.dumps(build_stage2_figures(args.run_root, args.output_dir), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
