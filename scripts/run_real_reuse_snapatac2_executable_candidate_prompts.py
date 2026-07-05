#!/usr/bin/env python
"""Generate SNAP executable-candidate scripts from prepared prompt packets."""

from __future__ import annotations

import argparse
import json
import os
import re
import time
from pathlib import Path
from typing import Any

from run_model_ablation_prompts import WIRE_APIS, extract_content, request_json, wire_endpoint


SCHEMA_VERSION = "0.1"
DEFAULT_PLAN_JSON = Path("results/real_reuse/snapatac2_executable_candidate_prompt_plan.json")


def root_path() -> Path:
    return Path(__file__).resolve().parents[1]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def relative(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def resolve(root: Path, raw_path: str | Path) -> Path:
    path = Path(raw_path)
    return path if path.is_absolute() else root / path


def extract_python_code(text: str) -> str:
    match = re.search(r"```(?:python|py)?\s*(.*?)```", text, flags=re.IGNORECASE | re.DOTALL)
    return match.group(1).strip() if match else text.strip()


def fixture_response_path(fixture_dir: Path, expected_script_name: str) -> Path | None:
    stem = Path(expected_script_name).stem
    for name in (expected_script_name, f"{stem}.md", f"{stem}.txt"):
        path = fixture_dir / name
        if path.exists():
            return path
    return None


def build_wire_request(
    *,
    wire_api: str,
    model_alias: str,
    prompt: str,
    max_tokens: int,
    anthropic_version: str,
) -> tuple[dict[str, Any], dict[str, str]]:
    system = (
        "You are generating a Python candidate script for a locked "
        "SnapATAC2 executable-candidate diagnostic rerun. Return one Python "
        "script only, without Markdown fences."
    )
    if wire_api == "openai_responses":
        return {"model": model_alias, "input": f"{system}\n\n{prompt}", "max_output_tokens": max_tokens}, {}
    if wire_api == "anthropic_messages":
        return (
            {
                "model": model_alias,
                "system": system,
                "max_tokens": max_tokens,
                "messages": [{"role": "user", "content": prompt}],
            },
            {"anthropic-version": anthropic_version},
        )
    return (
        {
            "model": model_alias,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": prompt}],
            "temperature": 0,
            "max_tokens": max_tokens,
        },
        {},
    )


def call_model(args: argparse.Namespace, prompt: str) -> tuple[str | None, dict[str, Any]]:
    base_url = args.base_url or os.environ.get(args.base_url_env, "")
    api_key = args.api_key or os.environ.get(args.api_key_env, "")
    if not base_url or not api_key:
        return None, {
            "status": "skipped",
            "selection_reason": "missing_base_url_or_api_key_env",
            "base_url_env": args.base_url_env,
            "api_key_env": args.api_key_env,
        }

    body, headers = build_wire_request(
        wire_api=args.wire_api,
        model_alias=args.model_alias,
        prompt=prompt,
        max_tokens=args.max_tokens,
        anthropic_version=args.anthropic_version,
    )
    last_error = ""
    for attempt in range(1, max(1, args.max_attempts) + 1):
        try:
            status, response = request_json(
                wire_endpoint(base_url, args.wire_api),
                api_key,
                method="POST",
                body=body,
                extra_headers=headers,
                timeout_seconds=args.timeout_seconds,
            )
            content = extract_content(response).strip()
            return content, {
                "status": "success",
                "selection_reason": "live_endpoint_response",
                "http_status": status,
                "attempts": attempt,
                "usage": response.get("usage", {}) if isinstance(response, dict) else {},
            }
        except RuntimeError as exc:
            last_error = str(exc)
            if attempt < max(1, args.max_attempts) and args.retry_delay_seconds:
                time.sleep(max(0.0, args.retry_delay_seconds))
    return None, {
        "status": "error",
        "selection_reason": "provider_or_model_error",
        "attempts": max(1, args.max_attempts),
        "error_message": last_error,
    }


def run_packet(args: argparse.Namespace, root: Path, packet: dict[str, Any]) -> dict[str, Any]:
    prompt_path = resolve(root, packet["prompt_path"])
    expected_script_name = packet["expected_script_name"]
    prompt = prompt_path.read_text(encoding="utf-8")
    response_path = args.response_dir / f"{Path(expected_script_name).stem}.txt"
    script_path = args.script_dir / expected_script_name
    if args.skip_existing and script_path.exists():
        return {
            "task_id": packet["task_id"],
            "condition": packet["condition"],
            "expected_script_name": expected_script_name,
            "prompt_path": packet["prompt_path"],
            "response_path": relative(root, response_path) if response_path.exists() else "",
            "script_path": relative(root, script_path),
            "status": "cached",
            "call_status": {"status": "cached", "selection_reason": "existing_candidate_script"},
        }
    response_text: str | None = None
    if args.fixture_response_dir:
        fixture_path = fixture_response_path(args.fixture_response_dir, expected_script_name)
        if fixture_path is None:
            call_status = {
                "status": "skipped",
                "selection_reason": "missing_fixture_response",
                "fixture_response_dir": str(args.fixture_response_dir),
            }
        else:
            response_text = fixture_path.read_text(encoding="utf-8")
            call_status = {
                "status": "success",
                "selection_reason": "fixture_response",
                "fixture_response_path": str(fixture_path),
            }
    else:
        response_text, call_status = call_model(args, prompt)

    if response_text is not None:
        response_path.parent.mkdir(parents=True, exist_ok=True)
        script_path.parent.mkdir(parents=True, exist_ok=True)
        response_path.write_text(response_text.rstrip() + "\n", encoding="utf-8")
        script_path.write_text(extract_python_code(response_text).rstrip() + "\n", encoding="utf-8")

    return {
        "task_id": packet["task_id"],
        "condition": packet["condition"],
        "expected_script_name": expected_script_name,
        "prompt_path": packet["prompt_path"],
        "response_path": relative(root, response_path) if response_path.exists() else "",
        "script_path": relative(root, script_path) if script_path.exists() else "",
        "status": call_status["status"],
        "call_status": call_status,
    }


def build_report(args: argparse.Namespace, rows: list[dict[str, Any]], expected_count: int | None = None) -> dict[str, Any]:
    counts: dict[str, int] = {}
    for row in rows:
        counts[row["status"]] = counts.get(row["status"], 0) + 1
    completed = counts.get("success", 0) + counts.get("cached", 0)
    selected_count = len(rows) if expected_count is None else expected_count
    if selected_count and completed == selected_count:
        overall = "complete"
    elif completed:
        overall = "partial"
    elif counts.get("error"):
        overall = "blocked_by_provider_or_model_availability"
    else:
        overall = "pending"
    return {
        "schema_version": SCHEMA_VERSION,
        "run_id": args.run_id,
        "overall_status": overall,
        "status_counts": counts,
        "model_family": args.model_family,
        "model_alias": args.model_alias,
        "wire_api": args.wire_api,
        "prompt_plan": str(args.plan_json),
        "candidate_script_dir": str(args.script_dir),
        "response_dir": str(args.response_dir),
        "selected_packet_count": selected_count,
        "recorded_row_count": len(rows),
        "raw_rows_policy": "not_appended_to_main_raw_rows",
        "evidence_boundary": (
            "This run only generates candidate Python scripts from prompt "
            "packets. It does not execute candidates, score outputs, append "
            "raw rows, or replace paper-facing main rows."
        ),
        "rows": rows,
    }


def markdown_table(rows: list[dict[str, Any]]) -> str:
    lines = [
        "| Task | Condition | Status | Script | Call Status |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        values = [
            row["task_id"],
            row["condition"],
            row["status"],
            row["script_path"],
            row["call_status"].get("selection_reason", ""),
        ]
        lines.append("| " + " | ".join(value.replace("|", "\\|").replace("\n", " ") for value in values) + " |")
    return "\n".join(lines)


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    lines = [
        "# SNAP Executable-Candidate Script Generation Report",
        "",
        f"Evidence boundary: {report['evidence_boundary']}",
        "",
        f"- Run ID: `{report['run_id']}`",
        f"- Overall status: `{report['overall_status']}`",
        f"- Status counts: {report['status_counts']}",
        f"- Model family: `{report['model_family']}`",
        f"- Model alias: `{report['model_alias']}`",
        f"- Candidate script dir: `{report['candidate_script_dir']}`",
        "",
        markdown_table(report["rows"]),
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    root = root_path()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=root)
    parser.add_argument("--plan-json", type=Path, default=DEFAULT_PLAN_JSON)
    parser.add_argument("--task", action="append", choices=("SNAP-T1", "SNAP-T2"), default=[])
    parser.add_argument("--condition", action="append", choices=("summary", "papertoskill"), default=[])
    parser.add_argument("--model-family", default="GPT-family")
    parser.add_argument("--model-alias", default="gpt-5.5")
    parser.add_argument("--wire-api", choices=WIRE_APIS, default="openai_responses")
    parser.add_argument("--base-url-env", default="PAPERTOSKILL_GPT_OPENAI_BASE_URL")
    parser.add_argument("--api-key-env", default="PAPERTOSKILL_GPT_OPENAI_API_KEY")
    parser.add_argument("--base-url")
    parser.add_argument("--api-key")
    parser.add_argument("--max-tokens", type=int, default=2400)
    parser.add_argument("--timeout-seconds", type=float, default=300.0)
    parser.add_argument("--max-attempts", type=int, default=5)
    parser.add_argument("--retry-delay-seconds", type=float, default=5.0)
    parser.add_argument("--anthropic-version", default="2023-06-01")
    parser.add_argument("--fixture-response-dir", type=Path)
    parser.add_argument("--skip-existing", action="store_true")
    parser.add_argument("--run-id", default="")
    parser.add_argument("--script-dir", type=Path)
    parser.add_argument("--response-dir", type=Path)
    parser.add_argument(
        "--output-json",
        type=Path,
        default=root / "results" / "real_reuse" / "snapatac2_executable_candidate_script_generation_report.json",
    )
    parser.add_argument(
        "--output-md",
        type=Path,
        default=root / "results" / "real_reuse" / "snapatac2_executable_candidate_script_generation_report.md",
    )
    args = parser.parse_args()

    args.root = args.root.resolve()
    args.plan_json = resolve(args.root, args.plan_json)
    args.run_id = args.run_id or time.strftime("snap_exec_candidate_scripts_%Y%m%d_%H%M%S")
    if args.script_dir is None:
        args.script_dir = args.root / "results" / "real_reuse" / "snapatac2_executable_candidate_scripts" / args.run_id
    else:
        args.script_dir = resolve(args.root, args.script_dir)
    if args.response_dir is None:
        args.response_dir = args.root / "results" / "real_reuse" / "snapatac2_executable_candidate_script_responses" / args.run_id
    else:
        args.response_dir = resolve(args.root, args.response_dir)

    plan = load_json(args.plan_json)
    packets = plan.get("packets", [])
    if args.task:
        allowed_tasks = set(args.task)
        packets = [packet for packet in packets if packet.get("task_id") in allowed_tasks]
    if args.condition:
        allowed_conditions = set(args.condition)
        packets = [packet for packet in packets if packet.get("condition") in allowed_conditions]
    rows: list[dict[str, Any]] = []
    report = build_report(args, rows, expected_count=len(packets))
    write_json(args.output_json, report)
    write_markdown(args.output_md, report)
    for packet in packets:
        rows.append(run_packet(args, args.root, packet))
        report = build_report(args, rows, expected_count=len(packets))
        write_json(args.output_json, report)
        write_markdown(args.output_md, report)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
