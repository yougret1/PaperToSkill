#!/usr/bin/env python
"""Run a direct OpenAI-compatible endpoint probe.

This diagnostic bypasses the local ai-scientist-v2 LLM wrapper and calls the
configured OpenAI-compatible `/chat/completions` endpoint directly. It uses the
same tiny marker contract as the AI-Scientist-v2 smoke test, but it does not
prove that the AI-Scientist-v2 client path or a full BFTS run works.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SECRET_PATTERN = re.compile(r"sk-[A-Za-z0-9]{20,}")
REQUIRED_MARKERS = ("PAPERTOSKILL_SMOKE_OK", "ai-scientist-v2", "paper-to-skill")


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


def redact(text: str) -> str:
    return SECRET_PATTERN.sub("sk-REDACTED", text)


def endpoint(base_url: str, suffix: str) -> str:
    return base_url.rstrip("/") + "/" + suffix.lstrip("/")


def request_json(
    url: str,
    api_key: str,
    body: dict[str, Any],
    timeout_seconds: float,
) -> tuple[int, dict[str, Any]]:
    data = json.dumps(body).encode("utf-8")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    request = urllib.request.Request(url, data=data, headers=headers, method="POST")
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
    except Exception as exc:  # noqa: BLE001 - redacted diagnostic boundary
        raise RuntimeError(redact(str(exc))) from exc


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
    return ""


def response_contract_checks(response_text: str, output_path: Path) -> list[Check]:
    lowered = response_text.lower()
    checks = []
    for marker in REQUIRED_MARKERS:
        checks.append(
            Check(
                f"direct_probe_marker_{marker.lower().replace('-', '_')}",
                "ready" if marker.lower() in lowered else "fail",
                "present" if marker.lower() in lowered else "missing",
                str(output_path),
            )
        )
    return checks


def build_report(
    *,
    model: str,
    attempted_models: list[dict[str, str]],
    base_url_env: str,
    auth_env: str,
    base_url: str | None,
    api_key_present: bool,
    response_path: Path,
    response_text: str | None,
    started_at: int,
    completed_at: int,
    max_tokens: int,
    timeout_seconds: float,
    error: str | None = None,
) -> dict[str, Any]:
    checks: list[Check] = [
        Check(
            "direct_probe_configuration",
            "ready" if base_url and api_key_present else "pending",
            f"base_url_present={bool(base_url)}; api_key_present={api_key_present}",
            f"{base_url_env}; {auth_env}",
        ),
        Check(
            "direct_probe_response_saved",
            "ready" if response_text and response_path.exists() else "pending",
            f"response_chars={len(response_text or '')}",
            str(response_path),
        ),
    ]
    if response_text:
        checks.extend(response_contract_checks(response_text, response_path))
    if error:
        checks.append(
            Check(
                "direct_probe_error",
                "pending",
                redact(error)[:500],
                "provider/model availability",
            )
        )
    for index, attempt in enumerate(attempted_models, start=1):
        checks.append(
            Check(
                f"direct_probe_alias_attempt_{index}",
                "ready",
                f"{attempt.get('model')}: {attempt.get('status')}; {attempt.get('detail')}",
                "provider/model availability",
            )
        )

    status_counts = {"ready": 0, "pending": 0, "fail": 0}
    for check in checks:
        status_counts[check.status] = status_counts.get(check.status, 0) + 1

    if not base_url or not api_key_present:
        overall = "pending_configuration"
    elif status_counts.get("fail", 0):
        overall = "fail"
    elif response_text and not status_counts.get("pending", 0):
        overall = "complete"
    elif error:
        overall = "blocked_by_provider_or_model_availability"
    else:
        overall = "pending"

    return {
        "schema_version": "0.1",
        "evidence_boundary": (
            "Direct OpenAI-compatible endpoint diagnostic. A complete report proves "
            "the configured endpoint can return the tiny marker-contract response "
            "without using ai_scientist.llm. It does not complete the AI-Scientist-v2 "
            "LLM-client smoke, BFTS, or a live research task."
        ),
        "model": model,
        "attempted_models": attempted_models,
        "base_url_env": base_url_env,
        "base_url": base_url or "",
        "auth_env": auth_env,
        "api_key_present": api_key_present,
        "max_tokens": max_tokens,
        "timeout_seconds": timeout_seconds,
        "started_at_unix": started_at,
        "completed_at_unix": completed_at,
        "overall_status": overall,
        "status_counts": status_counts,
        "checks": [check.as_dict() for check in checks],
    }


def run_model_attempt(args: argparse.Namespace, model: str, base_url: str, api_key: str) -> tuple[str | None, str | None, int | None]:
    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": args.system_message},
            {"role": "user", "content": args.prompt},
        ],
        "temperature": 0,
        "max_tokens": args.max_tokens,
    }
    try:
        status, response = request_json(
            endpoint(base_url, "chat/completions"),
            api_key,
            body,
            args.timeout_seconds,
        )
        content = extract_content(response)
        if not content:
            return None, "empty response content", status
        return content, None, status
    except RuntimeError as exc:
        return None, str(exc), None


def run(args: argparse.Namespace) -> dict[str, Any]:
    started_at = int(time.time())
    base_url = args.base_url or os.environ.get(args.base_url_env)
    api_key = args.api_key or os.environ.get(args.auth_env)
    api_key_present = bool(api_key)
    attempted_models: list[dict[str, str]] = []
    response_text: str | None = None
    error: str | None = None
    model_aliases = args.model_aliases or [args.model]

    if base_url and api_key:
        for model in model_aliases:
            response_text, error, http_status = run_model_attempt(args, model, base_url, api_key)
            if response_text:
                detail = f"response_chars={len(response_text)}"
                if http_status is not None:
                    detail += f"; http_status={http_status}"
                attempted_models.append({"model": model, "status": "success", "detail": detail})
                break
            attempted_models.append({"model": model, "status": "blocked", "detail": redact(error or "empty response")[:500]})
        if not response_text and attempted_models:
            error = "; ".join(f"{attempt['model']}: {attempt['detail']}" for attempt in attempted_models)
    else:
        error = "missing_base_url_or_api_key_env"

    args.response_output.parent.mkdir(parents=True, exist_ok=True)
    if response_text:
        args.response_output.write_text(response_text.strip() + "\n", encoding="utf-8")
    elif args.response_output.exists():
        args.response_output.unlink()

    return build_report(
        model=model_aliases[0],
        attempted_models=attempted_models,
        base_url_env=args.base_url_env,
        auth_env=args.auth_env,
        base_url=base_url,
        api_key_present=api_key_present,
        response_path=args.response_output,
        response_text=response_text,
        started_at=started_at,
        completed_at=int(time.time()),
        max_tokens=args.max_tokens,
        timeout_seconds=args.timeout_seconds,
        error=error,
    )


def write_json(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    lines = [
        "# OpenAI-Compatible Direct Probe Report",
        "",
        "Evidence boundary: this direct endpoint diagnostic bypasses "
        "`ai_scientist.llm`; it does not complete the AI-Scientist-v2 smoke "
        "or any BFTS/live research run.",
        "",
        f"- Overall status: {report['overall_status']}",
        f"- Model: {report['model']}",
        f"- Attempted models: {', '.join(attempt.get('model', '') for attempt in report.get('attempted_models', []))}",
        f"- Base URL env: {report['base_url_env']}",
        f"- Auth env: {report['auth_env']}",
        f"- Max tokens: {report['max_tokens']}",
        f"- Timeout seconds: {report['timeout_seconds']}",
        f"- Ready checks: {report['status_counts'].get('ready', 0)}",
        f"- Pending checks: {report['status_counts'].get('pending', 0)}",
        f"- Failed checks: {report['status_counts'].get('fail', 0)}",
        "",
        "| Check | Status | Detail | Evidence |",
        "| --- | --- | --- | --- |",
    ]
    for check in report["checks"]:
        row = [
            check["id"],
            check["status"],
            check["detail"],
            check["evidence"],
        ]
        values = [value.replace("|", "\\|").replace("\n", " ") for value in row]
        lines.append("| " + " | ".join(values) + " |")
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def status_summary(report: dict[str, Any]) -> str:
    counts = report.get("status_counts", {})
    return (
        f"overall_status={report.get('overall_status')}; "
        f"ready={counts.get('ready', 0)}; "
        f"pending={counts.get('pending', 0)}; "
        f"fail={counts.get('fail', 0)}"
    )


def exit_code(report: dict[str, Any], *, strict: bool, require_complete: bool) -> int:
    if require_complete and report.get("overall_status") != "complete":
        return 1
    if strict and report.get("overall_status") == "fail":
        return 1
    return 0


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    default_output_dir = root / "results" / "openai_compatible_direct_probe"
    parser = argparse.ArgumentParser(description="Run a direct OpenAI-compatible endpoint probe.")
    parser.add_argument("--model", default="claude-opus-4-8")
    parser.add_argument(
        "--model-alias",
        dest="model_aliases",
        action="append",
        help="Candidate model alias to try, in order. Can be repeated.",
    )
    parser.add_argument("--base-url-env", default="AI_SCIENTIST_OPENAI_BASE_URL")
    parser.add_argument("--auth-env", default="AI_SCIENTIST_OPENAI_API_KEY")
    parser.add_argument("--base-url", help="Override base URL. Prefer env vars for normal runs.")
    parser.add_argument("--api-key", help="Override API key. Prefer env vars and never commit keys.")
    parser.add_argument("--timeout-seconds", type=float, default=30.0)
    parser.add_argument("--max-tokens", type=int, default=128)
    parser.add_argument(
        "--system-message",
        default=(
            "You are a direct OpenAI-compatible endpoint probe. Reply concisely "
            "and follow the exact marker contract."
        ),
    )
    parser.add_argument(
        "--prompt",
        default=(
            "Return a two-sentence response containing exactly these three markers: "
            "PAPERTOSKILL_SMOKE_OK, ai-scientist-v2, and paper-to-skill. Do not include secrets."
        ),
    )
    parser.add_argument("--response-output", type=Path, default=default_output_dir / "response.md")
    parser.add_argument("--output-json", type=Path, default=default_output_dir / "run_report.json")
    parser.add_argument("--output-md", type=Path, default=default_output_dir / "run_report.md")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero if probe checks fail.")
    parser.add_argument(
        "--require-complete",
        action="store_true",
        help="Exit non-zero unless the endpoint returns a response satisfying the marker contract.",
    )
    args = parser.parse_args()

    report = run(args)
    write_json(args.output_json, report)
    write_markdown(args.output_md, report)
    print(args.output_json)
    print(args.output_md)
    print(status_summary(report))
    return exit_code(report, strict=args.strict, require_complete=args.require_complete)


if __name__ == "__main__":
    raise SystemExit(main())
