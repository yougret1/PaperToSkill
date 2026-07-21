from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


RUN_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = Path(__file__).resolve().parents[6]
DEFAULT_V4_SUMMARY = RUN_ROOT / "logs" / "confirmation_v4_summary.json"
DEFAULT_V5_ANALYSIS = RUN_ROOT / "derived" / "confirmation_v5r2" / "analysis.json"
DEFAULT_V5_CROSSCHECK = (
    RUN_ROOT / "derived" / "confirmation_v5r2" / "independent_crosscheck.json"
)
DEFAULT_V4_CROSSCHECK = (
    RUN_ROOT / "derived" / "confirmation_v4" / "independent_crosscheck.json"
)
DEFAULT_OUTPUT_TEX = (
    PROJECT_ROOT / "paper" / "effectslice_aaai" / "generated_results_v3.tex"
)
DEFAULT_MANIFEST = RUN_ROOT / "manuscript" / "generated_results_manifest_v5.json"
DEFAULT_V4_RAW_ROOT = RUN_ROOT / "experiment_results" / "confirmation_v4"
DEFAULT_V5_RAW_ROOT = RUN_ROOT / "experiment_results" / "confirmation_v5r2"
BLOCK_EVIDENCE_FILENAMES = frozenset({"pair_manifest.json", "run_report.json"})
CONDITION_EVIDENCE_FILENAMES = frozenset(
    {"candidate.patch", "run_result.json", "transcript.json"}
)

V4_SCHEMA = "effectslice-stage2-confirmation-summary.v4"
V5_ANALYSIS_SCHEMA = "effectslice-confirmation-v5r2-analysis.v1"
V5_CROSSCHECK_SCHEMA = "effectslice-confirmation-v5r2-independent-crosscheck.v1"
V4_CROSSCHECK_SCHEMA = "effectslice-confirmation-v4-independent-crosscheck.v1"
V4_PREFIXES = {
    "snap_mfse": "SnapReal",
    "toolformer_negative": "ToolformerReal",
    "toolformer_positive": "PlantedPositive",
    "toolformer_identity": "IdentityControl",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _load(path: Path, schema: str, label: str) -> tuple[Path, dict[str, Any]]:
    source = Path(path).resolve()
    payload = json.loads(source.read_text(encoding="utf-8"))
    if payload.get("schema_version") != schema:
        raise ValueError(f"unexpected {label} schema")
    return source, payload


def _macro(name: str, value: Any) -> str:
    return f"\\newcommand{{\\{name}}}{{{value}}}"


def _candidate_decision(value: bool) -> str:
    return "Admit" if value else "Reject"


def _artifact(path: Path) -> dict[str, str]:
    resolved = Path(path).resolve()
    try:
        portable_path = resolved.relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        portable_path = resolved.as_posix()
    return {"path": portable_path, "sha256": _sha256(resolved)}


def _raw_inventory(root: Path) -> list[dict[str, str]]:
    source = Path(root).resolve()
    if source.is_symlink() or not source.is_dir():
        raise ValueError(f"raw evidence root is missing: {source}")
    inventory = []
    for path in source.rglob("*"):
        relative_to_output = path.relative_to(source)
        is_block_file = (
            len(relative_to_output.parts) == 3
            and path.name in BLOCK_EVIDENCE_FILENAMES
        )
        is_condition_file = (
            len(relative_to_output.parts) == 4
            and path.name in CONDITION_EVIDENCE_FILENAMES
        )
        if not is_block_file and not is_condition_file:
            continue
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"raw evidence is missing or linked: {path}")
        inventory.append(
            {
                "run_relative_path": path.relative_to(RUN_ROOT).as_posix(),
                "sha256": _sha256(path),
            }
        )
    return sorted(inventory, key=lambda row: row["run_relative_path"])


def _raw_inventory_digest(inventory: list[dict[str, str]]) -> str:
    normalized = [
        {"path": row["run_relative_path"], "sha256": row["sha256"]}
        for row in inventory
    ]
    payload = json.dumps(normalized, sort_keys=True, separators=(",", ":")).encode(
        "ascii"
    )
    return hashlib.sha256(payload).hexdigest()


