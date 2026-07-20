from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any


RUN_ROOT = Path(__file__).resolve().parent
DEFAULT_PREREGISTRATION = (
    RUN_ROOT / "artifacts" / "confirmation_v5" / "preregistration.json"
)
DEFAULT_RESULTS = RUN_ROOT / "experiment_results" / "confirmation_v5"
DEFAULT_SUMMARY = RUN_ROOT / "derived" / "confirmation_v5" / "analysis.json"
DEFAULT_OUTPUT = RUN_ROOT / "derived" / "confirmation_v5" / "independent_crosscheck.json"
FAMILY_ORDER = ("toolformer_natural",)
CONDITIONS = ("B", "F", "S")
SUCCESS_THRESHOLD = 0.95


def _sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _load_json(path: Path) -> dict[str, Any]:
    source = Path(path)
    if source.is_symlink() or not source.is_file():
        raise ValueError(f"required regular JSON file is missing: {source}")
    payload = json.loads(source.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"JSON root must be an object: {source}")
    return payload


def _public_test_counts(observations: list[dict[str, Any]]) -> tuple[int, int]:
    requests = 0
    passes = 0
    for observation in observations:
        if (observation.get("action") or {}).get("action") != "test":
            continue
        requests += 1
        try:
            message = json.loads(observation.get("message", ""))
        except (TypeError, json.JSONDecodeError):
            message = {}
        if observation.get("status") == "public_tested" and message.get("status") == "passed":
            passes += 1
    return requests, passes


def _condition_result(condition_dir: Path) -> tuple[dict[str, Any], list[dict[str, str]], list[str]]:
    paths = {
        "candidate.patch": condition_dir / "candidate.patch",
        "run_result.json": condition_dir / "run_result.json",
        "transcript.json": condition_dir / "transcript.json",
    }
    for path in paths.values():
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"registered condition output is missing: {path}")

    result = _load_json(paths["run_result.json"])
    if result.get("status") != "scored":
        raise ValueError(f"condition did not terminate with a score: {condition_dir}")
    if result.get("private_score_count") != 1:
        raise ValueError(f"condition does not have exactly one private score: {condition_dir}")
    if result.get("private_feedback_exposed") is not False:
        raise ValueError(f"private feedback was exposed: {condition_dir}")

    scorer_metrics = result.get("scorer_metrics")
    if not isinstance(scorer_metrics, list) or len(scorer_metrics) != 1:
        raise ValueError(f"condition must preserve one scorer metric: {condition_dir}")
    metric = scorer_metrics[0]
    score = float(result["task_score"])
    if not math.isclose(score, float(metric["task_score"]), abs_tol=1e-12):
        raise ValueError(f"top-level and scorer task scores differ: {condition_dir}")
    case_scores = metric.get("case_scores")
    if not isinstance(case_scores, list):
        raise ValueError(f"private case scores are missing: {condition_dir}")
    total_cases = len(case_scores)
    passed_cases = sum(int(value) for value in case_scores)
    if total_cases != 64 or passed_cases != round(score * total_cases):
        raise ValueError(f"private case accounting changed: {condition_dir}")
    operational_success = bool(
        metric.get("contract_passed")
        and metric.get("patch_applied")
        and score >= SUCCESS_THRESHOLD
    )
    if bool(result.get("success")) != operational_success:
        raise ValueError(f"operational success was not reproducible: {condition_dir}")

    observations = result.get("state", {}).get("observations", [])
    turns = result.get("turns", [])
    if not isinstance(observations, list) or not isinstance(turns, list):
        raise ValueError(f"condition trajectory is malformed: {condition_dir}")
    if len(observations) != len(turns):
        raise ValueError(f"provider turns and recorded actions differ: {condition_dir}")
    action_counts = Counter(
        (observation.get("action") or {}).get("action", "invalid")
        for observation in observations
    )
    public_requests, public_passes = _public_test_counts(observations)
    response_ids = [turn.get("provider_response_id") for turn in turns]
    if any(not isinstance(response_id, str) or not response_id for response_id in response_ids):
        raise ValueError(f"condition has a missing provider response ID: {condition_dir}")

    row = {
        "task_score": score,
        "passed_cases": passed_cases,
        "operational_success": operational_success,
        "hard_contract_passed": bool(metric.get("contract_passed")),
        "patch_applied": bool(metric.get("patch_applied")),
        "actions_used": len(observations),
        "action_counts": dict(sorted(action_counts.items())),
        "provider_turns": len(turns),
        "transport_attempts": int(result["transport_attempts"]),
        "input_tokens": int(result["input_tokens"]),
        "output_tokens": int(result["output_tokens"]),
        "public_test_requests": public_requests,
        "public_test_passes": public_passes,
        "terminal_reason": result["terminal_reason"],
        "submitted": bool(result.get("submitted")),
    }
    digests = [
        {"path": path.relative_to(RUN_ROOT).as_posix(), "sha256": _sha256(path)}
        for path in paths.values()
    ]
    return row, digests, response_ids


