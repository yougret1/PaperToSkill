from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


RUN_ROOT = Path(__file__).resolve().parent


def summarize_pairs(
    pairs: list[dict[str, Any]],
    *,
    candidate_atom_counts: dict[str, int],
    delta_min: float,
    epsilon: float,
    delta_delete: float,
) -> dict[str, Any]:
    for value, label in (
        (delta_min, "delta_min"),
        (epsilon, "epsilon"),
        (delta_delete, "delta_delete"),
    ):
        if not math.isfinite(value) or value < 0:
            raise ValueError(f"{label} must be finite and nonnegative")

    eligibility = []
    preservation: dict[str, list[dict[str, Any]]] = {}
    deletion: dict[str, list[dict[str, Any]]] = {}
    for pair in pairs:
        scores = pair["scores"]
        role = pair["comparison_role"]
        base = {
            "pair_id": pair["pair_id"],
            "scores": scores,
            "input_tokens": pair.get("input_tokens", {}),
            "evidence_level": "development",
        }
        if role == "eligibility":
            effect = float(scores["F"]) - float(scores["B"])
            eligibility.append({**base, "effect": effect, "meets_delta": effect >= delta_min})
        elif role == "preservation":
            candidate_id = str(pair["candidate_id"])
            full_minus_slice = float(scores["F"]) - float(scores["S"])
            preservation.setdefault(candidate_id, []).append(
                {
                    **base,
                    "full_minus_slice": full_minus_slice,
                    "within_margin": full_minus_slice <= epsilon,
                }
            )
        elif role == "singleton_deletion_neighbor":
            candidate_id = str(pair["candidate_id"])
            slice_minus_neighbor = float(scores["S"]) - float(scores["B"])
            deletion.setdefault(candidate_id, []).append(
                {
                    **base,
                    "slice_minus_neighbor": slice_minus_neighbor,
                    "witnessed": slice_minus_neighbor >= delta_delete,
                }
            )
        elif role == "development_triage":
            candidate_id = str(pair["candidate_id"])
            eligibility_effect = float(scores["F"]) - float(scores["B"])
            full_minus_slice = float(scores["F"]) - float(scores["S"])
            slice_minus_neighbor = float(scores["S"]) - float(scores["B"])
            eligibility.append(
                {
                    **base,
                    "effect": eligibility_effect,
                    "meets_delta": eligibility_effect >= delta_min,
                }
            )
            preservation.setdefault(candidate_id, []).append(
                {
                    **base,
                    "full_minus_slice": full_minus_slice,
                    "within_margin": full_minus_slice <= epsilon,
                }
            )
            deletion.setdefault(candidate_id, []).append(
                {
                    **base,
                    "slice_minus_neighbor": slice_minus_neighbor,
                    "witnessed": slice_minus_neighbor >= delta_delete,
                }
            )
        else:
            raise ValueError(f"unknown comparison role: {role}")

    candidates = []
    for candidate_id, atom_count in candidate_atom_counts.items():
        preservation_rows = preservation.get(candidate_id, [])
        deletion_rows = deletion.get(candidate_id, [])
        preservation_observed = bool(preservation_rows) and all(
            row["within_margin"] for row in preservation_rows
        )
        if atom_count == 1:
            neighbor_observed = bool(deletion_rows) and all(row["witnessed"] for row in deletion_rows)
        else:
            neighbor_observed = False
        if preservation_observed and neighbor_observed:
            candidates.append((atom_count, candidate_id))
    selected = min(candidates)[1] if candidates else None
    return {
        "schema_version": "effectslice-aide-development-summary.v1",
        "evidence_boundary": (
            "Adaptive development pairs only. These rows select a candidate but "
            "do not establish eligibility, preservation, necessity, or EffectSlice effectiveness."
        ),
        "thresholds": {
            "delta_min": delta_min,
            "epsilon": epsilon,
            "delta_delete": delta_delete,
        },
        "pair_count": len(pairs),
        "eligibility": eligibility,
        "preservation": preservation,
        "deletion_neighbor": deletion,
        "selected_development_candidate": selected,
        "scientific_claim_ready": False,
    }


def _role_for_conditions(conditions: tuple[str, ...]) -> str:
    mapping = {
        ("B", "F"): "eligibility",
        ("B", "S"): "singleton_deletion_neighbor",
        ("F", "S"): "preservation",
        ("B", "F", "S"): "development_triage",
    }
    if conditions not in mapping:
        raise ValueError(f"unsupported pair conditions: {conditions}")
    return mapping[conditions]


