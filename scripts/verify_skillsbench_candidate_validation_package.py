#!/usr/bin/env python3
"""Verify a packaged SkillsBench candidate-validation report offline."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


BASE_EXPECTED_FILES = {
    "PACKAGE_MANIFEST.sha256",
    "README.md",
    "REPORT.md",
    "SUMMARY.json",
    "analysis/decision_summary.json",
    "analysis/selection_summary.json",
    "annotations/blind_label_summary.json",
    "attestations/confirmatory_terminal.json",
    "attestations/confirmatory_platform_repairs.json",
    "attestations/screen_platform_repairs.json",
    "attestations/screen_terminal.json",
    "outputs/binding_manifest.json",
    "outputs/final_report.json",
    "protocol/design_summary.json",
    "scripts/analyze_skillsbench_candidate_validation_sol.py",
    "scripts/package_skillsbench_candidate_validation_report.py",
    "verify_package.py",
}
AMENDMENT_FILE = "protocol/candidate_amendment.json"
WINDOWS_ABSOLUTE_PATH = re.compile(r"(?<![A-Za-z0-9_])[A-Za-z]:[\\/]")
SENSITIVE_JSON_KEYS = re.compile(
    r'"(?:api[_-]?key|access[_-]?token|authorization|cookie|password|secret)"\s*:',
    re.IGNORECASE,
)


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"expected JSON object: {path}")
    return payload


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def parse_manifest(path: Path) -> dict[str, str]:
    records: dict[str, str] = {}
    for line_number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        parts = raw.split("  ", 1)
        require(len(parts) == 2, f"invalid package-manifest line {line_number}")
        digest, relative = parts
        require(re.fullmatch(r"[0-9a-f]{64}", digest) is not None, "invalid SHA-256")
        require(relative not in records, f"duplicate package-manifest path: {relative}")
        records[relative] = digest
    return records


def sha256_value(payload: dict[str, Any], *keys: str) -> str | None:
    for key in keys:
        value = payload.get(key)
        if value is not None:
            return str(value)
    return None


def candidate_tree_hashes(amendment: dict[str, Any]) -> tuple[str | None, str | None]:
    old_hash = sha256_value(
        amendment,
        "old_candidate_tree_sha256",
        "old_tree_sha256",
        "previous_candidate_tree_sha256",
    )
    new_hash = sha256_value(
        amendment,
        "new_candidate_tree_sha256",
        "new_tree_sha256",
        "amended_candidate_tree_sha256",
    )
    hashes = amendment.get("candidate_tree_sha256")
    if isinstance(hashes, dict):
        old_hash = old_hash or sha256_value(hashes, "old", "before")
        new_hash = new_hash or sha256_value(hashes, "new", "after")
    candidate = amendment.get("candidate")
    if isinstance(candidate, dict):
        old_hash = old_hash or sha256_value(candidate, "P1_skills_sha256")
        new_hash = new_hash or sha256_value(candidate, "P2_skills_sha256")
    return old_hash, new_hash


def validate_candidate_amendment(amendment: dict[str, Any]) -> tuple[str, str]:
    require(
        amendment.get("schema_version")
        == "skillsbench-candidate-validation-amendment-v1",
        "candidate amendment schema changed",
    )
    require(
        isinstance(amendment.get("task_id"), str) and amendment["task_id"],
        "candidate amendment task is missing",
    )
    require(
        amendment.get("outcome_access") == "prohibited",
        "candidate amendment accessed outcomes",
    )
    require(
        amendment.get("candidate_outcomes_used") is False,
        "candidate amendment used P/D outcomes",
    )
    generator = amendment.get("generator")
    require(
        isinstance(generator, dict) or generator is None,
        "candidate amendment generator is invalid",
    )
    generator = generator or amendment
    require(generator.get("mode") == "heuristic/no-llm", "candidate amendment mode changed")
    require(
        type(generator.get("stage")) is int and generator["stage"] == 1,
        "candidate amendment stage must be 1",
    )
    require(generator.get("tscg") is False, "candidate amendment must disable TSCG")
    old_hash, new_hash = candidate_tree_hashes(amendment)
    require(
        isinstance(old_hash, str) and re.fullmatch(r"[0-9a-f]{64}", old_hash) is not None,
        "candidate amendment old tree SHA-256 is invalid",
    )
    require(
        isinstance(new_hash, str) and re.fullmatch(r"[0-9a-f]{64}", new_hash) is not None,
        "candidate amendment new tree SHA-256 is invalid",
    )
    require(old_hash != new_hash, "candidate amendment old and new tree hashes are identical")
    return old_hash, new_hash


def verify(root: Path) -> dict[str, Any]:
    root = root.resolve()
    actual_files = {
        path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()
    }
    expected_files = set(BASE_EXPECTED_FILES)
    amendment_present = AMENDMENT_FILE in actual_files
    if amendment_present:
        expected_files.add(AMENDMENT_FILE)
    require(actual_files == expected_files, "package file set differs from the frozen contract")

    hashes = parse_manifest(root / "PACKAGE_MANIFEST.sha256")
    expected_hashed = expected_files - {"PACKAGE_MANIFEST.sha256"}
    require(set(hashes) == expected_hashed, "package manifest file set differs")
    for relative, expected in hashes.items():
        require(sha256_file(root / relative) == expected, f"package hash mismatch: {relative}")

    summary = load_json(root / "SUMMARY.json")
    design = load_json(root / "protocol" / "design_summary.json")
    selection = load_json(root / "analysis" / "selection_summary.json")
    decisions = load_json(root / "analysis" / "decision_summary.json")
    labels = load_json(root / "annotations" / "blind_label_summary.json")
    screen = load_json(root / "attestations" / "screen_terminal.json")
    confirm = load_json(root / "attestations" / "confirmatory_terminal.json")
    binding = load_json(root / "outputs" / "binding_manifest.json")
    final_report = load_json(root / "outputs" / "final_report.json")
    screen_repairs = load_json(root / "attestations" / "screen_platform_repairs.json")
    confirm_repairs = load_json(root / "attestations" / "confirmatory_platform_repairs.json")

    require(summary.get("status") == "complete", "summary is not complete")
    require(binding.get("status") == "verified", "source binding is not verified")
    for label, ledger in (("screen", screen_repairs), ("confirm", confirm_repairs)):
        require(
            ledger.get("schema_version") == "skillsbench-bfs-platform-repairs-v2",
            f"{label} platform-repair schema changed",
        )
        events = ledger.get("events") or []
        require(events and ledger.get("event_count") == len(events), f"{label} repair events invalid")
        require(
            ledger.get("repaired_file_count")
            == sum(int(event.get("repaired_file_count", -1)) for event in events),
            f"{label} repair counts are inconsistent",
        )
    source_hashes = binding.get("source_evidence_sha256") or {}
    expected_bindings = binding.get("analysis_expected_bindings") or {}
    amendment_declarations = [
        summary.get("candidate_amendment"),
        design.get("candidate_amendment"),
        selection.get("candidate_amendment"),
        source_hashes.get("candidate_amendment"),
        expected_bindings.get("candidate_amendment"),
        sha256_value(final_report, "candidate_amendment_sha256", "amendment_sha256"),
    ]
    require(
        amendment_present == any(value is not None for value in amendment_declarations),
        "candidate amendment declarations differ from the package contents",
    )
    if amendment_present:
        amendment_path = root / AMENDMENT_FILE
        amendment = load_json(amendment_path)
        old_hash, new_hash = validate_candidate_amendment(amendment)
        amendment_sha256 = sha256_file(amendment_path)
        require(
            source_hashes.get("candidate_amendment") == amendment_sha256,
            "candidate amendment source binding differs",
        )
        require(
            expected_bindings.get("candidate_amendment") == amendment_sha256,
            "candidate amendment analysis binding differs",
        )
        task_id = str(amendment["task_id"])
        task_material_hashes = (
            (binding.get("candidate_material_hashes") or {}).get(task_id) or {}
        )
        material_hash = (task_material_hashes.get("P") or {}).get(
            "frozen_source_sha256"
        )
        require(
            material_hash == new_hash,
            "candidate amendment new tree hash differs from confirmatory materials",
        )
        final_amendment_sha256 = sha256_value(
            final_report, "candidate_amendment_sha256", "amendment_sha256"
        )
        if final_amendment_sha256 is not None:
            require(
                final_amendment_sha256 == amendment_sha256,
                "candidate amendment final-report binding differs",
            )
        expected_summary = {
            "present": True,
            "sha256": amendment_sha256,
            "candidate_outcomes_used": False,
            "mode": "heuristic/no-llm",
            "stage": 1,
            "tscg": False,
            "old_candidate_tree_sha256": old_hash,
            "new_candidate_tree_sha256": new_hash,
        }
        for label, payload in (
            ("summary", summary),
            ("design", design),
            ("selection", selection),
        ):
            require(
                payload.get("candidate_amendment") == expected_summary,
                f"candidate amendment {label} summary differs",
            )
    require(
        sha256_file(root / "attestations" / "screen_platform_repairs.json")
        == source_hashes.get("screen_platform_repairs"),
        "screen platform-repair binding differs",
    )
    require(
        sha256_file(root / "attestations" / "confirmatory_platform_repairs.json")
        == source_hashes.get("confirm_platform_repairs"),
        "confirmatory platform-repair binding differs",
    )
    require(screen.get("status") == "passed", "screening terminal gate did not pass")
    require(screen.get("final_reportable") is True, "screening is not reportable")
    require(confirm.get("status") == "passed", "confirmatory terminal gate did not pass")
    require(confirm.get("final_reportable") is True, "confirmation is not reportable")
    require(labels.get("outcome_access") == "prohibited", "blind labels were not outcome blind")
    require(selection.get("candidate_outcomes_used_for_selection") is False, "selection used P/D")
    require(
        selection.get("selected_tasks")
        == decisions.get("tasks")
        == (design.get("confirmation") or {}).get("tasks"),
        "selected tasks differ across package files",
    )

    screen_design = design["screening"]
    confirm_design = design["confirmation"]
    require(
        screen_design["registered_main_rows"]
        == len(screen_design["tasks"])
        * len(screen_design["conditions"])
        * screen_design["repetitions_per_arm"],
        "screening registered-row count is inconsistent",
    )
    require(
        confirm_design["registered_main_rows"]
        == len(confirm_design["tasks"])
        * len(confirm_design["conditions"])
        * confirm_design["repetitions_per_arm"],
        "confirmatory registered-row count is inconsistent",
    )
    require(
        screen.get("terminal_rows") == screen_design["registered_main_rows"],
        "screening terminal-row count differs from the design",
    )
    require(
        confirm.get("terminal_rows") == confirm_design["registered_main_rows"],
        "confirmatory terminal-row count differs from the design",
    )
    for attestation in (screen, confirm):
        require(attestation.get("missing_rows") == 0, "registered rows are missing")
        require(attestation.get("unexpected_rows") == 0, "unexpected rows are present")
        require(attestation.get("invalid_rows") == 0, "invalid rows are present")
        require(attestation.get("contaminated_rows") == 0, "B contamination was detected")
        require(attestation.get("credential_reflection_rows") == 0, "credential reflection was detected")
        require(attestation.get("protocol_invalid_reasons") == [], "protocol is invalid")

    rows = decisions.get("decisions") or []
    counts = dict(sorted(Counter(str(row.get("state")) for row in rows).items()))
    require(counts == decisions.get("decision_counts"), "decision counts are inconsistent")
    require(len(rows) == 2 * len(decisions.get("tasks") or []), "candidate decision grid is incomplete")

    for relative in sorted(expected_files - {"PACKAGE_MANIFEST.sha256"}):
        path = root / relative
        text = path.read_text(encoding="utf-8", errors="strict")
        require(WINDOWS_ABSOLUTE_PATH.search(text) is None, f"absolute Windows path found: {relative}")
        if path.suffix == ".json":
            require(SENSITIVE_JSON_KEYS.search(text) is None, f"sensitive JSON field found: {relative}")

    return {
        "status": "passed",
        "files": len(actual_files),
        "screening_rows": screen.get("terminal_rows"),
        "confirmatory_rows": confirm.get("terminal_rows"),
        "tasks": decisions.get("tasks"),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package", nargs="?", type=Path, default=Path(__file__).resolve().parent)
    return parser.parse_args()


def main() -> int:
    result = verify(parse_args().package)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
