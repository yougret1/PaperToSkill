#!/usr/bin/env python3
"""Obtain two outcome-blind candidate labels through the documented API."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
import urllib.error
import urllib.request
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


TASKS = (
    "flink-query",
    "lab-unit-harmonization",
    "sec-financial-report",
    "organize-messy-files",
)
LABELS = {"intended-preserving", "destructive", "unclear"}
TEXT_SUFFIXES = {".md", ".txt", ".yaml", ".yml", ".json"}
DEFAULT_REVIEWERS = (
    ("reviewer_a_deepseek_v4_pro", "deepseek-v4-pro"),
    ("reviewer_b_deepseek_v4_flash", "deepseek-v4-flash"),
)
SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


def atomic_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_tree(root: Path) -> str:
    if not root.is_dir():
        raise RuntimeError(f"input tree is missing: {root}")
    digest = hashlib.sha256()
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        relative = path.relative_to(root).as_posix().encode("utf-8")
        payload = path.read_bytes()
        digest.update(len(relative).to_bytes(8, "big"))
        digest.update(relative)
        digest.update(len(payload).to_bytes(8, "big"))
        digest.update(payload)
    return digest.hexdigest()


def load_credentials(path: Path) -> tuple[str, str]:
    text = path.read_text(encoding="utf-8")
    key_match = re.search(r"\bsk-[A-Za-z0-9_-]{20,}\b", text)
    base_match = re.search(r"https://api\.deepseek\.com", text)
    if not key_match or not base_match:
        raise RuntimeError("documented DeepSeek credentials are incomplete")
    return key_match.group(0), base_match.group(0)


def text_tree(root: Path) -> str:
    sections: list[str] = []
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        relative = path.relative_to(root).as_posix()
        content = path.read_text(encoding="utf-8", errors="replace")
        sections.append(f"\n--- FILE {relative} ---\n{content}")
    return "".join(sections)


def prompt_for(
    task_id: str,
    skillsbench_root: Path,
    materials: Path,
    p_pool: Path | None = None,
) -> str:
    task_root = skillsbench_root / "tasks" / task_id
    task_text = (task_root / "task.md").read_text(encoding="utf-8", errors="replace")
    official = text_tree(task_root / "environment" / "skills")
    effective_p_pool = p_pool or materials / "candidate_pool" / "P"
    preserving = text_tree(effective_p_pool / task_id / "skills")
    destructive = text_tree(materials / "candidate_pool" / "D" / task_id / "skills")
    return f"""You are an independent outcome-blind specification annotator.

You are given a public task contract, official full skill F, reducer candidate P,
and negative-control candidate D. You have no execution outcomes. Do not infer or
invent model scores. Label each transformation only from its specification intent.

Labels:
- intended-preserving: task-critical instructions remain in eager text or in an
  accessible referenced resource included in the candidate.
- destructive: a task-critical procedure, output contract, or required resource
  is removed.
- unclear: the supplied text is insufficient to decide.

Return one JSON object with exactly these string fields:
task_id, P_label, D_label, P_rationale, D_rationale.

TASK_ID: {task_id}

=== TASK CONTRACT ===
{task_text}

=== OFFICIAL FULL SKILL F ===
{official}

=== REDUCER CANDIDATE P ===
{preserving}

