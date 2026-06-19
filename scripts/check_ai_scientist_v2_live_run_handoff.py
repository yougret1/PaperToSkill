#!/usr/bin/env python
"""Build a local handoff report for the pending AI-Scientist-v2 live run."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REQUIRED_ENV_NAMES = (
    "AI_SCIENTIST_OPENAI_BASE_URL",
    "AI_SCIENTIST_OPENAI_API_KEY",
    "AI_SCIENTIST_FORCE_OPENAI_COMPATIBLE",
)


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


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="ignore")


def resolve(root: Path, raw_path: str | Path) -> Path:
    path = Path(raw_path)
    return path if path.is_absolute() else root / path


def relative(root: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except ValueError:
        return str(path)


def dry_run_dirs(ai_scientist_root: Path, idea_name: str) -> list[Path]:
    experiments = ai_scientist_root / "experiments"
    if not experiments.exists():
        return []
    return sorted(experiments.glob(f"*_{idea_name}_attempt_*"), key=lambda path: path.name)


def dry_run_artifacts_ready(paths: list[Path]) -> bool:
    return any(
        (path / "idea.json").exists()
        and (path / "idea.md").exists()
        and (path / "bfts_config.yaml").exists()
        for path in paths
    )


def completion_dirs(paths: list[Path]) -> list[Path]:
    complete = []
    for path in paths:
        has_token_tracker = (path / "token_tracker.json").exists()
        has_run_outputs = (
            (path / "logs").exists()
            or (path / "experiment_results").exists()
            or any(path.glob("*.pdf"))
        )
        if has_token_tracker and has_run_outputs:
            complete.append(path)
    return complete


def command_block(seed_path: Path, idea_idx: int) -> list[str]:
    return [
        "cd D:\\a_work\\gitee\\ai-scientist-v2",
        "$env:AI_SCIENTIST_OPENAI_BASE_URL='https://coderxiaoc.com/v1'",
        "$env:AI_SCIENTIST_OPENAI_API_KEY='<set locally>'",
        "$env:AI_SCIENTIST_FORCE_OPENAI_COMPATIBLE='1'",
        "python launch_scientist_bfts.py `",
        f"  --load_ideas {seed_path} `",
        f"  --idea_idx {idea_idx} `",
        "  --skip_writeup `",
        "  --skip_review",
    ]


def build_report(
    root: Path,
    ai_scientist_root: Path,
    seed_ideas_path: Path,
    config_path: Path,
    smoke_report_path: Path,
    idea_idx: int,
) -> dict[str, Any]:
    root = root.resolve()
    ai_scientist_root = resolve(root, ai_scientist_root)
    seed_ideas_path = resolve(root, seed_ideas_path)
    config_path = resolve(ai_scientist_root, config_path)
    smoke_report_path = resolve(root, smoke_report_path)
    launcher_path = ai_scientist_root / "launch_scientist_bfts.py"
    smoke_report = load_json(smoke_report_path)
    seed_ideas = load_json(seed_ideas_path)
    ideas = seed_ideas if isinstance(seed_ideas, list) else []
    selected_idea = ideas[idea_idx] if 0 <= idea_idx < len(ideas) else {}
    idea_name = str(selected_idea.get("Name", ""))
    config_text = read_text(config_path)
    launcher_text = read_text(launcher_path)
    candidates = dry_run_dirs(ai_scientist_root, idea_name) if idea_name else []
    complete_dirs = completion_dirs(candidates)
    next_commands = command_block(seed_ideas_path, idea_idx)

    checks = [
        Check(
            "ai_scientist_v2_live_root_present",
            "ready" if ai_scientist_root.exists() else "fail",
            "present" if ai_scientist_root.exists() else "missing",
            str(ai_scientist_root),
        ),
        Check(
            "ai_scientist_v2_live_launcher_present",
            "ready" if launcher_path.exists() else "fail",
            "present" if launcher_path.exists() else "missing",
            str(launcher_path),
        ),
        Check(
            "ai_scientist_v2_live_launcher_flags_ready",
            "ready"
            if all(flag in launcher_text for flag in ["--dry_run", "--skip_writeup", "--skip_review"])
            else "fail",
            "dry_run/skip flags present",
            str(launcher_path),
        ),
        Check(
            "ai_scientist_v2_live_config_present",
            "ready" if config_path.exists() else "fail",
            "present" if config_path.exists() else "missing",
            str(config_path),
        ),
        Check(
            "ai_scientist_v2_live_config_laptop_profile",
            "ready" if "num_workers: 1" in config_text and "claude-opus-4-8" in config_text else "fail",
            "num_workers=1 and claude-opus-4-8 profile present",
            str(config_path),
        ),
        Check(
            "ai_scientist_v2_live_seed_ideas_present",
            "ready" if seed_ideas_path.exists() else "fail",
            "present" if seed_ideas_path.exists() else "missing",
            str(seed_ideas_path),
        ),
        Check(
            "ai_scientist_v2_live_seed_idea_selected",
            "ready" if idea_name == "papertoskill_extractor" else "fail",
            f"idea_idx={idea_idx}; name={idea_name or 'missing'}",
            str(seed_ideas_path),
        ),
        Check(
            "ai_scientist_v2_live_dry_run_artifacts_present",
            "ready" if dry_run_artifacts_ready(candidates) else "fail",
            f"candidate_dirs={len(candidates)}",
            "; ".join(str(path) for path in candidates) or str(ai_scientist_root / "experiments"),
        ),
        Check(
            "ai_scientist_v2_live_env_names_declared",
            "ready",
            "env_names=" + ",".join(REQUIRED_ENV_NAMES),
            "local shell environment",
        ),
        Check(
            "ai_scientist_v2_live_next_commands_declared",
            "ready" if "launch_scientist_bfts.py" in "\n".join(next_commands) else "fail",
            "full live command declared",
            "next_commands",
        ),
        Check(
            "ai_scientist_v2_live_smoke_complete",
            "ready" if smoke_report.get("overall_status") == "complete" else "pending",
            f"smoke_overall={smoke_report.get('overall_status')}",
            str(smoke_report_path),
        ),
        Check(
            "ai_scientist_v2_live_completion_artifacts_present",
            "ready" if complete_dirs else "pending",
            f"completion_dirs={len(complete_dirs)}",
            "; ".join(str(path) for path in complete_dirs) or str(ai_scientist_root / "experiments"),
        ),
    ]

    status_counts = {"ready": 0, "pending": 0, "fail": 0}
    for check in checks:
        status_counts[check.status] = status_counts.get(check.status, 0) + 1

    if status_counts.get("fail", 0):
        overall_status = "fail"
    elif smoke_report.get("overall_status") != "complete":
        overall_status = "blocked_by_provider_smoke"
    elif not complete_dirs:
        overall_status = "ready_to_run"
    else:
        overall_status = "complete"

    return {
        "schema_version": "0.1",
        "evidence_boundary": (
            "Local AI-Scientist-v2 full live-run handoff/preflight only. This "
            "report does not run BFTS, does not call an LLM, and does not prove "
            "live research-task success."
        ),
        "overall_status": overall_status,
        "ai_scientist_root": str(ai_scientist_root),
        "launcher_path": str(launcher_path),
        "config_path": str(config_path),
        "seed_ideas_path": str(seed_ideas_path),
        "idea_idx": idea_idx,
        "selected_idea": {
            "name": idea_name,
            "title": selected_idea.get("Title", ""),
        },
        "dry_run_dirs": [str(path) for path in candidates],
        "completion_dirs": [str(path) for path in complete_dirs],
        "env_names": list(REQUIRED_ENV_NAMES),
        "next_commands": next_commands,
        "status_counts": status_counts,
        "checks": [check.as_dict() for check in checks],
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
    rows = [
        [check["id"], check["status"], check["detail"], check["evidence"]]
        for check in report["checks"]
    ]
    lines = [
        "# AI-Scientist-v2 Live Run Handoff",
        "",
        "Evidence boundary: this is a local handoff/preflight report. It does "
        "not run BFTS, does not call an LLM, and does not prove live research-task success.",
        "",
        f"- Overall status: {report['overall_status']}",
        f"- Selected idea: {report['selected_idea'].get('name', '')}",
        f"- Ready checks: {report['status_counts'].get('ready', 0)}",
        f"- Pending checks: {report['status_counts'].get('pending', 0)}",
        f"- Failed checks: {report['status_counts'].get('fail', 0)}",
        "",
        "## Next Command",
        "",
        "```powershell",
        *report["next_commands"],
        "```",
        "",
        "## Checks",
        "",
        markdown_table(rows, ["Check", "Status", "Detail", "Evidence"]),
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def write_json(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="Build the AI-Scientist-v2 full live-run handoff report.")
    parser.add_argument("--root", type=Path, default=root)
    parser.add_argument("--ai-scientist-root", type=Path, default=root.parent / "ai-scientist-v2")
    parser.add_argument("--seed-ideas", type=Path, default=Path("ai_scientist_inputs/papertoskill_seed_ideas.json"))
    parser.add_argument("--config", type=Path, default=Path("bfts_config.yaml"))
    parser.add_argument("--idea-idx", type=int, default=0)
    parser.add_argument(
        "--smoke-report",
        type=Path,
        default=Path("results/ai_scientist_v2_smoke/run_report.json"),
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        default=root / "results" / "ai_scientist_v2_live_run_handoff" / "handoff.json",
    )
    parser.add_argument(
        "--output-md",
        type=Path,
        default=root / "results" / "ai_scientist_v2_live_run_handoff" / "handoff.md",
    )
    parser.add_argument("--strict", action="store_true", help="Exit non-zero only if local handoff checks fail.")
    args = parser.parse_args()

    report = build_report(args.root, args.ai_scientist_root, args.seed_ideas, args.config, args.smoke_report, args.idea_idx)
    write_json(args.output_json, report)
    write_markdown(args.output_md, report)
    print(args.output_json)
    print(args.output_md)
    if args.strict and report["overall_status"] == "fail":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
