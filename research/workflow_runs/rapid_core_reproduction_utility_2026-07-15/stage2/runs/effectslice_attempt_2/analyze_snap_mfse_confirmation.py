from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

from scipy.stats import beta

from analyze_snap_mfse_eligibility import one_sided_cp_lower


RUN_ROOT = Path(__file__).resolve().parent
FINAL_SCORE_TERMINALS = {
    "submitted",
    "action_budget_exhausted_after_scored_test",
    "action_budget_exhausted_after_final_score",
}


def one_sided_cp_upper(violations: int, total: int, *, alpha: float) -> float:
    if isinstance(violations, bool) or not isinstance(violations, int):
        raise ValueError("violations must be an integer")
    if isinstance(total, bool) or not isinstance(total, int) or total < 1:
        raise ValueError("total must be a positive integer")
    if not 0 <= violations <= total:
        raise ValueError("violations must satisfy 0 <= violations <= total")
    if not math.isfinite(alpha) or not 0 < alpha < 1:
        raise ValueError("alpha must lie strictly between zero and one")
    if violations == total:
        return 1.0
    return float(beta.ppf(1.0 - alpha, violations + 1, total - violations))


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


def analyze_confirmation_bundle(
    bundle: dict[str, Any],
    *,
    family: dict[str, Any],
    expected_family_sha256: str,
    delta_min: float,
) -> dict[str, Any]:
    base = {
        "pair_id": str(bundle.get("pair_id", "")),
        "selected_candidate_id": family.get("selected_candidate_id"),
        "classification": "execution_failure",
        "preservation_violations": None,
        "beneficial_cases": None,
        "total_cases": family.get("case_count"),
        "preservation_cp_upper": None,
        "benefit_cp_lower": None,
        "hard_constraints_passed": False,
        "task_local_confirmation_ready": False,
        "general_effectslice_claim_ready": False,
        "scientific_claim_ready": False,
    }
    if bundle.get("confirmation_family_sha256") != expected_family_sha256:
        return {**base, "classification": "confirmation_family_mismatch"}
    if bundle.get("slice_candidate_id") != family.get("selected_candidate_id"):
        return {**base, "classification": "confirmation_candidate_mismatch"}
    results = bundle.get("results", {})
    if bundle.get("case_block") != "confirmation" or set(results) != {"B", "F", "S"}:
        return {**base, "classification": "unsupported_bundle_shape"}
    if any(
        result.get("terminal_reason") == "provider_error"
        for result in results.values()
    ):
        return {**base, "classification": "provider_failure"}
    if not all(_has_final_score(result) for result in results.values()):
        return base
    scores = {
        condition: _case_scores(result.get("final_metric", {}))
        for condition, result in results.items()
    }
    expected_count = int(family["case_count"])
    if any(value is None or len(value) != expected_count for value in scores.values()):
        return {**base, "classification": "invalid_case_vector"}
    base_scores = scores["B"] or []
    full_scores = scores["F"] or []
    slice_scores = scores["S"] or []
    preservation_violations = sum(
        selected != complete for selected, complete in zip(slice_scores, full_scores)
    )
    beneficial = sum(
        selected - no_artifact >= delta_min
        for selected, no_artifact in zip(slice_scores, base_scores)
    )
    alpha = float(family["alpha"])
    preservation_upper = one_sided_cp_upper(
        preservation_violations,
        expected_count,
        alpha=alpha,
    )
    benefit_lower = one_sided_cp_lower(beneficial, expected_count, alpha=alpha)
    slice_metric = results["S"].get("final_metric", {})
    hard_constraints = bool(
        slice_metric.get("contract_passed") is True
        and slice_metric.get("matrix_free_guard_passed") is True
    )
    passed = bool(
        preservation_violations == 0
        and preservation_upper <= float(family["maximum_violation_rate"])
        and benefit_lower >= float(family["minimum_beneficial_prevalence"])
        and hard_constraints
    )
    return {
        **base,
        "classification": (
            "task_local_confirmation_passed"
            if passed
            else "task_local_confirmation_failed"
        ),
        "preservation_violations": preservation_violations,
        "beneficial_cases": beneficial,
        "preservation_cp_upper": preservation_upper,
        "benefit_cp_lower": benefit_lower,
        "hard_constraints_passed": hard_constraints,
        "task_local_confirmation_ready": passed,
    }


