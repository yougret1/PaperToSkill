import argparse
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "package_skillsbench_candidate_validation_report.py"
)
SPEC = importlib.util.spec_from_file_location(
    "package_skillsbench_candidate_validation_report", SCRIPT
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def fixture(root: Path, *, with_amendment: bool = False) -> argparse.Namespace:
    materials = root / "materials"
    selection_output = root / "selection-output"
    analysis_output = root / "analysis-output"
    screen_run = root / "screen-run"
    confirm_run = root / "confirm-run"
    output = root / "report-package"
    tasks = ["task-alpha", "task-beta"]

    screen_protocol_path = materials / "screen_protocol.json"
    blind_labels_path = materials / "blind_labels.json"
    confirm_protocol_path = selection_output / "confirm_materials" / "protocol.json"
    write_json(
        screen_protocol_path,
        {
            "executor": {"model": "gpt-5.6-sol", "conditions": ["B", "F"]},
            "main": {"tasks": [*tasks, "task-gamma", "task-delta"], "repetitions": 3},
        },
    )
    write_json(blind_labels_path, {"outcome_access": "prohibited", "records": []})
    effective_blind_labels_path = blind_labels_path
    amendment_path = selection_output / "candidate_amendment.json"
    amendment_reference = None
    if with_amendment:
        write_json(
            amendment_path,
            {
                "schema_version": "skillsbench-candidate-validation-amendment-v1",
                "task_id": "task-alpha",
                "outcome_access": "prohibited",
                "candidate_outcomes_used": False,
                "generator": {
                    "mode": "heuristic/no-llm",
                    "stage": 1,
                    "tscg": False,
                },
                "candidate": {
                    "P1_skills_sha256": "1" * 64,
                    "P2_skills_sha256": "2" * 64,
                },
            },
        )
        amendment_reference = {
            "path": str(amendment_path.resolve()),
            "sha256": MODULE.sha256_file(amendment_path),
        }
        effective_blind_labels_path = selection_output / "amended_blind_labels.json"
        write_json(
            effective_blind_labels_path,
            {"outcome_access": "prohibited", "records": []},
        )
    confirm_protocol = {
        "executor": {"model": "gpt-5.6-sol", "conditions": ["B", "F", "P", "D"]},
        "main": {"tasks": tasks, "repetitions": 48},
    }
    if amendment_reference is not None:
        confirm_protocol["candidate_amendment"] = amendment_reference
        confirm_protocol["blind_labels"] = str(effective_blind_labels_path.resolve())
    write_json(confirm_protocol_path, confirm_protocol)

    for run_root, audit in ((screen_run, False), (confirm_run, True)):
        write_json(run_root / "manifest.json", {"status": "prepared"})
        write_json(run_root / "schedule.json", {"jobs": []})
        write_json(run_root / "main_gate.json", {"status": "passed", "final_reportable": True})
        write_json(
            run_root / "platform_repairs.json",
            {
                "schema_version": "skillsbench-bfs-platform-repairs-v2",
                "event_count": 1,
                "repaired_file_count": 0,
                "events": [{"repaired_file_count": 0, "repairs": []}],
            },
        )
        (run_root / "run_state.jsonl").write_text("{}\n", encoding="utf-8")
        if audit:
            write_json(run_root / "audit_report.json", {"status": "passed", "final_reportable": True})

    task_results = []
    for task in [*tasks, "task-gamma", "task-delta"]:
        selected = task in tasks
        task_results.append(
            {
                "task_id": task,
                "arms": {"B": {"successes": 0}, "F": {"successes": 3}},
                "blind_label_consensus": {
                    "P": "intended-preserving" if selected else "destructive",
                    "D": "destructive",
                },
                "label_eligible": selected,
                "eligible": selected,
            }
        )
    selection_path = selection_output / "selection.json"
    selection = {
        "status": "passed",
        "selected_tasks": tasks,
        "candidate_outcomes_used": False,
        "task_results": task_results,
        "screen_protocol_sha256": MODULE.sha256_file(screen_protocol_path),
        "screen_manifest_sha256": MODULE.sha256_file(screen_run / "manifest.json"),
        "screen_schedule_sha256": MODULE.sha256_file(screen_run / "schedule.json"),
        "screen_main_gate_sha256": MODULE.sha256_file(screen_run / "main_gate.json"),
        "screen_run_state_sha256": MODULE.sha256_file(screen_run / "run_state.jsonl"),
        "screen_platform_repairs_sha256": MODULE.sha256_file(
            screen_run / "platform_repairs.json"
        ),
    }
    if amendment_reference is not None:
        selection["candidate_amendment"] = amendment_reference
    write_json(selection_path, selection)

    decisions = []
    for task in tasks:
        decisions.extend(
            [
                {
                    "task_id": task,
                    "candidate": "P",
                    "expected_class": "intended-preserving",
                    "k_B": 0,
                    "k_F": 48,
                    "k_S": 48,
                    "n": 48,
                    "effect": 0.0,
                    "ci_low": -0.074,
                    "ci_high": 0.074,
                    "state": "Accept",
                },
                {
                    "task_id": task,
                    "candidate": "D",
                    "expected_class": "destructive",
                    "k_B": 0,
                    "k_F": 48,
                    "k_S": 0,
                    "n": 48,
                    "effect": -1.0,
                    "ci_low": -1.0,
                    "ci_high": -0.926,
                    "state": "RejectCandidate",
                },
            ]
        )
    final_report = {
        "status": "complete",
        "confirmatory_tasks": tasks,
        "repetitions_per_arm": 48,
        "decisions": decisions,
        "unsafe_accepts": 0,
        "false_rejects": 0,
        "deferrals": 0,
        "boundary": {"screening_rows_excluded": True},
        "selection_sha256": MODULE.sha256_file(selection_path),
        "protocol_sha256": MODULE.sha256_file(confirm_protocol_path),
        "blind_labels_sha256": MODULE.sha256_file(effective_blind_labels_path),
        "manifest_sha256": MODULE.sha256_file(confirm_run / "manifest.json"),
        "schedule_sha256": MODULE.sha256_file(confirm_run / "schedule.json"),
        "main_gate_sha256": MODULE.sha256_file(confirm_run / "main_gate.json"),
        "audit_sha256": MODULE.sha256_file(confirm_run / "audit_report.json"),
        "run_state_sha256": MODULE.sha256_file(confirm_run / "run_state.jsonl"),
        "platform_repairs_sha256": MODULE.sha256_file(
            confirm_run / "platform_repairs.json"
        ),
    }
    if amendment_reference is not None:
        final_report["candidate_amendment_sha256"] = amendment_reference["sha256"]
        final_report["candidate_material_hashes"] = {
            "task-alpha": {"P": {"frozen_source_sha256": "2" * 64}}
        }
    write_json(analysis_output / "final_report.json", final_report)
    analysis_script = root / "analyze_skillsbench_candidate_validation_sol.py"
    analysis_script.write_text("# frozen analysis\n", encoding="utf-8")
    return argparse.Namespace(
        analysis_output=analysis_output,
        selection_output=selection_output,
        materials=materials,
        screen_run=screen_run,
        confirm_run=confirm_run,
        analysis_script=analysis_script,
        output=output,
    )


class PackageCandidateValidationReportTests(unittest.TestCase):
    def test_packages_path_neutral_summary_and_hash_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            args = fixture(Path(tmp))
            result = MODULE.package(args)

            self.assertEqual(result["status"], "complete")
            report = (args.output / "REPORT.md").read_text(encoding="utf-8")
            summary_text = (args.output / "SUMMARY.json").read_text(encoding="utf-8")
            summary = json.loads(summary_text)
            manifest = json.loads(
                (args.output / "outputs" / "binding_manifest.json").read_text(encoding="utf-8")
            )

            self.assertIn("384 registered confirmatory rows", report)
            self.assertIn("accepted 2/2", report)
            self.assertIn("rejected 2/2", report)
            self.assertEqual(summary["confirmation"]["unsafe_accepts"], 0)
            self.assertNotIn(str(Path(tmp)), summary_text)
            self.assertEqual(manifest["status"], "verified")
            self.assertFalse(manifest["raw_evidence_packaged"])
            self.assertTrue(
                (args.output / "attestations" / "screen_platform_repairs.json").is_file()
            )
            self.assertTrue(
                (
                    args.output
                    / "attestations"
                    / "confirmatory_platform_repairs.json"
                ).is_file()
            )
            verifier = args.output / "verify_package.py"
            self.assertTrue(verifier.is_file())

    def test_rejects_tampered_bound_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            args = fixture(Path(tmp))
            (args.confirm_run / "run_state.jsonl").write_text("tampered\n", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "confirm_run_state hash mismatch"):
                MODULE.package(args)

    def test_packages_and_binds_candidate_amendment(self):
        with tempfile.TemporaryDirectory() as tmp:
            args = fixture(Path(tmp), with_amendment=True)
            MODULE.package(args)

            amendment_path = args.output / "protocol" / "candidate_amendment.json"
            amendment_sha256 = MODULE.sha256_file(amendment_path)
            summary = json.loads((args.output / "SUMMARY.json").read_text(encoding="utf-8"))
            design = json.loads(
                (args.output / "protocol" / "design_summary.json").read_text(encoding="utf-8")
            )
            selection = json.loads(
                (args.output / "analysis" / "selection_summary.json").read_text(
                    encoding="utf-8"
                )
            )
            binding = json.loads(
                (args.output / "outputs" / "binding_manifest.json").read_text(
                    encoding="utf-8"
                )
            )

            self.assertTrue(amendment_path.is_file())
            self.assertEqual(summary["candidate_amendment"]["sha256"], amendment_sha256)
            self.assertEqual(design["candidate_amendment"], summary["candidate_amendment"])
            self.assertEqual(selection["candidate_amendment"], summary["candidate_amendment"])
            self.assertEqual(
                binding["source_evidence_sha256"]["candidate_amendment"],
                amendment_sha256,
            )
            self.assertEqual(
                binding["analysis_expected_bindings"]["candidate_amendment"],
                amendment_sha256,
            )

    def test_offline_verifier_rejects_outcome_aware_amendment_after_manifest_rehash(self):
        with tempfile.TemporaryDirectory() as tmp:
            args = fixture(Path(tmp), with_amendment=True)
            MODULE.package(args)

            amendment_path = args.output / "protocol" / "candidate_amendment.json"
            amendment = json.loads(amendment_path.read_text(encoding="utf-8"))
            amendment["candidate_outcomes_used"] = True
            write_json(amendment_path, amendment)
            manifest_path = args.output / "PACKAGE_MANIFEST.sha256"
            lines = manifest_path.read_text(encoding="utf-8").splitlines()
            lines = [
                f"{MODULE.sha256_file(amendment_path)}  protocol/candidate_amendment.json"
                if line.endswith("  protocol/candidate_amendment.json")
                else line
                for line in lines
            ]
            manifest_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

            verification = subprocess.run(
                [sys.executable, str(args.output / "verify_package.py"), str(args.output)],
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            self.assertNotEqual(verification.returncode, 0)
            self.assertIn("candidate amendment used P/D outcomes", verification.stderr)


if __name__ == "__main__":
    unittest.main()
