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
WIRE_APIS = ("openai_chat_completions", "openai_responses", "anthropic_messages")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def redact(text: str) -> str:
    return SECRET_PATTERN.sub("sk-REDACTED", text)


def endpoint(base_url: str, suffix: str) -> str:
    return base_url.rstrip("/") + "/" + suffix.lstrip("/")


def wire_endpoint(base_url: str, wire_api: str) -> str:
    base = base_url.rstrip("/")
    if wire_api == "anthropic_messages":
        suffix = "messages" if base.endswith("/v1") else "v1/messages"
        return endpoint(base_url, suffix)
    if wire_api == "openai_responses":
        return endpoint(base_url, "responses")
    return endpoint(base_url, "chat/completions")


def request_json(
    url: str,
    api_key: str,
    method: str = "GET",
    body: dict[str, Any] | None = None,
    *,
    extra_headers: dict[str, str] | None = None,
    timeout_seconds: float = 60.0,
) -> tuple[int, dict[str, Any]]:
    data = None if body is None else json.dumps(body).encode("utf-8")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    if extra_headers:
        headers.update(extra_headers)
    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
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
        "gpt-5.4",
        "gpt-5.5-chat",
        "gpt-5.4-chat",
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


def alias_candidates(model_slot: dict[str, Any]) -> list[str]:
    raw_aliases = model_slot.get("model_aliases") or [model_slot["model_alias"]]
    aliases = [str(alias) for alias in raw_aliases if str(alias)]
    configured = str(model_slot["model_alias"])
    if configured not in aliases:
        aliases.insert(0, configured)
    return aliases


def select_model_alias(model_slot: dict[str, Any], available: list[str]) -> tuple[str | None, str]:
    candidates = alias_candidates(model_slot)
    for candidate in candidates:
        if candidate in available:
            return candidate, "exact"
    if model_slot["id"] == "gpt_5_5_or_gpt_family":
        fallback = gpt_fallback(available)
        if fallback:
            return fallback, f"fallback_from_{candidates[0]}"
    if not available and candidates[0] != "deepseek-to-be-filled":
        return candidates[0], "unverified_no_model_list"
    return None, f"unavailable_{candidates[0]}"


def alias_attempts(model_slot: dict[str, Any], available: list[str]) -> list[tuple[str, str]]:
    attempts = [(candidate, "exact") for candidate in alias_candidates(model_slot) if candidate in available]
    if attempts:
        return attempts

    if model_slot["id"] == "gpt_5_5_or_gpt_family":
        fallback = gpt_fallback(available)
        if fallback:
            return [(fallback, f"fallback_from_{alias_candidates(model_slot)[0]}")]

    candidates = alias_candidates(model_slot)
    if not available and candidates[0] != "deepseek-to-be-filled":
        return [(candidate, "unverified_no_model_list") for candidate in candidates]
    return []


def extract_content(response: dict[str, Any]) -> str:
    if isinstance(response.get("content"), list):
        parts = []
        for item in response["content"]:
            if isinstance(item, dict) and item.get("text") is not None:
                parts.append(str(item["text"]))
        if parts:
            return "\n".join(parts)
    choices = response.get("choices", [])
    if choices and isinstance(choices[0], dict):
        message = choices[0].get("message", {})
        if isinstance(message, dict) and message.get("content") is not None:
            return str(message["content"])
        if choices[0].get("text") is not None:
            return str(choices[0]["text"])
    if response.get("output_text") is not None:
        return str(response["output_text"])
    output = response.get("output", [])
    if isinstance(output, list):
        parts = []
        for item in output:
            if not isinstance(item, dict):
                continue
            for content in item.get("content", []):
                if isinstance(content, dict) and content.get("text") is not None:
                    parts.append(str(content["text"]))
        if parts:
            return "\n".join(parts)
    return json.dumps(response, indent=2, ensure_ascii=False)


def slot_wire_api(model_slot: dict[str, Any]) -> str:
    wire_api = str(model_slot.get("wire_api", "openai_chat_completions"))
    if wire_api not in WIRE_APIS:
        raise ValueError(f"unsupported wire_api for {model_slot.get('id', '')}: {wire_api}")
    return wire_api


def should_fetch_model_list(wire_api: str) -> bool:
    return wire_api != "anthropic_messages"


def build_wire_request(
    *,
    wire_api: str,
    model: str,
    prompt_text: str,
    max_tokens: int,
    anthropic_version: str,
) -> tuple[dict[str, Any], dict[str, str]]:
    system_message = (
        "You are executing a PaperToSkill model-ablation prompt. "
        "Follow the output contract and do not invent completed evidence."
    )
    if wire_api == "openai_responses":
        return (
            {
                "model": model,
                "input": f"{system_message}\n\n{prompt_text}",
                "max_output_tokens": max_tokens,
            },
            {},
        )
    if wire_api == "anthropic_messages":
        return (
            {
                "model": model,
                "system": system_message,
                "max_tokens": max_tokens,
                "messages": [
                    {"role": "user", "content": prompt_text},
                ],
            },
            {"anthropic-version": anthropic_version},
        )
    return (
        {
            "model": model,
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt_text},
            ],
            "temperature": 0,
            "max_tokens": max_tokens,
        },
        {},
    )


def max_attempts(args: argparse.Namespace) -> int:
    return max(1, int(getattr(args, "max_attempts", 5)))


