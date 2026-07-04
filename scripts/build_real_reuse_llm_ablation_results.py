#!/usr/bin/env python
"""Aggregate collected real-reuse LLM ablation raw rows against the plan."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


DEFAULT_PLAN = Path("results/real_reuse/llm_ablation_plan.json")
DEFAULT_RAW_ROWS = Path("results/real_reuse/raw_rows.jsonl")
DEFAULT_OUTPUT_CSV = Path("results/real_reuse/llm_ablation_raw_rows.csv")
DEFAULT_OUTPUT_JSON = Path("results/real_reuse/llm_ablation_summary.json")
DEFAULT_OUTPUT_MD = Path("results/real_reuse/llm_ablation_summary.md")


def root_path() -> Path:
    return Path(__file__).resolve().parents[1]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_raw_rows(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def fmt_score(value: Any) -> str:
    try:
        return f"{float(value):.3f}"
    except (TypeError, ValueError):
        return ""


def build_summary(plan: dict[str, Any], raw_rows: list[dict[str, Any]]) -> dict[str, Any]:
    expected: list[dict[str, Any]] = []
    for command in plan["commands"]:
        for condition in command["conditions"]:
            expected.append(
                {
                    "run_id": command["run_id"],
                    "task_id": command["task_id"],
                    "model_slot": command["model_slot"],
                    "model_family": command["model_family"],
                    "model_alias": command["model_alias"],
                    "condition": condition,
                }
            )
    raw_by_key = {
        (row.get("run_id"), row.get("task_id"), row.get("model_alias"), row.get("condition")): row
        for row in raw_rows
    }
    collected_rows: list[dict[str, Any]] = []
    pending_rows: list[dict[str, Any]] = []
    for item in expected:
        key = (item["run_id"], item["task_id"], item["model_alias"], item["condition"])
        raw = raw_by_key.get(key)
        if not raw:
            pending_rows.append({**item, "status": "pending"})
            continue
        collected_rows.append(
            {
                **item,
                "status": raw.get("status", ""),
                "task_score": fmt_score(raw.get("task_score")),
                "success": str(bool(raw.get("success"))),
                "tokens": str(raw.get("tokens", "")),
                "attempts": str(raw.get("call_status", {}).get("attempts", "")),
                "failure_reason": raw.get("failure_reason", ""),
                "output_path": raw.get("output_path", ""),
                "metric_path": raw.get("metric_path", ""),
            }
        )

    pairs: list[dict[str, Any]] = []
    for command in plan["commands"]:
        task_rows = [
            row
            for row in collected_rows
            if row["run_id"] == command["run_id"] and row["task_id"] == command["task_id"]
        ]
        by_condition = {row["condition"]: row for row in task_rows}
        summary = by_condition.get("summary")
        skill = by_condition.get("papertoskill")
        pairs.append(
            {
                "task_id": command["task_id"],
                "model_slot": command["model_slot"],
                "model_family": command["model_family"],
                "model_alias": command["model_alias"],
                "summary_score": summary["task_score"] if summary else "",
                "papertoskill_score": skill["task_score"] if skill else "",
                "pair_status": "complete" if summary and skill else "pending",
            }
        )

    return {
        "schema_version": "0.1",
        "evidence_boundary": (
            "Aggregates only rows whose run_id was pre-registered in the real-reuse "
            "LLM ablation plan. Pending rows are not negative evidence."
        ),
        "expected_rows": len(expected),
        "collected_rows": len(collected_rows),
        "pending_rows": len(pending_rows),
        "collected": collected_rows,
        "pending": pending_rows,
        "pairs": pairs,
    }


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "task_id",
        "model_family",
        "model_alias",
        "condition",
        "task_score",
        "success",
        "tokens",
        "attempts",
        "failure_reason",
        "run_id",
        "output_path",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def md_table(headers: list[str], rows: list[list[Any]]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(cell) for cell in row) + " |")
    return "\n".join(lines)


def write_markdown(path: Path, summary: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pair_rows = [
        [
            row["task_id"],
            row["model_family"],
            row["model_alias"],
            row["summary_score"],
            row["papertoskill_score"],
            row["pair_status"],
        ]
        for row in summary["pairs"]
    ]
    collected_rows = [
        [
            row["task_id"],
            row["model_family"],
            row["model_alias"],
            row["condition"],
            row["task_score"],
            row["success"],
            row["attempts"],
        ]
        for row in summary["collected"]
    ]
    text = "\n\n".join(
        [
            "# Real-Reuse LLM Ablation Summary",
            f"Evidence boundary: {summary['evidence_boundary']}",
            f"- Expected rows: {summary['expected_rows']}",
            f"- Collected rows: {summary['collected_rows']}",
            f"- Pending rows: {summary['pending_rows']}",
            "## Pair Status",
            md_table(
                ["Task ID", "Family", "Alias", "Summary", "PaperToSkill", "Status"],
                pair_rows,
            ),
            "## Collected Raw Rows",
            md_table(
                ["Task ID", "Family", "Alias", "Condition", "Score", "Success", "Attempts"],
                collected_rows,
            ),
        ]
    )
    path.write_text(text + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=root_path())
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--raw-rows", type=Path, default=DEFAULT_RAW_ROWS)
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_OUTPUT_CSV)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    args = parser.parse_args()

    root = args.root.resolve()
    plan_path = args.plan if args.plan.is_absolute() else root / args.plan
    raw_path = args.raw_rows if args.raw_rows.is_absolute() else root / args.raw_rows
    summary = build_summary(load_json(plan_path), read_raw_rows(raw_path))
    output_csv = args.output_csv if args.output_csv.is_absolute() else root / args.output_csv
    output_json = args.output_json if args.output_json.is_absolute() else root / args.output_json
    output_md = args.output_md if args.output_md.is_absolute() else root / args.output_md
    write_csv(output_csv, summary["collected"])
    write_json(output_json, summary)
    write_markdown(output_md, summary)
    print(output_csv)
    print(output_json)
    print(output_md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
