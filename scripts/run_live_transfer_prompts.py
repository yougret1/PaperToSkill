#!/usr/bin/env python
"""Run PaperToSkill live-transfer prompt packets with an OpenAI-compatible API."""

from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path
from typing import Any

from run_model_ablation_prompts import endpoint, extract_content, model_ids_from_response, request_json


DEFAULT_ALIASES = ["claude-opus-4-8", "claude-opus-4.8", "claude-opus-4-7", "claude-opus-4-6"]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def resolve(root: Path, raw_path: str | Path) -> Path:
    path = Path(raw_path)
    return path if path.is_absolute() else root / path


def select_alias(candidates: list[str], available: list[str]) -> tuple[str | None, str]:
    for candidate in candidates:
        if candidate in available:
            return candidate, "exact"
    if not available and candidates:
        return candidates[0], "unverified_no_model_list"
    return None, "unavailable_" + (candidates[0] if candidates else "missing_alias")


def candidate_attempts(candidates: list[str], available: list[str]) -> list[tuple[str, str]]:
    exact = [(candidate, "exact") for candidate in candidates if candidate in available]
    if exact:
        return exact
    if not available and candidates:
        return [(candidates[0], "unverified_no_model_list")]
    return []


def prompt_row_id(index_path: Path, prompt: dict[str, Any]) -> str:
    return "::".join(
        [
            index_path.parent.name,
            str(prompt.get("harness_id", "")),
            str(prompt.get("variant_id", "")),
        ]
    )