def load_bundles(run_root: Path) -> list[dict[str, Any]]:
    root = Path(run_root).resolve()
    bundles: list[dict[str, Any]] = []
    for manifest_path in sorted((root / "experiment_results").glob("snap_mfse_*/pair_manifest.json")):
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("case_block") != "confirmation":
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
                "slice_candidate_id": manifest.get("slice_candidate_id"),
                "confirmation_family_sha256": manifest.get(
                    "confirmation_family_sha256"
                ),
                "manifest_path": manifest_path.relative_to(root).as_posix(),
                "results": results,
            }
        )
    return bundles


def write_summary(run_root: Path, output_json: Path, output_md: Path) -> dict[str, Any]:
    config = json.loads(
        (run_root / "configs" / "experiment_config.json").read_text(encoding="utf-8")
    )
    adapter = config["task_adapters"]["SNAP-MFSE"]
    family_path = run_root / adapter["confirmation_family"]
    family = json.loads(family_path.read_text(encoding="utf-8"))
    family_sha256 = hashlib.sha256(family_path.read_bytes()).hexdigest()
    bundles = load_bundles(run_root)
    matching = [
        bundle
        for bundle in bundles
        if bundle.get("confirmation_family_sha256") == family_sha256
    ]
    if len(matching) == 1:
        result = analyze_confirmation_bundle(
            matching[0],
            family=family,
            expected_family_sha256=family_sha256,
            delta_min=float(config["statistics"]["delta_min"]),
        )
    elif not matching:
        result = {
            "classification": "missing_confirmation_bundle",
            "task_local_confirmation_ready": False,
            "general_effectslice_claim_ready": False,
            "scientific_claim_ready": False,
        }
    else:
        result = {
            "classification": "multiple_confirmation_bundles",
            "task_local_confirmation_ready": False,
            "general_effectslice_claim_ready": False,
            "scientific_claim_ready": False,
        }
    summary = {
        "schema_version": "effectslice-snap-mfse-confirmation-summary.v1",
        "evidence_boundary": (
            "Sealed task-local confirmation. This does not establish general "
            "EffectSlice effectiveness across papers or tasks."
        ),
        "confirmation_family_path": family_path.relative_to(run_root).as_posix(),
        "confirmation_family_sha256": family_sha256,
        "bundle_count": len(bundles),
        "matching_bundle_count": len(matching),
        "result": result,
        "task_local_confirmation_ready": result.get(
            "task_local_confirmation_ready", False
        ),
        "general_effectslice_claim_ready": False,
        "scientific_claim_ready": False,
    }
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    lines = [
        "# SNAP-MFSE Sealed Confirmation Audit",
        "",
        f"- Classification: {result['classification']}",
        f"- Task-local confirmation ready: {summary['task_local_confirmation_ready']}",
        "- General EffectSlice claim ready: False",
        "- Scientific claim ready: False",
    ]
    if "preservation_violations" in result:
        lines.extend(
            [
                f"- Preservation violations: {result['preservation_violations']}",
                f"- Beneficial cases: {result['beneficial_cases']}",
                f"- Preservation CP upper: {result['preservation_cp_upper']:.6f}",
                f"- Benefit CP lower: {result['benefit_cp_lower']:.6f}",
            ]
        )
    lines.append("")
    output_md.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit SNAP-MFSE sealed confirmation")
    parser.add_argument("--run-root", type=Path, default=RUN_ROOT)
    parser.add_argument(
        "--output-json",
        type=Path,
        default=RUN_ROOT / "derived" / "snap_mfse_confirmation_summary.json",
    )
    parser.add_argument(
        "--output-md",
        type=Path,
        default=RUN_ROOT / "derived" / "snap_mfse_confirmation_summary.md",
    )
    args = parser.parse_args()
    summary = write_summary(args.run_root, args.output_json, args.output_md)
    print(
        json.dumps(
            {
                "classification": summary["result"]["classification"],
                "task_local_confirmation_ready": summary[
                    "task_local_confirmation_ready"
                ],
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
