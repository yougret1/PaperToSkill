#!/usr/bin/env python
"""Build a pre-registered real-reuse LLM ablation execution plan."""

from __future__ import annotations

import argparse
import csv
import json
import os
from pathlib import Path
from typing import Any


DEFAULT_SPEC = Path("benchmarks/real_reuse/llm_ablation_v0.json")
DEFAULT_MAIN_TABLE = Path("results/real_reuse/main_results_plan.csv")
DEFAULT_OUTPUT_JSON = Path("results/real_reuse/llm_ablation_plan.json")
DEFAULT_OUTPUT_MD = Path("results/real_reuse/llm_ablation_plan.md")


def root_path() -> Path:
    return Path(__file__).resolve().parents[1]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def read_main_table(path: Path) -> dict[str, dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return {row["Task ID"]: row for row in csv.DictReader(handle)}


def task_prefix(task_id: str) -> str:
    if task_id.startswith("AIDE-"):
        return "AIDE"
    if task_id.startswith("SWE-"):
        return "SWE"
    if task_id.startswith("REF-"):
        return "REF"
    if task_id.startswith("SNAP-"):
        return "SNAP"
    raise ValueError(f"unsupported task id: {task_id}")


def run_id(model_slot: dict[str, Any], task_id: str, prefix: str) -> str:
    return f"{prefix}_{model_slot['id']}_{task_id.lower().replace('-', '_')}"


def env_status(*names: str) -> dict[str, str]:
    return {name: "present" if os.environ.get(name) else "missing" for name in names}


def build_command(
    *,
    script: str,
    task_id: str,
    model_slot: dict[str, Any],
    runner_defaults: dict[str, Any],
    conditions: list[str],
    run_id_prefix: str,
) -> str:
    parts = [
        "python",
        script.replace("/", "\\"),
        "--task",
        task_id,
    ]
    for condition in conditions:
        parts.extend(["--condition", condition])
    parts.extend(
        [
            "--model-family",
            str(model_slot["model_family"]),
            "--model-alias",
            str(model_slot["model_alias"]),
            "--wire-api",
            str(model_slot["wire_api"]),
            "--base-url-env",
            str(model_slot["base_url_env"]),
            "--api-key-env",
            str(model_slot["api_key_env"]),
            "--timeout-seconds",
            str(model_slot["timeout_seconds"]),
            "--max-attempts",
            str(model_slot["max_attempts"]),
            "--retry-delay-seconds",
            str(model_slot["retry_delay_seconds"]),
            "--max-tokens",
            str(runner_defaults["max_tokens"]),
            "--run-id",
            run_id(model_slot, task_id, run_id_prefix),
        ]
    )
    if "score_timeout_seconds" in runner_defaults:
        parts.extend(["--score-timeout-seconds", str(runner_defaults["score_timeout_seconds"])])
    return " ".join(parts)


def build_plan(root: Path, spec_path: Path, main_table_path: Path) -> dict[str, Any]:
    spec = load_json(root / spec_path if not spec_path.is_absolute() else spec_path)
    main_rows = read_main_table(root / main_table_path if not main_table_path.is_absolute() else main_table_path)
    conditions = list(spec.get("conditions", ["summary", "papertoskill"]))
    model_slots = list(spec["model_slots"])
    runner_defaults = dict(spec["runner_defaults"])
    selected_tasks = list(spec["selection_policy"]["primary_subset"])
    run_id_prefix = str(spec.get("run_id_prefix", "phaseXX_llm_ablation"))

    tasks: list[dict[str, Any]] = []
    commands: list[dict[str, Any]] = []
    env_names: set[str] = set()
    for task in selected_tasks:
        task_id = task["task_id"]
        if task_id not in main_rows:
            raise ValueError(f"selected task missing from main table: {task_id}")
        prefix = task_prefix(task_id)
        if prefix not in runner_defaults:
            raise ValueError(f"no runner defaults for task prefix {prefix}")
        main = main_rows[task_id]
        tasks.append(
            {
                "task_id": task_id,
                "role": task["role"],
                "reason": task["reason"],
                "source_paper": main["Source Paper"],
                "metric": main["Metric"],
                "current_summary_score": main["Summary Score"],
                "current_papertoskill_score": main["PaperToSkill Score"],
            }
        )
        for slot in model_slots:
            env_names.add(str(slot["base_url_env"]))
            env_names.add(str(slot["api_key_env"]))
            commands.append(
                {
                    "task_id": task_id,
                    "model_slot": slot["id"],
                    "model_family": slot["model_family"],
                    "model_alias": slot["model_alias"],
                    "wire_api": slot["wire_api"],
                    "conditions": conditions,
                    "expected_raw_rows": len(conditions),
                    "run_id": run_id(slot, task_id, run_id_prefix),
                    "command": build_command(
                        script=runner_defaults[prefix]["script"],
                        task_id=task_id,
                        model_slot=slot,
                        runner_defaults=runner_defaults[prefix],
                        conditions=conditions,
                        run_id_prefix=run_id_prefix,
                    ),
                }
            )

    return {
        "schema_version": "0.1",
        "spec_path": spec_path.as_posix(),
        "main_table_path": main_table_path.as_posix(),
        "run_id_prefix": run_id_prefix,
        "purpose": spec["purpose"],
        "evidence_boundary": spec["evidence_boundary"],
        "tasks": tasks,
        "model_slots": model_slots,
        "commands": commands,
        "expected_scored_raw_rows": sum(item["expected_raw_rows"] for item in commands),
        "deferred_until_contract_fix": spec["selection_policy"].get("deferred_until_contract_fix", []),
        "optional_expansion_after_pilot": spec["selection_policy"].get("optional_expansion_after_pilot", []),
        "aggregation_plan": spec["aggregation_plan"],
        "environment_status": env_status(*sorted(env_names)),
    }


def md_table(headers: list[str], rows: list[list[Any]]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(cell) for cell in row) + " |")
    return "\n".join(lines)


