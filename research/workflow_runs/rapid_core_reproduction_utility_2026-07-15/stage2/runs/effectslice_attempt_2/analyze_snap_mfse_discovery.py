from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


RUN_ROOT = Path(__file__).resolve().parent
FINAL_SCORE_TERMINALS = {
    "submitted",
    "action_budget_exhausted_after_scored_test",
    "action_budget_exhausted_after_final_score",
}


def _case_scores(metric: dict[str, Any]) -> list[float] | None:
    value = metric.get("case_scores")
    if not isinstance(value, list) or not value:
        return None
    scores: list[float] = []
    for item in value:
        if isinstance(item, bool) or not isinstance(item, (int, float)):
            return None
        score = float(item)
        if not math.isfinite(score) or score not in {0.0, 1.0}:
            return None
        scores.append(score)
    return scores


def _has_final_score(result: dict[str, Any]) -> bool:
    terminal = result.get("terminal_reason")
    if result.get("status") != "scored" or terminal not in FINAL_SCORE_TERMINALS:
        return False
    if terminal == "submitted":
        return result.get("last_action") == "submit"
    if terminal == "action_budget_exhausted_after_scored_test":
        return (
            result.get("last_action") == "test"
            and result.get("last_observation_status") == "scored"
        )
    return True


def _compare_pair(
    bundle: dict[str, Any],
    *,
    reference_condition: str,
    candidate_condition: str,
    epsilon: float,
) -> dict[str, Any]:
    base = {
        "pair_id": str(bundle.get("pair_id", "")),
        "candidate_id": bundle.get("slice_candidate_id"),
        "classification": "execution_failure",
        "effect_gap_F_minus_candidate": None,
        "effect_gap_F_minus_S": None,
        "case_mismatches": None,
        "total_cases": None,
        "contract_passed": None,
        "matrix_free_guard_passed": None,
    }
    results = bundle.get("results", {})
    if set(results) != {reference_condition, candidate_condition}:
        return {**base, "classification": "unsupported_bundle_shape"}
    if any(
        result.get("terminal_reason") == "provider_error"
        for result in results.values()
    ):
        return {**base, "classification": "provider_failure"}
    if not all(_has_final_score(result) for result in results.values()):
        return base
    reference_metric = results[reference_condition].get("final_metric", {})
    candidate_metric = results[candidate_condition].get("final_metric", {})
    reference_scores = _case_scores(reference_metric)
    candidate_scores = _case_scores(candidate_metric)
    if (
        reference_scores is None
        or candidate_scores is None
        or len(reference_scores) != len(candidate_scores)
    ):
        return {**base, "classification": "invalid_case_vector"}
    reference_mean = sum(reference_scores) / len(reference_scores)
    candidate_mean = sum(candidate_scores) / len(candidate_scores)
    gap = reference_mean - candidate_mean
    contract_passed = candidate_metric.get("contract_passed") is True
    guard_passed = candidate_metric.get("matrix_free_guard_passed") is True
    if not contract_passed or not guard_passed:
        classification = "candidate_hard_constraint_failure"
    elif abs(gap) <= epsilon:
        classification = "candidate_equivalent"
    else:
        classification = "candidate_inferior"
    return {
        **base,
        "classification": classification,
        "effect_gap_F_minus_candidate": gap,
        "effect_gap_F_minus_S": gap,
        "case_mismatches": sum(
            reference != candidate
            for reference, candidate in zip(reference_scores, candidate_scores)
        ),
        "total_cases": len(reference_scores),
        "contract_passed": contract_passed,
        "matrix_free_guard_passed": guard_passed,
    }