def load_pairs(run_root: Path) -> tuple[list[dict[str, Any]], dict[str, int]]:
    root = Path(run_root).resolve()
    atom_map = json.loads(
        (root / "artifacts" / "aide_t2" / "source_atom_map.json").read_text(encoding="utf-8")
    )
    candidates = atom_map["development_candidates"]
    digest_to_candidate = {
        candidate.get("context_sha256", candidate["sha256"]): candidate_id
        for candidate_id, candidate in candidates.items()
    }
    atom_counts = {
        candidate_id: len(candidate["atom_ids"]) for candidate_id, candidate in candidates.items()
    }
    pairs = []
    for manifest_path in sorted((root / "experiment_results").glob("aide_t2_*/pair_manifest.json")):
        report_path = manifest_path.with_name("run_report.json")
        if not report_path.exists():
            continue
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        report = json.loads(report_path.read_text(encoding="utf-8"))
        rows = {row["condition"]: row for row in report.get("results", [])}
        conditions = tuple(sorted(rows))
        if any(row.get("status") != "scored" or row.get("task_score") is None for row in rows.values()):
            continue
        role = manifest.get("comparison_role") or _role_for_conditions(conditions)
        candidate_id = None
        if "S" in manifest.get("conditions", {}):
            candidate_id = digest_to_candidate.get(
                manifest["conditions"]["S"].get("context_sha256")
            )
        pairs.append(
            {
                "pair_id": manifest["pair_id"],
                "comparison_role": role,
                "candidate_id": candidate_id,
                "scores": {condition: rows[condition]["task_score"] for condition in conditions},
                "input_tokens": {
                    condition: rows[condition].get("call_status", {}).get("usage", {}).get("input_tokens")
                    for condition in conditions
                },
                "total_tokens": {condition: rows[condition].get("tokens") for condition in conditions},
                "time_seconds": {condition: rows[condition].get("time_seconds") for condition in conditions},
                "manifest_path": manifest_path.relative_to(root).as_posix(),
                "report_path": report_path.relative_to(root).as_posix(),
            }
        )
    return pairs, atom_counts


def write_summary(run_root: Path, output_json: Path, output_md: Path) -> dict[str, Any]:
    pairs, atom_counts = load_pairs(run_root)
    summary = summarize_pairs(
        pairs,
        candidate_atom_counts=atom_counts,
        delta_min=0.01,
        epsilon=0.025,
        delta_delete=0.01,
    )
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    lines = [
        "# AIDE-T2 Development Pair Summary",
        "",
        "Evidence boundary: adaptive development only; no PAC or confirmatory claim.",
        "",
        f"- Parsed pairs: {summary['pair_count']}",
        f"- Selected development candidate: {summary['selected_development_candidate']}",
        f"- Scientific claim ready: {summary['scientific_claim_ready']}",
        "",
        "| Role | Candidate | Pair | Contrast | Gate (development only) |",
        "| --- | --- | --- | ---: | --- |",
    ]
    for row in summary["eligibility"]:
        lines.append(
            f"| eligibility | F | {row['pair_id']} | {row['effect']:.6f} | {row['meets_delta']} |"
        )
    for candidate_id, rows in summary["preservation"].items():
        for row in rows:
            lines.append(
                f"| preservation | {candidate_id} | {row['pair_id']} | "
                f"{row['full_minus_slice']:.6f} | {row['within_margin']} |"
            )
    for candidate_id, rows in summary["deletion_neighbor"].items():
        for row in rows:
            lines.append(
                f"| deletion neighbor | {candidate_id} | {row['pair_id']} | "
                f"{row['slice_minus_neighbor']:.6f} | {row['witnessed']} |"
            )
    lines.append("")
    output_md.write_text("\n".join(lines), encoding="utf-8")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Aggregate real AIDE EffectSlice development pairs")
    parser.add_argument("--run-root", type=Path, default=RUN_ROOT)
    parser.add_argument(
        "--output-json",
        type=Path,
        default=RUN_ROOT / "derived" / "aide_t2_development_summary.json",
    )
    parser.add_argument(
        "--output-md",
        type=Path,
        default=RUN_ROOT / "derived" / "aide_t2_development_summary.md",
    )
    args = parser.parse_args()
    summary = write_summary(args.run_root, args.output_json, args.output_md)
    print(json.dumps({"pair_count": summary["pair_count"], "selected": summary["selected_development_candidate"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
