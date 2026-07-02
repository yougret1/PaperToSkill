#!/usr/bin/env python
"""Summarize local token accounting from existing proxy reports."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def int_or_zero(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def context_input_summary(context_report: dict[str, Any]) -> dict[str, Any]:
    rows = context_report.get("context_size", [])
    by_paper: dict[str, dict[str, int]] = defaultdict(lambda: {
        "full_extracted_tokens": 0,
        "generated_skill_tokens": 0,
        "token_reduction": 0,
    })
    for row in rows:
        paper = str(row.get("Paper", "")).strip() or "unknown"
        variant = str(row.get("Variant", "")).strip()
        tokens = int_or_zero(row.get("Estimated input tokens"))
        if variant == "Full extracted paper":
            by_paper[paper]["full_extracted_tokens"] = tokens
        elif variant == "Generated skill":
            by_paper[paper]["generated_skill_tokens"] = tokens

    paper_rows = []
    generated_total = 0
    full_total = 0
    for paper, values in sorted(by_paper.items()):
        reduction = max(0, values["full_extracted_tokens"] - values["generated_skill_tokens"])
        generated_total += values["generated_skill_tokens"]
        full_total += values["full_extracted_tokens"]
        paper_rows.append(
            {
                "paper": paper,
                "full_extracted_tokens": values["full_extracted_tokens"],
                "generated_skill_tokens": values["generated_skill_tokens"],
                "token_reduction": reduction,
                "compression_ratio": round(values["generated_skill_tokens"] / values["full_extracted_tokens"], 6)
                if values["full_extracted_tokens"]
                else None,
            }
        )

    return {
        "tokenizer_name": context_report.get("tokenizer_name", "unknown"),
        "context_rows": len(rows),
        "generated_skill_rows": len(paper_rows),
        "generated_skill_total_tokens": generated_total,
        "full_extracted_total_tokens": full_total,
        "token_reduction_total": max(0, full_total - generated_total),
        "by_paper": paper_rows,
    }


def response_output_summary(response_report: dict[str, Any]) -> dict[str, Any]:
    rows = response_report.get("results", [])
    by_model: dict[str, dict[str, int]] = defaultdict(lambda: {
        "rows": 0,
        "output_tokens": 0,
    })
    for row in rows:
        model_id = str(row.get("Model ID", "")).strip() or "unknown"
        by_model[model_id]["rows"] += 1
        by_model[model_id]["output_tokens"] += int_or_zero(row.get("Tokenizer output tokens"))

    model_rows = [
        {
            "model_id": model_id,
            "rows": values["rows"],
            "output_tokens": values["output_tokens"],
        }
        for model_id, values in sorted(by_model.items())
    ]
    return {
        "tokenizer_name": response_report.get("summary", {}).get("tokenizer_name", "unknown"),
        "measured_rows": int_or_zero(response_report.get("summary", {}).get("measured_rows")),
        "pending_rows": int_or_zero(response_report.get("summary", {}).get("pending_rows")),
        "total_output_tokens": int_or_zero(response_report.get("summary", {}).get("total_tokenizer_output_tokens")),
        "by_model": model_rows,
    }


def build_report(root: Path) -> dict[str, Any]:
    root = root.resolve()
    context_path = root / "results/tables/context_cost_proxy_tokenizer.json"
    response_path = root / "results/tables/model_response_cost_proxy.json"

    errors: list[str] = []
    if not context_path.exists():
        errors.append("missing context_cost_proxy_tokenizer.json")
    if not response_path.exists():
        errors.append("missing model_response_cost_proxy.json")

    context_report = load_json(context_path) if context_path.exists() else {}
    response_report = load_json(response_path) if response_path.exists() else {}
    input_summary = context_input_summary(context_report) if context_report else {}
    output_summary = response_output_summary(response_report) if response_report else {}

    if context_report and not input_summary.get("by_paper"):
        errors.append("context proxy report did not yield any paper rows")
    if response_report and int_or_zero(response_report.get("summary", {}).get("pending_rows")) != 0:
        errors.append("saved-response output proxy still has pending rows")
    if response_report and int_or_zero(response_report.get("summary", {}).get("measured_rows")) == 0:
        errors.append("saved-response output proxy has no measured rows")

    accounting_status = "complete" if not errors else "pending"
    combined_generated = int_or_zero(input_summary.get("generated_skill_total_tokens"))
    combined_output = int_or_zero(output_summary.get("total_output_tokens"))

    return {
        "schema_version": "0.1",
        "evidence_boundary": (
            "Local token accounting summary over tokenizer-aware input proxies and saved-response output proxies. "
            "This is not provider billing, live invoices, or success-per-dollar evidence."
        ),
        "accounting_status": accounting_status,
        "errors": errors,
        "source_reports": {
            "context_cost_proxy_tokenizer": str(context_path.relative_to(root)),
            "model_response_cost_proxy": str(response_path.relative_to(root)),
        },
        "input_proxy": input_summary,
        "output_proxy": output_summary,
        "composite_proxy": {
            "generated_skill_input_tokens": combined_generated,
            "saved_response_output_tokens": combined_output,
            "composite_local_token_proxy": combined_generated + combined_output,
        },
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


def format_int(value: Any) -> str:
    try:
        return f"{int(value):,}"
    except (TypeError, ValueError):
        return "n/a"


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    input_proxy = report.get("input_proxy", {})
    output_proxy = report.get("output_proxy", {})
    input_rows = [
        [
            row["paper"],
            format_int(row["generated_skill_tokens"]),
            format_int(row["full_extracted_tokens"]),
            format_int(row["token_reduction"]),
        ]
        for row in input_proxy.get("by_paper", [])
    ]
    output_rows = [
        [
            row["model_id"],
            format_int(row["rows"]),
            format_int(row["output_tokens"]),
        ]
        for row in output_proxy.get("by_model", [])
    ]
    lines = [
        "# Local Token Accounting Summary",
        "",
        "Evidence boundary: local token accounting over existing input/output proxies. "
        "This replaces provider-billing style cost claims for the current project state.",
        "",
        f"- Accounting status: {report['accounting_status']}",
        f"- Input proxy tokenizer: {input_proxy.get('tokenizer_name', 'unknown')}",
        f"- Output proxy tokenizer: {output_proxy.get('tokenizer_name', 'unknown')}",
        f"- Generated-skill input tokens: {format_int(input_proxy.get('generated_skill_total_tokens'))}",
        f"- Full-extracted input tokens: {format_int(input_proxy.get('full_extracted_total_tokens'))}",
        f"- Saved-response output tokens: {format_int(output_proxy.get('total_output_tokens'))}",
        f"- Composite local token proxy: {format_int(report.get('composite_proxy', {}).get('composite_local_token_proxy'))}",
        "",
        "## Input Proxy By Paper",
        "",
        markdown_table(input_rows, ["Paper", "Generated-skill tokens", "Full-extracted tokens", "Reduction"]),
        "",
        "## Output Proxy By Model",
        "",
        markdown_table(output_rows, ["Model", "Rows", "Output tokens"]),
        "",
    ]
    if report.get("errors"):
        lines.extend(["## Errors", ""])
        lines.extend(f"- {error}" for error in report["errors"])
        lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def write_json(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="Summarize local token accounting evidence.")
    parser.add_argument(
        "--output-json",
        type=Path,
        default=root / "results" / "token_accounting" / "token_accounting_summary.json",
    )
    parser.add_argument(
        "--output-md",
        type=Path,
        default=root / "results" / "token_accounting" / "token_accounting_summary.md",
    )
    parser.add_argument("--strict", action="store_true", help="Exit non-zero if token accounting is not complete.")
    args = parser.parse_args()

    report = build_report(root)
    write_json(args.output_json, report)
    write_markdown(args.output_md, report)
    print(args.output_json)
    print(args.output_md)
    if args.strict and report.get("accounting_status") != "complete":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
