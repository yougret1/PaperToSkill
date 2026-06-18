#!/usr/bin/env python
"""Estimate output-token cost proxies for saved model-ablation responses."""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
from pathlib import Path
from typing import Any, Callable


DEFAULT_INDEX = Path("results/model_ablation_prompts/v0/index.json")
DEFAULT_RUN_REPORTS = [
    Path("results/model_ablation_prompts/v0/run_report.json"),
    Path("results/model_ablation_prompts/v0/gpt_retry_run_report.json"),
]
DEFAULT_TOKENIZER = "o200k_base"
TOKEN_PROXY_CHARS = 4

TokenCounter = Callable[[str], int]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def words(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text))


def estimate_tokens(text: str, chars_per_token: int = TOKEN_PROXY_CHARS) -> int:
    if chars_per_token <= 0:
        raise ValueError("chars_per_token must be positive")
    return max(1, math.ceil(len(text) / chars_per_token))


def tokenizer_counter(tokenizer_name: str) -> tuple[TokenCounter | None, str | None]:
    try:
        import tiktoken  # type: ignore[import-not-found]
    except ImportError:
        return None, "tiktoken is not installed"

    try:
        encoding = tiktoken.get_encoding(tokenizer_name)
    except Exception as exc:  # pragma: no cover - depends on installed tiktoken data.
        return None, f"could not load tokenizer {tokenizer_name}: {exc}"

    def count(text: str) -> int:
        return max(1, len(encoding.encode(text)))

    return count, None


def estimate_cost(tokens: int, price_per_million_tokens: float) -> float:
    return round(tokens * price_per_million_tokens / 1_000_000, 6)


def format_cost(value: float) -> str:
    text = f"{value:.6f}"
    return text.rstrip("0").rstrip(".") or "0"


def alias_records(root: Path, run_report_paths: list[Path]) -> dict[tuple[str, str], dict[str, Any]]:
    records: dict[tuple[str, str], dict[str, Any]] = {}
    for raw_path in run_report_paths:
        path = raw_path if raw_path.is_absolute() else root / raw_path
        if not path.exists():
            continue
        report = load_json(path)
        evidence = str(path.relative_to(root)) if path.is_relative_to(root) else str(path)
        for row in report.get("results", []):
            key = (str(row.get("model_id", "")), str(row.get("case_id", "")))
            if not key[0] or not key[1]:
                continue
            existing = records.get(key)
            if existing and existing.get("status") == "success":
                continue
            records[key] = {
                "status": row.get("status", ""),
                "alias_used": row.get("alias_used", ""),
                "attempted_aliases": row.get("attempted_aliases", []),
                "evidence": evidence,
            }
    return records


