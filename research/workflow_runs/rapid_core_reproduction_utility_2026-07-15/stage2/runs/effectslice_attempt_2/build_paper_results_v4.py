from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


RUN_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = Path(__file__).resolve().parents[6]
DEFAULT_SUMMARY = RUN_ROOT / "logs" / "confirmation_v4_summary.json"
DEFAULT_OUTPUT_TEX = PROJECT_ROOT / "paper" / "effectslice_aaai" / "generated_results_v3.tex"
DEFAULT_MANIFEST = RUN_ROOT / "manuscript" / "generated_results_manifest_v4.json"
DEFAULT_CROSSCHECK = RUN_ROOT / "derived" / "confirmation_v4" / "independent_crosscheck.json"
DEFAULT_CROSSCHECK_SCRIPT = RUN_ROOT / "crosscheck_confirmation_v4.py"
DEFAULT_CROSSCHECK_TEST = RUN_ROOT / "tests" / "test_crosscheck_confirmation_v4.py"
DEFAULT_BOUND_ANALYZER = RUN_ROOT / "analyze_confirmation_v4.py"
DEFAULT_ADAPTER = RUN_ROOT / "analyze_confirmation_v4_role_repair.py"
DEFAULT_ADAPTER_TEST = RUN_ROOT / "tests" / "test_analyze_confirmation_v4_role_repair.py"
SUMMARY_SCHEMA = "effectslice-stage2-confirmation-summary.v4"
PREFIXES = {
    "snap_mfse": "SnapReal",
    "toolformer_negative": "ToolformerReal",
    "toolformer_positive": "PlantedPositive",
    "toolformer_identity": "IdentityControl",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _macro(name: str, value: Any) -> str:
    return f"\\newcommand{{\\{name}}}{{{value}}}"


def _decision(value: bool) -> str:
    return "Pass" if value else "Reject"


def build_paper_results(summary_path: Path, output_tex: Path, manifest_path: Path) -> dict[str, str]:
    source = Path(summary_path).resolve()
    summary = json.loads(source.read_text(encoding="utf-8"))
    if summary.get("schema_version") != SUMMARY_SCHEMA:
        raise ValueError("unexpected V4 summary schema")
    families = {row["family_key"]: row for row in summary["families"]}
    if set(families) != set(PREFIXES):
        raise ValueError("V4 paper macro family set changed")

    resource = summary["resource_summary"]
    resource_by_family = summary["resource_by_family_condition"]
    values: dict[str, Any] = {
        "VFourRegisteredBlocks": int(summary["registered_blocks"]),
        "VFourProviderConversations": int(summary["registered_condition_runs"]),
        "VFourRegisteredStrata": int(summary["registered_strata"]),
        "VFourRealCandidateCount": 2,
        "VFourRealAdmissions": int(summary["real_candidate_admissions"]),
        "VFourCalibrationDecision": (
            "Pass" if summary["calibration"]["passed"] else "Fail"
        ),
        "VFourProviderTurns": int(resource["provider_turns"]),
        "VFourActions": int(resource["actions_used"]),
        "VFourInputTokens": f"{int(resource['input_tokens']):,}",
        "VFourOutputTokens": f"{int(resource['output_tokens']):,}",
        "VFourTransportAttempts": f"{int(resource['transport_attempts']):,}",
        "VFourPublicTestRequests": int(resource["public_test_requests"]),
        "VFourPublicTestPasses": int(resource["public_test_passes"]),
        "VFourPublicTestFailures": int(resource["public_test_failures"]),
        "VFourInvalidActions": int(resource["action_counts"].get("invalid", 0)),
        "VFourExtraTransportAttempts": int(resource["extra_transport_attempts"]),
        "VFourMinimumPassingCases": 61,
        "VFourSubmittedRuns": int(summary["terminal_reason_counts"].get("submitted", 0)),
        "VFourPreregistrationDigest": summary["sources"]["preregistration"]["sha256"],
        "VFourAnalyzerRepair": "Disclosed post-hoc compatibility audit",
    }
    for key, prefix in PREFIXES.items():
        values[f"{prefix}PublicTestFailures"] = sum(
            int(resource_by_family[key][condition]["public_test_failures"])
            for condition in "BFS"
        )
    for key, prefix in PREFIXES.items():
        row = families[key]
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
            values[f"{prefix}Decision"] = "Instr. Pass" if instrument["passed"] else "Instr. Fail"
            values[f"{prefix}Matches"] = int(instrument["full_slice_success_matches"])
            values[f"{prefix}SuccessGap"] = int(instrument["full_slice_success_count_gap"])
        else:
            decision = row["admission_decision"]
            values[f"{prefix}Decision"] = _decision(bool(decision["passed"]))

    lines = [
        "% Generated from confirmation V4 analysis; main_v3.tex is the final manuscript.",
        "% Do not edit empirical values by hand.",
    ]
    lines.extend(_macro(name, value) for name, value in values.items())
    tex = Path(output_tex).resolve()
    tex.parent.mkdir(parents=True, exist_ok=True)
    tex.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")

    manifest = {
        "schema_version": "effectslice-paper-results-manifest.v4",
        "manuscript_version": "v3-final",
        "experiment_version": "confirmation-v4",
        "source": {"path": source.as_posix(), "sha256": _sha256(source)},
        "output_tex": {"path": tex.as_posix(), "sha256": _sha256(tex)},
        "analysis_provenance": {
            "bound_analyzer": {
                "path": DEFAULT_BOUND_ANALYZER.resolve().as_posix(),
                "sha256": _sha256(DEFAULT_BOUND_ANALYZER),
            },
            "compatibility_adapter": {
                "path": DEFAULT_ADAPTER.resolve().as_posix(),
                "sha256": _sha256(DEFAULT_ADAPTER),
            },
            "compatibility_adapter_test": {
                "path": DEFAULT_ADAPTER_TEST.resolve().as_posix(),
                "sha256": _sha256(DEFAULT_ADAPTER_TEST),
            },
            "independent_crosscheck": {
                "path": DEFAULT_CROSSCHECK.resolve().as_posix(),
                "sha256": _sha256(DEFAULT_CROSSCHECK),
            },
            "independent_crosscheck_implementation": {
                "path": DEFAULT_CROSSCHECK_SCRIPT.resolve().as_posix(),
                "sha256": _sha256(DEFAULT_CROSSCHECK_SCRIPT),
            },
            "independent_crosscheck_test": {
                "path": DEFAULT_CROSSCHECK_TEST.resolve().as_posix(),
                "sha256": _sha256(DEFAULT_CROSSCHECK_TEST),
            },
        },
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
    parser = argparse.ArgumentParser(description="Build final-manuscript V4 result macros")
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument("--output-tex", type=Path, default=DEFAULT_OUTPUT_TEX)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    args = parser.parse_args()
    print(
        json.dumps(
            build_paper_results(args.summary, args.output_tex, args.manifest),
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