def summarize_discovery_bundles(
    bundles: list[dict[str, Any]],
    *,
    registry: dict[str, Any],
    epsilon: float,
    delta_delete: float,
) -> dict[str, Any]:
    if not math.isfinite(epsilon) or epsilon < 0:
        raise ValueError("epsilon must be finite and nonnegative")
    if not math.isfinite(delta_delete) or delta_delete < 0:
        raise ValueError("delta_delete must be finite and nonnegative")
    baseline_bundles = [
        bundle
        for bundle in bundles
        if set(bundle.get("results", {})) == {"B", "F"}
    ]
    baseline_row = None
    if baseline_bundles:
        baseline_row = _compare_pair(
            sorted(baseline_bundles, key=lambda row: str(row.get("pair_id", "")))[0],
            reference_condition="F",
            candidate_condition="B",
            epsilon=epsilon,
        )
        baseline_row["neighbor_id"] = "B"

    bundles_by_candidate: dict[str, list[dict[str, Any]]] = {}
    for bundle in bundles:
        candidate_id = bundle.get("slice_candidate_id")
        if isinstance(candidate_id, str):
            bundles_by_candidate.setdefault(candidate_id, []).append(bundle)
    candidate_rows = []
    for candidate in registry.get("candidates", []):
        candidate_id = candidate["candidate_id"]
        candidate_bundles = bundles_by_candidate.get(candidate_id, [])
        if not candidate_bundles:
            continue
        row = _compare_pair(
            sorted(candidate_bundles, key=lambda item: str(item.get("pair_id", "")))[0],
            reference_condition="F",
            candidate_condition="S",
            epsilon=epsilon,
        )
        row["candidate_id"] = candidate_id
        row["retained_atom_ids"] = candidate["retained_atom_ids"]
        row["retained_scc_count"] = candidate["retained_scc_count"]
        candidate_rows.append(row)

    selected_row = next(
        (row for row in candidate_rows if row["classification"] == "candidate_equivalent"),
        None,
    )
    selected_id = selected_row["candidate_id"] if selected_row else None
    deletion_rows: list[dict[str, Any]] = []
    deletion_complete = False
    if selected_id is not None:
        registry_row = next(
            row for row in registry["candidates"] if row["candidate_id"] == selected_id
        )
        rows_by_id = {row["candidate_id"]: row for row in candidate_rows}
        for neighbor in registry_row["deletion_neighbors"]:
            if neighbor.get("condition") == "B":
                source = baseline_row
                neighbor_id = "B"
            else:
                neighbor_id = neighbor["candidate_id"]
                source = rows_by_id.get(neighbor_id)
            if source is None:
                deletion_rows.append(
                    {
                        "neighbor_id": neighbor_id,
                        "removed_atom_id": neighbor["removed_atom_id"],
                        "classification": "missing_neighbor_result",
                        "deletion_failed": False,
                    }
                )
                continue
            gap = source["effect_gap_F_minus_candidate"]
            hard_failure = source["classification"] == "candidate_hard_constraint_failure"
            deletion_failed = bool(
                hard_failure or (gap is not None and gap >= delta_delete)
            )
            deletion_rows.append(
                {
                    "neighbor_id": neighbor_id,
                    "removed_atom_id": neighbor["removed_atom_id"],
                    "classification": source["classification"],
                    "effect_gap_F_minus_neighbor": gap,
                    "deletion_failed": deletion_failed,
                }
            )
        deletion_complete = bool(deletion_rows) and all(
            row["deletion_failed"] for row in deletion_rows
        )

    registered_ids = [row["candidate_id"] for row in registry.get("candidates", [])]
    attempted_ids = [row["candidate_id"] for row in candidate_rows]
    if selected_id is not None and deletion_complete:
        disposition = "candidate_locked_for_confirmation"
    elif selected_id is not None:
        disposition = "candidate_selected_deletion_audit_incomplete"
    elif set(attempted_ids) == set(registered_ids):
        disposition = "abstain_no_equivalent_slice"
    else:
        disposition = "continue_search"
    return {
        "schema_version": "effectslice-snap-mfse-discovery-summary.v1",
        "evidence_boundary": (
            "Discovery and deletion audit only. The selected candidate remains "
            "unconfirmed until sealed confirmation."
        ),
        "thresholds": {"epsilon": epsilon, "delta_delete": delta_delete},
        "registered_candidate_ids": registered_ids,
        "attempted_candidate_ids": attempted_ids,
        "baseline_row": baseline_row,
        "candidate_rows": candidate_rows,
        "selected_candidate_id": selected_id,
        "deletion_rows": deletion_rows,
        "deletion_audit_complete": deletion_complete,
        "task_disposition": disposition,
        "scientific_claim_ready": False,
    }


