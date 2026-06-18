#!/usr/bin/env python
"""Run PaperToSkill model-ablation prompt packets against OpenAI-compatible APIs.

The runner reads credentials from environment variables and never writes API
keys to artifacts. Successful responses are saved to the expected response
paths from the prompt index; provider errors are recorded in a redacted run
report.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


SECRET_PATTERN = re.compile(r"sk-[A-Za-z0-9]{20,}")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def redact(text: str) -> str:
    return SECRET_PATTERN.sub("sk-REDACTED", text)


def endpoint(base_url: str, suffix: str) -> str:
    return base_url.rstrip("/") + "/" + suffix.lstrip("/")


def request_json(url: str, api_key: str, method: str = "GET", body: dict[str, Any] | None = None) -> tuple[int, dict[str, Any]]:
    data = None if body is None else json.dumps(body).encode("utf-8")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            payload = response.read().decode("utf-8", errors="replace")
            return response.status, json.loads(payload) if payload else {}
    except urllib.error.HTTPError as exc:
        payload = exc.read().decode("utf-8", errors="replace")
        try:
            parsed: dict[str, Any] = json.loads(payload) if payload else {}
        except json.JSONDecodeError:
            parsed = {"raw_body": payload[:2000]}
        parsed["http_error"] = exc.code
        raise RuntimeError(redact(json.dumps(parsed, ensure_ascii=False))) from exc
    except Exception as exc:  # noqa: BLE001 - redacted report path is the boundary
        raise RuntimeError(redact(str(exc))) from exc


def model_ids_from_response(response: dict[str, Any]) -> list[str]:
    if isinstance(response.get("data"), list):
        ids = [str(item.get("id", "")) for item in response["data"] if isinstance(item, dict)]
    elif isinstance(response.get("models"), list):
        ids = [
            str(item.get("id", "")) if isinstance(item, dict) else str(item)
            for item in response["models"]
        ]
    else:
        ids = []
    return sorted({model_id for model_id in ids if model_id})


def gpt_fallback(available: list[str]) -> str | None:
    lowered = {model.lower(): model for model in available}
    exact_preferences = [
        "gpt-5.5",
        "gpt-5.5-chat",
        "gpt-5.1",
        "gpt-5",
        "gpt-4.1",
        "gpt-4o",
    ]
    for preference in exact_preferences:
        if preference in lowered:
            return lowered[preference]
    gpt_models = [model for model in available if model.lower().startswith("gpt")]
    return sorted(gpt_models, reverse=True)[0] if gpt_models else None


def select_model_alias(model_slot: dict[str, Any], available: list[str]) -> tuple[str | None, str]:
    configured = str(model_slot["model_alias"])
    if configured in available:
        return configured, "exact"
    if model_slot["id"] == "gpt_5_5_or_gpt_family":
        fallback = gpt_fallback(available)
        if fallback:
            return fallback, f"fallback_from_{configured}"
    if not available and configured != "deepseek-to-be-filled":
        return configured, "unverified_no_model_list"
    return None, f"unavailable_{configured}"


def extract_content(response: dict[str, Any]) -> str:
    choices = response.get("choices", [])
    if choices and isinstance(choices[0], dict):
        message = choices[0].get("message", {})
        if isinstance(message, dict) and message.get("content") is not None:
            return str(message["content"])
        if choices[0].get("text") is not None:
            return str(choices[0]["text"])
    if response.get("output_text") is not None:
        return str(response["output_text"])
    return json.dumps(response, indent=2, ensure_ascii=False)


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    rows = []
    for item in report["results"]:
        detail = item.get("error_message") or item.get("selection_reason", "")
        rows.append(
            "| "
            + " | ".join(
                [
                    item["model_id"],
                    item["case_id"],
                    item["status"],
                    item.get("alias_used") or "",
                    detail.replace("|", "\\|").replace("\n", " ")[:240],
                ]
            )
            + " |"
        )
    lines = [
        "# Model Ablation Run Report",
        "",
        f"- Overall status: {report['overall_status']}",
        f"- Started at unix time: {report['started_at_unix']}",
        f"- Completed at unix time: {report['completed_at_unix']}",
        f"- Successes: {report['status_counts'].get('success', 0)}",
        f"- Errors: {report['status_counts'].get('error', 0)}",
        f"- Skipped: {report['status_counts'].get('skipped', 0)}",
        "",
        "Evidence boundary: credentials are read from environment variables and "
        "errors are redacted. A model ablation is complete only for rows with "
        "saved response files and subsequent scoring.",
        "",
        "| Model | Case | Status | Alias Used | Detail |",
        "| --- | --- | --- | --- | --- |",
        *rows,
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def run(args: argparse.Namespace) -> dict[str, Any]:
    task = load_json(args.task)
    index = load_json(args.index)
    model_slots = {slot["id"]: slot for slot in task["model_slots"]}
    selected_model_ids = set(args.model_id or [])

    started = int(time.time())
    results: list[dict[str, Any]] = []
    model_cache: dict[tuple[str, str], list[str]] = {}
    model_catalogs: dict[str, dict[str, Any]] = {}

    for prompt in index["prompts"]:
        model_id = prompt["model_id"]
        if selected_model_ids and model_id not in selected_model_ids:
            continue
        slot = model_slots[model_id]
        is_placeholder_model = str(slot.get("model_alias", "")) == "deepseek-to-be-filled"
        if is_placeholder_model and not args.include_placeholder_models:
            results.append(
                {
                    "model_id": model_id,
                    "case_id": prompt["case_id"],
                    "status": "skipped",
                    "selection_reason": "placeholder_model_slot",
                    "expected_response_path": prompt["expected_response_path"],
                }
            )
            continue

        base_url = args.base_url or os.environ.get(slot.get("base_url_env", ""), "")
        api_key = args.api_key or os.environ.get(slot.get("auth_env", ""), "")
        if not base_url or not api_key:
            results.append(
                {
                    "model_id": model_id,
                    "case_id": prompt["case_id"],
                    "status": "skipped",
                    "selection_reason": "missing_base_url_or_api_key_env",
                    "expected_response_path": prompt["expected_response_path"],
                }
            )
            continue

        cache_key = (base_url, slot.get("auth_env", ""))
        available = model_cache.get(cache_key)
        if available is None:
            try:
                _, model_response = request_json(endpoint(base_url, "models"), api_key)
                available = model_ids_from_response(model_response)
                model_catalogs[base_url] = {
                    "base_url": base_url,
                    "auth_env": slot.get("auth_env", ""),
                    "status": "success",
                    "model_count": len(available),
                    "model_ids": available,
                }
            except RuntimeError as exc:
                available = []
                model_catalogs[base_url] = {
                    "base_url": base_url,
                    "auth_env": slot.get("auth_env", ""),
                    "status": "error",
                    "error_message": str(exc),
                    "model_count": 0,
                    "model_ids": [],
                }
                results.append(
                    {
                        "model_id": model_id,
                        "case_id": prompt["case_id"],
                        "status": "error",
                        "selection_reason": "model_list_failed",
                        "error_message": str(exc),
                        "expected_response_path": prompt["expected_response_path"],
                    }
                )
                model_cache[cache_key] = available
                continue
            model_cache[cache_key] = available

        alias, reason = select_model_alias(slot, available)
        if alias is None:
            results.append(
                {
                    "model_id": model_id,
                    "case_id": prompt["case_id"],
                    "status": "skipped",
                    "selection_reason": reason,
                    "available_gpt_models": [model for model in available if model.lower().startswith("gpt")][:20],
                    "expected_response_path": prompt["expected_response_path"],
                }
            )
            continue

        prompt_text = Path(prompt["prompt_path"]).read_text(encoding="utf-8")
        body = {
            "model": alias,
            "messages": [
                {
                    "role": "system",
                    "content": "You are executing a PaperToSkill model-ablation prompt. Follow the output contract and do not invent completed evidence.",
                },
                {"role": "user", "content": prompt_text},
            ],
            "temperature": 0,
            "max_tokens": args.max_tokens,
        }
        try:
            status, response = request_json(endpoint(base_url, "chat/completions"), api_key, method="POST", body=body)
            content = extract_content(response)
            response_path = Path(prompt["expected_response_path"])
            response_path.parent.mkdir(parents=True, exist_ok=True)
            response_path.write_text(content.strip() + "\n", encoding="utf-8")
            results.append(
                {
                    "model_id": model_id,
                    "case_id": prompt["case_id"],
                    "status": "success",
                    "alias_used": alias,
                    "selection_reason": reason,
                    "http_status": status,
                    "response_chars": len(content),
                    "expected_response_path": prompt["expected_response_path"],
                }
            )
        except RuntimeError as exc:
            results.append(
                {
                    "model_id": model_id,
                    "case_id": prompt["case_id"],
                    "status": "error",
                    "alias_used": alias,
                    "selection_reason": reason,
                    "error_message": str(exc),
                    "expected_response_path": prompt["expected_response_path"],
                }
            )

    counts: dict[str, int] = {}
    for item in results:
        counts[item["status"]] = counts.get(item["status"], 0) + 1
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
        "task": task["id"],
        "index_path": str(args.index),
        "evidence_boundary": (
            "Live endpoint attempt report. Successful rows have saved response files; "
            "failed rows are provider/model availability evidence only."
        ),
        "started_at_unix": started,
        "completed_at_unix": int(time.time()),
        "overall_status": overall,
        "status_counts": counts,
        "model_catalogs": list(model_catalogs.values()),
        "results": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run PaperToSkill model-ablation prompt packets.")
    parser.add_argument("--task", required=True, type=Path)
    parser.add_argument("--index", required=True, type=Path)
    parser.add_argument("--output-json", required=True, type=Path)
    parser.add_argument("--output-md", required=True, type=Path)
    parser.add_argument("--model-id", action="append", help="Limit run to one or more model slot IDs.")
    parser.add_argument("--base-url", help="Override base URL for all selected model slots.")
    parser.add_argument("--api-key", help="Override API key for all selected model slots. Prefer env vars.")
    parser.add_argument("--max-tokens", type=int, default=900)
    parser.add_argument("--include-placeholder-models", action="store_true")
    args = parser.parse_args()

    report = run(args)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_markdown(args.output_md, report)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
