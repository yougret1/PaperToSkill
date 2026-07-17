from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

from scipy.stats import beta


RUN_ROOT = Path(__file__).resolve().parent
FINAL_SCORE_TERMINALS = {
    "submitted",
    "action_budget_exhausted_after_scored_test",
    "action_budget_exhausted_after_final_score",
}


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


def _finite_binary_case_scores(value: Any) -> list[float] | None:
    if not isinstance(value, list):
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


def _condition_has_final_score(
    result: dict[str, Any],
    *,
    harness_protocol_version: str,
) -> bool:
    terminal = result.get("terminal_reason")
    if result.get("status") != "scored" or terminal not in FINAL_SCORE_TERMINALS:
        return False
    if terminal == "action_budget_exhausted_after_scored_test":
        return (
            result.get("last_action") == "test"
            and result.get("last_observation_status") == "scored"
        )
    if terminal == "action_budget_exhausted_after_final_score":
        return harness_protocol_version == "effectslice-toolformer-filter-aci.v2"
    return result.get("last_action") == "submit"


def classify_eligibility_bundle(
    bundle: dict[str, Any],
    *,
    delta_min: float,
    alpha: float,
    minimum_prevalence: float,
    minimum_pairs: int,
) -> dict[str, Any]:
    if not math.isfinite(delta_min) or delta_min < 0:
        raise ValueError("delta_min must be finite and nonnegative")
    if not math.isfinite(minimum_prevalence) or not 0 < minimum_prevalence <= 1:
        raise ValueError("minimum_prevalence must lie in (0, 1]")
    if isinstance(minimum_pairs, bool) or not isinstance(minimum_pairs, int) or minimum_pairs < 1:
        raise ValueError("minimum_pairs must be a positive integer")
    results = bundle.get("results", {})
    base = {
        "pair_id": str(bundle.get("pair_id", "")),
        "model_family": bundle.get("model_family"),
        "case_block": bundle.get("case_block"),
        "harness_protocol_version": bundle.get("harness_protocol_version"),
        "evidence_level": "eligibility",
        "beneficial_cases": None,
        "total_cases": None,
        "aggregate_effect": None,
        "one_sided_cp_lower": None,
        "proceed_to_discovery": False,
        "usable_for_scientific_claim": False,
    }
    if bundle.get("case_block") != "eligibility" or set(results) != {"B", "F"}:
        return {**base, "classification": "unsupported_bundle_shape"}
    if any(
        result.get("terminal_reason") == "provider_error"
        for result in results.values()
    ):
        return {**base, "classification": "provider_failure"}

    harness = str(bundle.get("harness_protocol_version", ""))
    if not all(
        _condition_has_final_score(result, harness_protocol_version=harness)
        for result in results.values()
    ):
        if any(
            result.get("terminal_reason") == "action_budget_exhausted"
            and result.get("last_action") != "test"
            for result in results.values()
        ):
            return {**base, "classification": "unscored_final_state"}
        return {**base, "classification": "execution_failure"}

    base_scores = _finite_binary_case_scores(
        results["B"].get("final_metric", {}).get("case_scores")
    )
    full_scores = _finite_binary_case_scores(
        results["F"].get("final_metric", {}).get("case_scores")
    )
    if (
        base_scores is None
        or full_scores is None
        or len(base_scores) != minimum_pairs
        or len(full_scores) != minimum_pairs
    ):
        return {**base, "classification": "invalid_case_vector"}

    effects = [full - no_artifact for no_artifact, full in zip(base_scores, full_scores)]
    beneficial = sum(effect >= delta_min for effect in effects)
    lower = one_sided_cp_lower(beneficial, minimum_pairs, alpha=alpha)
    aggregate_effect = sum(effects) / minimum_pairs
    eligible = lower >= minimum_prevalence and aggregate_effect >= delta_min
    return {
        **base,
        "classification": (
            "eligible_full_artifact" if eligible else "ineligible_full_artifact"
        ),
        "beneficial_cases": beneficial,
        "total_cases": minimum_pairs,
        "aggregate_effect": aggregate_effect,
        "one_sided_cp_lower": lower,
        "proceed_to_discovery": eligible,
    }


