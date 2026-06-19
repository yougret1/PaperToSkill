#!/usr/bin/env python
"""Build a local handoff report for the pending DeepSeek follow-up slot."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


PLACEHOLDER_ALIAS = "deepseek-to-be-filled"
DEEPSEEK_SLOT_ID = "deepseek_followup_slot"


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


def resolve(root: Path, raw_path: str | Path) -> Path:
    path = Path(raw_path)
    return path if path.is_absolute() else root / path


def relative(root: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except ValueError:
        return str(path)


def deepseek_slot(task: dict[str, Any]) -> dict[str, Any]:
    for slot in task.get("model_slots", []):
        if slot.get("id") == DEEPSEEK_SLOT_ID:
            return slot
    return {}


def deepseek_prompts(index: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        prompt
        for prompt in index.get("prompts", [])
        if prompt.get("model_id") == DEEPSEEK_SLOT_ID
    ]


def command_block(task_path: Path, index_path: Path) -> list[str]:
    return [
        "python scripts\\configure_deepseek_followup.py `",
        f"  --task {task_path} `",
        "  --model-alias <deepseek-model-alias> `",
        "  --auth-env DEEPSEEK_API_KEY `",
        "  --base-url-env DEEPSEEK_BASE_URL",
        "",
        "python scripts\\build_model_ablation_prompts.py `",
        f"  --task {task_path} `",
        "  --output-dir results\\model_ablation_prompts\\v0",
        "",
        "python scripts\\run_model_ablation_prompts.py `",
        f"  --task {task_path} `",
        f"  --index {index_path} `",
        "  --output-json results\\model_ablation_prompts\\v0\\deepseek_run_report.json `",
        "  --output-md results\\model_ablation_prompts\\v0\\deepseek_run_report.md `",
        "  --model-id deepseek_followup_slot",
        "",
        "python scripts\\evaluate_model_ablation_responses.py `",
        f"  --index {index_path} `",
        "  --output-json results\\model_ablation_prompts\\v0\\evaluation.json `",
        "  --output-md results\\model_ablation_prompts\\v0\\evaluation.md",
        "",
        "python scripts\\check_deepseek_followup.py --strict",
    ]


def build_report(root: Path, task_path: Path, index_path: Path) -> dict[str, Any]:
    root = root.resolve()
    task_path = resolve(root, task_path)
    index_path = resolve(root, index_path)
    task = load_json(task_path)
    index = load_json(index_path)
    slot = deepseek_slot(task)
    prompts = deepseek_prompts(index)
    alias = str(slot.get("model_alias", ""))
    auth_env = str(slot.get("auth_env", ""))
    base_url_env = str(slot.get("base_url_env", ""))

    prompt_missing = [
        relative(root, resolve(root, prompt.get("prompt_path", "")))
        for prompt in prompts
        if not resolve(root, prompt.get("prompt_path", "")).exists()
    ]
    response_paths = [
        relative(root, resolve(root, prompt.get("expected_response_path", "")))
        for prompt in prompts
        if prompt.get("expected_response_path")
    ]
    saved_responses = [
        path
        for path in response_paths
        if resolve(root, path).exists()
    ]

    checks = [
        Check(
            "deepseek_followup_slot_present",
            "ready" if slot else "fail",
            "present" if slot else "missing",
            relative(root, task_path),
        ),
        Check(
            "deepseek_followup_index_rows",
            "ready" if len(prompts) == len(task.get("context_cases", [])) == 2 else "fail",
            f"rows={len(prompts)}; expected_cases={len(task.get('context_cases', []))}",
            relative(root, index_path),
        ),
        Check(
            "deepseek_followup_prompt_files",
            "ready" if prompts and not prompt_missing else "fail",
            "present" if not prompt_missing else "missing=" + ",".join(prompt_missing),
            relative(root, index_path),
        ),
        Check(
            "deepseek_followup_response_paths_declared",
            "ready" if len(response_paths) == len(prompts) and response_paths else "fail",
            f"response_paths={len(response_paths)}",
            relative(root, index_path),
        ),
        Check(
            "deepseek_followup_env_names_declared",
            "ready" if auth_env and base_url_env else "fail",
            f"auth_env={auth_env}; base_url_env={base_url_env}",
            relative(root, task_path),
        ),
        Check(
            "deepseek_followup_alias_configured",
            "pending" if alias == PLACEHOLDER_ALIAS else "ready",
            (
                "placeholder alias awaits user-provided DeepSeek model"
                if alias == PLACEHOLDER_ALIAS
                else f"alias={alias}"
            ),
            relative(root, task_path),
        ),
        Check(
            "deepseek_followup_responses_saved",
            "ready" if len(saved_responses) == len(response_paths) and response_paths else "pending",
            f"saved={len(saved_responses)}; expected={len(response_paths)}",
            "; ".join(response_paths),
        ),
    ]

    status_counts = {"ready": 0, "pending": 0, "fail": 0}
    for check in checks:
        status_counts[check.status] = status_counts.get(check.status, 0) + 1

    if status_counts.get("fail", 0):
        overall_status = "fail"
    elif alias == PLACEHOLDER_ALIAS:
        overall_status = "pending_user_configuration"
    elif status_counts.get("pending", 0):
        overall_status = "ready_to_run"
    else:
        overall_status = "responses_present"

    return {
        "schema_version": "0.1",
        "evidence_boundary": (
            "Local DeepSeek follow-up handoff only. This report does not call "
            "DeepSeek, does not save model responses, and does not complete "
            "the DeepSeek ablation."
        ),
        "overall_status": overall_status,
        "task_path": relative(root, task_path),
        "index_path": relative(root, index_path),
        "slot": {
            "id": DEEPSEEK_SLOT_ID,
            "model_alias": alias,
            "auth_env": auth_env,
            "base_url_env": base_url_env,
            "provider_status": slot.get("provider_status", ""),
        },
        "prompt_rows": [
            {
                "case_id": prompt.get("case_id", ""),
                "prompt_path": relative(root, resolve(root, prompt.get("prompt_path", ""))),
                "expected_response_path": relative(root, resolve(root, prompt.get("expected_response_path", ""))),
            }
            for prompt in prompts
        ],
        "next_commands": command_block(Path("benchmarks/model_ablation_v0.json"), Path("results/model_ablation_prompts/v0/index.json")),
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
        "# DeepSeek Follow-Up Handoff",
        "",
        "Evidence boundary: this is a local handoff/preflight report. It does "
        "not call DeepSeek and does not complete the DeepSeek ablation.",
        "",
        f"- Overall status: {report['overall_status']}",
        f"- Model alias: {report['slot'].get('model_alias', '')}",
        f"- Auth env: {report['slot'].get('auth_env', '')}",
        f"- Base URL env: {report['slot'].get('base_url_env', '')}",
        f"- Ready checks: {report['status_counts'].get('ready', 0)}",
        f"- Pending checks: {report['status_counts'].get('pending', 0)}",
        f"- Failed checks: {report['status_counts'].get('fail', 0)}",
        "",
        "## Configuration Helper",
        "",
        "`scripts/configure_deepseek_followup.py` updates only non-secret slot "
        "metadata: model alias, auth environment-variable name, base-URL "
        "environment-variable name, and provider status. Keep raw keys in local "
        "environment variables and never commit them.",
        "",
        "## Prompt Rows",
        "",
        markdown_table(
            [
                [
                    row["case_id"],
                    row["prompt_path"],
                    row["expected_response_path"],
                ]
                for row in report["prompt_rows"]
            ],
            ["Case", "Prompt", "Expected Response"],
        ),
        "",
        "## Next Commands",
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
    parser = argparse.ArgumentParser(description="Build the DeepSeek follow-up handoff report.")
    parser.add_argument("--root", type=Path, default=root)
    parser.add_argument("--task", type=Path, default=Path("benchmarks/model_ablation_v0.json"))
    parser.add_argument("--index", type=Path, default=Path("results/model_ablation_prompts/v0/index.json"))
    parser.add_argument(
        "--output-json",
        type=Path,
        default=root / "results" / "deepseek_followup_handoff" / "handoff.json",
    )
    parser.add_argument(
        "--output-md",
        type=Path,
        default=root / "results" / "deepseek_followup_handoff" / "handoff.md",
    )
    parser.add_argument("--strict", action="store_true", help="Exit non-zero only if local handoff checks fail.")
    args = parser.parse_args()

    report = build_report(args.root, args.task, args.index)
    write_json(args.output_json, report)
    write_markdown(args.output_md, report)
    print(args.output_json)
    print(args.output_md)
    if args.strict and report["overall_status"] == "fail":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
