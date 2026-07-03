#!/usr/bin/env python
"""Run locked Reflexion real-reuse tasks under Summary/PaperToSkill contexts."""

from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path
from typing import Any

from run_model_ablation_prompts import WIRE_APIS, extract_content, request_json, wire_endpoint
from score_real_reuse_reflexion import score_ref_t1, score_ref_t2


SCHEMA_VERSION = "0.1"
TASK_IDS = ("REF-T1", "REF-T2")
CONDITIONS = ("summary", "papertoskill")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def root_path() -> Path:
    return Path(__file__).resolve().parents[1]


def resolve(root: Path, raw_path: str | Path) -> Path:
    path = Path(raw_path)
    return path if path.is_absolute() else root / path


def relative(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def task_spec_path(root: Path, task_id: str) -> Path:
    return root / "benchmarks" / "real_reuse" / "tasks" / f"{task_id}.json"


def asset_manifest_path(root: Path, task_id: str) -> Path:
    return root / "benchmarks" / "real_reuse" / "assets" / task_id / "asset_manifest.json"


def asset_file(manifest: dict[str, Any], slot: str) -> str:
    for item in manifest.get("files", []):
        if item.get("slot") == slot:
            return str(item["path"])
    raise KeyError(f"missing asset slot {slot}")


def condition_path(task_spec: dict[str, Any], condition: str) -> str:
    for item in task_spec.get("conditions", []):
        if item.get("id") == condition:
            return str(item["context_path"])
    raise KeyError(f"missing condition {condition}")


def token_proxy(*texts: str) -> int:
    """Small local proxy when provider usage tokens are absent."""
    return sum(len(text.split()) for text in texts if text)


def build_prompt(root: Path, task_id: str, condition: str) -> str:
    task_spec = load_json(task_spec_path(root, task_id))
    manifest = load_json(asset_manifest_path(root, task_id))
    context = resolve(root, condition_path(task_spec, condition)).read_text(encoding="utf-8")
    task_prompt = resolve(root, asset_file(manifest, "task_prompt")).read_text(encoding="utf-8")
    output_format = {
        "REF-T1": (
            "Return only JSON with keys `first_attempt`, `reflection`, and "
            "`final_answer`. Keep `final_answer` as the short answer itself "
            "(for yes/no questions, use `yes` or `no`). Do not mention hidden "
            "answer keys."
        ),
        "REF-T2": (
            "Return a short reflection and one corrected Python code block "
            "containing `def has_close_elements`. Do not mention hidden tests "
            "or canonical solutions."
        ),
    }[task_id]
    return "\n\n".join(
        [
            f"# Real-Reuse Condition: {condition}",
            "You are running a locked PaperToSkill real-reuse task. Use only "
            "the model-visible context and task prompt below.",
            "# Condition Context",
            context.strip(),
            "# Locked Task Prompt",
            task_prompt.strip(),
            "# Output Contract",
            output_format,
        ]
    ).strip() + "\n"


def fixture_response_path(fixture_dir: Path, task_id: str, condition: str) -> Path | None:
    for suffix in (".json", ".md", ".txt", ".py"):
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
        "You are executing a PaperToSkill real-reuse task. Follow the output "
        "contract, use only model-visible assets, and do not claim hidden "
        "scorer information or unavailable runs."
    )
    if wire_api == "openai_responses":
        return (
            {
                "model": model_alias,
                "input": f"{system}\n\n{prompt}",
                "max_output_tokens": max_tokens,
            },
            {},
        )
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
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
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


def score_output(root: Path, task_id: str, output_path: Path, timeout_seconds: float) -> dict[str, Any]:
    asset_dir = root / "benchmarks" / "real_reuse" / "assets" / task_id
    if task_id == "REF-T1":
        return score_ref_t1(output_path, asset_dir / "answer_key.json")
    return score_ref_t2(output_path, asset_dir / "tests.json", timeout_seconds)


def workflow_score(task_id: str, text: str) -> float:
    lowered = text.lower()
    if task_id == "REF-T1":
        checks = [
            "first_attempt" in lowered or "first attempt" in lowered,
            "reflection" in lowered,
            "final_answer" in lowered or "final answer" in lowered,
        ]
    else:
        checks = [
            "reflection" in lowered,
            "def has_close_elements" in lowered,
        ]
    return sum(1 for passed in checks if passed) / len(checks)