def load_bundles(run_root: Path) -> list[dict[str, Any]]:
    root = Path(run_root).resolve()
    bundles: list[dict[str, Any]] = []
    for manifest_path in sorted((root / "experiment_results").glob("snap_mfse_*/pair_manifest.json")):
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("case_block") != "discovery":
            continue
        results: dict[str, Any] = {}
        for condition in sorted(manifest.get("results", {})):
            result_path = manifest_path.parent / condition / "run_result.json"
            if not result_path.is_file():
                continue
            result = json.loads(result_path.read_text(encoding="utf-8"))
            turns = result.get("turns", [])
            last_turn = turns[-1] if turns else {}
            action = last_turn.get("action")
            metrics = result.get("scorer_metrics", [])
            results[condition] = {
                "status": result.get("status"),
                "terminal_reason": result.get("terminal_reason"),
                "last_action": action.get("action") if isinstance(action, dict) else None,
                "last_observation_status": last_turn.get("observation_status"),
                "final_metric": metrics[-1] if metrics else {},
                "run_result_path": result_path.relative_to(root).as_posix(),
            }
        bundles.append(
            {
                "pair_id": manifest.get("pair_id"),
                "case_block": manifest.get("case_block"),
                "conditions": sorted(results),
                "slice_candidate_id": manifest.get("slice_candidate_id"),
                "manifest_path": manifest_path.relative_to(root).as_posix(),
                "results": results,
            }
        )
    return bundles


def write_summary(run_root: Path, output_json: Path, output_md: Path) -> dict[str, Any]:
    config = json.loads(
        (run_root / "configs" / "experiment_config.json").read_text(encoding="utf-8")
    )
    statistics = config["statistics"]
    adapter = config["task_adapters"]["SNAP-MFSE"]
    registry = json.loads(
        (run_root / adapter["slice_registry"]).read_text(encoding="utf-8")
    )
    summary = summarize_discovery_bundles(
        load_bundles(run_root),
        registry=registry,
        epsilon=float(statistics["epsilon"]),
        delta_delete=float(statistics["delta_delete"]),
    )
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    lines = [
        "# SNAP-MFSE Discovery Audit",
        "",
        "Evidence boundary: discovery only; confirmation remains sealed.",
        "",
        f"- Task disposition: {summary['task_disposition']}",
        f"- Selected candidate: {summary['selected_candidate_id']}",
        f"- Deletion audit complete: {summary['deletion_audit_complete']}",
        f"- Scientific claim ready: {summary['scientific_claim_ready']}",
        "",
        "| Candidate | Atoms | Classification | F-S | Mismatches |",
        "| --- | ---: | --- | ---: | ---: |",
    ]
    for row in summary["candidate_rows"]:
        gap = row["effect_gap_F_minus_S"]
        rendered_gap = "n/a" if gap is None else f"{gap:.6f}"
        lines.append(
            f"| {row['candidate_id']} | {row['retained_scc_count']} | "
            f"{row['classification']} | {rendered_gap} | {row['case_mismatches']} |"
        )
    lines.append("")
    output_md.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit SNAP-MFSE discovery bundles")
    parser.add_argument("--run-root", type=Path, default=RUN_ROOT)
    parser.add_argument(
        "--output-json",
        type=Path,
        default=RUN_ROOT / "derived" / "snap_mfse_discovery_summary.json",
    )
    parser.add_argument(
        "--output-md",
        type=Path,
        default=RUN_ROOT / "derived" / "snap_mfse_discovery_summary.md",
    )
    args = parser.parse_args()
    summary = write_summary(args.run_root, args.output_json, args.output_md)
    print(
        json.dumps(
            {
                "task_disposition": summary["task_disposition"],
                "selected_candidate_id": summary["selected_candidate_id"],
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