def build_paper_results(
    v4_summary_path: Path,
    v5_analysis_path: Path,
    v5_crosscheck_path: Path,
    output_tex: Path,
    manifest_path: Path,
) -> dict[str, str]:
    v4_source, v4 = _load(v4_summary_path, V4_SCHEMA, "V4 summary")
    v5_source, v5 = _load(v5_analysis_path, V5_ANALYSIS_SCHEMA, "V5 analysis")
    cross_source, cross = _load(
        v5_crosscheck_path, V5_CROSSCHECK_SCHEMA, "V5 crosscheck"
    )
    v4_cross_source, v4_cross = _load(
        DEFAULT_V4_CROSSCHECK, V4_CROSSCHECK_SCHEMA, "V4 crosscheck"
    )

    if not cross["expected_analysis"]["all_compared_fields_match"]:
        raise ValueError("V5 crosscheck does not match the bound analysis")
    if cross["expected_analysis"]["sha256"] != _sha256(v5_source):
        raise ValueError("V5 analysis digest does not match the crosscheck")
    if cross["preregistration"]["sha256"] != v5["preregistration_sha256"]:
        raise ValueError("V5 preregistration digest changed")
    if set(cross["families"]) != {"toolformer_natural"}:
        raise ValueError("unexpected V5 family set")
    if cross["families"]["toolformer_natural"]["admission_decision"] != v5[
        "natural_candidate_decision"
    ]:
        raise ValueError("V5 admission decisions differ")

    v4_families = {row["family_key"]: row for row in v4["families"]}
    if set(v4_families) != set(V4_PREFIXES):
        raise ValueError("V4 paper macro family set changed")

    v4_resource = v4["resource_summary"]
    v4_by_family = v4["resource_by_family_condition"]
    v5_family = cross["families"]["toolformer_natural"]
    v5_resource = cross["resource_summary"]
    v5_by_condition = cross["resource_by_family_condition"]["toolformer_natural"]
    values: dict[str, Any] = {
        "VFourRegisteredBlocks": int(v4["registered_blocks"]),
        "VFourProviderConversations": int(v4["registered_condition_runs"]),
        "VFourRegisteredStrata": int(v4["registered_strata"]),
        "VFourRealCandidateCount": 2,
        "VFourRealAdmissions": int(v4["real_candidate_admissions"]),
        "VFourCalibrationDecision": "Pass" if v4["calibration"]["passed"] else "Fail",
        "VFourProviderTurns": int(v4_resource["provider_turns"]),
        "VFourActions": int(v4_resource["actions_used"]),
        "VFourInputTokens": f"{int(v4_resource['input_tokens']):,}",
        "VFourOutputTokens": f"{int(v4_resource['output_tokens']):,}",
        "VFourTransportAttempts": f"{int(v4_resource['transport_attempts']):,}",
        "VFourPublicTestRequests": int(v4_resource["public_test_requests"]),
        "VFourPublicTestPasses": int(v4_resource["public_test_passes"]),
        "VFourPublicTestFailures": int(v4_resource["public_test_failures"]),
        "VFourInvalidActions": int(v4_resource["action_counts"].get("invalid", 0)),
        "VFourExtraTransportAttempts": int(v4_resource["extra_transport_attempts"]),
        "VFourMinimumPassingCases": 61,
        "VFourSubmittedRuns": int(v4["terminal_reason_counts"].get("submitted", 0)),
        "VFourPreregistrationDigest": v4["sources"]["preregistration"]["sha256"],
        "VFourAnalyzerRepair": "Disclosed post-hoc compatibility audit",
        "VFiveRegisteredBlocks": int(cross["registered_blocks"]),
        "VFiveProviderConversations": int(cross["registered_condition_runs"]),
        "VFiveNaturalCandidateCount": 1,
        "VFiveNaturalAdmissions": int(bool(cross["natural_candidate_admitted"])),
        "VFiveProviderTurns": int(v5_resource["provider_turns"]),
        "VFiveActions": int(v5_resource["actions_used"]),
        "VFiveInputTokens": f"{int(v5_resource['input_tokens']):,}",
        "VFiveOutputTokens": f"{int(v5_resource['output_tokens']):,}",
        "VFiveTransportAttempts": int(v5_resource["transport_attempts"]),
        "VFivePublicTestRequests": int(v5_resource["public_test_requests"]),
        "VFivePublicTestPasses": int(v5_resource["public_test_passes"]),
        "VFivePublicTestFailures": int(
            v5_resource["public_test_requests"] - v5_resource["public_test_passes"]
        ),
        "VFiveInvalidActions": int(v5_resource["action_counts"].get("invalid", 0)),
        "VFiveExtraTransportAttempts": int(v5_resource["extra_transport_attempts"]),
        "VFiveSubmittedRuns": int(cross["terminal_reason_counts"].get("submitted", 0)),
        "VFivePreregistrationDigest": cross["preregistration"]["sha256"],
        "VFiveAnalysisDigest": cross["expected_analysis"]["sha256"],
        "VFiveCrosscheckDigest": _sha256(cross_source),
        "VFiveRawEvidenceDigest": cross["raw_evidence_digest"],
        "VFiveRawFileCount": int(cross["raw_file_count"]),
        "VFiveProviderResponseIDs": int(
            cross["validation"]["provider_response_id_count"]
        ),
        "AllRegisteredBlocks": int(v4["registered_blocks"])
        + int(cross["registered_blocks"]),
        "AllProviderConversations": int(v4["registered_condition_runs"])
        + int(cross["registered_condition_runs"]),
        "AllProviderTurns": int(v4_resource["provider_turns"])
        + int(v5_resource["provider_turns"]),
        "AllActions": int(v4_resource["actions_used"])
        + int(v5_resource["actions_used"]),
        "AllInputTokens": f"{int(v4_resource['input_tokens']) + int(v5_resource['input_tokens']):,}",
        "AllOutputTokens": f"{int(v4_resource['output_tokens']) + int(v5_resource['output_tokens']):,}",
        "AllTransportAttempts": f"{int(v4_resource['transport_attempts']) + int(v5_resource['transport_attempts']):,}",
        "AllPublicTestRequests": int(v4_resource["public_test_requests"])
        + int(v5_resource["public_test_requests"]),
        "AllPublicTestPasses": int(v4_resource["public_test_passes"])
        + int(v5_resource["public_test_passes"]),
        "AllPublicTestFailures": int(v4_resource["public_test_failures"])
        + int(v5_resource["public_test_requests"] - v5_resource["public_test_passes"]),
        "NonPlantedCandidateCount": 3,
        "NonPlantedAdmissions": 1,
    }

    for key, prefix in V4_PREFIXES.items():
        values[f"{prefix}PublicTestFailures"] = sum(
            int(v4_by_family[key][condition]["public_test_failures"])
            for condition in "BFS"
        )
        row = v4_families[key]
        counts = row["operational_success_counts"]
        means = row["mean_task_score"]
        values[f"{prefix}Blocks"] = int(row["registered_blocks"])
        for condition in "BFS":
            values[f"{prefix}{condition}Successes"] = int(counts[condition])
            values[f"{prefix}{condition}MeanScore"] = f"{float(means[condition]):.3f}"
        values[f"{prefix}FullSliceGap"] = int(row["full_minus_slice_success_gap"])
        paired = row["paired_success_status"]
        values[f"{prefix}SuccessMatches"] = int(paired["matches"])
        values[f"{prefix}FullSuccessSliceFailure"] = int(
            paired["full_success_slice_failure"]
        )
        values[f"{prefix}FullFailureSliceSuccess"] = int(
            paired["full_failure_slice_success"]
        )
        if key == "toolformer_identity":
            instrument = row["identity_instrumentation"]
            values[f"{prefix}Decision"] = (
                "Pass" if instrument["passed"] else "Fail"
            )
            values[f"{prefix}Matches"] = int(
                instrument["full_slice_success_matches"]
            )
            values[f"{prefix}SuccessGap"] = int(
                instrument["full_slice_success_count_gap"]
            )
        elif key == "toolformer_positive":
            values[f"{prefix}Decision"] = (
                "Pass" if row["admission_decision"]["passed"] else "Fail"
            )
        else:
            values[f"{prefix}Decision"] = _candidate_decision(
                bool(row["admission_decision"]["passed"])
            )

    values["ToolformerNaturalPublicTestFailures"] = sum(
        int(v5_by_condition[condition]["public_test_failures"])
        for condition in "BFS"
    )
    values["ToolformerNaturalBlocks"] = int(v5_family["registered_blocks"])
    for condition in "BFS":
        values[f"ToolformerNatural{condition}Successes"] = int(
            v5_family["operational_success_counts"][condition]
        )
        values[f"ToolformerNatural{condition}MeanScore"] = (
            f"{float(v5_family['mean_task_score'][condition]):.3f}"
        )
    values["ToolformerNaturalFullSliceGap"] = int(
        v5_family["full_minus_slice_success_gap"]
    )
    paired = v5_family["paired_success_status"]
    values["ToolformerNaturalSuccessMatches"] = int(paired["matches"])
    values["ToolformerNaturalFullSuccessSliceFailure"] = int(
        paired["full_success_slice_failure"]
    )
    values["ToolformerNaturalFullFailureSliceSuccess"] = int(
        paired["full_failure_slice_success"]
    )
    values["ToolformerNaturalDecision"] = _candidate_decision(
        bool(v5_family["admission_decision"]["passed"])
    )

    lines = [
        "% Generated from confirmation V4 and V5 analyses; main_v3.tex is final.",
        "% Do not edit empirical values by hand.",
    ]
    lines.extend(_macro(name, value) for name, value in values.items())
    tex = Path(output_tex).resolve()
    tex.parent.mkdir(parents=True, exist_ok=True)
    tex.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")

    v4_raw_inventory = _raw_inventory(DEFAULT_V4_RAW_ROOT)
    v5_raw_inventory = _raw_inventory(DEFAULT_V5_RAW_ROOT)
    if len(v4_raw_inventory) != int(v4_cross["raw_file_count"]):
        raise ValueError("V4 raw evidence file count changed")
    if len(v5_raw_inventory) != int(cross["raw_file_count"]):
        raise ValueError("V5 raw evidence file count changed")
    if _raw_inventory_digest(v4_raw_inventory) != v4_cross["raw_evidence_digest"]:
        raise ValueError("V4 raw evidence digest changed")
    if _raw_inventory_digest(v5_raw_inventory) != cross["raw_evidence_digest"]:
        raise ValueError("V5 raw evidence digest changed")

    manifest = {
        "schema_version": "effectslice-paper-results-manifest.v5",
        "canonical": True,
        "path_root": "project_root",
        "run_root": RUN_ROOT.relative_to(PROJECT_ROOT).as_posix(),
        "supersedes": [
            "generated_results_manifest.json",
            "generated_results_manifest_v3.json",
            "generated_results_manifest_v4.json",
        ],
        "manuscript_version": "v3-final",
        "experiment_versions": ["confirmation-v4", "confirmation-v5r2"],
        "pre_run_roots": {
            "v4": _artifact(
                RUN_ROOT / "artifacts" / "confirmation_v4" / "preregistration.json"
            ),
            "v5": _artifact(
                RUN_ROOT / "artifacts" / "confirmation_v5r2" / "preregistration.json"
            ),
        },
        "output_sets": {
            "v4": {
                "raw_root": DEFAULT_V4_RAW_ROOT.relative_to(RUN_ROOT).as_posix(),
                "registered_blocks": int(v4_cross["registered_blocks"]),
                "registered_condition_runs": int(
                    v4_cross["registered_condition_runs"]
                ),
                "raw_file_count": int(v4_cross["raw_file_count"]),
                "raw_evidence_digest": v4_cross["raw_evidence_digest"],
                "raw_inventory": v4_raw_inventory,
                "crosscheck": _artifact(v4_cross_source),
            },
            "v5": {
                "raw_root": DEFAULT_V5_RAW_ROOT.relative_to(RUN_ROOT).as_posix(),
                "registered_blocks": int(cross["registered_blocks"]),
                "registered_condition_runs": int(cross["registered_condition_runs"]),
                "raw_file_count": int(cross["raw_file_count"]),
                "raw_evidence_digest": cross["raw_evidence_digest"],
                "raw_inventory": v5_raw_inventory,
                "crosscheck": _artifact(cross_source),
            },
        },
        "decisions": {
            "v4": {
                "candidate_count": values["VFourRealCandidateCount"],
                "admissions": values["VFourRealAdmissions"],
                "calibration": values["VFourCalibrationDecision"],
                "snap_prefix_03": values["SnapRealDecision"],
                "toolformer_prefix_01": values["ToolformerRealDecision"],
            },
            "v5": {
                "candidate_count": values["VFiveNaturalCandidateCount"],
                "admissions": values["VFiveNaturalAdmissions"],
                "toolformer_prefix_04": values["ToolformerNaturalDecision"],
            },
        },
        "sources": {
            "v4_summary": _artifact(v4_source),
            "v5_analysis": _artifact(v5_source),
            "v5_crosscheck": _artifact(cross_source),
        },
        "analysis_provenance": {
            "v4_bound_analyzer": _artifact(RUN_ROOT / "analyze_confirmation_v4.py"),
            "v4_compatibility_adapter": _artifact(
                RUN_ROOT / "analyze_confirmation_v4_role_repair.py"
            ),
            "v4_independent_crosscheck": _artifact(
                RUN_ROOT / "derived" / "confirmation_v4" / "independent_crosscheck.json"
            ),
            "v5_bound_analyzer": _artifact(RUN_ROOT / "analyze_confirmation_v5.py"),
            "v5_compatibility_adapter": _artifact(
                RUN_ROOT / "analyze_confirmation_v5_role_repair.py"
            ),
            "v5_compatibility_adapter_test": _artifact(
                RUN_ROOT / "tests" / "test_analyze_confirmation_v5_role_repair.py"
            ),
            "v5_independent_crosscheck_implementation": _artifact(
                RUN_ROOT / "crosscheck_confirmation_v5.py"
            ),
            "v5_independent_crosscheck_test": _artifact(
                RUN_ROOT / "tests" / "test_crosscheck_confirmation_v5.py"
            ),
            "release_verifier": _artifact(RUN_ROOT / "verify_effectslice_release.py"),
        },
        "verification_tests": {
            "v4_outputs": _artifact(
                RUN_ROOT / "tests" / "test_confirmation_v4_outputs.py"
            ),
            "v4_crosscheck": _artifact(
                RUN_ROOT / "tests" / "test_crosscheck_confirmation_v4.py"
            ),
            "v5_registration": _artifact(
                RUN_ROOT / "tests" / "test_confirmation_v5.py"
            ),
            "shared_analysis_contract": _artifact(
                RUN_ROOT / "tests" / "test_analyze_confirmation_v3.py"
            ),
            "v5_crosscheck": _artifact(
                RUN_ROOT / "tests" / "test_crosscheck_confirmation_v5.py"
            ),
            "manuscript_contract": _artifact(
                RUN_ROOT / "tests" / "test_effectslice_manuscript_v3.py"
            ),
        },
        "output_tex": _artifact(tex),
        "builder": _artifact(Path(__file__)),
        "macros": values,
    }
    destination = Path(manifest_path).resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return {"tex": tex.as_posix(), "manifest": destination.as_posix()}


def main() -> int:
    parser = argparse.ArgumentParser(description="Build final V4+V5 paper macros")
    parser.add_argument("--v4-summary", type=Path, default=DEFAULT_V4_SUMMARY)
    parser.add_argument("--v5-analysis", type=Path, default=DEFAULT_V5_ANALYSIS)
    parser.add_argument("--v5-crosscheck", type=Path, default=DEFAULT_V5_CROSSCHECK)
    parser.add_argument("--output-tex", type=Path, default=DEFAULT_OUTPUT_TEX)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    args = parser.parse_args()
    print(
        json.dumps(
            build_paper_results(
                args.v4_summary,
                args.v5_analysis,
                args.v5_crosscheck,
                args.output_tex,
                args.manifest,
            ),
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