def run_single(args: argparse.Namespace, task_id: str, condition: str, run_id: str) -> dict[str, Any]:
    root = args.root.resolve()
    task_spec = load_json(task_spec_path(root, task_id))
    prompt = build_prompt(root, task_id, condition)
    run_dir = args.output_dir / task_id / condition / run_id
    prompt_path = run_dir / "prompt.md"
    response_path = run_dir / "response.txt"
    metric_path = run_dir / "metric.json"
    run_dir.mkdir(parents=True, exist_ok=True)
    prompt_path.write_text(prompt, encoding="utf-8")

    started = time.perf_counter()
    response_text: str | None = None
    call_status: dict[str, Any]
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
    metric = score_output(root, task_id, response_path, args.score_timeout_seconds)
    write_json(metric_path, metric)
    usage = call_status.get("usage", {})
    total_tokens = usage.get("total_tokens") or usage.get("input_tokens")
    if total_tokens is None:
        total_tokens = token_proxy(prompt, response_text)
    raw_row = {
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
        "workflow_score": workflow_score(task_id, response_text),
        "unsupported_errors": None,
        "unsupported_errors_status": "not_automatically_judged",
        "tokens": total_tokens,
        "token_source": "provider_usage_or_whitespace_proxy",
        "time_seconds": round(elapsed, 4),
        "interventions": 0,
        "failure_reason": metric.get("failure_reason", ""),
        "output_path": relative(root, response_path),
        "prompt_path": relative(root, prompt_path),
        "metric_path": relative(root, metric_path),
        "call_status": call_status,
        "evidence_boundary": (
            "Single REF real-reuse scored output. This row is not aggregate "
            "evidence for all eight planned paper-tasks."
        ),
    }
    return raw_row


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
            "Runner report for locked Reflexion real-reuse tasks. It can "
            "compare Summary and PaperToSkill for REF-T1/REF-T2 only when "
            "both conditions have scored rows. It does not complete the full "
            "eight-task real-reuse benchmark."
        ),
        "results": rows,
    }


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    lines = [
        "# Reflexion Real-Reuse Run Report",
        "",
        "Evidence boundary: this report covers only locked Reflexion real-reuse "
        "tasks. Provider/model errors are availability evidence, not model-quality "
        "failures. Aggregate PaperToSkill claims require the broader real-reuse "
        "benchmark.",
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
    parser = argparse.ArgumentParser(description="Run locked Reflexion real-reuse tasks.")
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
    parser.add_argument("--max-tokens", type=int, default=1200)
    parser.add_argument("--timeout-seconds", type=float, default=90.0)
    parser.add_argument("--score-timeout-seconds", type=float, default=5.0)
    parser.add_argument("--max-attempts", type=int, default=2)
    parser.add_argument("--retry-delay-seconds", type=float, default=2.0)
    parser.add_argument("--anthropic-version", default="2023-06-01")
    parser.add_argument("--fixture-response-dir", type=Path)
    parser.add_argument("--run-id", default="")
    parser.add_argument("--output-dir", type=Path, default=root / "results" / "real_reuse" / "runs")
    parser.add_argument("--raw-rows-output", type=Path, default=root / "results" / "real_reuse" / "raw_rows.jsonl")
    parser.add_argument("--output-json", type=Path, default=root / "results" / "real_reuse" / "reflexion_run_report.json")
    parser.add_argument("--output-md", type=Path, default=root / "results" / "real_reuse" / "reflexion_run_report.md")
    args = parser.parse_args()

    if not args.task:
        args.task = list(TASK_IDS)
    if not args.condition:
        args.condition = list(CONDITIONS)
    run_id = args.run_id or time.strftime("run_%Y%m%d_%H%M%S")

    rows = [
        run_single(args, task_id, condition, run_id)
        for task_id in args.task
        for condition in args.condition
    ]
    scored_rows = [row for row in rows if row.get("status") == "scored"]
    append_jsonl(args.raw_rows_output, scored_rows)
    report = build_report(args, run_id, rows)
    write_json(args.output_json, report)
    write_markdown(args.output_md, report)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
