#!/usr/bin/env python
"""Summarize provider-billing evidence rows without treating blanks as bills."""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


REQUIRED_COLUMNS = [
    "evidence_id",
    "evidence_label",
    "evidence_kind",
    "provider",
    "model_alias",
    "billing_period",
    "input_tokens",
    "output_tokens",
    "billed_usd",
    "currency",
    "invoice_or_usage_evidence",
    "success_metric",
    "success_value",
    "reviewer_id",
    "notes",
]

NUMERIC_COLUMNS = ["input_tokens", "output_tokens", "billed_usd", "success_value"]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_template(path: Path, config: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=REQUIRED_COLUMNS)
        writer.writeheader()
        for slot in config["evidence_slots"]:
            writer.writerow(
                {
                    "evidence_id": slot["evidence_id"],
                    "evidence_label": slot["evidence_label"],
                    "evidence_kind": slot["evidence_kind"],
                    "provider": "",
                    "model_alias": "",
                    "billing_period": "",
                    "input_tokens": "",
                    "output_tokens": "",
                    "billed_usd": "",
                    "currency": "",
                    "invoice_or_usage_evidence": "",
                    "success_metric": "",
                    "success_value": "",
                    "reviewer_id": "",
                    "notes": "",
                }
            )


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        missing = [column for column in REQUIRED_COLUMNS if column not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(f"Missing required billing columns: {', '.join(missing)}")
        return list(reader)


def parse_number(value: str, row_number: int, column: str) -> float | None:
    value = value.strip()
    if value == "":
        return None
    try:
        number = float(value)
    except ValueError as exc:
        raise ValueError(f"Row {row_number}: {column} must be numeric or blank") from exc
    if number < 0:
        raise ValueError(f"Row {row_number}: {column} must be non-negative")
    return number


def row_has_measurement(row: dict[str, str]) -> bool:
    return any(row[column].strip() for column in REQUIRED_COLUMNS if column not in {"evidence_id", "evidence_label", "evidence_kind", "notes"})


def summarize(rows: list[dict[str, str]], config: dict[str, Any]) -> dict[str, Any]:
    expected_ids = {slot["evidence_id"] for slot in config["evidence_slots"]}
    seen_ids = {row["evidence_id"].strip() for row in rows}
    errors: list[str] = []
    measured_rows = 0
    totals_by_provider: dict[str, dict[str, float]] = defaultdict(lambda: {"billed_usd": 0.0, "input_tokens": 0.0, "output_tokens": 0.0, "success_value": 0.0})

    missing_ids = sorted(expected_ids - seen_ids)
    extra_ids = sorted(seen_ids - expected_ids)
    if missing_ids:
        errors.append("Missing evidence slots: " + ", ".join(missing_ids))
    if extra_ids:
        errors.append("Unexpected evidence slots: " + ", ".join(extra_ids))

    for index, row in enumerate(rows, start=2):
        numbers = {column: parse_number(row[column], index, column) for column in NUMERIC_COLUMNS}
        if not row_has_measurement(row):
            continue

        measured_rows += 1
        for column in [
            "provider",
            "model_alias",
            "billing_period",
            "currency",
            "invoice_or_usage_evidence",
            "success_metric",
            "reviewer_id",
        ]:
            if not row[column].strip():
                errors.append(f"Row {index}: measured billing row requires {column}")
        for column, number in numbers.items():
            if number is None:
                errors.append(f"Row {index}: measured billing row requires {column}")

        provider = row["provider"].strip() or "unknown"
        if all(numbers[column] is not None for column in NUMERIC_COLUMNS):
            totals_by_provider[provider]["billed_usd"] += numbers["billed_usd"] or 0
            totals_by_provider[provider]["input_tokens"] += numbers["input_tokens"] or 0
            totals_by_provider[provider]["output_tokens"] += numbers["output_tokens"] or 0
            totals_by_provider[provider]["success_value"] += numbers["success_value"] or 0

    total_billed = sum(item["billed_usd"] for item in totals_by_provider.values())
    total_success = sum(item["success_value"] for item in totals_by_provider.values())
    return {
        "schema_version": "0.1",
        "evidence_boundary": (
            "Summarizes provider-billing evidence rows. Blank rows are pending, not realized bills. "
            "Do not claim provider billing or success-per-dollar until billing_status is complete and errors are empty."
        ),
        "total_rows": len(rows),
        "measured_rows": measured_rows,
        "pending_rows": len(rows) - measured_rows,
        "billing_status": "complete" if rows and measured_rows == len(rows) and not errors else "pending",
        "errors": errors,
        "total_billed_usd": round(total_billed, 6),
        "total_success_value": round(total_success, 6),
        "success_per_dollar": round(total_success / total_billed, 6) if total_billed > 0 else None,
        "by_provider": {provider: {key: round(value, 6) for key, value in values.items()} for provider, values in sorted(totals_by_provider.items())},
    }


def format_decimal(value: float | None) -> str:
    if value is None:
        return "n/a"
    text = f"{value:.6f}"
    return text.rstrip("0").rstrip(".") or "0"


def markdown_table(rows: list[list[str]], columns: list[str]) -> str:
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for row in rows:
        values = [value.replace("|", "\\|").replace("\n", " ") for value in row]
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def write_markdown(path: Path, summary: dict[str, Any]) -> None:
    provider_rows = [
        [
            provider,
            format_decimal(values["billed_usd"]),
            format_decimal(values["input_tokens"]),
            format_decimal(values["output_tokens"]),
            format_decimal(values["success_value"]),
        ]
        for provider, values in summary["by_provider"].items()
    ]
    lines = [
        "# Provider Billing Evidence Summary",
        "",
        "Evidence boundary: blank rows are pending, not realized bills. Do not claim "
        "provider billing, live invoices, or success-per-dollar until "
        "`billing_status=complete` and errors are empty.",
        "",
        f"- Billing status: {summary['billing_status']}",
        f"- Total rows: {summary['total_rows']}",
        f"- Measured rows: {summary['measured_rows']}",
        f"- Pending rows: {summary['pending_rows']}",
        f"- Errors: {len(summary['errors'])}",
        f"- Total billed USD: {format_decimal(summary['total_billed_usd'])}",
        f"- Success per dollar: {format_decimal(summary['success_per_dollar'])}",
        "",
        "## By Provider",
        "",
        markdown_table(provider_rows, ["Provider", "Billed USD", "Input tokens", "Output tokens", "Success value"]) if provider_rows else "No measured provider-billing rows yet.",
        "",
    ]
    if summary["errors"]:
        lines.extend(["## Errors", ""])
        lines.extend(f"- {error}" for error in summary["errors"])
        lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def write_json(path: Path, summary: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="Summarize provider-billing evidence rows.")
    parser.add_argument("--config", type=Path, default=root / "benchmarks" / "provider_billing_evidence_v0.json")
    parser.add_argument("--template", type=Path, default=root / "results" / "provider_billing_evidence" / "billing_template.csv")
    parser.add_argument("--output-json", type=Path, default=root / "results" / "provider_billing_evidence" / "billing_summary.json")
    parser.add_argument("--output-md", type=Path, default=root / "results" / "provider_billing_evidence" / "billing_summary.md")
    parser.add_argument("--init-template", action="store_true", help="Write or refresh the blank billing evidence template.")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero if measured rows have validation errors.")
    args = parser.parse_args()

    config = load_json(args.config)
    if args.init_template or not args.template.exists():
        write_template(args.template, config)
    summary = summarize(load_rows(args.template), config)
    write_json(args.output_json, summary)
    write_markdown(args.output_md, summary)
    print(args.template)
    print(args.output_json)
    print(args.output_md)
    if args.strict and summary["errors"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