def run(args: argparse.Namespace) -> dict[str, Any]:
    root = args.root.resolve()
    aliases = args.model_alias or DEFAULT_ALIASES
    base_url = args.base_url or os.environ.get(args.base_url_env, "")
    api_key = args.api_key or os.environ.get(args.api_key_env, "")
    started = int(time.time())
    results: list[dict[str, Any]] = []
    catalog: dict[str, Any] = {
        "base_url": base_url,
        "base_url_env": args.base_url_env,
        "api_key_env": args.api_key_env,
        "status": "not_requested",
        "model_count": 0,
        "model_ids": [],
    }

    if not base_url or not api_key:
        for raw_index in args.index:
            index_path = resolve(root, raw_index)
            index = load_json(index_path)
            for prompt in index.get("prompts", []):
                results.append(
                    {
                        "task": index.get("task", ""),
                        "index_path": str(index_path.relative_to(root)) if index_path.is_relative_to(root) else str(index_path),
                        "row_id": prompt_row_id(index_path, prompt),
                        "harness_id": prompt.get("harness_id", ""),
                        "variant_id": prompt.get("variant_id", ""),
                        "status": "skipped",
                        "selection_reason": "missing_base_url_or_api_key",
                        "expected_response_path": prompt.get("expected_response_path", ""),
                    }
                )
        return build_report(args, started, catalog, results)

    try:
        _, model_response = request_json(endpoint(base_url, "models"), api_key)
        available = model_ids_from_response(model_response)
        catalog.update({"status": "success", "model_count": len(available), "model_ids": available})
    except RuntimeError as exc:
        available = []
        catalog.update({"status": "error", "error_message": str(exc), "model_count": 0, "model_ids": []})

    if catalog["status"] == "error" and not args.allow_unverified_model:
        for raw_index in args.index:
            index_path = resolve(root, raw_index)
            index = load_json(index_path)
            for prompt in index.get("prompts", []):
                results.append(
                    {
                        "task": index.get("task", ""),
                        "index_path": str(index_path.relative_to(root)) if index_path.is_relative_to(root) else str(index_path),
                        "row_id": prompt_row_id(index_path, prompt),
                        "harness_id": prompt.get("harness_id", ""),
                        "variant_id": prompt.get("variant_id", ""),
                        "status": "error",
                        "selection_reason": "model_list_failed",
                        "error_message": catalog.get("error_message", ""),
                        "expected_response_path": prompt.get("expected_response_path", ""),
                    }
                )
        return build_report(args, started, catalog, results)

    alias, reason = select_alias(aliases, available)
    if alias is None:
        for raw_index in args.index:
            index_path = resolve(root, raw_index)
            index = load_json(index_path)
            for prompt in index.get("prompts", []):
                results.append(
                    {
                        "task": index.get("task", ""),
                        "index_path": str(index_path.relative_to(root)) if index_path.is_relative_to(root) else str(index_path),
                        "row_id": prompt_row_id(index_path, prompt),
                        "harness_id": prompt.get("harness_id", ""),
                        "variant_id": prompt.get("variant_id", ""),
                        "status": "skipped",
                        "selection_reason": reason,
                        "expected_response_path": prompt.get("expected_response_path", ""),
                    }
                )
        return build_report(args, started, catalog, results)

    attempts = candidate_attempts(aliases, available) if not args.allow_unverified_model else [(alias, reason)]
    for raw_index in args.index:
        index_path = resolve(root, raw_index)
        index = load_json(index_path)
        for prompt in index.get("prompts", []):
            prompt_path = resolve(root, prompt["prompt_path"])
            response_path = resolve(root, prompt["expected_response_path"])
            if args.skip_existing and response_path.exists():
                results.append(
                    {
                        "task": index.get("task", ""),
                        "index_path": str(index_path.relative_to(root)) if index_path.is_relative_to(root) else str(index_path),
                        "row_id": prompt_row_id(index_path, prompt),
                        "harness_id": prompt.get("harness_id", ""),
                        "variant_id": prompt.get("variant_id", ""),
                        "status": "skipped",
                        "selection_reason": "response_already_exists",
                        "alias_used": alias,
                        "expected_response_path": prompt.get("expected_response_path", ""),
                    }
                )
                continue

            prompt_text = prompt_path.read_text(encoding="utf-8")
            attempt_records = []
            saved = None
            for candidate, candidate_reason in attempts:
                body = {
                    "model": candidate,
                    "messages": [
                        {
                            "role": "system",
                            "content": (
                                "You are executing a PaperToSkill live-transfer prompt. "
                                "Follow the required output contract. Do not invent completed experiments, "
                                "human scores, provider bills, or unavailable tools."
                            ),
                        },
                        {"role": "user", "content": prompt_text},
                    ],
                    "temperature": 0,
                    "max_tokens": args.max_tokens,
                }
                try:
                    status, response = request_json(endpoint(base_url, "chat/completions"), api_key, method="POST", body=body)
                    content = extract_content(response).strip()
                    response_path.parent.mkdir(parents=True, exist_ok=True)
                    response_path.write_text(content + "\n", encoding="utf-8")
                    attempt_records.append({"alias": candidate, "selection_reason": candidate_reason, "status": "success"})
                    saved = {
                        "task": index.get("task", ""),
                        "index_path": str(index_path.relative_to(root)) if index_path.is_relative_to(root) else str(index_path),
                        "row_id": prompt_row_id(index_path, prompt),
                        "harness_id": prompt.get("harness_id", ""),
                        "variant_id": prompt.get("variant_id", ""),
                        "status": "success",
                        "alias_used": candidate,
                        "selection_reason": candidate_reason,
                        "attempted_aliases": attempt_records,
                        "http_status": status,
                        "response_chars": len(content),
                        "expected_response_path": prompt.get("expected_response_path", ""),
                    }
                    break
                except RuntimeError as exc:
                    attempt_records.append(
                        {
                            "alias": candidate,
                            "selection_reason": candidate_reason,
                            "status": "error",
                            "error_message": str(exc),
                        }
                    )
            if saved is not None:
                results.append(saved)
            else:
                results.append(
                    {
                        "task": index.get("task", ""),
                        "index_path": str(index_path.relative_to(root)) if index_path.is_relative_to(root) else str(index_path),
                        "row_id": prompt_row_id(index_path, prompt),
                        "harness_id": prompt.get("harness_id", ""),
                        "variant_id": prompt.get("variant_id", ""),
                        "status": "error",
                        "alias_used": attempts[-1][0] if attempts else "",
                        "selection_reason": "all_candidate_aliases_failed",
                        "attempted_aliases": attempt_records,
                        "error_message": attempt_records[-1].get("error_message", "") if attempt_records else "",
                        "expected_response_path": prompt.get("expected_response_path", ""),
                    }
                )

    return build_report(args, started, catalog, results)