def retry_delay_seconds(args: argparse.Namespace) -> float:
    return max(0.0, float(getattr(args, "retry_delay_seconds", 2.0)))


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    rows = []
    for item in report["results"]:
        attempts = item.get("attempted_aliases") or []
        if attempts:
            detail = "; ".join(
                f"{attempt['alias']}={attempt['status']}"
                for attempt in attempts
            )
        else:
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
        f"- Max attempts per alias: {report.get('max_attempts_per_alias', 1)}",
        f"- Retry delay seconds: {report.get('retry_delay_seconds', 0)}",
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
    model_cache: dict[tuple[str, str, str], list[str]] = {}
    model_catalogs: dict[tuple[str, str, str], dict[str, Any]] = {}

    for prompt in index["prompts"]:
        model_id = prompt["model_id"]
        if selected_model_ids and model_id not in selected_model_ids:
            continue
        slot = model_slots[model_id]
        wire_api = slot_wire_api(slot)
        is_placeholder_model = str(slot.get("model_alias", "")) == "deepseek-to-be-filled"
        if is_placeholder_model and not args.include_placeholder_models:
            results.append(
                {
                    "model_id": model_id,
                    "case_id": prompt["case_id"],
                    "status": "skipped",
                    "selection_reason": "placeholder_model_slot",
                    "wire_api": wire_api,
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
                    "wire_api": wire_api,
                    "expected_response_path": prompt["expected_response_path"],
                }
            )
            continue

        auth_env = slot.get("auth_env", "")
        cache_key = (base_url, auth_env, wire_api)
        available = model_cache.get(cache_key)
        if available is None:
            if should_fetch_model_list(wire_api):
                try:
                    _, model_response = request_json(
                        endpoint(base_url, "models"),
                        api_key,
                        timeout_seconds=args.timeout_seconds,
                    )
                    available = model_ids_from_response(model_response)
                    catalog_status = "success"
                    catalog_error = ""
                except RuntimeError as exc:
                    available = []
                    catalog_status = "error_continued_unverified"
                    catalog_error = str(exc)
            else:
                available = []
                catalog_status = "skipped_for_wire_api"
                catalog_error = "anthropic_messages model catalog is not required by the local API docs"
            model_catalogs[cache_key] = {
                "base_url": base_url,
                "auth_env": auth_env,
                "wire_api": wire_api,
                "status": catalog_status,
                "error_message": catalog_error,
                "model_count": len(available),
                "model_ids": available,
            }
            model_cache[cache_key] = available

        attempts = alias_attempts(slot, available)
        if not attempts:
            _, reason = select_model_alias(slot, available)
            results.append(
                {
                    "model_id": model_id,
                    "case_id": prompt["case_id"],
                    "status": "skipped",
                    "selection_reason": reason,
                    "wire_api": wire_api,
                    "available_gpt_models": [model for model in available if model.lower().startswith("gpt")][:20],
                    "expected_response_path": prompt["expected_response_path"],
                }
            )
            continue

        prompt_text = Path(prompt["prompt_path"]).read_text(encoding="utf-8")
        attempt_records = []
        saved_result: dict[str, Any] | None = None
        for alias, reason in attempts:
            body, extra_headers = build_wire_request(
                wire_api=wire_api,
                model=alias,
                prompt_text=prompt_text,
                max_tokens=args.max_tokens,
                anthropic_version=args.anthropic_version,
            )
            last_error = ""
            for attempt_number in range(1, max_attempts(args) + 1):
                try:
                    status, response = request_json(
                        wire_endpoint(base_url, wire_api),
                        api_key,
                        method="POST",
                        body=body,
                        extra_headers=extra_headers,
                        timeout_seconds=args.timeout_seconds,
                    )
                    content = extract_content(response)
                    response_path = Path(prompt["expected_response_path"])
                    response_path.parent.mkdir(parents=True, exist_ok=True)
                    response_path.write_text(content.strip() + "\n", encoding="utf-8")
                    attempt_records.append(
                        {
                            "alias": alias,
                            "selection_reason": reason,
                            "status": "success",
                            "attempts": attempt_number,
                        }
                    )
                    saved_result = {
                        "model_id": model_id,
                        "case_id": prompt["case_id"],
                        "status": "success",
                        "wire_api": wire_api,
                        "alias_used": alias,
                        "selection_reason": reason,
                        "attempted_aliases": attempt_records,
                        "http_status": status,
                        "response_chars": len(content),
                        "expected_response_path": prompt["expected_response_path"],
                    }
                    break
                except RuntimeError as exc:
                    last_error = str(exc)
                    if attempt_number < max_attempts(args) and retry_delay_seconds(args):
                        time.sleep(retry_delay_seconds(args))
            if saved_result is not None:
                break
            attempt_records.append(
                {
                    "alias": alias,
                    "selection_reason": reason,
                    "status": "error",
                    "attempts": max_attempts(args),
                    "error_message": last_error,
                }
            )

        if saved_result is not None:
            results.append(saved_result)
        else:
            results.append(
                {
                    "model_id": model_id,
                    "case_id": prompt["case_id"],
                    "status": "error",
                    "wire_api": wire_api,
                    "alias_used": attempts[-1][0],
                    "selection_reason": "all_candidate_aliases_failed",
                    "attempted_aliases": attempt_records,
                    "error_message": attempt_records[-1]["error_message"],
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
        "max_attempts_per_alias": max_attempts(args),
        "retry_delay_seconds": retry_delay_seconds(args),
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
    parser.add_argument("--timeout-seconds", type=float, default=60.0)
    parser.add_argument("--max-attempts", type=int, default=5)
    parser.add_argument("--retry-delay-seconds", type=float, default=2.0)
    parser.add_argument("--anthropic-version", default="2023-06-01")
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
