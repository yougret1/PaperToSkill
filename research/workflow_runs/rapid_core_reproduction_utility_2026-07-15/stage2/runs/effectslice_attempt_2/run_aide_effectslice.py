from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path
from typing import Any


RUN_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = Path(__file__).resolve().parents[6]
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

import run_real_reuse_aide as aide_runner  # noqa: E402


ALLOWED_CONDITIONS = ("B", "F", "S")
PAIR_ROLE_BY_CONDITIONS = {
    ("B", "F"): "eligibility",
    ("B", "S"): "singleton_deletion_neighbor",
    ("F", "S"): "preservation",
    ("B", "F", "S"): "development_triage",
}
NO_SKILL_CONTEXT = (
    "No paper-derived procedural context is supplied for this condition. "
    "Solve the locked task using only the task prompt and the common system scaffold."
)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _full_context_path(project_root: Path) -> Path:
    task_spec = aide_runner.load_json(
        project_root / "benchmarks" / "real_reuse" / "tasks" / "AIDE-T2.json"
    )
    return aide_runner.resolve(
        project_root,
        aide_runner.condition_path(task_spec, "papertoskill"),
    )


def build_prompt(
    project_root: Path,
    condition: str,
    slice_context_path: Path | None = None,
) -> tuple[str, str]:
    if condition not in ALLOWED_CONDITIONS:
        raise ValueError(f"unsupported EffectSlice condition: {condition}")
    root = Path(project_root).resolve()
    manifest = aide_runner.load_json(
        root / "benchmarks" / "real_reuse" / "assets" / "AIDE-T2" / "asset_manifest.json"
    )
    if condition == "B":
        context = NO_SKILL_CONTEXT
    elif condition == "F":
        context = _full_context_path(root).read_text(encoding="utf-8").strip()
    else:
        if slice_context_path is None:
            raise ValueError("S condition requires slice_context_path")
        context = Path(slice_context_path).resolve().read_text(encoding="utf-8").strip()
    task_prompt = aide_runner.resolve(
        root,
        aide_runner.asset_file(manifest, "task_prompt"),
    ).read_text(encoding="utf-8").strip()
    prompt = "\n\n".join(
        [
            "You are running a locked EffectSlice development task. Use only "
            "the procedural context and task prompt below. Do not request or "
            "invent hidden validation labels.",
            "# Procedural Context",
            context,
            "# Locked Task Prompt",
            task_prompt,
            "# Output Contract",
            "Return exactly one Python code block. The script must run from "
            "the provided starter workspace and create `submission.csv` with "
            "`PassengerId` and `Transported` columns.",
        ]
    ).strip() + "\n"
    return prompt, context


