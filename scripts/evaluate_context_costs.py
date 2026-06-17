#!/usr/bin/env python
"""Estimate context compactness and cost proxies for PaperToSkill artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
from pathlib import Path
from typing import Any


PAPER_CONFIGS = [
    {
        "id": "ai_scientist_v2",
        "paper": "AI Scientist-v2",
        "full_paper": "papers/extracted/ai_scientist_v2.txt",
        "note": "papers/notes/ai_scientist_v2_note.md",
        "task": "benchmarks/tasks/ai_scientist_v2_research_run.json",
        "context": "results/evaluations/ai_scientist_v2_context_baselines_v0.json",
    },
    {
        "id": "reflexion",
        "paper": "Reflexion",
        "full_paper": "papers/extracted/reflexion.txt",
        "note": "papers/notes/reflexion_note.md",
        "task": "benchmarks/tasks/reflexion_research_run.json",
        "context": "results/evaluations/reflexion_context_baselines_v0.json",
    },
    {
        "id": "aide",
        "paper": "AIDE",
        "full_paper": "papers/extracted/aide.txt",
        "note": "papers/notes/aide_note.md",
        "task": "benchmarks/tasks/aide_research_run.json",
        "context": "results/evaluations/aide_context_baselines_v0.json",
    },
]

TOKEN_PROXY_CHARS = 4


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def words(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text))


def estimate_tokens(text: str, chars_per_token: int = TOKEN_PROXY_CHARS) -> int:
    if chars_per_token <= 0:
        raise ValueError("chars_per_token must be positive")
    return max(1, math.ceil(len(text) / chars_per_token))


def estimate_cost(tokens: int, price_per_million_tokens: float) -> float:
    return round(tokens * price_per_million_tokens / 1_000_000, 6)


def format_decimal(value: float, digits: int = 3) -> str:
    text = f"{float(value):.{digits}f}"
    return text.rstrip("0").rstrip(".")


def format_cost(value: float) -> str:
    text = f"{value:.6f}"
    return text.rstrip("0").rstrip(".") or "0"


def escape_markdown(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def markdown_table(rows: list[dict[str, Any]], columns: list[str]) -> str:
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(escape_markdown(row.get(column, "")) for column in columns) + " |")
    return "\n".join(lines) + "\n"


def write_csv(path: Path, rows: list[dict[str, Any]], columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def context_results(path: Path) -> dict[str, dict[str, Any]]:
    return {item["id"]: item for item in load_json(path)["results"]}


def variant_paths(root: Path, config: dict[str, str]) -> dict[str, str]:
    task = load_json(root / config["task"])
    paths = {
        "full_paper": config["full_paper"],
        "curated_note": config["note"],
    }
    for variant in task["context_variants"]:
        paths[variant["id"]] = variant["path"]
    return paths


def variant_labels() -> dict[str, str]:
    return {
        "full_paper": "Full extracted paper",
        "curated_note": "Curated source note",
        "skill": "Generated skill",
        "generic_summary": "Generic summary",
        "abstract_only": "Abstract-only",
    }


def build_context_size_rows(
    root: Path,
    chars_per_token: int,
    price_per_million_tokens: float,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    labels = variant_labels()
    for config in PAPER_CONFIGS:
        paths = variant_paths(root, config)
        full_text = (root / config["full_paper"]).read_text(encoding="utf-8", errors="ignore")
        full_tokens = estimate_tokens(full_text, chars_per_token)
        for variant_id in ["full_paper", "curated_note", "skill", "generic_summary", "abstract_only"]:
            path = root / paths[variant_id]
            text = path.read_text(encoding="utf-8", errors="ignore")
            tokens = estimate_tokens(text, chars_per_token)
            reduction = 1 - (tokens / full_tokens)
            rows.append(
                {
                    "Paper": config["paper"],
                    "Variant": labels[variant_id],
                    "Path": paths[variant_id],
                    "Words": words(text),
                    "Characters": len(text),
                    "Estimated input tokens": tokens,
                    "Tokens vs full paper": format_decimal(tokens / full_tokens, 4),
                    "Token reduction vs full paper": format_decimal(reduction, 4),
                    "Estimated input cost": format_cost(estimate_cost(tokens, price_per_million_tokens)),
                }
            )
    return rows


def build_efficiency_rows(
    root: Path,
    chars_per_token: int,
    price_per_million_tokens: float,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    labels = variant_labels()
    for config in PAPER_CONFIGS:
        paths = variant_paths(root, config)
        context = context_results(root / config["context"])
        for variant_id in ["skill", "generic_summary", "abstract_only"]:
            result = context[variant_id]
            path = root / paths[variant_id]
            text = path.read_text(encoding="utf-8", errors="ignore")
            tokens = estimate_tokens(text, chars_per_token)
            normalized = float(result["score"]) / float(result["max_score"])
            rows.append(
                {
                    "Paper": config["paper"],
                    "Variant": labels[variant_id],
                    "Coverage score": f"{format_decimal(result['score'])}/{format_decimal(result['max_score'])}",
                    "Normalized coverage": format_decimal(normalized, 4),
                    "Estimated input tokens": tokens,
                    "Coverage per 1k tokens": format_decimal(float(result["score"]) / tokens * 1000, 3),
                    "Normalized coverage per 1k tokens": format_decimal(normalized / tokens * 1000, 3),
                    "Estimated input cost": format_cost(estimate_cost(tokens, price_per_million_tokens)),
                }
            )
    return rows


def write_markdown_report(
    path: Path,
    size_rows: list[dict[str, Any]],
    efficiency_rows: list[dict[str, Any]],
    price_per_million_tokens: float,
    chars_per_token: int,
) -> None:
    size_columns = [
        "Paper",
        "Variant",
        "Words",
        "Estimated input tokens",
        "Tokens vs full paper",
        "Token reduction vs full paper",
        "Estimated input cost",
    ]
    efficiency_columns = [
        "Paper",
        "Variant",
        "Coverage score",
        "Normalized coverage",
        "Estimated input tokens",
        "Coverage per 1k tokens",
        "Normalized coverage per 1k tokens",
    ]
    lines = [
        "# Context Cost Proxy",
        "",
        "Evidence boundary: token counts are deterministic proxies, estimated as "
        f"`ceil(characters / {chars_per_token})`. Cost uses a configurable "
        f"`{price_per_million_tokens}` dollars per million input-token proxy. "
        "These are not provider bills or tokenizer-exact measurements.",
        "",
        "## Context Size Proxy",
        "",
        markdown_table(size_rows, size_columns).strip(),
        "",
        "## Coverage Per Context Budget",
        "",
        "Coverage scores are the existing deterministic context-coverage scores. "
        "Rows are limited to context variants that were already evaluated.",
        "",
        markdown_table(efficiency_rows, efficiency_columns).strip(),
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def generate_cost_artifacts(
    root: Path,
    output_dir: Path,
    price_per_million_tokens: float,
    chars_per_token: int = TOKEN_PROXY_CHARS,
) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    size_rows = build_context_size_rows(root, chars_per_token, price_per_million_tokens)
    efficiency_rows = build_efficiency_rows(root, chars_per_token, price_per_million_tokens)

    size_columns = [
        "Paper",
        "Variant",
        "Path",
        "Words",
        "Characters",
        "Estimated input tokens",
        "Tokens vs full paper",
        "Token reduction vs full paper",
        "Estimated input cost",
    ]
    efficiency_columns = [
        "Paper",
        "Variant",
        "Coverage score",
        "Normalized coverage",
        "Estimated input tokens",
        "Coverage per 1k tokens",
        "Normalized coverage per 1k tokens",
        "Estimated input cost",
    ]

    size_csv = output_dir / "context_cost_proxy.csv"
    efficiency_csv = output_dir / "coverage_cost_efficiency.csv"
    report_md = output_dir / "context_cost_proxy.md"
    report_json = output_dir / "context_cost_proxy.json"

    write_csv(size_csv, size_rows, size_columns)
    write_csv(efficiency_csv, efficiency_rows, efficiency_columns)
    write_markdown_report(report_md, size_rows, efficiency_rows, price_per_million_tokens, chars_per_token)
    report_json.write_text(
        json.dumps(
            {
                "schema_version": "0.1",
                "evidence_boundary": "Deterministic token/cost proxy, not provider billing or tokenizer-exact accounting.",
                "chars_per_token": chars_per_token,
                "price_per_million_input_token_proxy": price_per_million_tokens,
                "context_size": size_rows,
                "coverage_efficiency": efficiency_rows,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    return {
        "context_cost_proxy_csv": size_csv,
        "coverage_cost_efficiency_csv": efficiency_csv,
        "context_cost_proxy_md": report_md,
        "context_cost_proxy_json": report_json,
    }


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="Estimate PaperToSkill context compactness and cost proxies.")
    parser.add_argument("--root", type=Path, default=root)
    parser.add_argument("--output-dir", type=Path, default=root / "results" / "tables")
    parser.add_argument("--chars-per-token", type=int, default=TOKEN_PROXY_CHARS)
    parser.add_argument("--price-per-million-input-tokens", type=float, default=1.0)
    args = parser.parse_args()

    written = generate_cost_artifacts(
        args.root,
        args.output_dir,
        args.price_per_million_input_tokens,
        args.chars_per_token,
    )
    for path in written.values():
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