def summarize_eligibility_bundles(
    bundles: list[dict[str, Any]],
    *,
    delta_min: float,
    alpha: float,
    minimum_prevalence: float,
    minimum_pairs: int,
) -> dict[str, Any]:
    rows = [
        classify_eligibility_bundle(
            bundle,
            delta_min=delta_min,
            alpha=alpha,
            minimum_prevalence=minimum_prevalence,
            minimum_pairs=minimum_pairs,
        )
        for bundle in bundles
    ]
    counts: dict[str, int] = {}
    for row in rows:
        classification = row["classification"]
        counts[classification] = counts.get(classification, 0) + 1
    eligible = sorted(
        (row for row in rows if row["classification"] == "eligible_full_artifact"),
        key=lambda row: row["pair_id"],
    )
    valid_ineligible = [
        row for row in rows if row["classification"] == "ineligible_full_artifact"
    ]
    if eligible:
        disposition = "proceed_to_discovery"
        selected = eligible[0]["pair_id"]
    elif valid_ineligible:
        disposition = "abstain_full_artifact_ineligible"
        selected = None
    else:
        disposition = "inconclusive_no_valid_eligibility_pair"
        selected = None
    return {
        "schema_version": "effectslice-toolformer-filter-eligibility-summary.v1",
        "evidence_boundary": (
            "Frozen eligibility only. Passing authorizes discovery but is not sealed "
            "confirmation evidence or evidence that EffectSlice is effective."
        ),
        "thresholds": {
            "delta_min": delta_min,
            "alpha": alpha,
            "minimum_beneficial_prevalence": minimum_prevalence,
            "minimum_pairs": minimum_pairs,
        },
        "bundle_count": len(rows),
        "classification_counts": counts,
        "bundles": rows,
        "task_disposition": disposition,
        "selected_eligibility_pair_id": selected,
        "scientific_claim_ready": False,
    }


def load_bundles(run_root: Path) -> list[dict[str, Any]]:
    root = Path(run_root).resolve()
    bundles: list[dict[str, Any]] = []
    for manifest_path in sorted((root / "experiment_results").glob("toolformer_filter_*/pair_manifest.json")):
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("case_block") != "eligibility":
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
                "diff_present": bool(result.get("diff_text")),
                "final_metric": metrics[-1] if metrics else {},
                "run_result_path": result_path.relative_to(root).as_posix(),
            }
        bundles.append(
            {
                "pair_id": manifest.get("pair_id"),
                "model_family": manifest.get("model_family"),
                "case_block": manifest.get("case_block"),
                "harness_protocol_version": manifest.get("harness_protocol_version"),
                "provider_protocol_version": manifest.get("provider_protocol_version"),
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
    summary = summarize_eligibility_bundles(
        load_bundles(run_root),
        delta_min=float(statistics["delta_min"]),
        alpha=float(statistics["alpha_F"]),
        minimum_prevalence=float(statistics["minimum_beneficial_prevalence"]),
        minimum_pairs=int(statistics["minimum_eligibility_pairs"]),
    )
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    lines = [
        "# TOOLFORMER-FILTER Eligibility Audit",
        "",
        "Evidence boundary: frozen eligibility only; confirmation remains sealed.",
        "",
        f"- Bundles: {summary['bundle_count']}",
        f"- Task disposition: {summary['task_disposition']}",
        f"- Selected pair: {summary['selected_eligibility_pair_id']}",
        f"- Scientific claim ready: {summary['scientific_claim_ready']}",
        "",
        "| Pair | Harness | Classification | Beneficial | CP lower |",
        "| --- | --- | --- | ---: | ---: |",
    ]
    for row in summary["bundles"]:
        beneficial = row["beneficial_cases"]
        total = row["total_cases"]
        rendered_count = "n/a" if beneficial is None else f"{beneficial}/{total}"
        lower = row["one_sided_cp_lower"]
        rendered_lower = "n/a" if lower is None else f"{lower:.6f}"
        lines.append(
            f"| {row['pair_id']} | {row['harness_protocol_version']} | "
            f"{row['classification']} | {rendered_count} | {rendered_lower} |"
        )
    lines.append("")
    output_md.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit TOOLFORMER-FILTER eligibility bundles")
    parser.add_argument("--run-root", type=Path, default=RUN_ROOT)
    parser.add_argument(
        "--output-json",
        type=Path,
        default=RUN_ROOT / "derived" / "toolformer_filter_eligibility_summary.json",
    )
    parser.add_argument(
        "--output-md",
        type=Path,
        default=RUN_ROOT / "derived" / "toolformer_filter_eligibility_summary.md",
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