def build_pair_manifest(
    *,
    pair_id: str,
    case_id: str,
    seed_block_id: str,
    model_alias: str,
    prompts: dict[str, str],
    contexts: dict[str, str],
    artifact_digest: str,
    authorization_evidence: str,
    comparison_role: str,
) -> dict[str, Any]:
    pair_conditions = tuple(sorted(prompts))
    if pair_conditions not in PAIR_ROLE_BY_CONDITIONS or tuple(sorted(contexts)) != pair_conditions:
        raise ValueError("manifest requires B/F, F/S, singleton B/S, or development B/F/S")
    if comparison_role != PAIR_ROLE_BY_CONDITIONS[pair_conditions]:
        raise ValueError("comparison_role does not match the condition pair")
    if len(artifact_digest) != 64:
        raise ValueError("artifact_digest must be a SHA-256 digest")
    return {
        "schema_version": "effectslice-aide-pair.v1",
        "evidence_boundary": "development_only_not_confirmation",
        "pair_id": pair_id,
        "case_id": case_id,
        "seed_block_id": seed_block_id,
        "task_id": "AIDE-T2",
        "model_alias": model_alias,
        "artifact_sha256": artifact_digest,
        "authorization_evidence": authorization_evidence,
        "comparison_role": comparison_role,
        "same_scaffold": True,
        "conditions": {
            condition: {
                "prompt_sha256": sha256_text(prompts[condition]),
                "context_sha256": sha256_text(contexts[condition]),
                "retry_lineage_id": f"{pair_id}:{condition}",
            }
            for condition in pair_conditions
        },
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def run(args: argparse.Namespace) -> dict[str, Any]:
    root = args.root.resolve()
    prompts_and_contexts = {
        condition: build_prompt(root, condition, args.slice_context)
        for condition in args.condition
    }
    prompts = {condition: value[0] for condition, value in prompts_and_contexts.items()}
    contexts = {condition: value[1] for condition, value in prompts_and_contexts.items()}
    full_context_path = _full_context_path(root)
    manifest = build_pair_manifest(
        pair_id=args.pair_id,
        case_id=args.case_id,
        seed_block_id=args.seed_block_id,
        model_alias=args.model_alias,
        prompts=prompts,
        contexts=contexts,
        artifact_digest=sha256_file(full_context_path),
        authorization_evidence=args.authorization_evidence,
        comparison_role=args.comparison_role,
    )
    write_json(args.pair_manifest, manifest)

    original_builder = aide_runner.build_prompt

    def effect_slice_prompt(_root: Path, task_id: str, condition: str) -> str:
        if task_id != "AIDE-T2":
            raise ValueError("EffectSlice AIDE runner only supports AIDE-T2")
        return prompts[condition]

    aide_runner.build_prompt = effect_slice_prompt
    try:
        rows = [
            aide_runner.run_single(args, "AIDE-T2", condition, args.run_id)
            for condition in args.condition
        ]
    finally:
        aide_runner.build_prompt = original_builder

    scored_rows = [row for row in rows if row.get("status") == "scored"]
    aide_runner.append_jsonl(args.raw_rows_output, scored_rows)
    report = aide_runner.build_report(args, args.run_id, rows)
    aide_runner.write_json(args.output_json, report)
    aide_runner.write_markdown(args.output_md, report)

    manifest["results"] = {
        row["condition"]: {
            "status": row.get("status"),
            "task_score": row.get("task_score"),
            "success": row.get("success"),
            "failure_reason": row.get("failure_reason", ""),
            "transport_attempts": row.get("call_status", {}).get("attempts"),
            "output_path": row.get("output_path", ""),
            "metric_path": row.get("metric_path", ""),
        }
        for row in rows
    }
    write_json(args.pair_manifest, manifest)
    return report


def main() -> int:
    default_output = RUN_ROOT / "experiment_results" / "aide_t2_bf_pair"
    parser = argparse.ArgumentParser(description="Run a paired AIDE-T2 EffectSlice B/F development case")
    parser.add_argument("--root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--condition", action="append", choices=ALLOWED_CONDITIONS, default=[])
    parser.add_argument("--pair-id", required=True)
    parser.add_argument("--case-id", required=True)
    parser.add_argument("--seed-block-id", default="development:001")
    parser.add_argument("--authorization-evidence", default="user-confirmed trusted endpoint")
    parser.add_argument(
        "--comparison-role",
        choices=tuple(sorted(set(PAIR_ROLE_BY_CONDITIONS.values()))),
    )
    parser.add_argument(
        "--slice-context",
        type=Path,
        default=RUN_ROOT / "artifacts" / "aide_t2" / "slice_v0.md",
    )
    parser.add_argument("--model-family", default="GPT-family")
    parser.add_argument("--model-alias", default="gpt-5.6")
    parser.add_argument("--wire-api", choices=aide_runner.WIRE_APIS, default="openai_responses")
    parser.add_argument("--base-url-env", default="EFFECTSLICE_GPT_BASE_URL")
    parser.add_argument("--api-key-env", default="EFFECTSLICE_GPT_API_KEY")
    parser.add_argument("--base-url")
    parser.add_argument("--api-key")
    parser.add_argument("--max-tokens", type=int, default=4000)
    parser.add_argument("--timeout-seconds", type=float, default=240.0)
    parser.add_argument("--score-timeout-seconds", type=float, default=300.0)
    parser.add_argument("--max-attempts", type=int, default=5)
    parser.add_argument("--retry-delay-seconds", type=float, default=2.0)
    parser.add_argument("--anthropic-version", default="2023-06-01")
    parser.add_argument("--fixture-response-dir", type=Path)
    parser.add_argument("--run-id", default="")
    parser.add_argument("--output-dir", type=Path, default=default_output / "runs")
    parser.add_argument("--raw-rows-output", type=Path, default=default_output / "raw_rows.jsonl")
    parser.add_argument("--output-json", type=Path, default=default_output / "run_report.json")
    parser.add_argument("--output-md", type=Path, default=default_output / "run_report.md")
    parser.add_argument("--pair-manifest", type=Path, default=default_output / "pair_manifest.json")
    args = parser.parse_args()

    if not args.condition:
        args.condition = ["B", "F"]
    pair_conditions = tuple(sorted(args.condition))
    if pair_conditions not in PAIR_ROLE_BY_CONDITIONS:
        parser.error("conditions must be B/F, F/S, singleton B/S, or development B/F/S")
    expected_role = PAIR_ROLE_BY_CONDITIONS[pair_conditions]
    if args.comparison_role is None:
        args.comparison_role = expected_role
    elif args.comparison_role != expected_role:
        parser.error(f"comparison role for {pair_conditions} must be {expected_role}")
    args.task = ["AIDE-T2"]
    args.run_id = args.run_id or time.strftime("run_%Y%m%d_%H%M%S")
    report = run(args)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