def _admission_decision(counts: dict[str, int], contract: dict[str, Any]) -> dict[str, Any]:
    checks = {
        "baseline_ceiling": counts["B"] <= int(contract["maximum_baseline_successes"]),
        "full_sufficiency": counts["F"] >= int(contract["minimum_full_successes"]),
        "slice_sufficiency": counts["S"] >= int(contract["minimum_slice_successes"]),
        "slice_shortfall": (
            counts["F"] - counts["S"]
            <= int(contract["maximum_full_minus_slice_success_gap"])
        ),
        "outputs_complete": True,
        "integrity_passed": True,
    }
    return {"checks": checks, "passed": all(checks.values())}


def _compare_summary(crosscheck: dict[str, Any], summary: dict[str, Any]) -> None:
    if summary.get("registered_blocks") != crosscheck["registered_blocks"]:
        raise ValueError("analysis block count disagrees with raw crosscheck")
    if summary.get("registered_condition_runs") != crosscheck["registered_condition_runs"]:
        raise ValueError("analysis condition count disagrees with raw crosscheck")

    expected_families = summary.get("family_summaries", {})
    for key, observed in crosscheck["families"].items():
        expected = expected_families.get(key)
        if expected is None:
            raise ValueError(f"analysis is missing family {key}")
        if expected["operational_success_counts"] != observed["operational_success_counts"]:
            raise ValueError(f"analysis success counts disagree for {key}")
        for condition in CONDITIONS:
            if not math.isclose(
                float(expected["mean_task_score"][condition]),
                float(observed["mean_task_score"][condition]),
                abs_tol=1e-12,
            ):
                raise ValueError(f"analysis mean score disagrees for {key}/{condition}")
        if expected["admission_decision"]["passed"] != observed["admission_decision"]["passed"]:
            raise ValueError(f"analysis admission decision disagrees for {key}")

    if summary.get("natural_candidate_decision", {}).get("passed") != crosscheck[
        "natural_candidate_admitted"
    ]:
        raise ValueError("analysis natural-candidate decision disagrees with raw crosscheck")

    resource = summary["resource_summary"]
    for key in (
        "actions_used",
        "provider_turns",
        "transport_attempts",
        "input_tokens",
        "output_tokens",
        "public_test_requests",
        "public_test_passes",
    ):
        if int(resource[key]) != int(crosscheck["resource_summary"][key]):
            raise ValueError(f"analysis resource total disagrees for {key}")
    if resource["action_counts"] != crosscheck["resource_summary"]["action_counts"]:
        raise ValueError("analysis action counts disagree with raw crosscheck")


