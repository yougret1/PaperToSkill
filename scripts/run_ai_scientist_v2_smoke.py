#!/usr/bin/env python
"""Run a bounded AI-Scientist-v2 live LLM smoke check.

This script imports the local ai-scientist-v2 LLM client and performs one
OpenAI-compatible chat completion. It records endpoint/model availability and a
short response contract, but it does not run BFTS experiments or claim research
task success.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import threading
import time
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


def load_ai_scientist_llm(ai_scientist_root: Path):
    root = ai_scientist_root.resolve()
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    from ai_scientist.llm import create_client, get_response_from_llm  # type: ignore

    return create_client, get_response_from_llm


def response_contract_checks(response_text: str, output_path: Path) -> list[Check]:
    lowered = response_text.lower()
    checks = []
    for marker in REQUIRED_MARKERS:
        checks.append(
            Check(
                f"ai_scientist_v2_smoke_marker_{marker.lower().replace('-', '_')}",
                "ready" if marker.lower() in lowered else "fail",
                "present" if marker.lower() in lowered else "missing",
                str(output_path),
            )
        )
    return checks


def build_report(
    *,
    ai_scientist_root: Path,
    model: str,
    base_url: str | None,
    response_path: Path,
    response_text: str | None,
    started_at: int,
    completed_at: int,
    error: str | None = None,
) -> dict[str, Any]:
    checks: list[Check] = [
        Check(
            "ai_scientist_v2_root",
            "ready" if ai_scientist_root.exists() else "fail",
            "present" if ai_scientist_root.exists() else "missing",
            str(ai_scientist_root),
        ),
        Check(
            "ai_scientist_v2_llm_response_saved",
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
                "ai_scientist_v2_llm_error",
                "pending",
                redact(error)[:500],
                "provider/model availability",
            )
        )

    status_counts = {"ready": 0, "pending": 0, "fail": 0}
    for check in checks:
        status_counts[check.status] = status_counts.get(check.status, 0) + 1

    if status_counts.get("fail", 0):
        overall = "fail"
    elif error or status_counts.get("pending", 0):
        overall = "blocked_by_provider_or_model_availability" if error else "pending"
    else:
        overall = "complete"

    return {
        "schema_version": "0.1",
        "evidence_boundary": (
            "Bounded AI-Scientist-v2 LLM-client smoke check. A complete report proves "
            "the local ai-scientist-v2 client can reach the configured model and satisfy "
            "a tiny response contract. It does not run BFTS or prove research-task success."
        ),
        "ai_scientist_root": str(ai_scientist_root),
        "model": model,
        "base_url_env": "AI_SCIENTIST_OPENAI_BASE_URL",
        "base_url": base_url or "",
        "auth_env": "AI_SCIENTIST_OPENAI_API_KEY",
        "started_at_unix": started_at,
        "completed_at_unix": completed_at,
        "overall_status": overall,
        "status_counts": status_counts,
        "checks": [check.as_dict() for check in checks],
    }


def call_llm_with_timeout(args: argparse.Namespace) -> str:
    create_client, get_response_from_llm = load_ai_scientist_llm(args.ai_scientist_root)
    client, client_model = create_client(args.model)
    response_text, _ = get_response_from_llm(
        args.prompt,
        client,
        client_model,
        args.system_message,
        temperature=0,
    )
    return response_text


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    rows = [
        [check["id"], check["status"], check["detail"], check["evidence"]]
        for check in report["checks"]
    ]
    lines = [
        "# AI-Scientist-v2 Live LLM Smoke Report",
        "",
        "Evidence boundary: this is a bounded LLM-client smoke check. It does "
        "not run BFTS or prove research-task success.",
        "",
        f"- Overall status: {report['overall_status']}",
        f"- Model: {report['model']}",
        f"- Base URL env: {report['base_url_env']}",
        f"- Auth env: {report['auth_env']}",
        f"- Ready checks: {report['status_counts'].get('ready', 0)}",
        f"- Pending checks: {report['status_counts'].get('pending', 0)}",
        f"- Failed checks: {report['status_counts'].get('fail', 0)}",
        "",
        "| Check | Status | Detail | Evidence |",
        "| --- | --- | --- | --- |",
    ]
    for row in rows:
        values = [value.replace("|", "\\|").replace("\n", " ") for value in row]
        lines.append("| " + " | ".join(values) + " |")
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def run(args: argparse.Namespace) -> dict[str, Any]:
    started_at = int(time.time())
    base_url = os.environ.get("AI_SCIENTIST_OPENAI_BASE_URL") or os.environ.get("OPENAI_BASE_URL")
    response_text: str | None = None
    error: str | None = None

    try:
        result: dict[str, str] = {}

        def target() -> None:
            try:
                result["response_text"] = call_llm_with_timeout(args)
            except Exception as exc:  # noqa: BLE001 - report is redacted evidence
                result["error"] = redact(str(exc))

        thread = threading.Thread(target=target, daemon=True)
        thread.start()
        thread.join(args.timeout_seconds)
        if thread.is_alive():
            error = f"Timed out after {args.timeout_seconds:g} seconds waiting for provider response"
        elif "error" in result:
            error = result["error"]
        else:
            response_text = result.get("response_text", "")
        args.response_output.parent.mkdir(parents=True, exist_ok=True)
        if response_text:
            args.response_output.write_text(response_text.strip() + "\n", encoding="utf-8")
        elif args.response_output.exists():
            args.response_output.unlink()
    except Exception as exc:  # noqa: BLE001 - report is redacted evidence
        error = redact(str(exc))

    return build_report(
        ai_scientist_root=args.ai_scientist_root,
        model=args.model,
        base_url=base_url,
        response_path=args.response_output,
        response_text=response_text,
        started_at=started_at,
        completed_at=int(time.time()),
        error=error,
    )


def write_json(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


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
    parser = argparse.ArgumentParser(description="Run a bounded AI-Scientist-v2 LLM smoke check.")
    parser.add_argument(
        "--ai-scientist-root",
        type=Path,
        default=root.parent / "ai-scientist-v2",
        help="Path to the local ai-scientist-v2 checkout.",
    )
    parser.add_argument("--model", default="claude-opus-4-8")
    parser.add_argument(
        "--timeout-seconds",
        type=float,
        default=30.0,
        help="Maximum seconds to wait for the provider before writing a blocked report.",
    )
    parser.add_argument(
        "--system-message",
        default=(
            "You are an AI-Scientist-v2 smoke-test assistant. Reply concisely and "
            "follow the exact marker contract."
        ),
    )
    parser.add_argument(
        "--prompt",
        default=(
            "Return a two-sentence response containing exactly these three markers: "
            "PAPERTOSKILL_SMOKE_OK, ai-scientist-v2, and paper-to-skill. Do not include secrets."
        ),
    )
    parser.add_argument(
        "--response-output",
        type=Path,
        default=root / "results" / "ai_scientist_v2_smoke" / "response.md",
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        default=root / "results" / "ai_scientist_v2_smoke" / "run_report.json",
    )
    parser.add_argument(
        "--output-md",
        type=Path,
        default=root / "results" / "ai_scientist_v2_smoke" / "run_report.md",
    )
    parser.add_argument("--strict", action="store_true", help="Exit non-zero if smoke checks fail.")
    parser.add_argument(
        "--require-complete",
        action="store_true",
        help="Exit non-zero unless the provider returns a response that satisfies the smoke contract.",
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