def write_markdown(path: Path, plan: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    task_rows = [
        [
            task["task_id"],
            task["source_paper"],
            task["role"],
            task["metric"],
            task["current_summary_score"],
            task["current_papertoskill_score"],
        ]
        for task in plan["tasks"]
    ]
    model_rows = [
        [
            slot["model_family"],
            slot["model_alias"],
            slot["wire_api"],
            slot["base_url_env"],
            slot["api_key_env"],
            slot["timeout_seconds"],
            slot["max_attempts"],
        ]
        for slot in plan["model_slots"]
    ]
    command_rows = [
        [
            command["task_id"],
            command["model_slot"],
            command["expected_raw_rows"],
            f"`{command['run_id']}`",
        ]
        for command in plan["commands"]
    ]
    env_rows = [[name, status] for name, status in sorted(plan["environment_status"].items())]
    text = "\n\n".join(
        [
            "# Real-Reuse LLM Ablation Plan",
            f"Purpose: {plan['purpose']}",
            f"Evidence boundary: {plan['evidence_boundary']}",
            f"Expected scored raw rows if fully run: {plan['expected_scored_raw_rows']}",
            "## Selected Tasks",
            md_table(
                ["Task ID", "Source Paper", "Role", "Metric", "Summary", "PaperToSkill"],
                task_rows,
            ),
            "## Model Slots",
            md_table(
                ["Family", "Alias", "Wire API", "Base URL Env", "API Key Env", "Timeout", "Attempts"],
                model_rows,
            ),
            "## Command Matrix",
            md_table(["Task ID", "Model Slot", "Expected Raw Rows", "Run ID"], command_rows),
            "## Environment Status",
            md_table(["Env", "Status"], env_rows),
            "## Commands",
            "\n\n".join(f"```powershell\n{item['command']}\n```" for item in plan["commands"]),
        ]
    )
    path.write_text(text + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=root_path())
    parser.add_argument("--spec", type=Path, default=DEFAULT_SPEC)
    parser.add_argument("--main-table", type=Path, default=DEFAULT_MAIN_TABLE)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    args = parser.parse_args()

    root = args.root.resolve()
    plan = build_plan(root, args.spec, args.main_table)
    output_json = args.output_json if args.output_json.is_absolute() else root / args.output_json
    output_md = args.output_md if args.output_md.is_absolute() else root / args.output_md
    write_json(output_json, plan)
    write_markdown(output_md, plan)
    print(output_json)
    print(output_md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