def build_crosscheck(
    preregistration_path: Path,
    results_root: Path,
    summary_path: Path,
    output_path: Path,
) -> Path:
    prereg_path = Path(preregistration_path).resolve()
    result_root = Path(results_root).resolve()
    summary_source = Path(summary_path).resolve()
    prereg = _load_json(prereg_path)
    if prereg.get("schema_version") != "effectslice-confirmation-v5-preregistration.v1":
        raise ValueError("unexpected V5 preregistration schema")
    schedule = prereg.get("global_interleaved_schedule", [])
    if len(schedule) != 18 or prereg.get("registered_condition_run_count") != 54:
        raise ValueError("V5 preregistered schedule is incomplete")

    family_runs: dict[str, list[dict[str, Any]]] = {key: [] for key in FAMILY_ORDER}
    resource_totals: Counter[str] = Counter()
    action_totals: Counter[str] = Counter()
    terminal_totals: Counter[str] = Counter()
    breakdown: dict[str, dict[str, Counter[str]]] = {
        family: {condition: Counter() for condition in CONDITIONS}
        for family in FAMILY_ORDER
    }
    raw_digests: list[dict[str, str]] = []
    response_ids: list[str] = []
    seen_blocks: set[tuple[str, str]] = set()

    for block in schedule:
        family = block["family_key"]
        replicate = block["replicate_id"]
        if family not in family_runs or (family, replicate) in seen_blocks:
            raise ValueError("V5 schedule contains an unknown or duplicate block")
        seen_blocks.add((family, replicate))
        block_dir = result_root / family / replicate
        for name in ("pair_manifest.json", "run_report.json"):
            path = block_dir / name
            if path.is_symlink() or not path.is_file():
                raise ValueError(f"registered block output is missing: {path}")
            raw_digests.append(
                {"path": path.relative_to(RUN_ROOT).as_posix(), "sha256": _sha256(path)}
            )

        condition_rows: dict[str, dict[str, Any]] = {}
        for condition in CONDITIONS:
            row, digests, ids = _condition_result(block_dir / condition)
            condition_rows[condition] = row
            raw_digests.extend(digests)
            response_ids.extend(ids)
            action_totals.update(row["action_counts"])
            terminal_totals[row["terminal_reason"]] += 1
            resource_totals.update(
                {
                    "actions_used": row["actions_used"],
                    "provider_turns": row["provider_turns"],
                    "transport_attempts": row["transport_attempts"],
                    "input_tokens": row["input_tokens"],
                    "output_tokens": row["output_tokens"],
                    "public_test_requests": row["public_test_requests"],
                    "public_test_passes": row["public_test_passes"],
                }
            )
            family_condition = breakdown[family][condition]
            family_condition.update(
                {
                    "condition_runs": 1,
                    "actions_used": row["actions_used"],
                    "invalid_actions": row["action_counts"].get("invalid", 0),
                    "transport_attempts": row["transport_attempts"],
                    "extra_transport_attempts": row["transport_attempts"]
                    - row["provider_turns"],
                    "public_test_requests": row["public_test_requests"],
                    "public_test_passes": row["public_test_passes"],
                    "public_test_failures": row["public_test_requests"]
                    - row["public_test_passes"],
                    "budget_exhaustions": int(
                        row["terminal_reason"]
                        == "action_budget_exhausted_after_final_score"
                    ),
                }
            )
        family_runs[family].append(condition_rows)

    if len(response_ids) != resource_totals["provider_turns"]:
        raise ValueError("provider response ID accounting is incomplete")
    if len(response_ids) != len(set(response_ids)):
        raise ValueError("provider response IDs are not globally unique")

    contract = prereg["finite_schedule_contract"]
    families: dict[str, dict[str, Any]] = {}
    for family in FAMILY_ORDER:
        rows = family_runs[family]
        counts = {
            condition: sum(int(row[condition]["operational_success"]) for row in rows)
            for condition in CONDITIONS
        }
        means = {
            condition: sum(float(row[condition]["task_score"]) for row in rows) / len(rows)
            for condition in CONDITIONS
        }
        f_success_s_failure = sum(
            int(row["F"]["operational_success"] and not row["S"]["operational_success"])
            for row in rows
        )
        f_failure_s_success = sum(
            int(not row["F"]["operational_success"] and row["S"]["operational_success"])
            for row in rows
        )
        matches = len(rows) - f_success_s_failure - f_failure_s_success
        family_row: dict[str, Any] = {
            "registered_blocks": len(rows),
            "operational_success_counts": counts,
            "mean_task_score": means,
            "full_minus_slice_success_gap": counts["F"] - counts["S"],
            "paired_success_status": {
                "matches": matches,
                "full_success_slice_failure": f_success_s_failure,
                "full_failure_slice_success": f_failure_s_success,
            },
        }
        family_row["admission_decision"] = _admission_decision(counts, contract)
        families[family] = family_row
    resource_summary = dict(resource_totals)
    resource_summary["action_counts"] = dict(sorted(action_totals.items()))
    resource_summary["extra_transport_attempts"] = (
        resource_summary["transport_attempts"] - resource_summary["provider_turns"]
    )
    resource_summary["provider_conversations"] = 54
    resource_breakdown = {
        family: {
            condition: dict(sorted(values.items()))
            for condition, values in conditions.items()
        }
        for family, conditions in breakdown.items()
    }
    digest_payload = json.dumps(
        sorted(raw_digests, key=lambda row: row["path"]),
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    payload: dict[str, Any] = {
        "schema_version": "effectslice-confirmation-v5-independent-crosscheck.v1",
        "implementation": {
            "path": Path(__file__).resolve().as_posix(),
            "sha256": _sha256(Path(__file__).resolve()),
            "imports_bound_analyzer": False,
            "imports_compatibility_adapter": False,
        },
        "preregistration": {"path": prereg_path.as_posix(), "sha256": _sha256(prereg_path)},
        "registered_blocks": len(seen_blocks),
        "registered_condition_runs": sum(len(rows) * 3 for rows in family_runs.values()),
        "raw_file_count": len(raw_digests),
        "raw_evidence_digest": hashlib.sha256(digest_payload).hexdigest(),
        "validation": {
            "all_outputs_complete": True,
            "all_private_score_counts_equal_one": True,
            "private_feedback_exposed": False,
            "provider_response_ids_unique": True,
            "provider_response_id_count": len(response_ids),
            "private_cases_per_condition": 64,
            "minimum_cases_for_operational_success": math.ceil(64 * SUCCESS_THRESHOLD),
        },
        "registered_gap_check_is_logically_redundant": bool(
            int(contract["registered_blocks"])
            - int(contract["minimum_slice_successes"])
            <= int(contract["maximum_full_minus_slice_success_gap"])
        ),
        "families": families,
        "resource_summary": resource_summary,
        "resource_by_family_condition": resource_breakdown,
        "terminal_reason_counts": dict(sorted(terminal_totals.items())),
        "natural_candidate_admitted": families["toolformer_natural"][
            "admission_decision"
        ]["passed"],
    }
    summary = _load_json(summary_source)
    _compare_summary(payload, summary)
    payload["expected_analysis"] = {
        "path": summary_source.as_posix(),
        "sha256": _sha256(summary_source),
        "all_compared_fields_match": True,
    }

    destination = Path(output_path).resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return destination


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Independently recompute confirmation V5 decisions from raw outputs"
    )
    parser.add_argument("--preregistration", type=Path, default=DEFAULT_PREREGISTRATION)
    parser.add_argument("--results", type=Path, default=DEFAULT_RESULTS)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    output = build_crosscheck(args.preregistration, args.results, args.summary, args.output)
    print(json.dumps({"crosscheck": output.as_posix(), "sha256": _sha256(output)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