def build_rows(
    root: Path,
    index_path: Path,
    run_report_paths: list[Path],
    price_per_million_output_tokens: float,
    chars_per_token: int,
    tokenizer_name: str | None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    index = load_json(index_path)
    aliases = alias_records(root, run_report_paths)
    tokenizer_count: TokenCounter | None = None
    tokenizer_error = None
    if tokenizer_name:
        tokenizer_count, tokenizer_error = tokenizer_counter(tokenizer_name)

    rows: list[dict[str, Any]] = []
    for prompt in index.get("prompts", []):
        response_path = root / prompt["expected_response_path"]
        alias = aliases.get((prompt["model_id"], prompt["case_id"]), {})
        if response_path.exists():
            text = response_path.read_text(encoding="utf-8", errors="ignore")
            char_proxy_tokens = estimate_tokens(text, chars_per_token)
            tokenizer_tokens = tokenizer_count(text) if tokenizer_count else None
            status = "measured"
            word_count = words(text)
            characters = len(text)
        else:
            char_proxy_tokens = 0
            tokenizer_tokens = None
            status = "pending"
            word_count = 0
            characters = 0

        rows.append(
            {
                "Model ID": prompt["model_id"],
                "Case ID": prompt["case_id"],
                "Configured alias": prompt.get("model_alias", ""),
                "Actual alias": alias.get("alias_used", ""),
                "Status": status,
                "Response path": prompt["expected_response_path"],
                "Words": word_count,
                "Characters": characters,
                "Character proxy output tokens": char_proxy_tokens,
                "Tokenizer output tokens": tokenizer_tokens if tokenizer_tokens is not None else "",
                "Estimated output cost proxy": format_cost(
                    estimate_cost(tokenizer_tokens if tokenizer_tokens is not None else char_proxy_tokens, price_per_million_output_tokens)
                )
                if status == "measured"
                else "",
                "Alias evidence": alias.get("evidence", ""),
            }
        )

    measured = [row for row in rows if row["Status"] == "measured"]
    tokenizer_values = [int(row["Tokenizer output tokens"]) for row in measured if row["Tokenizer output tokens"] != ""]
    summary = {
        "total_rows": len(rows),
        "measured_rows": len(measured),
        "pending_rows": len(rows) - len(measured),
        "total_character_proxy_output_tokens": sum(int(row["Character proxy output tokens"]) for row in measured),
        "total_tokenizer_output_tokens": sum(tokenizer_values) if tokenizer_values else None,
        "price_per_million_output_token_proxy": price_per_million_output_tokens,
        "chars_per_token": chars_per_token,
        "tokenizer_name": tokenizer_name,
        "tokenizer_error": tokenizer_error,
    }
    return rows, summary


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    columns = [
        "Model ID",
        "Case ID",
        "Configured alias",
        "Actual alias",
        "Status",
        "Words",
        "Characters",
        "Character proxy output tokens",
        "Tokenizer output tokens",
        "Estimated output cost proxy",
        "Response path",
        "Alias evidence",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def markdown_table(rows: list[dict[str, Any]], columns: list[str]) -> str:
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for row in rows:
        values = [str(row.get(column, "")).replace("|", "\\|").replace("\n", " ") for column in columns]
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def write_markdown(path: Path, rows: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    columns = [
        "Model ID",
        "Case ID",
        "Actual alias",
        "Status",
        "Words",
        "Character proxy output tokens",
        "Tokenizer output tokens",
        "Estimated output cost proxy",
    ]
    tokenizer_line = (
        f"- Tokenizer: `{summary['tokenizer_name']}`"
        if summary.get("total_tokenizer_output_tokens") is not None
        else f"- Tokenizer: unavailable or skipped ({summary.get('tokenizer_error') or 'not requested'})"
    )
    lines = [
        "# Model Response Output-Token Proxy",
        "",
        "Evidence boundary: this report measures saved model-ablation response files only. "
        "Token counts and costs are local output-token proxies, not provider bills, live invoices, "
        "or success-per-dollar evidence. Pending rows are missing response files, not negative model-quality evidence.",
        "",
        f"- Total rows: {summary['total_rows']}",
        f"- Measured rows: {summary['measured_rows']}",
        f"- Pending rows: {summary['pending_rows']}",
        f"- Character proxy output tokens: {summary['total_character_proxy_output_tokens']}",
        f"- Tokenizer output tokens: {summary.get('total_tokenizer_output_tokens')}",
        f"- Price proxy: `{summary['price_per_million_output_token_proxy']}` dollars per million output tokens",
        tokenizer_line,
        "",
        markdown_table(rows, columns),
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def write_json(path: Path, rows: list[dict[str, Any]], summary: dict[str, Any], index_path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "schema_version": "0.1",
                "index_path": str(index_path),
                "evidence_boundary": (
                    "Measures saved model-ablation response files only. Token counts and costs are local "
                    "output-token proxies, not provider bills, live invoices, or success-per-dollar evidence."
                ),
                "summary": summary,
                "results": rows,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="Estimate saved model-response output-token proxies.")
    parser.add_argument("--root", type=Path, default=root)
    parser.add_argument("--index", type=Path, default=root / DEFAULT_INDEX)
    parser.add_argument("--run-report", action="append", type=Path, help="Run report JSON used to recover actual aliases.")
    parser.add_argument("--output-json", type=Path, default=root / "results" / "tables" / "model_response_cost_proxy.json")
    parser.add_argument("--output-md", type=Path, default=root / "results" / "tables" / "model_response_cost_proxy.md")
    parser.add_argument("--output-csv", type=Path, default=root / "results" / "tables" / "model_response_cost_proxy.csv")
    parser.add_argument("--chars-per-token", type=int, default=TOKEN_PROXY_CHARS)
    parser.add_argument("--price-per-million-output-tokens", type=float, default=1.0)
    parser.add_argument("--tokenizer", default=DEFAULT_TOKENIZER, help="Optional tiktoken encoding; use '' to skip.")
    args = parser.parse_args()

    run_reports = args.run_report or [args.root / path for path in DEFAULT_RUN_REPORTS]
    rows, summary = build_rows(
        args.root,
        args.index,
        run_reports,
        args.price_per_million_output_tokens,
        args.chars_per_token,
        args.tokenizer or None,
    )
    write_csv(args.output_csv, rows)
    write_markdown(args.output_md, rows, summary)
    write_json(args.output_json, rows, summary, args.index)
    print(args.output_csv)
    print(args.output_md)
    print(args.output_json)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
