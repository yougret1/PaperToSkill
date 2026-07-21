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
    if ablation.get("schema_version") != "effectslice-stage2-ablation-summary.v2":
        raise ValueError("figure requires the v2 ablation summary")
    if research.get("schema_version") != "effectslice-stage2-research-summary.v2":
        raise ValueError("figure requires the v2 research summary")
    if (
        ablation.get("statistical_unit") != "independent_agent_run"
        or research.get("statistical_unit") != "independent_agent_run"
    ):
        raise ValueError("figure inputs must use independent_agent_run")

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
            "axes.titlesize": 9,
            "axes.labelsize": 8,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "legend.fontsize": 7,
            "axes.spines.top": False,
            "axes.spines.right": False,
        }
    )
    colors = {"B": "#6B7280", "F": "#277DA1", "S": "#43AA8B"}
    width_inches = 7.2
    height_inches = 3.25
    figure, axes = plt.subplots(1, 2, figsize=(width_inches, height_inches))

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
    axes[0].set_title("(a) Condition success across fresh runs", loc="left")
    axes[0].set_ylabel("Successful API agent runs")
    axes[0].set_xticks(x_tasks, task_labels)
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
            alpha=0.78,
            label=_display_task(task),
        )
        axes[1].scatter(
            x_indicators + offset,
            data["cp_lowers"][task],
            marker="D",
            s=24,
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
        label=f"gate = {threshold:.1f}",
    )
    axes[1].set_title("(b) Registered run-level indicators", loc="left")
    axes[1].set_ylabel("Observed rate; diamond = CP lower")
    axes[1].set_xticks(x_indicators, indicator_labels, rotation=12, ha="right")
    axes[1].set_ylim(0, 1.14)
    axes[1].set_yticks(np.linspace(0, 1, 6))
    axes[1].grid(axis="y", color="#D1D5DB", linewidth=0.6, alpha=0.8)
    axes[1].legend(frameon=False, loc="lower left")

    figure.tight_layout(w_pad=2.0)
    figure_path = destination / "effectslice_run_level_evidence.png"
    figure.savefig(
        figure_path,
        dpi=300,
        bbox_inches="tight",
        facecolor="white",
        metadata={"Software": "EffectSlice Stage 2 v2 figure builder"},
    )
    plt.close(figure)

    report = {
        "schema_version": "effectslice-plot-aggregation-report.v2",
        "generated_figures": [figure_path.name],
        "data_sources": list(DATA_SOURCES),
        "figure_data_sha256": figure_data_sha256,
        "statistical_unit": "independent_agent_run",
        "replicate_denominator_per_task": denominator,
        "clustered_hidden_checks_per_run": data[
            "clustered_hidden_checks_per_run"
        ],
        "dpi": 300,
        "traceability_notes": [
            "All empirical values are loaded from v2 Stage 2 JSON summaries.",
            "Diamonds are one-sided Clopper-Pearson lower bounds over independent runs.",
            "Hidden cases define each run score and are not plotted as independent observations.",
        ],
        "excluded_figures": [
            "Contaminated case-level confirmation plots are excluded.",
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
        description="Build final run-level EffectSlice figures"
    )
    parser.add_argument("--run-root", type=Path, default=RUN_ROOT)
    parser.add_argument("--output-dir", type=Path, default=RUN_ROOT / "figures")
    args = parser.parse_args()
    print(json.dumps(build_stage2_figures(args.run_root, args.output_dir), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
