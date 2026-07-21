from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


RUN_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = Path(__file__).resolve().parents[6]
TASK_MACRO_PREFIX = {
    "snap_mfse": "SnapMFSE",
    "toolformer_filter": "ToolformerFilter",
}
INDICATOR_FIELDS = {
    "full_benefit": "FullBenefit",
    "slice_preservation": "SlicePreservation",
    "slice_benefit": "SliceBenefit",
}


def _load(path: Path, *, schema: str) -> dict[str, Any]:
    source = Path(path).resolve()
    payload = json.loads(source.read_text(encoding="utf-8"))
    if payload.get("schema_version") != schema:
        raise ValueError(f"unexpected summary schema: {source}")
    if payload.get("statistical_unit") != "independent_agent_run":
        raise ValueError("paper results require independent_agent_run summaries")
    return payload


def _macro(name: str, value: Any) -> str:
    return f"\\newcommand{{\\{name}}}{{{value}}}"


def _decision(classification: str) -> str:
    if classification == "task_local_admission_passed":
        return "Admit"
    if classification == "task_local_admission_rejected":
        return "Reject"
    raise ValueError(f"unsupported task classification: {classification}")


def build_paper_results(
    *,
    research_path: Path,
    ablation_path: Path,
    output_tex: Path,
    output_manifest: Path,
) -> dict[str, str]:
    research_file = Path(research_path).resolve()
    ablation_file = Path(ablation_path).resolve()
    research = _load(
        research_file,
        schema="effectslice-stage2-research-summary.v2",
    )
    ablation = _load(
        ablation_file,
        schema="effectslice-stage2-ablation-summary.v2",
    )
    research_rows = {row["task_key"]: row for row in research["task_rows"]}
    ablation_rows = {row["task_key"]: row for row in ablation["task_rows"]}
    if not research_rows or set(research_rows) != set(ablation_rows):
        raise ValueError("paper summaries must contain the same task keys")
    unknown_tasks = set(research_rows) - set(TASK_MACRO_PREFIX)
    if unknown_tasks:
        raise ValueError(f"paper macro mapping is missing tasks: {sorted(unknown_tasks)}")
    denominator = int(ablation["replicate_denominator_per_task"])
    hidden_checks = int(ablation["clustered_hidden_checks_per_run"])
    task_count = len(research_rows)
    provider_conversations = task_count * denominator * 3
    admission_count = sum(
        row.get("classification") == "task_local_admission_passed"
        for row in research_rows.values()
    )

    lines = [
        "% Generated from Stage 2 v2 JSON. Do not edit empirical values by hand.",
        _macro("EffectSliceTaskCount", task_count),
        _macro("EffectSliceReplicatesPerTask", denominator),
        _macro("EffectSliceProviderConversations", provider_conversations),
        _macro("EffectSliceHiddenChecksPerRun", hidden_checks),
        _macro("EffectSliceAdmissions", admission_count),
    ]
    macro_values: dict[str, Any] = {
        "EffectSliceTaskCount": task_count,
        "EffectSliceReplicatesPerTask": denominator,
        "EffectSliceProviderConversations": provider_conversations,
        "EffectSliceHiddenChecksPerRun": hidden_checks,
        "EffectSliceAdmissions": admission_count,
    }
    for task_key in research_rows:
        prefix = TASK_MACRO_PREFIX[task_key]
        research_row = research_rows[task_key]
        ablation_row = ablation_rows[task_key]
        condition_counts = ablation_row["condition_successes"]
        for condition in ("B", "F", "S"):
            name = f"{prefix}{condition}Successes"
            value = int(condition_counts[condition])
            lines.append(_macro(name, value))
            macro_values[name] = value
        for field, field_prefix in INDICATOR_FIELDS.items():
            indicator = research_row[field]
            success_name = f"{prefix}{field_prefix}Successes"
            lower_name = f"{prefix}{field_prefix}CPLower"
            successes = int(indicator["successes"])
            lower = f"{float(indicator['one_sided_cp_lower']):.3f}"
            if int(indicator["total"]) != denominator:
                raise ValueError("paper indicator denominator mismatch")
            lines.append(_macro(success_name, successes))
            lines.append(_macro(lower_name, lower))
            macro_values[success_name] = successes
            macro_values[lower_name] = lower
        decision_name = f"{prefix}Decision"
        decision = _decision(str(research_row["classification"]))
        lines.append(_macro(decision_name, decision))
        macro_values[decision_name] = decision

    tex_path = Path(output_tex).resolve()
    manifest_path = Path(output_manifest).resolve()
    tex_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    tex_path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    source_sha256 = {
        research_file.as_posix(): hashlib.sha256(research_file.read_bytes()).hexdigest(),
        ablation_file.as_posix(): hashlib.sha256(ablation_file.read_bytes()).hexdigest(),
    }
    manifest = {
        "schema_version": "effectslice-paper-results-manifest.v2",
        "statistical_unit": "independent_agent_run",
        "analysis_unit": "matched_BFS_replicate",
        "replicates_per_task": denominator,
        "provider_conversations": provider_conversations,
        "hidden_checks_per_run": hidden_checks,
        "source_sha256": source_sha256,
        "output_tex": tex_path.as_posix(),
        "output_tex_sha256": hashlib.sha256(tex_path.read_bytes()).hexdigest(),
        "macros": macro_values,
    }
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return {"tex": str(tex_path), "manifest": str(manifest_path)}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate traceable LaTeX macros from Stage 2 v2 summaries"
    )
    parser.add_argument(
        "--research-summary",
        type=Path,
        default=RUN_ROOT / "logs" / "research_summary.json",
    )
    parser.add_argument(
        "--ablation-summary",
        type=Path,
        default=RUN_ROOT / "logs" / "ablation_summary.json",
    )
    parser.add_argument(
        "--output-tex",
        type=Path,
        default=PROJECT_ROOT / "paper" / "effectslice_aaai" / "generated_results.tex",
    )
    parser.add_argument(
        "--output-manifest",
        type=Path,
        default=RUN_ROOT / "manuscript" / "generated_results_manifest.json",
    )
    args = parser.parse_args()
    print(
        json.dumps(
            build_paper_results(
                research_path=args.research_summary,
                ablation_path=args.ablation_summary,
                output_tex=args.output_tex,
                output_manifest=args.output_manifest,
            ),
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
