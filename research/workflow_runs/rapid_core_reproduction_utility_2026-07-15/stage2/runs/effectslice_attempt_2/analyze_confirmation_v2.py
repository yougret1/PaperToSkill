from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

from scipy.stats import beta


HYPOTHESIS_IDS = (
    "H_full_benefit_run_level",
    "H_slice_preservation_run_level",
    "H_slice_benefit_run_level",
)

RUN_ROOT = Path(__file__).resolve().parent


def one_sided_cp_lower(successes: int, total: int, *, alpha: float) -> float:
    if isinstance(successes, bool) or not isinstance(successes, int):
        raise ValueError("successes must be an integer")
    if isinstance(total, bool) or not isinstance(total, int) or total < 1:
        raise ValueError("total must be a positive integer")
    if not 0 <= successes <= total:
        raise ValueError("successes must satisfy 0 <= successes <= total")
    if not math.isfinite(alpha) or not 0 < alpha < 1:
        raise ValueError("alpha must lie strictly between zero and one")
    if successes == 0:
        return 0.0
    return float(beta.ppf(alpha, successes, total - successes + 1))


def _finite_score(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    score = float(value)
    if not math.isfinite(score) or not 0.0 <= score <= 1.0:
        return None
    return score


def _condition_audit(
    result: dict[str, Any],
    *,
    task_key: str,
    case_count: int,
    success_threshold: float,
) -> dict[str, Any]:
    violations: list[str] = []
    provider_model_ids: list[str] = []
    provider_response_ids: list[str] = []
    provider_created_values: list[int] = []
    if result.get("private_score_policy") != "final_only":
        violations.append("private_score_policy_not_final_only")
    if result.get("private_feedback_exposed") is not False:
        violations.append("private_feedback_exposed")

    score_count = result.get("private_score_count")
    metrics = result.get("scorer_metrics")
    if (
        isinstance(score_count, bool)
        or not isinstance(score_count, int)
        or score_count not in {0, 1}
        or not isinstance(metrics, list)
        or len(metrics) != score_count
    ):
        violations.append("private_score_count_not_final_only")
        metrics = metrics if isinstance(metrics, list) else []

    for turn in result.get("turns", []):
        if not isinstance(turn, dict):
            violations.append("invalid_transcript_turn")
            continue
        if turn.get("observation_status") == "provider_error":
            continue
        if not isinstance(turn.get("provider_model_id"), str) or not turn.get(
            "provider_model_id"
        ):
            violations.append("missing_provider_model_id")
        else:
            provider_model_ids.append(turn["provider_model_id"])
        if not isinstance(turn.get("provider_response_id"), str) or not turn.get(
            "provider_response_id"
        ):
            violations.append("missing_provider_response_id")
        else:
            provider_response_ids.append(turn["provider_response_id"])
        created = turn.get("provider_created")
        if isinstance(created, bool) or not isinstance(created, int) or created < 0:
            violations.append("missing_provider_created")
        else:
            provider_created_values.append(created)

    metric = metrics[-1] if metrics and isinstance(metrics[-1], dict) else None
    score = None
    hard_constraints_passed = False
    case_checks_valid = False
    if metric is not None:
        score = _finite_score(metric.get("task_score"))
        case_scores = metric.get("case_scores")
        if isinstance(case_scores, list) and len(case_scores) == case_count:
            normalized = [_finite_score(item) for item in case_scores]
            case_checks_valid = all(item in {0.0, 1.0} for item in normalized)
            if case_checks_valid and score is not None:
                empirical_score = sum(item or 0.0 for item in normalized) / case_count
                case_checks_valid = math.isclose(
                    empirical_score,
                    score,
                    rel_tol=0.0,
                    abs_tol=1e-12,
                )
        if not case_checks_valid:
            violations.append("invalid_clustered_case_checks")
        hard_constraints_passed = metric.get("contract_passed") is True
        if task_key == "snap_mfse":
            hard_constraints_passed = bool(
                hard_constraints_passed
                and metric.get("matrix_free_guard_passed") is True
            )

    success = bool(
        metric is not None
        and score is not None
        and score >= success_threshold
        and hard_constraints_passed
        and case_checks_valid
    )
    return {
        "status": result.get("status"),
        "terminal_reason": result.get("terminal_reason"),
        "task_score": score,
        "success": success,
        "hard_constraints_passed": hard_constraints_passed,
        "private_score_count": score_count,
        "private_feedback_exposed": result.get("private_feedback_exposed"),
        "provider_model_ids": sorted(set(provider_model_ids)),
        "provider_response_ids": provider_response_ids,
        "provider_created_values": provider_created_values,
        "integrity_violations": sorted(set(violations)),
    }


def _audit_replicate(
    row: dict[str, Any],
    *,
    family: dict[str, Any],
    expected_family_sha256: str,
    expected_order: list[str],
) -> dict[str, Any]:
    replicate_id = str(row.get("replicate_id", ""))
    violations: list[str] = []
    if row.get("execution_status") == "failed":
        return {
            "replicate_id": replicate_id,
            "classification": "registered_execution_failure",
            "execution_status": "failed",
            "condition_execution_order": None,
            "conditions": {},
            "indicators": {name: False for name in HYPOTHESIS_IDS},
            "hard_constraints_passed": False,
            "integrity_violations": [],
            "error_type": row.get("error_type"),
            "error_message": row.get("error_message"),
        }

    expected_pair_id = f"{family['task_key']}:confirmation-v2:{replicate_id}"
    if row.get("pair_id") != expected_pair_id:
        violations.append("pair_id_mismatch")
    if row.get("case_block") != "confirmation_v2":
        violations.append("case_block_not_confirmation_v2")
    if row.get("selected_candidate_id") != family.get("selected_candidate_id"):
        violations.append("selected_candidate_mismatch")
    if row.get("confirmation_family_sha256") != expected_family_sha256:
        violations.append("confirmation_family_mismatch")
    if row.get("workspace_tree_sha256") != family.get("workspace_tree_sha256"):
        violations.append("workspace_tree_mismatch")
    if row.get("model_alias") != family.get("model_alias"):
        violations.append("model_alias_mismatch")
    if row.get("manifest_private_score_policy") != family.get(
        "private_score_policy"
    ):
        violations.append("manifest_private_score_policy_mismatch")
    if row.get("condition_execution_order") != expected_order:
        violations.append("condition_order_mismatch")
    results = row.get("results")
    if not isinstance(results, dict) or set(results) != {"B", "F", "S"}:
        violations.append("condition_set_mismatch")
        results = {}

    condition_rows: dict[str, dict[str, Any]] = {}
    for condition in ("B", "F", "S"):
        result = results.get(condition)
        if not isinstance(result, dict):
            continue
        condition_rows[condition] = _condition_audit(
            result,
            task_key=str(family["task_key"]),
            case_count=int(family["case_count"]),
            success_threshold=float(family["run_success_threshold"]),
        )
        violations.extend(condition_rows[condition]["integrity_violations"])

    indicators = {name: False for name in HYPOTHESIS_IDS}
    if set(condition_rows) == {"B", "F", "S"} and not violations:
        baseline = condition_rows["B"]
        full = condition_rows["F"]
        selected = condition_rows["S"]
        indicators["H_full_benefit_run_level"] = bool(
            full["success"] and not baseline["success"]
        )
        indicators["H_slice_benefit_run_level"] = bool(
            selected["success"] and not baseline["success"]
        )
        if full["task_score"] is not None and selected["task_score"] is not None:
            indicators["H_slice_preservation_run_level"] = bool(
                selected["success"] == full["success"]
                and abs(selected["task_score"] - full["task_score"])
                <= float(family["maximum_score_gap"])
            )

    hard_constraints_passed = bool(
        set(condition_rows) == {"B", "F", "S"}
        and all(
            condition_rows[condition]["hard_constraints_passed"]
            for condition in ("B", "F", "S")
        )
    )
    return {
        "replicate_id": replicate_id,
        "classification": (
            "audited" if not violations else "integrity_violation"
        ),
        "execution_status": row.get("execution_status", "completed"),
        "condition_execution_order": row.get("condition_execution_order"),
        "conditions": condition_rows,
        "indicators": indicators,
        "hard_constraints_passed": hard_constraints_passed,
        "integrity_violations": sorted(set(violations)),
    }


def analyze_replicates(
    family: dict[str, Any],
    replicates: list[dict[str, Any]],
    *,
    expected_family_sha256: str,
) -> dict[str, Any]:
    if family.get("schema_version") != "effectslice-confirmation-v2-family.v1":
        raise ValueError("invalid confirmation-v2 family")
    if family.get("statistical_unit") != "independent_agent_run":
        raise ValueError("confirmation-v2 statistical unit must be independent_agent_run")
    schedule = family.get("replicate_schedule")
    if not isinstance(schedule, list) or len(schedule) != int(family["replicate_count"]):
        raise ValueError("replicate schedule does not match replicate_count")

    expected = {
        str(item["replicate_id"]): list(item["condition_order"])
        for item in schedule
    }
    by_id: dict[str, list[dict[str, Any]]] = {}
    for row in replicates:
        by_id.setdefault(str(row.get("replicate_id", "")), []).append(row)
    missing = [replicate_id for replicate_id in expected if replicate_id not in by_id]
    duplicates = sorted(
        replicate_id for replicate_id, rows in by_id.items() if len(rows) != 1
    )
    extras = sorted(replicate_id for replicate_id in by_id if replicate_id not in expected)

    audited: list[dict[str, Any]] = []
    for replicate_id, order in expected.items():
        if replicate_id not in by_id:
            audited.append(
                {
                    "replicate_id": replicate_id,
                    "classification": "missing_registered_replicate",
                    "execution_status": "missing",
                    "condition_execution_order": None,
                    "conditions": {},
                    "indicators": {name: False for name in HYPOTHESIS_IDS},
                    "hard_constraints_passed": False,
                    "integrity_violations": [],
                }
            )
            continue
        audited.append(
            _audit_replicate(
                by_id[replicate_id][0],
                family=family,
                expected_family_sha256=expected_family_sha256,
                expected_order=order,
            )
        )

    denominator = int(family["replicate_count"])
    alpha = float(family["alpha"])
    hypotheses = {}
    for hypothesis_id in HYPOTHESIS_IDS:
        successes = sum(
            bool(row["indicators"][hypothesis_id]) for row in audited
        )
        hypotheses[hypothesis_id] = {
            "successes": successes,
            "total": denominator,
            "one_sided_cp_lower": one_sided_cp_lower(
                successes,
                denominator,
                alpha=alpha,
            ),
            "alpha": alpha,
            "minimum_prevalence": float(family["minimum_prevalence"]),
        }

    schedule_complete = not missing and not duplicates and not extras
    integrity_passed = bool(
        not duplicates
        and not extras
        and all(not row["integrity_violations"] for row in audited)
    )
    hard_constraints_passed = all(
        row["hard_constraints_passed"] for row in audited
    )
    prevalence_gate_passed = all(
        item["one_sided_cp_lower"] > item["minimum_prevalence"]
        for item in hypotheses.values()
    )
    admitted = bool(
        schedule_complete
        and integrity_passed
        and hard_constraints_passed
        and prevalence_gate_passed
    )
    condition_audits = [
        condition
        for replicate in audited
        for condition in replicate.get("conditions", {}).values()
    ]
    provider_model_ids = sorted(
        {
            model_id
            for condition in condition_audits
            for model_id in condition.get("provider_model_ids", [])
        }
    )
    provider_response_ids = [
        response_id
        for condition in condition_audits
        for response_id in condition.get("provider_response_ids", [])
    ]
    provider_created_values = [
        created
        for condition in condition_audits
        for created in condition.get("provider_created_values", [])
    ]
    return {
        "schema_version": "effectslice-confirmation-v2-task-summary.v1",
        "task_key": family["task_key"],
        "selected_candidate_id": family["selected_candidate_id"],
        "confirmation_family_sha256": expected_family_sha256,
        "classification": (
            "task_local_admission_passed"
            if admitted
            else "task_local_admission_rejected"
            if schedule_complete
            else "incomplete_registered_schedule"
        ),
        "statistical_unit": "independent_agent_run",
        "condition_run_unit": "independent_provider_conversation",
        "analysis_unit": "matched_BFS_replicate",
        "provider_conversations": denominator * 3,
        "provider_model_ids": provider_model_ids,
        "provider_response_id_count": len(set(provider_response_ids)),
        "provider_turns_with_identity": len(provider_response_ids),
        "provider_created_min": (
            min(provider_created_values) if provider_created_values else None
        ),
        "provider_created_max": (
            max(provider_created_values) if provider_created_values else None
        ),
        "replicate_denominator": denominator,
        "clustered_hidden_checks_per_run": int(family["case_count"]),
        "schedule_complete": schedule_complete,
        "missing_replicate_ids": missing,
        "duplicate_replicate_ids": duplicates,
        "extra_replicate_ids": extras,
        "integrity_passed": integrity_passed,
        "hard_constraints_passed": hard_constraints_passed,
        "prevalence_gate_passed": prevalence_gate_passed,
        "hypotheses": hypotheses,
        "replicates": audited,
        "task_local_admission_ready": admitted,
        "general_effectslice_claim_ready": False,
        "cross_paper_claim_ready": False,
        "human_benefit_claim_ready": False,
        "prior_confirmation_status": "contaminated_development_excluded",
    }


def load_registered_replicates(
    *,
    family_path: Path,
    output_root: Path,
    progress_path: Path,
) -> tuple[dict[str, Any], str, list[dict[str, Any]]]:
    family_file = Path(family_path).resolve()
    family = json.loads(family_file.read_text(encoding="utf-8"))
    family_sha256 = hashlib.sha256(family_file.read_bytes()).hexdigest()
    progress = json.loads(Path(progress_path).read_text(encoding="utf-8"))
    if progress.get("schema_version") != "effectslice-confirmation-v2-progress.v1":
        raise ValueError("invalid confirmation-v2 progress file")
    task_key = str(family["task_key"])
    root = Path(output_root).resolve()
    rows: list[dict[str, Any]] = []
    for record in progress.get("records", []):
        if not isinstance(record, dict) or record.get("task_key") != task_key:
            continue
        replicate_id = str(record.get("replicate_id", ""))
        status = str(record.get("status", ""))
        if status == "failed":
            rows.append(
                {
                    "replicate_id": replicate_id,
                    "execution_status": "failed",
                    "error_type": record.get("error_type"),
                    "error_message": record.get("error_message"),
                }
            )
            continue
        bundle_root = root / task_key / replicate_id
        manifest_path = bundle_root / "pair_manifest.json"
        if not manifest_path.is_file():
            rows.append(
                {
                    "replicate_id": replicate_id,
                    "execution_status": "failed",
                    "error_type": "MissingPairManifest",
                    "error_message": "registered bundle lacks pair_manifest.json",
                }
            )
            continue
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        results: dict[str, Any] = {}
        for condition in ("B", "F", "S"):
            result_path = bundle_root / condition / "run_result.json"
            if result_path.is_file():
                results[condition] = json.loads(
                    result_path.read_text(encoding="utf-8")
                )
        rows.append(
            {
                "replicate_id": replicate_id,
                "execution_status": status,
                "pair_id": manifest.get("pair_id"),
                "case_block": manifest.get("case_block"),
                "selected_candidate_id": manifest.get("slice_candidate_id"),
                "confirmation_family_sha256": manifest.get(
                    "confirmation_family_sha256"
                ),
                "model_alias": manifest.get("model_alias"),
                "manifest_private_score_policy": manifest.get(
                    "private_score_policy"
                ),
                "workspace_tree_sha256": (
                    manifest.get("workspace_state", {}).get("sha256")
                    if isinstance(manifest.get("workspace_state"), dict)
                    else None
                ),
                "condition_execution_order": manifest.get(
                    "condition_execution_order"
                ),
                "manifest_path": manifest_path.as_posix(),
                "results": results,
            }
        )
    return family, family_sha256, rows


def write_task_summary(
    summary: dict[str, Any],
    *,
    output_json: Path,
    output_md: Path,
) -> None:
    json_path = Path(output_json)
    md_path = Path(output_md)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    lines = [
        f"# {summary['task_key']} Confirmation V2",
        "",
        f"- Classification: {summary['classification']}",
        (
            f"- Statistical sample: {summary['replicate_denominator']} "
            "independent API agent runs"
        ),
        (
            f"- Within-run evaluation: {summary['clustered_hidden_checks_per_run']} "
            "clustered hidden checks per run"
        ),
        f"- Schedule complete: {summary['schedule_complete']}",
        f"- Integrity passed: {summary['integrity_passed']}",
        f"- Hard constraints passed: {summary['hard_constraints_passed']}",
        f"- Task-local admission ready: {summary['task_local_admission_ready']}",
        "",
        "| Hypothesis | Successes | Total | One-sided CP lower | Threshold |",
        "|---|---:|---:|---:|---:|",
    ]
    for hypothesis_id in HYPOTHESIS_IDS:
        row = summary["hypotheses"][hypothesis_id]
        lines.append(
            f"| {hypothesis_id} | {row['successes']} | {row['total']} | "
            f"{row['one_sided_cp_lower']:.6f} | {row['minimum_prevalence']:.6f} |"
        )
    lines.extend(
        [
            "",
            "Cases are clustered checks inside a run and are not treated as "
            "independent Bernoulli observations.",
            "",
        ]
    )
    md_path.write_text("\n".join(lines), encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit registered EffectSlice confirmation-v2 runs"
    )
    parser.add_argument("--family", action="append", type=Path, default=[])
    parser.add_argument(
        "--output-root",
        type=Path,
        default=RUN_ROOT / "experiment_results" / "confirmation_v2",
    )
    parser.add_argument(
        "--derived-dir",
        type=Path,
        default=RUN_ROOT / "derived" / "confirmation_v2",
    )
    args = parser.parse_args()
    families = args.family or [
        RUN_ROOT / "artifacts" / "snap_mfse" / "confirmation_v2_family_r2.json",
        RUN_ROOT
        / "artifacts"
        / "toolformer_filter"
        / "confirmation_v2_family_r2.json",
    ]
    progress_path = args.output_root / "confirmation_v2_progress.json"
    outputs = {}
    for family_path in families:
        family, family_sha256, rows = load_registered_replicates(
            family_path=family_path,
            output_root=args.output_root,
            progress_path=progress_path,
        )
        summary = analyze_replicates(
            family,
            rows,
            expected_family_sha256=family_sha256,
        )
        task_key = str(family["task_key"])
        output_json = args.derived_dir / f"{task_key}_confirmation_v2_summary.json"
        output_md = args.derived_dir / f"{task_key}_confirmation_v2_summary.md"
        write_task_summary(summary, output_json=output_json, output_md=output_md)
        outputs[task_key] = {
            "classification": summary["classification"],
            "json": output_json.as_posix(),
            "markdown": output_md.as_posix(),
        }
    print(json.dumps(outputs, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
