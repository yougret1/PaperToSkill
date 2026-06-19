#!/usr/bin/env python
"""Configure the DeepSeek follow-up model slot without storing secrets."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


DEEPSEEK_SLOT_ID = "deepseek_followup_slot"
SECRET_PATTERN = re.compile(r"sk-[A-Za-z0-9]{20,}")
ENV_NAME_PATTERN = re.compile(r"^[A-Z][A-Z0-9_]*$")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def validate_no_secret(label: str, value: str) -> None:
    if SECRET_PATTERN.search(value):
        raise ValueError(f"{label} looks like a raw API key; provide an environment variable name instead")


def validate_env_name(label: str, value: str) -> None:
    validate_no_secret(label, value)
    if not ENV_NAME_PATTERN.match(value):
        raise ValueError(f"{label} must be an uppercase environment variable name")


def configure_slot(
    task: dict[str, Any],
    *,
    model_alias: str,
    auth_env: str,
    base_url_env: str,
    provider_status: str,
) -> dict[str, Any]:
    validate_no_secret("model_alias", model_alias)
    validate_env_name("auth_env", auth_env)
    validate_env_name("base_url_env", base_url_env)
    validate_no_secret("provider_status", provider_status)
    if not model_alias.strip():
        raise ValueError("model_alias must not be blank")

    for slot in task.get("model_slots", []):
        if slot.get("id") != DEEPSEEK_SLOT_ID:
            continue
        slot["model_alias"] = model_alias.strip()
        slot["auth_env"] = auth_env.strip()
        slot["base_url_env"] = base_url_env.strip()
        slot["provider_status"] = provider_status.strip()
        run_notes = list(slot.get("run_notes", []))
        note = (
            "Configured by scripts/configure_deepseek_followup.py; keep raw "
            "API keys only in local environment variables."
        )
        if note not in run_notes:
            run_notes.append(note)
        slot["run_notes"] = run_notes
        return task
    raise ValueError(f"missing model slot: {DEEPSEEK_SLOT_ID}")


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="Configure the DeepSeek follow-up slot without storing secrets.")
    parser.add_argument("--task", type=Path, default=root / "benchmarks" / "model_ablation_v0.json")
    parser.add_argument("--model-alias", required=True, help="Concrete DeepSeek model alias, e.g. deepseek-reasoner.")
    parser.add_argument("--auth-env", default="DEEPSEEK_API_KEY", help="Environment variable name containing the key.")
    parser.add_argument("--base-url-env", default="DEEPSEEK_BASE_URL", help="Environment variable name containing the base URL.")
    parser.add_argument(
        "--provider-status",
        default="configured_pending_live_run",
        help="Non-secret status note to store in the benchmark slot.",
    )
    args = parser.parse_args()

    task_path = args.task
    task = load_json(task_path)
    updated = configure_slot(
        task,
        model_alias=args.model_alias,
        auth_env=args.auth_env,
        base_url_env=args.base_url_env,
        provider_status=args.provider_status,
    )
    write_json(task_path, updated)
    print(task_path)
    print(f"configured {DEEPSEEK_SLOT_ID} with alias={args.model_alias}; auth_env={args.auth_env}; base_url_env={args.base_url_env}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
