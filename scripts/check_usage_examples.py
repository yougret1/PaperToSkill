#!/usr/bin/env python
"""Check PaperToSkill usage examples and run a local example chain."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REQUIRED_EXAMPLE_FILES = {
    "usage_readme": "examples/usage/README.md",
    "codex_skill_usage": "examples/usage/codex_skill_usage.md",
    "auto_note_scaffold_usage": "examples/usage/auto_note_scaffold_usage.md",
    "model_ablation_usage": "examples/usage/model_ablation_usage.md",
}

CODEX_USAGE_INPUTS = {
    "codex_toolformer_skill": "generated_skills/toolformer/SKILL.md",
    "codex_toolformer_source_map": "generated_skills/toolformer/references/source_map.json",
    "codex_toolformer_prompt": "results/live_transfer_prompts/toolformer_v0/codex_skill__full_skill.md",
}

AUTO_NOTE_USAGE_INPUTS = {
    "auto_note_source_text": "papers/extracted/aide.txt",
    "auto_note_rubric": "benchmarks/rubric_aide_v0.json",
    "auto_note_script": "scripts/papertoskill_note_from_text.py",
    "extract_script": "scripts/papertoskill_extract.py",
    "evaluate_script": "scripts/evaluate_skill.py",
}

MODEL_ABLATION_INPUTS = {
    "model_ablation_task": "benchmarks/model_ablation_v0.json",
    "model_ablation_prompt_index": "results/model_ablation_prompts/v0/index.json",
    "model_ablation_builder": "scripts/build_model_ablation_prompts.py",
    "model_ablation_runner": "scripts/run_model_ablation_prompts.py",
    "model_ablation_evaluator": "scripts/evaluate_model_ablation_responses.py",
}

EXPECTED_MODEL_SLOTS = {"claude_opus_4_8", "gpt_5_5_or_gpt_family", "deepseek_followup_slot"}
EXPECTED_CASES = {"toolformer_curated_skill_usage", "aide_auto_skill_usage"}


@dataclass
class Check:
    id: str
    status: str
    detail: str
    evidence: str

    def as_dict(self) -> dict[str, str]:
        return {
            "id": self.id,
            "status": self.status,
            "detail": self.detail,
            "evidence": self.evidence,
        }


def resolve_path(root: Path, raw_path: str | Path) -> Path:
    path = Path(raw_path)
    return path if path.is_absolute() else root / path


def evidence_path(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def required_file_checks(root: Path, files: dict[str, str]) -> list[Check]:
    checks = []
    for check_id, raw_path in files.items():
        path = resolve_path(root, raw_path)
        status = "ready" if path.exists() else "fail"
        detail = "present" if path.exists() else "missing"
        checks.append(Check(check_id, status, detail, str(raw_path).replace("\\", "/")))
    return checks


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def markdown_mentions_checks(root: Path) -> list[Check]:
    checks: list[Check] = []
    expected_mentions = {
        "usage_readme_mentions_codex": ("examples/usage/README.md", "codex_skill_usage.md"),
        "usage_readme_mentions_auto_note": ("examples/usage/README.md", "auto_note_scaffold_usage.md"),
        "usage_readme_mentions_model_ablation": ("examples/usage/README.md", "model_ablation_usage.md"),
        "codex_usage_mentions_prompt": (
            "examples/usage/codex_skill_usage.md",
            "results/live_transfer_prompts/toolformer_v0/codex_skill__full_skill.md",
        ),
        "auto_note_usage_mentions_profile": ("examples/usage/auto_note_scaffold_usage.md", "--profile aide"),
        "model_ablation_usage_mentions_deepseek": ("examples/usage/model_ablation_usage.md", "deepseek_followup_slot"),
    }
    for check_id, (raw_path, needle) in expected_mentions.items():
        path = resolve_path(root, raw_path)
        if not path.exists():
            checks.append(Check(check_id, "fail", "missing example file", raw_path))
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        status = "ready" if needle in text else "fail"
        detail = f"mentions {needle}" if status == "ready" else f"missing {needle}"
        checks.append(Check(check_id, status, detail, raw_path))
    return checks


def model_ablation_prompt_grid_checks(root: Path) -> list[Check]:
    index_path = root / "results/model_ablation_prompts/v0/index.json"
    if not index_path.exists():
        return [Check("usage_model_ablation_prompt_grid", "fail", "missing index", evidence_path(root, index_path))]

    index = load_json(index_path)
    prompts = index.get("prompts", [])
    model_ids = {item.get("model_id") for item in prompts}
    case_ids = {item.get("case_id") for item in prompts}
    prompt_missing = [
        item.get("prompt_path", "")
        for item in prompts
        if not resolve_path(root, item.get("prompt_path", "")).exists()
    ]
    response_paths = [item.get("expected_response_path", "") for item in prompts]

    checks = [
        Check(
            "usage_model_ablation_prompt_grid",
            "ready" if len(prompts) == 6 else "fail",
            f"prompt_packets={len(prompts)}",
            evidence_path(root, index_path),
        ),
        Check(
            "usage_model_ablation_model_slots",
            "ready" if EXPECTED_MODEL_SLOTS <= model_ids else "fail",
            "models=" + ",".join(sorted(str(item) for item in model_ids)),
            evidence_path(root, index_path),
        ),
        Check(
            "usage_model_ablation_cases",
            "ready" if EXPECTED_CASES <= case_ids else "fail",
            "cases=" + ",".join(sorted(str(item) for item in case_ids)),
            evidence_path(root, index_path),
        ),
        Check(
            "usage_model_ablation_prompts_exist",
            "ready" if not prompt_missing else "fail",
            f"missing_prompts={len(prompt_missing)}",
            evidence_path(root, index_path),
        ),
        Check(
            "usage_model_ablation_response_slots",
            "ready" if len(response_paths) == 6 and all(response_paths) else "fail",
            f"response_slots={sum(1 for item in response_paths if item)}",
            evidence_path(root, index_path),
        ),
    ]
    return checks


def run_command(command: list[str], root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=root, check=True, capture_output=True, text=True)


def run_auto_note_example(root: Path) -> tuple[list[Check], dict[str, Any]]:
    with tempfile.TemporaryDirectory(prefix="papertoskill_usage_") as tmp:
        tmp_path = Path(tmp)
        note_path = tmp_path / "aide_auto_note.md"
        note_report_path = tmp_path / "aide_auto_note_report.json"
        skill_dir = tmp_path / "aide_auto_skill"
        rubric_path = tmp_path / "aide_auto_rubric.json"

        commands = [
            [
                sys.executable,
                "scripts/papertoskill_note_from_text.py",
                "--source",
                "papers/extracted/aide.txt",
                "--output",
                str(note_path),
                "--paper-id",
                "aide_auto_usage_check",
                "--title",
                "AIDE: AI-Driven Exploration in the Space of Code",
                "--profile",
                "aide",
                "--report",
                str(note_report_path),
            ],
            [
                sys.executable,
                "scripts/papertoskill_extract.py",
                "--source",
                str(note_path),
                "--output",
                str(skill_dir),
                "--name",
                "aide-auto-usage-check",
            ],
            [
                sys.executable,
                "scripts/evaluate_skill.py",
                "--skill",
                str(skill_dir / "SKILL.md"),
                "--rubric",
                "benchmarks/rubric_aide_v0.json",
                "--output",
                str(rubric_path),
            ],
        ]
        for command in commands:
            run_command(command, root)

        note_report = load_json(note_report_path)
        rubric = load_json(rubric_path)
        skill_path = skill_dir / "SKILL.md"
        source_map_path = skill_dir / "references/source_map.json"
        score = float(rubric.get("score", 0))
        max_score = float(rubric.get("max_score", 20))
        selected = note_report.get("selected", {})
        method_count = len(selected.get("methods", []))
        experiment_count = len(selected.get("experiments", []))
        limitation_count = len(selected.get("limitations", []))

        checks = [
            Check(
                "usage_auto_note_example_note_created",
                "ready" if note_path.exists() else "fail",
                "created in temporary directory",
                "temporary/aide_auto_note.md",
            ),
            Check(
                "usage_auto_note_example_report_created",
                "ready" if note_report_path.exists() else "fail",
                "created in temporary directory",
                "temporary/aide_auto_note_report.json",
            ),
            Check(
                "usage_auto_note_example_skill_created",
                "ready" if skill_path.exists() else "fail",
                "created in temporary directory",
                "temporary/aide_auto_skill/SKILL.md",
            ),
            Check(
                "usage_auto_note_example_source_map_created",
                "ready" if source_map_path.exists() else "fail",
                "created in temporary directory",
                "temporary/aide_auto_skill/references/source_map.json",
            ),
            Check(
                "usage_auto_note_example_selected_windows",
                "ready" if method_count >= 4 and experiment_count >= 3 and limitation_count >= 3 else "fail",
                f"methods={method_count}; experiments={experiment_count}; limitations={limitation_count}",
                "temporary/aide_auto_note_report.json",
            ),
            Check(
                "usage_auto_note_example_rubric_score",
                "ready" if score == max_score else "fail",
                f"{score:g}/{max_score:g}",
                "temporary/aide_auto_rubric.json",
            ),
        ]
        sample = {
            "note_report": {
                "paper_id": note_report.get("paper_id"),
                "profile": note_report.get("profile"),
                "method_windows": method_count,
                "experiment_windows": experiment_count,
                "limitation_windows": limitation_count,
            },
            "rubric": {
                "score": score,
                "max_score": max_score,
                "skill": "temporary/aide_auto_skill/SKILL.md",
            },
        }
        return checks, sample


def build_report(root: Path, *, run_examples: bool = True) -> dict[str, Any]:
    root = root.resolve()
    checks: list[Check] = []
    checks.extend(required_file_checks(root, REQUIRED_EXAMPLE_FILES))
    checks.extend(required_file_checks(root, CODEX_USAGE_INPUTS))
    checks.extend(required_file_checks(root, AUTO_NOTE_USAGE_INPUTS))
    checks.extend(required_file_checks(root, MODEL_ABLATION_INPUTS))
    checks.extend(markdown_mentions_checks(root))
    checks.extend(model_ablation_prompt_grid_checks(root))
    auto_note_sample: dict[str, Any] | None = None
    if run_examples:
        auto_note_checks, auto_note_sample = run_auto_note_example(root)
        checks.extend(auto_note_checks)

    status_counts = {"ready": 0, "fail": 0}
    for check in checks:
        status_counts[check.status] = status_counts.get(check.status, 0) + 1
    overall = "fail" if status_counts.get("fail", 0) else "ready"
    return {
        "schema_version": "0.1",
        "evidence_boundary": (
            "Checks local usage-example files, input artifacts, prompt/response slots, and an offline "
            "auto-note-to-skill example chain. It does not execute live model calls or score model responses."
        ),
        "overall_status": overall,
        "status_counts": status_counts,
        "checks": [check.as_dict() for check in checks],
        "auto_note_example_sample": auto_note_sample,
    }


def markdown_table(rows: list[list[str]], columns: list[str]) -> str:
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for row in rows:
        values = [value.replace("|", "\\|").replace("\n", " ") for value in row]
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    rows = [[check["id"], check["status"], check["detail"], check["evidence"]] for check in report["checks"]]
    counts = report["status_counts"]
    lines = [
        "# Usage Example Report",
        "",
        "Evidence boundary: this report checks local usage-example files and runs "
        "an offline auto-note-to-skill example chain. It does not execute live "
        "model calls or score model responses.",
        "",
        f"- Overall status: {report['overall_status']}",
        f"- Ready checks: {counts.get('ready', 0)}",
        f"- Failed checks: {counts.get('fail', 0)}",
        "",
        "## Checks",
        "",
        markdown_table(rows, ["Check", "Status", "Detail", "Evidence"]),
        "",
    ]
    sample = report.get("auto_note_example_sample")
    if sample:
        note = sample.get("note_report", {})
        rubric = sample.get("rubric", {})
        lines.extend(
            [
                "## Offline Example Sample",
                "",
                f"- Paper ID: {note.get('paper_id')}",
                f"- Profile: {note.get('profile')}",
                f"- Selected windows: methods={note.get('method_windows')}, "
                f"experiments={note.get('experiment_windows')}, limitations={note.get('limitation_windows')}",
                f"- Temporary skill rubric score: {rubric.get('score'):g}/{rubric.get('max_score'):g}",
                "",
            ]
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def write_json(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="Check PaperToSkill usage examples.")
    parser.add_argument("--output-json", type=Path, default=root / "results" / "reproducibility" / "usage_example_report.json")
    parser.add_argument("--output-md", type=Path, default=root / "results" / "reproducibility" / "usage_example_report.md")
    parser.add_argument("--skip-run", action="store_true", help="Only check files and prompt slots; skip the offline example chain.")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero if any usage-example check fails.")
    args = parser.parse_args()

    report = build_report(root, run_examples=not args.skip_run)
    write_json(args.output_json, report)
    write_markdown(args.output_md, report)
    print(args.output_json)
    print(args.output_md)
    if args.strict and report["overall_status"] == "fail":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
