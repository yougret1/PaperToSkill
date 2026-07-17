from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any


RUN_ROOT = Path(__file__).resolve().parent
KNOWN_HARNESS_EXCLUSIONS: dict[str, dict[str, Any]] = {
    "toolformer-filter:development:deepseek:bf:001": {
        "classification": "task_contract_failure",
        "reason": (
            "v1 omitted the source-grounded t=0 offset convention and explicit "
            "Boolean-threshold rejection; both conditions were hard-zeroed by the "
            "incidental threshold contract"
        ),
        "evidence": [
            "B: boolean_threshold:accepted",
            "F: boolean_threshold:accepted",
            "F used t=1 for the first future token",
        ],
    }
}


def _finite_score(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    score = float(value)
    return score if math.isfinite(score) else None


def _effective_score(result: dict[str, Any]) -> tuple[float | None, bool]:
    raw_score = _finite_score(result.get("task_score"))
    if result.get("status") == "scored" and raw_score is not None:
        return raw_score, False
    scorer_score = _finite_score(result.get("last_scorer_task_score"))
    if (
        result.get("terminal_reason") == "action_budget_exhausted"
        and result.get("last_action") == "test"
        and result.get("last_observation_status") == "scored"
        and result.get("diff_present") is True
        and scorer_score is not None
    ):
        return scorer_score, True
    return None, False


def classify_bundle(
    bundle: dict[str, Any],
    *,
    delta_min: float,
    primary_model_family: str = "DeepSeek-family",
    harness_exclusion: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if not math.isfinite(delta_min) or delta_min < 0:
        raise ValueError("delta_min must be finite and nonnegative")
    results = bundle.get("results", {})
    base = {
        "pair_id": str(bundle["pair_id"]),
        "model_family": bundle.get("model_family"),
        "model_alias": bundle.get("model_alias"),
        "primary_model_family": primary_model_family,
        "robustness_signal_only": False,
        "wire_api": bundle.get("wire_api"),
        "case_block": bundle.get("case_block", "development"),
        "conditions": sorted(results),
        "evidence_level": "development",
        "eligibility_effect": None,
        "meets_delta_min": None,
        "identical_candidate_patches": None,
        "score_normalization_applied": [],
        "proceed_to_frozen_eligibility": False,
        "usable_for_scientific_claim": False,
        "condition_results": results,
    }
    if harness_exclusion is not None:
        return {
            **base,
            "classification": str(
                harness_exclusion.get("classification", "harness_failure")
            ),
            "classification_reason": str(harness_exclusion["reason"]),
            "classification_evidence": list(harness_exclusion.get("evidence", [])),
        }
    if set(results) != {"B", "F"}:
        return {
            **base,
            "classification": "unsupported_bundle_shape",
            "classification_reason": "development eligibility requires exactly B and F",
            "classification_evidence": [],
        }
    if any(
        result.get("terminal_reason") == "provider_error" for result in results.values()
    ):
        return {
            **base,
            "classification": "provider_failure",
            "classification_reason": "at least one condition ended with provider_error",
            "classification_evidence": [],
        }

    base_score, base_normalized = _effective_score(results["B"])
    full_score, full_normalized = _effective_score(results["F"])
    normalized = [
        condition
        for condition, applied in (("B", base_normalized), ("F", full_normalized))
        if applied
    ]
    if base_score is None or full_score is None:
        return {
            **base,
            "classification": "execution_failure",
            "classification_reason": "bundle did not produce a comparable B/F score pair",
            "classification_evidence": [],
            "score_normalization_applied": normalized,
        }
    effect = full_score - base_score
    eligible = effect >= delta_min
    patches = (
        results["B"].get("candidate_patch_sha256"),
        results["F"].get("candidate_patch_sha256"),
    )
    same_patch = all(isinstance(item, str) and item for item in patches) and (
        patches[0] == patches[1]
    )
    is_primary = bundle.get("model_family") == primary_model_family
    return {
        **base,
        "classification": (
            "positive_development_signal" if eligible else "full_artifact_ineligible"
        ),
        "classification_reason": (
            "development F-B meets delta_min; frozen eligibility is still required"
            if eligible
            else "development F-B is below delta_min"
        ),
        "classification_evidence": [],
        "eligibility_effect": effect,
        "meets_delta_min": eligible,
        "identical_candidate_patches": same_patch,
        "score_normalization_applied": normalized,
        "robustness_signal_only": eligible and not is_primary,
        "proceed_to_frozen_eligibility": eligible and is_primary,
    }


def load_bundles(run_root: Path) -> list[dict[str, Any]]:
    root = Path(run_root).resolve()
    bundles = []
    for manifest_path in sorted(
        (root / "experiment_results").glob("toolformer_filter_*/pair_manifest.json")
    ):
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("case_block") != "development":
            continue
        results = {}
        for condition in sorted(manifest.get("results", {})):
            result_path = manifest_path.parent / condition / "run_result.json"
            if not result_path.is_file():
                continue
            run_result = json.loads(result_path.read_text(encoding="utf-8"))
            turns = run_result.get("turns", [])
            last_turn = turns[-1] if turns else {}
            last_action_record = last_turn.get("action")
            last_action = (
                last_action_record.get("action")
                if isinstance(last_action_record, dict)
                else None
            )
            scorer_metrics = run_result.get("scorer_metrics", [])
            last_scorer = scorer_metrics[-1] if scorer_metrics else {}
            diff_text = str(run_result.get("diff_text", ""))
            results[condition] = {
                "status": run_result.get("status"),
                "terminal_reason": run_result.get("terminal_reason"),
                "task_score": run_result.get("task_score"),
                "success": run_result.get("success"),
                "candidate_patch_sha256": hashlib.sha256(diff_text.encode("utf-8")).hexdigest(),
                "diff_present": bool(diff_text),
                "last_action": last_action,
                "last_observation_status": last_turn.get("observation_status"),
                "last_scorer_task_score": last_scorer.get("task_score"),
                "input_tokens": run_result.get("input_tokens"),
                "output_tokens": run_result.get("output_tokens"),
                "transport_attempts": run_result.get("transport_attempts"),
                "run_result_path": result_path.relative_to(root).as_posix(),
            }
        bundles.append(
            {
                "pair_id": manifest["pair_id"],
                "model_family": manifest.get("model_family"),
                "model_alias": manifest.get("model_alias"),
                "wire_api": manifest.get("wire_api"),
                "case_block": manifest.get("case_block"),
                "results": results,
                "manifest_path": manifest_path.relative_to(root).as_posix(),
            }
        )
    return bundles


def summarize_bundles(
    bundles: list[dict[str, Any]],
    *,
    delta_min: float,
    primary_model_family: str = "DeepSeek-family",
) -> dict[str, Any]:
    rows = [
        classify_bundle(
            bundle,
            delta_min=delta_min,
            primary_model_family=primary_model_family,
            harness_exclusion=KNOWN_HARNESS_EXCLUSIONS.get(str(bundle["pair_id"])),
        )
        for bundle in bundles
    ]
    counts: dict[str, int] = {}
    for row in rows:
        classification = row["classification"]
        counts[classification] = counts.get(classification, 0) + 1
    primary_positive = [
        row
        for row in rows
        if row["model_family"] == primary_model_family
        and row["classification"] == "positive_development_signal"
    ]
    primary_ineligible = [
        row
        for row in rows
        if row["model_family"] == primary_model_family
        and row["classification"] == "full_artifact_ineligible"
    ]
    robustness_positive_families = sorted(
        {
            str(row["model_family"])
            for row in rows
            if row["model_family"] != primary_model_family
            and row["classification"] == "positive_development_signal"
        }
    )
    if primary_positive:
        selected_family = primary_model_family
        disposition = "proceed_to_frozen_eligibility"
    elif primary_ineligible:
        selected_family = None
        disposition = "abstain_primary_full_artifact_ineligible"
    else:
        selected_family = None
        disposition = "inconclusive_primary_no_valid_scored_pair"
    return {
        "schema_version": "effectslice-toolformer-filter-development-summary.v2",
        "evidence_boundary": (
            "Development bundles only. Only a positive signal from the frozen primary "
            "model family authorizes the eligibility block; robustness signals cannot "
            "substitute for it or support a scientific claim."
        ),
        "thresholds": {"delta_min": delta_min},
        "primary_model_family": primary_model_family,
        "bundle_count": len(rows),
        "classification_counts": counts,
        "bundles": rows,
        "task_disposition": disposition,
        "selected_development_model_family": selected_family,
        "robustness_positive_model_families": robustness_positive_families,
        "scientific_claim_ready": False,
    }


def write_summary(run_root: Path, output_json: Path, output_md: Path) -> dict[str, Any]:
    config = json.loads(
        (run_root / "configs" / "experiment_config.json").read_text(encoding="utf-8")
    )
    adapter = config["task_adapters"]["TOOLFORMER-FILTER"]
    summary = summarize_bundles(
        load_bundles(run_root),
        delta_min=float(adapter["development_delta_min"]),
        primary_model_family=str(adapter["primary_model_family"]),
    )
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    lines = [
        "# TOOLFORMER-FILTER Development Audit",
        "",
        "Evidence boundary: development only; frozen eligibility is still required.",
        "",
        f"- Bundles: {summary['bundle_count']}",
        f"- Primary model family: {summary['primary_model_family']}",
        f"- Task disposition: {summary['task_disposition']}",
        f"- Selected model family: {summary['selected_development_model_family']}",
        "- Robustness-only positive families: "
        f"{summary['robustness_positive_model_families']}",
        f"- Scientific claim ready: {summary['scientific_claim_ready']}",
        "",
        "| Pair | Model | Classification | F-B | Same patch |",
        "| --- | --- | --- | ---: | --- |",
    ]
    for row in summary["bundles"]:
        effect = row["eligibility_effect"]
        rendered = "n/a" if effect is None else f"{effect:.6f}"
        lines.append(
            f"| {row['pair_id']} | {row['model_alias']} | {row['classification']} | "
            f"{rendered} | {row['identical_candidate_patches']} |"
        )
    lines.append("")
    output_md.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit TOOLFORMER-FILTER development bundles")
    parser.add_argument("--run-root", type=Path, default=RUN_ROOT)
    parser.add_argument(
        "--output-json",
        type=Path,
        default=RUN_ROOT / "derived" / "toolformer_filter_development_summary.json",
    )
    parser.add_argument(
        "--output-md",
        type=Path,
        default=RUN_ROOT / "derived" / "toolformer_filter_development_summary.md",
    )
    args = parser.parse_args()
    summary = write_summary(args.run_root, args.output_json, args.output_md)
    print(
        json.dumps(
            {
                "bundle_count": summary["bundle_count"],
                "task_disposition": summary["task_disposition"],
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
