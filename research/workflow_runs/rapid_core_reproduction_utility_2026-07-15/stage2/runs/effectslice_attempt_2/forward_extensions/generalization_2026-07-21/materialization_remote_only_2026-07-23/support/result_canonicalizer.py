from __future__ import annotations

import hashlib
import json
import sys
from typing import Any


def _canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _digest(value: object) -> str:
    data = value if isinstance(value, bytes) else _canonical(value)
    return hashlib.sha256(data).hexdigest()


def _openai_response_text(response: dict[str, Any]) -> str:
    for outer in response.get("output", []):
        if outer.get("type") != "message":
            continue
        for inner in outer.get("content", []):
            if inner.get("type") == "output_text" and isinstance(inner.get("text"), str):
                return inner["text"]
    raise ValueError("no output_text response item")


def _claude_text(response: dict[str, Any]) -> str:
    for item in response.get("content", []):
        if item.get("type") == "text" and isinstance(item.get("text"), str):
            return item["text"]
    raise ValueError("no Claude text block")


def _response_projection(
    slot: str, response: dict[str, Any]
) -> tuple[str, Any, tuple[int, int, int, int | None]]:
    if slot == "deepseek_primary":
        text = response["choices"][0]["message"]["content"]
        finish = response["choices"][0].get("finish_reason")
        usage = response.get("usage", {})
        values = (usage.get("prompt_tokens"), usage.get("completion_tokens"), usage.get("total_tokens"), usage.get("prompt_tokens_details", {}).get("cached_tokens"))
        return text, finish, values
    if slot in {"gpt_5_5", "gpt_5_6_sol", "gpt_5_6_terra", "gpt_5_6_luna"}:
        text = _openai_response_text(response)
        details = response.get("incomplete_details") or {}
        finish = details.get("reason") if details.get("reason") is not None else response.get("status")
        usage = response.get("usage", {})
        values = (usage.get("input_tokens"), usage.get("output_tokens"), usage.get("total_tokens"), usage.get("input_tokens_details", {}).get("cached_tokens"))
        return text, finish, values
    if slot == "claude_opus_4_7":
        text = _claude_text(response)
        usage = response.get("usage", {})
        input_tokens, output_tokens = usage.get("input_tokens"), usage.get("output_tokens")
        total = None if input_tokens is None or output_tokens is None else input_tokens + output_tokens
        values = (input_tokens, output_tokens, total, usage.get("cache_read_input_tokens"))
        return text, response.get("stop_reason"), values
    raise ValueError(f"unknown model slot: {slot}")


def _termination(slot: str, finish: Any, dispatch_state: str) -> str:
    if dispatch_state == "transport_terminal_failure":
        return "transport_failure"
    if dispatch_state == "provider_or_model_unavailable":
        return "not_dispatched"
    if slot == "deepseek_primary":
        return "length" if finish == "length" else "provider_stop"
    if slot in {"gpt_5_5", "gpt_5_6_sol", "gpt_5_6_terra", "gpt_5_6_luna"}:
        return "length" if finish == "max_output_tokens" else "provider_stop"
    if slot == "claude_opus_4_7":
        return "length" if finish == "max_tokens" else "provider_stop"
    raise ValueError(slot)


def canonicalize(fixture: dict[str, Any]) -> dict[str, Any]:
    execution_id = str(fixture["execution_id"])
    slot = str(fixture["model_slot_id"])
    dispatch_state = str(fixture["dispatch_state"])
    response = fixture.get("provider_response")
    unavailable = dispatch_state == "provider_or_model_unavailable"
    transport = dispatch_state == "transport_terminal_failure"
    text: str | None = None
    finish = None
    usage: tuple[int | None, int | None, int | None, int | None] = (None, None, None, None)
    malformed = False
    if not unavailable and not transport:
        try:
            text, finish, usage = _response_projection(slot, response)
        except (IndexError, KeyError, TypeError, ValueError):
            malformed = True
    reason = _termination(slot, finish, dispatch_state)
    if unavailable:
        outcome = "provider_or_model_unavailable"
    elif transport:
        outcome = "transport_terminal_failure"
    elif malformed or not bool(fixture.get("submission_valid", True)):
        outcome = "malformed_or_no_submission"
    else:
        outcome = str(fixture.get("scored_outcome", "operational_success"))
    invalid = outcome in {"provider_or_model_unavailable", "transport_terminal_failure", "integrity_or_digest_failure"}
    scored = outcome in {"action_budget_exhausted", "hard_contract_failure", "score_shortfall", "operational_success"}
    row_valid = not invalid
    private_score = None if invalid else (0.0 if outcome == "malformed_or_no_submission" else float(fixture.get("private_score", 1.0)))
    condition_success = None if invalid else outcome == "operational_success"
    raw_path = None if unavailable or transport else f"raw/{execution_id}.json"
    raw_sha = None if raw_path is None else _digest(response)
    canonical_path = f"canonical/{execution_id}.txt" if scored else None
    canonical_sha = _digest(text.encode("utf-8")) if canonical_path is not None and text is not None else None
    if unavailable:
        attempts = []
        terminal_ms = total_ms = sleep_ms = overhead_ms = None
    else:
        attempt_status = "transport_terminal_failure" if transport else "completed_body"
        attempts = [{"attempt_index": 1, "attempt_status_class": attempt_status, "attempt_elapsed_ms": 7, "retry_sleep_after_attempt_ms": 0}]
        terminal_ms = total_ms = 7
        sleep_ms = overhead_ms = 0
    if all(value is not None for value in usage[:3]):
        input_tokens, output_tokens, total_tokens, cached_tokens = usage
        missing_reason = None
    else:
        input_tokens = output_tokens = total_tokens = cached_tokens = None
        missing_reason = "not_dispatched" if unavailable else "transport_failure_no_usage" if transport else "provider_omitted_usage"
    hard_vector = [True, True] if scored else None
    return {
        "execution_id": execution_id,
        "terminal_outcome": outcome,
        "termination_reason": reason,
        "provider_finish_reason": finish,
        "row_valid": row_valid,
        "condition_success": condition_success,
        "private_score": private_score,
        "raw_response_path": raw_path,
        "raw_response_sha256": raw_sha,
        "canonical_output_path": canonical_path,
        "canonical_output_sha256": canonical_sha,
        "hard_contract_vector": hard_vector,
        "attempts": attempts,
        "candidate_artifact_bytes": int(fixture.get("candidate_artifact_bytes", 10)),
        "candidate_artifact_cl100k_tokens": int(fixture.get("candidate_artifact_cl100k_tokens", 3)),
        "canonical_model_visible_payload_bytes": int(fixture.get("canonical_model_visible_payload_bytes", 100)),
        "provider_reported_input_tokens": input_tokens,
        "provider_reported_output_tokens": output_tokens,
        "provider_reported_total_tokens": total_tokens,
        "provider_reported_cached_input_tokens": cached_tokens,
        "provider_usage_missing_reason": missing_reason,
        "terminal_attempt_elapsed_ms": terminal_ms,
        "total_execution_elapsed_ms": total_ms,
        "retry_sleep_elapsed_ms": sleep_ms,
        "retry_overhead_ms": overhead_ms,
    }


def main() -> None:
    fixture = json.load(sys.stdin)
    sys.stdout.buffer.write(_canonical(canonicalize(fixture)))


if __name__ == "__main__":
    main()
