#!/usr/bin/env python
"""Run locked SWE-agent real-reuse tasks under primary and sanity contexts."""

from __future__ import annotations

import argparse
import json
import os
import re
import time
from pathlib import Path
from typing import Any

from run_model_ablation_prompts import WIRE_APIS, extract_content, request_json, wire_endpoint
from score_real_reuse_swe import score_patch


SCHEMA_VERSION = "0.1"
TASK_IDS = ("SWE-T1", "SWE-T2")
PRIMARY_CONDITIONS = ("summary", "papertoskill")
CONDITIONS = PRIMARY_CONDITIONS + ("full_excerpt",)


def root_path() -> Path:
    return Path(__file__).resolve().parents[1]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def resolve(root: Path, raw_path: str | Path) -> Path:
    path = Path(raw_path)
    return path if path.is_absolute() else root / path


def relative(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def task_spec_path(root: Path, task_id: str) -> Path:
    return root / "benchmarks" / "real_reuse" / "tasks" / f"{task_id}.json"


def asset_manifest_path(root: Path, task_id: str) -> Path:
    return root / "benchmarks" / "real_reuse" / "assets" / task_id / "asset_manifest.json"


def asset_file(manifest: dict[str, Any], slot: str) -> str:
    for item in manifest.get("files", []):
        if item.get("slot") == slot:
            return str(item["path"])
    raise KeyError(f"missing asset slot {slot}")


def optional_asset_text(
    root: Path,
    manifest: dict[str, Any],
    slot: str,
    *,
    required_visibility: str | None = None,
) -> str:
    for item in manifest.get("files", []):
        if item.get("slot") == slot:
            if required_visibility is not None and item.get("visibility") != required_visibility:
                return ""
            path = resolve(root, item["path"])
            return path.read_text(encoding="utf-8") if path.exists() else ""
    return ""


def condition_path(task_spec: dict[str, Any], condition: str) -> str:
    for item in task_spec.get("conditions", []):
        if item.get("id") == condition:
            return str(item["context_path"])
    raise KeyError(f"missing condition {condition}")


def token_proxy(*texts: str) -> int:
    return sum(len(text.split()) for text in texts if text)


def extract_patch(text: str) -> str:
    fenced = re.search(r"```(?:diff|patch)?\s*(.*?)```", text, flags=re.IGNORECASE | re.DOTALL)
    if fenced:
        return fenced.group(1).strip()
    marker = re.search(r"(diff --git .*|---\s+a/.*)", text, flags=re.DOTALL)
    return marker.group(1).strip() if marker else text.strip()


def build_prompt(root: Path, task_id: str, condition: str) -> str:
    task_spec = load_json(task_spec_path(root, task_id))
    manifest = load_json(asset_manifest_path(root, task_id))
    context = resolve(root, condition_path(task_spec, condition)).read_text(encoding="utf-8")
    task_prompt = resolve(root, asset_file(manifest, "task_prompt")).read_text(encoding="utf-8")
    source_context = optional_asset_text(
        root,
        manifest,
        "source_context",
        required_visibility="model_visible",
    ).strip()
    parts = [
        f"# Real-Reuse Condition: {condition}",
        "You are running a locked SWE-agent PaperToSkill real-reuse task. "
        "Use only the model-visible context and task prompt below. Do not "
        "request gold patches, hidden test patches, or scorer-only assets.",
        "# Condition Context",
        context.strip(),
    ]
    if source_context:
        parts.extend(["# Shared Source Context", source_context])
    parts.extend(
        [
            "# Locked Task Prompt",
            task_prompt.strip(),
            "# Output Contract",
            "Return exactly one unified diff patch. The patch must apply from "
            "the starter workspace root and should be minimal.",
        ]
    )
    return "\n\n".join(parts).strip() + "\n"


def fixture_response_path(fixture_dir: Path, task_id: str, condition: str) -> Path | None:
    for suffix in (".diff", ".patch", ".md", ".txt"):
        path = fixture_dir / f"{task_id}_{condition}{suffix}"
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
        "You are executing a SWE-agent-style real-reuse task. Return only a "
        "unified diff patch in a code block. Do not claim tests passed unless "
        "the verification command succeeds."
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
            usage = response.get("usage", {}) if isinstance(response, dict) else {}
            return content, {
                "status": "success",
                "selection_reason": "live_endpoint_response",
                "http_status": status,
                "attempts": attempt,
                "usage": usage,
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


def workflow_score(text: str) -> float:
    lowered = text.lower()
    checks = [
        "diff --git" in lowered or "--- a/" in lowered,
        "+++" in lowered,
        "@@" in lowered,
        "test" in lowered or "pytest" in lowered or "unittest" in lowered,
    ]
    return sum(1 for passed in checks if passed) / len(checks)


def run_single(args: argparse.Namespace, task_id: str, condition: str, run_id: str) -> dict[str, Any]:
    root = args.root.resolve()
    task_spec = load_json(task_spec_path(root, task_id))
    manifest_path = asset_manifest_path(root, task_id)
    if not manifest_path.exists():
        return {
            "run_id": run_id,
            "task_id": task_id,
            "source_paper_id": task_spec["source_paper_id"],
            "domain": task_spec["domain"],
            "condition": condition,
            "model_family": args.model_family,
            "model_alias": args.model_alias,
            "wire_api": args.wire_api,
            "status": "skipped",
            "task_score": None,
            "success": None,
            "workflow_score": None,
            "unsupported_errors": None,
            "tokens": None,
            "time_seconds": 0.0,
            "interventions": 0,
            "failure_reason": "missing_fixture_assets",
            "output_path": "",
            "prompt_path": "",
            "metric_path": "",
            "call_status": {
                "status": "skipped",
                "selection_reason": "missing_fixture_assets",
                "asset_manifest": relative(root, manifest_path),
            },
        }
    manifest = load_json(manifest_path)
    prompt = build_prompt(root, task_id, condition)
    run_dir = args.output_dir / task_id / condition / run_id
    prompt_path = run_dir / "prompt.md"
    response_path = run_dir / "response.txt"
    patch_path = run_dir / "candidate.patch"
    metric_path = run_dir / "metric.json"
    run_dir.mkdir(parents=True, exist_ok=True)
    prompt_path.write_text(prompt, encoding="utf-8")

    started = time.perf_counter()
    response_text: str | None = None
    if args.fixture_response_dir:
        fixture_path = fixture_response_path(args.fixture_response_dir, task_id, condition)
        if fixture_path is None:
            call_status = {
                "status": "skipped",
                "selection_reason": "missing_fixture_response",
                "fixture_response_dir": str(args.fixture_response_dir),
            }
        else:
            response_text = fixture_path.read_text(encoding="utf-8").strip()
            call_status = {
                "status": "success",
                "selection_reason": "fixture_response",
                "fixture_response_path": str(fixture_path),
            }
    else:
        response_text, call_status = call_model(args, prompt)
    elapsed = time.perf_counter() - started

    if response_text is None:
        return {
            "run_id": run_id,
            "task_id": task_id,
            "source_paper_id": task_spec["source_paper_id"],
            "domain": task_spec["domain"],
            "condition": condition,
            "model_family": args.model_family,
            "model_alias": args.model_alias,
            "wire_api": args.wire_api,
            "status": call_status["status"],
            "task_score": None,
            "success": None,
            "workflow_score": None,
            "unsupported_errors": None,
            "tokens": None,
            "time_seconds": round(elapsed, 4),
            "interventions": 0,
            "failure_reason": call_status.get("error_message") or call_status.get("selection_reason", ""),
            "output_path": "",
            "prompt_path": relative(root, prompt_path),
            "metric_path": "",
            "call_status": call_status,
        }

    response_path.write_text(response_text.strip() + "\n", encoding="utf-8")
    patch_path.write_text(extract_patch(response_text).rstrip() + "\n", encoding="utf-8")
    workspace_dir = resolve(root, manifest["workspace_dir"])
    test_command_file = resolve(root, asset_file(manifest, "target_test_command"))
    test_patch_path = None
    try:
        test_patch_path = resolve(root, asset_file(manifest, "test_patch"))
    except KeyError:
        test_patch_path = None
    metric = score_patch(
        task_id=task_id,
        patch_path=patch_path,
        workspace=workspace_dir,
        test_command=test_command_file.read_text(encoding="utf-8").strip(),
        timeout_seconds=args.score_timeout_seconds,
        test_patch_path=test_patch_path,
    )
    write_json(metric_path, metric)
    usage = call_status.get("usage", {})
    total_tokens = usage.get("total_tokens") or usage.get("input_tokens")
    if total_tokens is None:
        total_tokens = token_proxy(prompt, response_text)
    return {
        "run_id": run_id,
        "task_id": task_id,
        "source_paper_id": task_spec["source_paper_id"],
        "domain": task_spec["domain"],
        "condition": condition,
        "model_family": args.model_family,
        "model_alias": args.model_alias,
        "wire_api": args.wire_api,
        "status": "scored",
        "task_score": metric["task_score"],
        "success": metric["success"],
        "workflow_score": workflow_score(response_text),
        "unsupported_errors": None,
        "unsupported_errors_status": "not_automatically_judged",
        "tokens": total_tokens,
        "token_source": "provider_usage_or_whitespace_proxy",
        "time_seconds": round(elapsed, 4),
        "interventions": 0,
        "failure_reason": metric.get("failure_reason", ""),
        "output_path": relative(root, patch_path),
        "prompt_path": relative(root, prompt_path),
        "metric_path": relative(root, metric_path),
        "call_status": call_status,
        "evidence_boundary": (
            "Single SWE real-reuse scored output. This row is not aggregate "
            "evidence for all eight planned paper-tasks."
        ),
    }


def append_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def markdown_table(rows: list[dict[str, Any]]) -> str:
    lines = [
        "| Task | Condition | Status | Score | Success | Failure | Output |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        values = [
            str(row.get("task_id", "")),
            str(row.get("condition", "")),
            str(row.get("status", "")),
            "" if row.get("task_score") is None else str(row.get("task_score")),
            "" if row.get("success") is None else str(row.get("success")),
            str(row.get("failure_reason", ""))[:160],
            str(row.get("output_path", "")),
        ]
        lines.append("| " + " | ".join(value.replace("|", "\\|").replace("\n", " ") for value in values) + " |")
    return "\n".join(lines)


def build_report(args: argparse.Namespace, run_id: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    counts: dict[str, int] = {}
    for row in rows:
        counts[str(row["status"])] = counts.get(str(row["status"]), 0) + 1
    if counts.get("scored") == len(rows) and rows:
        overall = "complete"
    elif counts.get("scored"):
        overall = "partial"
    elif counts.get("error"):
        overall = "blocked_by_provider_or_model_availability"
    else:
        overall = "pending"
    return {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id,
        "overall_status": overall,
        "status_counts": counts,
        "tasks": list(args.task),
        "conditions": list(args.condition),
        "model_family": args.model_family,
        "model_alias": args.model_alias,
        "wire_api": args.wire_api,
        "raw_rows_output": str(args.raw_rows_output),
        "evidence_boundary": (
            "Runner report for locked SWE real-reuse tasks. It can compare "
            "Summary and PaperToSkill for prepared SWE tasks only when both "
            "conditions have scored rows. It does not complete the full "
            "eight-task real-reuse benchmark."
        ),
        "results": rows,
    }


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    lines = [
        "# SWE Real-Reuse Run Report",
        "",
        "Evidence boundary: this report covers only prepared SWE real-reuse "
        "tasks. Provider/model errors are availability evidence, not "
        "model-quality failures. Aggregate PaperToSkill claims require the "
        "broader real-reuse benchmark.",
        "",
        f"- Run ID: {report['run_id']}",
        f"- Overall status: {report['overall_status']}",
        f"- Status counts: {report['status_counts']}",
        f"- Model family: {report['model_family']}",
        f"- Model alias: {report['model_alias']}",
        f"- Wire API: {report['wire_api']}",
        f"- Raw rows: {report['raw_rows_output']}",
        "",
        markdown_table(report["results"]),
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    root = root_path()
    parser = argparse.ArgumentParser(description="Run locked SWE real-reuse tasks.")
    parser.add_argument("--root", type=Path, default=root)
    parser.add_argument("--task", action="append", choices=TASK_IDS, default=[])
    parser.add_argument("--condition", action="append", choices=CONDITIONS, default=[])
    parser.add_argument("--model-family", default="GPT-family")
    parser.add_argument("--model-alias", default="gpt-5.5")
    parser.add_argument("--wire-api", choices=WIRE_APIS, default="openai_responses")
    parser.add_argument("--base-url-env", default="PAPERTOSKILL_GPT_OPENAI_BASE_URL")
    parser.add_argument("--api-key-env", default="PAPERTOSKILL_GPT_OPENAI_API_KEY")
    parser.add_argument("--base-url")
    parser.add_argument("--api-key")
    parser.add_argument("--max-tokens", type=int, default=1800)
    parser.add_argument("--timeout-seconds", type=float, default=120.0)
    parser.add_argument("--score-timeout-seconds", type=float, default=60.0)
    parser.add_argument("--max-attempts", type=int, default=2)
    parser.add_argument("--retry-delay-seconds", type=float, default=2.0)
    parser.add_argument("--anthropic-version", default="2023-06-01")
    parser.add_argument("--fixture-response-dir", type=Path)
    parser.add_argument("--run-id", default="")
    parser.add_argument("--output-dir", type=Path, default=root / "results" / "real_reuse" / "runs")
    parser.add_argument("--raw-rows-output", type=Path, default=root / "results" / "real_reuse" / "raw_rows.jsonl")
    parser.add_argument("--output-json", type=Path, default=root / "results" / "real_reuse" / "swe_run_report.json")
    parser.add_argument("--output-md", type=Path, default=root / "results" / "real_reuse" / "swe_run_report.md")
    args = parser.parse_args()

    if not args.task:
        args.task = list(TASK_IDS)
    if not args.condition:
        args.condition = list(PRIMARY_CONDITIONS)
    run_id = args.run_id or time.strftime("run_%Y%m%d_%H%M%S")

    rows = [run_single(args, task_id, condition, run_id) for task_id in args.task for condition in args.condition]
    scored_rows = [row for row in rows if row.get("status") == "scored"]
    append_jsonl(args.raw_rows_output, scored_rows)
    report = build_report(args, run_id, rows)
    write_json(args.output_json, report)
    write_markdown(args.output_md, report)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