=== BODY-DROP NEGATIVE CONTROL D ===
{destructive}
"""


def request_label(url: str, api_key: str, model: str, prompt: str) -> dict[str, Any]:
    body = json.dumps(
        {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": "Judge only the supplied specification. Return valid JSON and no markdown.",
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0,
            "max_tokens": 4096,
            "response_format": {"type": "json_object"},
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        url.rstrip("/") + "/chat/completions",
        data=body,
        method="POST",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
    )
    last_error: Exception | None = None
    for attempt in range(1, 6):
        try:
            with urllib.request.urlopen(request, timeout=180) as response:
                payload = json.loads(response.read().decode("utf-8"))
            content = payload["choices"][0]["message"]["content"]
            if not isinstance(content, str):
                raise ValueError("annotation content is not text")
            cleaned = content.strip()
            if cleaned.startswith("```"):
                cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
                cleaned = re.sub(r"\s*```$", "", cleaned)
            try:
                result = json.loads(cleaned)
            except json.JSONDecodeError:
                start, end = cleaned.find("{"), cleaned.rfind("}")
                if start < 0 or end <= start:
                    raise
                result = json.loads(cleaned[start : end + 1])
            result["model"] = model
            result["attempt"] = attempt
            return result
        except (
            OSError,
            KeyError,
            IndexError,
            ValueError,
            json.JSONDecodeError,
            urllib.error.HTTPError,
        ) as exc:
            last_error = exc
            if attempt < 5:
                time.sleep(2)
    raise RuntimeError(f"annotation request failed after five attempts: {type(last_error).__name__}")


def validate_record(record: dict[str, Any], task_id: str) -> None:
    if record.get("task_id") != task_id:
        raise RuntimeError(f"annotation task mismatch for {task_id}")
    for field in ("P_label", "D_label"):
        if record.get(field) not in LABELS:
            raise RuntimeError(f"invalid {field} for {task_id}")
    for field in ("P_rationale", "D_rationale"):
        if not isinstance(record.get(field), str) or not record[field].strip():
            raise RuntimeError(f"missing {field} for {task_id}")


def parse_reviewer_spec(value: str) -> tuple[str, str]:
    reviewer_id, separator, model = value.partition(":")
    if not separator or not SAFE_ID.fullmatch(reviewer_id) or not model.strip():
        raise argparse.ArgumentTypeError(
            "reviewer must use the path-safe REVIEWER_ID:MODEL form"
        )
    return reviewer_id, model.strip()


def reviewer_specs_for(args: argparse.Namespace) -> tuple[tuple[str, str], ...]:
    supplied = getattr(args, "reviewers", None)
    if supplied is None:
        return DEFAULT_REVIEWERS
    try:
        specs = []
        for item in supplied:
            if isinstance(item, tuple) and len(item) == 2:
                item = f"{item[0]}:{item[1]}"
            if not isinstance(item, str):
                raise argparse.ArgumentTypeError(
                    "reviewer must use the path-safe REVIEWER_ID:MODEL form"
                )
            specs.append(parse_reviewer_spec(item))
        normalized = tuple(specs)
    except (argparse.ArgumentTypeError, ValueError) as exc:
        raise RuntimeError(str(exc)) from exc
    if len(normalized) != 2:
        raise RuntimeError("exactly two --reviewer REVIEWER_ID:MODEL values are required")
    if len({reviewer_id for reviewer_id, _ in normalized}) != len(normalized):
        raise RuntimeError("reviewer IDs must be distinct")
    return normalized


def tasks_for(args: argparse.Namespace) -> tuple[str, ...]:
    supplied = getattr(args, "tasks", None)
    tasks = tuple(supplied) if supplied is not None else TASKS
    if not tasks:
        raise RuntimeError("at least one task is required")
    if any(not SAFE_ID.fullmatch(task_id) for task_id in tasks):
        raise RuntimeError("task IDs must be path-safe names")
    if len(set(tasks)) != len(tasks):
        raise RuntimeError("task IDs must be unique")
    return tasks


def input_bindings(
    skillsbench_root: Path,
    materials: Path,
    p_pool: Path,
    tasks: tuple[str, ...],
    *,
    explicit_p_pool: bool,
) -> dict[str, Any]:
    d_pool = materials / "candidate_pool" / "D"
    p_task_hashes: dict[str, str] = {}
    d_task_hashes: dict[str, str] = {}
    task_contract_hashes: dict[str, str] = {}
    official_skill_hashes: dict[str, str] = {}
    for task_id in tasks:
        task_root = skillsbench_root / "tasks" / task_id
        task_contract = task_root / "task.md"
        if not task_contract.is_file():
            raise RuntimeError(f"task contract is missing for {task_id}")
        p_task_hashes[task_id] = sha256_tree(p_pool / task_id / "skills")
        d_task_hashes[task_id] = sha256_tree(d_pool / task_id / "skills")
        official_skill_hashes[task_id] = sha256_tree(
            task_root / "environment" / "skills"
        )
        task_contract_hashes[task_id] = sha256_file(task_contract)
    return {
        "tasks": list(tasks),
        "effective_P_pool": {
            "source": "--p-pool" if explicit_p_pool else "materials/candidate_pool/P",
            "tree_sha256": sha256_tree(p_pool),
            "task_skills_sha256": p_task_hashes,
        },
        "D_pool": {
            "source": "materials/candidate_pool/D",
            "tree_sha256": sha256_tree(d_pool),
            "task_skills_sha256": d_task_hashes,
        },
        "skillsbench_public_inputs": {
            "task_contract_sha256": task_contract_hashes,
            "official_skills_sha256": official_skill_hashes,
        },
    }


def run(args: argparse.Namespace) -> dict[str, Any]:
    tasks = tasks_for(args)
    reviewer_specs = reviewer_specs_for(args)
    supplied_p_pool = getattr(args, "p_pool", None)
    p_pool = supplied_p_pool or args.materials / "candidate_pool" / "P"
    bindings = input_bindings(
        args.skillsbench_root,
        args.materials,
        p_pool,
        tasks,
        explicit_p_pool=supplied_p_pool is not None,
    )
    api_key, base_url = load_credentials(args.api_document)
    all_records: list[dict[str, Any]] = []
    raw_dir = args.output.parent / "blind_annotation_raw"
    for reviewer_id, model in reviewer_specs:
        reviewer_records: list[dict[str, Any]] = []
        for task_id in tasks:
            record = request_label(
                base_url,
                api_key,
                model,
                prompt_for(task_id, args.skillsbench_root, args.materials, p_pool),
            )
            validate_record(record, task_id)
            public_record = {
                "reviewer_id": reviewer_id,
                "task_id": task_id,
                "P_label": record["P_label"],
                "D_label": record["D_label"],
                "P_rationale": record["P_rationale"],
                "D_rationale": record["D_rationale"],
                "reviewed_at": utc_now(),
                "model": model,
                "outcome_access": "prohibited",
                "P_skills_sha256": bindings["effective_P_pool"][
                    "task_skills_sha256"
                ][task_id],
            }
            reviewer_records.append(public_record)
            all_records.append(public_record)
        atomic_json(
            raw_dir / f"{reviewer_id}.json",
            {
                "outcome_access": "prohibited",
                "input_bindings": bindings,
                "records": reviewer_records,
            },
        )
    payload = {
        "schema_version": "skillsbench-candidate-blind-labels-v1",
        "created_at": utc_now(),
        "outcome_access": "prohibited",
        "models": [model for _, model in reviewer_specs],
        "reviewers": [
            {"reviewer_id": reviewer_id, "model": model}
            for reviewer_id, model in reviewer_specs
        ],
        "input_bindings": bindings,
        "records": all_records,
    }
    atomic_json(args.output, payload)
    return payload


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--materials",
        type=Path,
        default=Path("research/workflow_runs/skillsbench_candidate_validation_sol/materials_v1"),
    )
    parser.add_argument(
        "--skillsbench-root", type=Path, default=Path(r"D:\a_work\gitee\skillsbench")
    )
    parser.add_argument(
        "--p-pool",
        type=Path,
        help="effective P pool root; defaults to MATERIALS/candidate_pool/P",
    )
    parser.add_argument(
        "--tasks",
        nargs="+",
        default=list(TASKS),
        metavar="TASK_ID",
        help="task IDs to annotate (default: the original four-task screen)",
    )
    parser.add_argument(
        "--reviewer",
        dest="reviewers",
        action="append",
        type=parse_reviewer_spec,
        metavar="REVIEWER_ID:MODEL",
        help="reviewer identity and model; provide exactly twice to override defaults",
    )
    parser.add_argument(
        "--api-document",
        type=Path,
        default=Path(r"C:\Users\Z\Desktop\论文\SelfPaper\LLMAPIDocument\DeepSeek大模型接口说明文档.md"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("research/workflow_runs/skillsbench_candidate_validation_sol/materials_v1/blind_labels.json"),
    )
    args = parser.parse_args(argv)
    if args.reviewers is not None and len(args.reviewers) != 2:
        parser.error("exactly two --reviewer REVIEWER_ID:MODEL values are required")
    return args


def main() -> int:
    payload = run(parse_args())
    print(json.dumps({"records": len(payload["records"]), "models": payload["models"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
