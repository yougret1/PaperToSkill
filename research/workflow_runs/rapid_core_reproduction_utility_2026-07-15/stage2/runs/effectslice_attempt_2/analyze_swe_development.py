from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any


RUN_ROOT = Path(__file__).resolve().parent

CURRENT_HIDDEN_BUDGET_SCAFFOLD_SHA256 = (
    "903785b3c7758109279f7b4a8c9ceed62a8543cb020d6ec6175055f636a3eda2"
)

KNOWN_HARNESS_EXCLUSIONS = {
    "swe-t2:dev:aci:gpt56:bf:001": {
        "reason": "pre_fix_aci_line_endings",
        "evidence": [
            "tests/test_aci_workspace.py",
            "experiment_results/swe_t2_aci_harness_diagnostic/line-ending-fix/candidate.patch",
            "experiment_results/swe_t2_aci_gpt56_bf_002/run_report.json",
        ],
    }
}


def _finite_score(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    score = float(value)
    return score if math.isfinite(score) else None


def _result_actions(result: dict[str, Any]) -> tuple[str | None, ...]:
    actions = result.get("actions", [])
    return tuple(action if isinstance(action, str) else None for action in actions)


def _effective_score(result: dict[str, Any]) -> tuple[float | None, bool]:
    raw_score = _finite_score(result.get("task_score"))
    if result.get("status") == "scored" and raw_score is not None:
        return raw_score, False
    actions = _result_actions(result)
    statuses = tuple(result.get("observation_statuses", []))
    scorer_score = _finite_score(result.get("last_scorer_task_score"))
    if (
        result.get("terminal_reason") == "action_budget_exhausted"
        and actions
        and actions[-1] == "test"
        and statuses
        and statuses[-1] == "scored"
        and result.get("diff_present") is True
        and scorer_score is not None
    ):
        return scorer_score, True
    return None, False


def classify_bundle(
    bundle: dict[str, Any],
    *,
    delta_min: float,
    harness_exclusion: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if not math.isfinite(delta_min) or delta_min < 0:
        raise ValueError("delta_min must be finite and nonnegative")

    pair_id = str(bundle["pair_id"])
    results = bundle.get("results", {})
    base = {
        "pair_id": pair_id,
        "model_family": bundle.get("model_family"),
        "model_alias": bundle.get("model_alias"),
        "wire_api": bundle.get("wire_api"),
        "conditions": sorted(results),
        "evidence_level": "development",
        "eligibility_effect": None,
        "meets_delta_min": None,
        "identical_candidate_patches": None,
        "score_normalization_applied": [],
        "usable_for_scientific_claim": False,
        "condition_results": results,
    }

    if harness_exclusion is not None:
        return {
            **base,
            "classification": "harness_failure",
            "classification_reason": str(harness_exclusion["reason"]),
            "classification_evidence": list(harness_exclusion.get("evidence", [])),
        }

    if set(results) != {"B", "F"}:
        return {
            **base,
            "classification": "unsupported_bundle_shape",
            "classification_reason": "eligibility analysis requires exactly B and F",
            "classification_evidence": [],
        }

    base_result = results["B"]
    full_result = results["F"]
    base_score, base_normalized = _effective_score(base_result)
    full_score, full_normalized = _effective_score(full_result)
    score_normalization_applied = [
        condition
        for condition, normalized in (("B", base_normalized), ("F", full_normalized))
        if normalized
    ]
    if base_score is not None and full_score is not None:
        effect = full_score - base_score
        patches = (
            base_result.get("candidate_patch_sha256"),
            full_result.get("candidate_patch_sha256"),
        )
        identical_patches = all(isinstance(item, str) and item for item in patches) and (
            patches[0] == patches[1]
        )
        eligible = effect >= delta_min
        return {
            **base,
            "classification": (
                "full_artifact_eligible" if eligible else "full_artifact_ineligible"
            ),
            "classification_reason": (
                "observed development F-B meets delta_min"
                if eligible
                else "observed development F-B is below delta_min"
            ),
            "classification_evidence": [],
            "eligibility_effect": effect,
            "meets_delta_min": eligible,
            "identical_candidate_patches": identical_patches,
            "score_normalization_applied": score_normalization_applied,
        }

    exhausted = all(
        result.get("terminal_reason") == "action_budget_exhausted"
        for result in (base_result, full_result)
    )
    terminal_actions = {"edit", "test", "submit"}
    no_terminal_action = all(
        terminal_actions.isdisjoint(action for action in _result_actions(result) if action)
        for result in (base_result, full_result)
    )
    if (
        exhausted
        and no_terminal_action
        and bundle.get("action_budget_visible_to_model") is False
    ):
        return {
            **base,
            "classification": "inconclusive_action_horizon",
            "classification_reason": (
                "both conditions exhausted a model-hidden action horizon before edit, test, or submit"
            ),
            "classification_evidence": [
                "pair_manifest.conditions.*.max_actions",
                "run_result.turns",
                "common_scaffold_sha256",
            ],
        }

    return {
        **base,
        "classification": "execution_failure",
        "classification_reason": "bundle did not produce a comparable scored B/F pair",
        "classification_evidence": [],
    }


def load_bundles(run_root: Path) -> list[dict[str, Any]]:
    root = Path(run_root).resolve()
    bundles = []
    pattern = "swe_t2_aci_*/pair_manifest.json"
    for manifest_path in sorted((root / "experiment_results").glob(pattern)):
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        results = {}
        for condition in sorted(manifest.get("results", {})):
            result_path = manifest_path.parent / condition / "run_result.json"
            if not result_path.is_file():
                continue
            run_result = json.loads(result_path.read_text(encoding="utf-8"))
            turns = run_result.get("turns", [])
            scorer_metrics = run_result.get("scorer_metrics", [])
            last_scorer_metric = scorer_metrics[-1] if scorer_metrics else {}
            diff_text = str(run_result.get("diff_text", ""))
            results[condition] = {
                "status": run_result.get("status"),
                "terminal_reason": run_result.get("terminal_reason"),
                "submitted": run_result.get("submitted"),
                "task_score": run_result.get("task_score"),
                "candidate_patch_sha256": hashlib.sha256(diff_text.encode("utf-8")).hexdigest(),
                "diff_present": bool(diff_text),
                "actions_used": run_result.get("state", {}).get("max_actions")
                if not turns
                else len(turns),
                "actions": [
                    turn.get("action", {}).get("action")
                    if isinstance(turn.get("action"), dict)
                    else None
                    for turn in turns
                ],
                "observation_statuses": [
                    turn.get("observation_status") for turn in turns
                ],
                "input_tokens": run_result.get("input_tokens"),
                "output_tokens": run_result.get("output_tokens"),
                "transport_attempts": run_result.get("transport_attempts"),
                "last_scorer_task_score": last_scorer_metric.get("task_score"),
                "last_scorer_success": last_scorer_metric.get("success"),
                "run_result_path": result_path.relative_to(root).as_posix(),
            }
        scaffold_sha256 = manifest.get("common_scaffold_sha256")
        explicit_budget_visibility = manifest.get("action_budget_visible_to_model")
        bundles.append(
            {
                "pair_id": manifest["pair_id"],
                "model_family": manifest.get("model_family"),
                "model_alias": manifest.get("model_alias"),
                "wire_api": manifest.get("wire_api"),
                "common_scaffold_sha256": scaffold_sha256,
                "action_budget_visible_to_model": (
                    explicit_budget_visibility
                    if isinstance(explicit_budget_visibility, bool)
                    else (
                        False
                        if scaffold_sha256 == CURRENT_HIDDEN_BUDGET_SCAFFOLD_SHA256
                        else None
                    )
                ),
                "results": results,
                "manifest_path": manifest_path.relative_to(root).as_posix(),
            }
        )
    return bundles


def summarize_bundles(
    bundles: list[dict[str, Any]],
    *,
    delta_min: float,
) -> dict[str, Any]:
    rows = [
        classify_bundle(
            bundle,
            delta_min=delta_min,
            harness_exclusion=KNOWN_HARNESS_EXCLUSIONS.get(str(bundle["pair_id"])),
        )
        for bundle in bundles
    ]
    classifications = {}
    for row in rows:
        classification = row["classification"]
        classifications[classification] = classifications.get(classification, 0) + 1

    eligible_rows = [row for row in rows if row["classification"] == "full_artifact_eligible"]
    ineligible_rows = [
        row for row in rows if row["classification"] == "full_artifact_ineligible"
    ]
    if eligible_rows:
        disposition = "development_eligibility_signal_only"
    elif ineligible_rows:
        disposition = "abstain_full_artifact_ineligible"
    else:
        disposition = "inconclusive_no_valid_scored_pair"

    return {
        "schema_version": "effectslice-swe-development-summary.v1",
        "evidence_boundary": (
            "Development bundles only. Harness exclusions, ineligibility, and inconclusive "
            "runs cannot establish EffectSlice effectiveness or a model ranking."
        ),
        "thresholds": {"delta_min": delta_min},
        "bundle_count": len(rows),
        "classification_counts": classifications,
        "bundles": rows,
        "task_disposition": disposition,
        "selected_development_candidate": None,
        "run_slice_or_deletion_neighbors": False,
        "scientific_claim_ready": False,
    }


def write_summary(run_root: Path, output_json: Path, output_md: Path) -> dict[str, Any]:
    summary = summarize_bundles(load_bundles(run_root), delta_min=0.01)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    lines = [
        "# SWE-T2 Development Bundle Audit",
        "",
        "Evidence boundary: development only; no scientific effectiveness or model-ranking claim.",
        "",
        f"- Bundles audited: {summary['bundle_count']}",
        f"- Task disposition: {summary['task_disposition']}",
        f"- Run slice/deletion neighbors: {summary['run_slice_or_deletion_neighbors']}",
        f"- Scientific claim ready: {summary['scientific_claim_ready']}",
        "",
        "| Pair | Model | Classification | F-B | Same patch |",
        "| --- | --- | --- | ---: | --- |",
    ]
    for row in summary["bundles"]:
        effect = row["eligibility_effect"]
        rendered_effect = "n/a" if effect is None else f"{effect:.6f}"
        lines.append(
            f"| {row['pair_id']} | {row['model_alias']} | {row['classification']} | "
            f"{rendered_effect} | {row['identical_candidate_patches']} |"
        )
    lines.append("")
    output_md.write_text("\n".join(lines), encoding="utf-8")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit SWE-T2 ACI development bundles")
    parser.add_argument("--run-root", type=Path, default=RUN_ROOT)
    parser.add_argument(
        "--output-json",
        type=Path,
        default=RUN_ROOT / "derived" / "swe_t2_development_summary.json",
    )
    parser.add_argument(
        "--output-md",
        type=Path,
        default=RUN_ROOT / "derived" / "swe_t2_development_summary.md",
    )
    args = parser.parse_args()
    summary = write_summary(args.run_root, args.output_json, args.output_md)
    print(
        json.dumps(
            {
                "bundle_count": summary["bundle_count"],
                "task_disposition": summary["task_disposition"],
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