def build_report(args: argparse.Namespace, started: int, catalog: dict[str, Any], results: list[dict[str, Any]]) -> dict[str, Any]:
    counts: dict[str, int] = {}
    for row in results:
        counts[row["status"]] = counts.get(row["status"], 0) + 1
    if counts.get("success") and not counts.get("error") and not counts.get("skipped"):
        overall = "complete"
    elif counts.get("success"):
        overall = "partial"
    elif counts.get("error"):
        overall = "blocked_by_provider_or_model_availability"
    else:
        overall = "pending"
    return {
        "schema_version": "0.1",
        "evidence_boundary": (
            "Live-transfer endpoint attempt report. Successful rows have saved response files. "
            "Failed rows are provider/model availability evidence only, not model-quality evidence."
        ),
        "index_paths": [str(path) for path in args.index],
        "model_aliases": args.model_alias or DEFAULT_ALIASES,
        "started_at_unix": started,
        "completed_at_unix": int(time.time()),
        "overall_status": overall,
        "status_counts": counts,
        "model_catalog": catalog,
        "results": results,
    }


def markdown_table(rows: list[dict[str, Any]]) -> str:
    lines = [
        "| Task | Harness | Variant | Status | Alias | Detail |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        attempts = row.get("attempted_aliases") or []
        if attempts:
            detail = "; ".join(f"{item['alias']}={item['status']}" for item in attempts)
        else:
            detail = row.get("selection_reason", "")
        values = [
            str(row.get("task", "")),
            str(row.get("harness_id", "")),
            str(row.get("variant_id", "")),
            str(row.get("status", "")),
            str(row.get("alias_used", "")),
            detail,
        ]
        lines.append("| " + " | ".join(value.replace("|", "\\|").replace("\n", " ")[:240] for value in values) + " |")
    return "\n".join(lines)


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    counts = report["status_counts"]
    lines = [
        "# Live Transfer Run Report",
        "",
        "Evidence boundary: successful rows have saved response files. Failed rows "
        "are provider/model availability evidence only, not model-quality evidence.",
        "",
        f"- Overall status: {report['overall_status']}",
        f"- Started at unix time: {report['started_at_unix']}",
        f"- Completed at unix time: {report['completed_at_unix']}",
        f"- Successes: {counts.get('success', 0)}",
        f"- Errors: {counts.get('error', 0)}",
        f"- Skipped: {counts.get('skipped', 0)}",
        f"- Model catalog status: {report['model_catalog'].get('status')}",
        f"- Model count: {report['model_catalog'].get('model_count', 0)}",
        "",
        markdown_table(report["results"]),
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="Run PaperToSkill live-transfer prompt packets.")
    parser.add_argument("--root", type=Path, default=root)
    parser.add_argument("--index", action="append", required=True, type=Path)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-md", type=Path, required=True)
    parser.add_argument("--model-alias", action="append")
    parser.add_argument("--base-url-env", default="AI_SCIENTIST_OPENAI_BASE_URL")
    parser.add_argument("--api-key-env", default="AI_SCIENTIST_OPENAI_API_KEY")
    parser.add_argument("--base-url")
    parser.add_argument("--api-key")
    parser.add_argument("--max-tokens", type=int, default=900)
    parser.add_argument("--skip-existing", action="store_true")
    parser.add_argument("--allow-unverified-model", action="store_true")
    args = parser.parse_args()

    report = run(args)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_markdown(args.output_md, report)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
