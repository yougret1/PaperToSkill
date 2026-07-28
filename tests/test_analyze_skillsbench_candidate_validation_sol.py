import argparse
import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "analyze_skillsbench_candidate_validation_sol.py"
)
SPEC = importlib.util.spec_from_file_location(
    "analyze_skillsbench_candidate_validation_sol", SCRIPT
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


TASKS = ["sec-financial-report", "task-beta"]


def blind_labels(
    path: Path,
    *,
    tasks: list[str] | None = None,
    reviewers: tuple[str, str] = ("reviewer-a", "reviewer-b"),
    sec_p_label: str = "intended-preserving",
) -> None:
    records = []
    for reviewer in reviewers:
        for task in tasks or TASKS:
            records.append(
                {
                    "reviewer_id": reviewer,
                    "task_id": task,
                    "P_label": sec_p_label if task == "sec-financial-report" else "intended-preserving",
                    "D_label": "destructive",
                }
            )
    MODULE.atomic_json(
        path,
        {
            "schema_version": "skillsbench-candidate-blind-labels-v1",
            "outcome_access": "prohibited",
            "records": records,
        },
    )


def prepared_run(
    root: Path,
    protocol_path: Path,
    tasks: list[str],
    conditions: tuple[str, ...],
    repetitions: int,
    reward_for,
    *,
    audit: bool,
) -> None:
    protocol = MODULE.load_json(protocol_path)
    skillsbench_root = Path(protocol["skillsbench"]["root"])
    pools = {key: Path(value) for key, value in (protocol.get("candidate_pools") or {}).items()}
    jobs = []
    events = []
    for task in tasks:
        for condition in conditions:
            mirror = root / "work" / condition / task
            (mirror / "environment").mkdir(parents=True, exist_ok=True)
            (mirror / "task.md").write_text("fixture task\n", encoding="utf-8")
            (mirror / "environment" / "Dockerfile").write_text(
                "FROM scratch\n", encoding="utf-8"
            )
            source = None
            if condition == "F":
                source = skillsbench_root / "tasks" / task / "environment" / "skills"
            elif condition in {"P", "D"}:
                source = pools[condition] / task / "skills"
            if source is not None:
                shutil.copytree(source, mirror / "environment" / "skills")
            for repetition in range(1, repetitions + 1):
                execution_id = f"main-{task}-{condition}-{repetition}"
                jobs.append(
                    {
                        "execution_id": execution_id,
                        "phase": "main",
                        "task_id": task,
                        "condition": condition,
                        "repetition": repetition,
                        "mirror_task_dir": str(mirror),
                    }
                )
                events.append(
                    {
                        "event": "start",
                        "timestamp": "2026-07-27T00:00:00+00:00",
                        "execution_id": execution_id,
                        "phase": "main",
                        "task_id": task,
                        "condition": condition,
                        "repetition": repetition,
                        "attempt_number": 1,
                        "status": "running",
                    }
                )
                events.append(
                    {
                        "event": "finish",
                        "timestamp": "2026-07-27T00:01:00+00:00",
                        "execution_id": execution_id,
                        "phase": "main",
                        "task_id": task,
                        "condition": condition,
                        "repetition": repetition,
                        "status": "scored",
                        "invalid": False,
                        "official_reward": reward_for(task, condition, repetition),
                        "attempt_number": 1,
                    }
                )
    schedule_path = root / "schedule.json"
    MODULE.atomic_json(schedule_path, {"jobs": jobs})
    compat_path = root / "benchflow_windows_compat.py"
    compat_path.write_text("# fixture compat\n", encoding="utf-8")
    repair_path = root / "platform_repairs.json"
    MODULE.atomic_json(
        repair_path,
        {
            "schema_version": "skillsbench-bfs-platform-repairs-v2",
            "created_at": "2026-07-26T00:00:00+00:00",
            "event_count": 1,
            "repaired_file_count": 0,
            "events": [
                {
                    "created_at": "2026-07-26T00:00:00+00:00",
                    "repaired_file_count": 0,
                    "repairs": [],
                }
            ],
        },
    )
    fingerprints = {
        condition: {
            task: MODULE.runner_mirror_fingerprint(root / "work" / condition / task)
            for task in tasks
        }
        for condition in conditions
    }
    MODULE.atomic_json(
        root / "manifest.json",
        {
            "protocol_sha256": MODULE.sha256_file(protocol_path),
            "schedule_sha256": MODULE.sha256_file(schedule_path),
            "conditions": list(conditions),
            "planned_by_phase": {"main": len(jobs)},
            "credential_values_recorded": False,
            "mirror_fingerprints": fingerprints,
            "platform_repairs_path": str(repair_path),
            "platform_repairs_sha256": MODULE.sha256_file(repair_path),
            "benchflow_compat_entrypoint": str(compat_path),
            "benchflow_compat_sha256": MODULE.sha256_file(compat_path),
        },
    )
    gate = {
        "status": "passed",
        "final_reportable": True,
        "schedule_count_valid": True,
        "expected_rows": len(jobs),
        "terminal_rows": len(jobs),
        "missing_execution_ids": [],
        "unexpected_execution_ids": [],
        "invalid_execution_ids": [],
        "contaminated_execution_ids": [],
        "credential_reflection_execution_ids": [],
        "protocol_invalid_reasons": [],
    }
    MODULE.atomic_json(root / "main_gate.json", gate)
    if audit:
        MODULE.atomic_json(
            root / "audit_report.json",
            {
                "status": "passed",
                "final_reportable": True,
                "protocol_invalid_reasons": [],
                "main_gate": gate,
            },
        )
    root.mkdir(parents=True, exist_ok=True)
    (root / "run_state.jsonl").write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in events),
        encoding="utf-8",
    )


def selection_case(root: Path) -> tuple[argparse.Namespace, Path]:
    materials = root / "materials"
    skillsbench_root = root / "skillsbench"
    material_rows = []
    for task in [*TASKS, "pilot-task"]:
        official = skillsbench_root / "tasks" / task / "environment" / "skills"
        preserving = materials / "candidate_pool" / "P" / task / "skills"
        destructive = materials / "candidate_pool" / "D" / task / "skills"
        for destination, marker in (
            (official, "official"),
            (preserving, "preserving"),
            (destructive, "destructive"),
        ):
            skill = destination / "core" / "SKILL.md"
            skill.parent.mkdir(parents=True, exist_ok=True)
            skill.write_text(f"---\nname: core\n---\n{marker}-{task}\n", encoding="utf-8")
        material_rows.append(
            {
                "task_id": task,
                "official_skills_sha256": MODULE.sha256_tree_contents(official),
                "P_skills_sha256": MODULE.sha256_tree_contents(preserving),
                "D_skills_sha256": MODULE.sha256_tree_contents(destructive),
            }
        )
    labels_path = materials / "blind_labels.json"
    blind_labels(labels_path)
    screen_protocol_path = materials / "screen_protocol.json"
    MODULE.atomic_json(
        screen_protocol_path,
        {
            "selection_seed": "screen-seed",
            "skillsbench": {
                "root": str(skillsbench_root),
                "commit": "commit",
                "task_set": "skillsbench-v1.1",
            },
            "executor": {
                "agent": "codex-acp",
                "model": "gpt-5.6-sol",
                "conditions": ["B", "F"],
            },
            "pilot": {"tasks": ["pilot-task"], "repetitions": 1},
            "main": {"tasks": TASKS, "repetitions": 3},
        },
    )
    MODULE.atomic_json(
        materials / "materials_manifest.json",
        {
            "pilot_task": "pilot-task",
            "confirmatory_repetitions_per_arm": 2,
            "tasks": material_rows,
            "decision_policy": {
                "b_max": 0,
                "f_min": 2,
                "s_min": 0,
                "noninferiority_margin": 0.7,
            },
        },
    )
    screen_run = root / "screen-run"
    prepared_run(
        screen_run,
        screen_protocol_path,
        TASKS,
        ("B", "F"),
        3,
        lambda _task, condition, _repetition: 0.0 if condition == "B" else 1.0,
        audit=False,
    )
    return (
        argparse.Namespace(
            materials=materials,
            screen_run=screen_run,
            blind_labels=labels_path,
            output=root / "selection-output",
        ),
        labels_path,
    )


def confirm_case(root: Path) -> tuple[argparse.Namespace, Path, Path]:
    select_args, labels_path = selection_case(root)
    MODULE.select_tasks(select_args)
    protocol_path = select_args.output / "confirm_materials" / "protocol.json"
    protocol = MODULE.load_json(protocol_path)
    confirm_run = root / "confirm-run"
    prepared_run(
        confirm_run,
        protocol_path,
        TASKS,
        MODULE.ARMS,
        2,
        lambda _task, condition, _repetition: 1.0 if condition in {"F", "P"} else 0.0,
        audit=True,
    )
    return (
        argparse.Namespace(
            protocol=protocol_path,
            confirm_run=confirm_run,
            output=root / "final-output",
        ),
        labels_path,
        select_args.output / "selection.json",
    )


def amended_selection_case(root: Path) -> tuple[argparse.Namespace, Path]:
    args, _ = selection_case(root)
    materials = args.materials
    original_labels = materials / "blind_labels.json"
    blind_labels(
        original_labels,
        tasks=["sec-financial-report"],
        reviewers=("original-a", "original-b"),
        sec_p_label="destructive",
    )

    amendment_dir = materials / "amendments" / "sec_p2_v1"
    effective_pool = amendment_dir / "effective_candidate_pool" / "P"
    shutil.copytree(materials / "candidate_pool" / "P", effective_pool)
    p2 = effective_pool / "sec-financial-report" / "skills" / "core" / "SKILL.md"
    p2.write_text("---\nname: core\n---\npreserving-sec-p2\n", encoding="utf-8")
    contract = {
        "identity": "independent SkillReducer implementation",
        "commit": "reducer-commit",
        "mode": "heuristic/no-llm",
        "stage": 1,
        "tscg": False,
        "configuration": {"use_llm": False, "tscg_enabled": False},
    }
    contract_path = amendment_dir / "generator_contract.json"
    MODULE.atomic_json(contract_path, contract)
    material_manifest_path = materials / "materials_manifest.json"
    screen_protocol_path = materials / "screen_protocol.json"
    manifest = MODULE.load_json(material_manifest_path)
    sec_row = next(row for row in manifest["tasks"] if row["task_id"] == "sec-financial-report")
    amendment = {
        "schema_version": MODULE.AMENDMENT_SCHEMA,
        "task_id": "sec-financial-report",
        "trigger": "unanimous-destructive-specification-label",
        "one_shot": True,
        "no_further_regeneration": True,
        "outcome_access": "prohibited",
        "candidate_outcomes_used": False,
        "base_bindings": {
            "materials_manifest_sha256": MODULE.sha256_file(material_manifest_path),
            "screen_protocol_sha256": MODULE.sha256_file(screen_protocol_path),
            "original_blind_labels_sha256": MODULE.sha256_file(original_labels),
        },
        "source": {"official_skills_sha256": sec_row["official_skills_sha256"]},
        "generator": contract,
        "generator_contract_sha256": MODULE.sha256_file(contract_path),
        "candidate": {
            "P1_skills_sha256": sec_row["P_skills_sha256"],
            "P2_skills_sha256": MODULE.sha256_tree_contents(
                effective_pool / "sec-financial-report" / "skills"
            ),
            "D_skills_sha256": sec_row["D_skills_sha256"],
            "effective_P_pool_sha256": MODULE.sha256_tree_contents(effective_pool),
        },
        "paths": {
            "effective_P_pool": "effective_candidate_pool/P",
            "new_blind_labels": "blind_labels.json",
        },
    }
    amendment_path = amendment_dir / "amendment.json"
    MODULE.atomic_json(amendment_path, amendment)
    new_labels = amendment_dir / "blind_labels.json"
    blind_labels(
        new_labels,
        reviewers=("fresh-a", "fresh-b"),
        sec_p_label="intended-preserving",
    )
    label_payload = MODULE.load_json(new_labels)
    label_payload["input_bindings"] = {
        "tasks": list(TASKS),
        "effective_P_pool": {
            "tree_sha256": MODULE.sha256_tree_contents(effective_pool),
            "task_skills_sha256": {
                row["task_id"]: MODULE.sha256_tree_contents(
                    effective_pool / row["task_id"] / "skills"
                )
                for row in manifest["tasks"]
                if row["task_id"] in TASKS
            },
        },
        "D_pool": {
            "task_skills_sha256": {
                row["task_id"]: row["D_skills_sha256"]
                for row in manifest["tasks"]
                if row["task_id"] in TASKS
            }
        },
        "skillsbench_public_inputs": {
            "official_skills_sha256": {
                row["task_id"]: row["official_skills_sha256"]
                for row in manifest["tasks"]
                if row["task_id"] in TASKS
            }
        },
    }
    MODULE.atomic_json(new_labels, label_payload)
    args.blind_labels = new_labels
    args.amendment = amendment_dir
    return args, amendment_path


class CandidateValidationAnalysisTests(unittest.TestCase):
    def test_all_success_pair_meets_round5_margin(self):
        result = MODULE.decide(
            0,
            48,
            48,
            48,
            {"b_max": 5, "f_min": 43, "s_min": 43, "noninferiority_margin": 2 / 18},
        )
        self.assertEqual(result["state"], "Accept")
        self.assertAlmostEqual(result["ci_low"], -0.0741, places=3)
        self.assertAlmostEqual(result["ci_high"], 0.0741, places=3)

    def test_ordered_gates_withhold_and_reject(self):
        policy = {"b_max": 5, "f_min": 43, "s_min": 43, "noninferiority_margin": 2 / 18}
        self.assertEqual(MODULE.decide(6, 48, 48, 48, policy)["state"], "baseline-inconclusive")
        self.assertEqual(MODULE.decide(0, 42, 48, 48, policy)["state"], "full-inconclusive")
        self.assertEqual(MODULE.decide(0, 48, 0, 48, policy)["state"], "RejectCandidate")

    def test_selection_writes_once_and_materializes_acyclic_runner_protocol(self):
        with tempfile.TemporaryDirectory() as tmp:
            args, _ = selection_case(Path(tmp))
            with mock.patch.object(MODULE, "atomic_json", wraps=MODULE.atomic_json) as writer:
                result = MODULE.select_tasks(args)

            selection_path = args.output / "selection.json"
            protocol_path = args.output / "confirm_materials" / "protocol.json"
            bundle_path = args.output / "bundle_manifest.json"
            selection = MODULE.load_json(selection_path)
            protocol = MODULE.load_json(protocol_path)
            bundle = MODULE.load_json(bundle_path)
            selection_writes = [
                call for call in writer.call_args_list if call.args[0] == selection_path
            ]

            self.assertEqual(result["status"], "passed")
            self.assertEqual(len(selection_writes), 1)
            self.assertNotIn("confirm_protocol_sha256", selection)
            self.assertEqual(selection["confirm_protocol"], str(protocol_path.resolve()))
            self.assertEqual(protocol["selection_record"], str(selection_path.resolve()))
            self.assertEqual(
                protocol["selection_record_sha256"], MODULE.sha256_file(selection_path)
            )
            self.assertEqual(bundle["selection_sha256"], MODULE.sha256_file(selection_path))
            self.assertEqual(bundle["protocol_sha256"], MODULE.sha256_file(protocol_path))

    def test_selection_binds_outcome_blind_amendment_effective_p2_and_fresh_labels(self):
        with tempfile.TemporaryDirectory() as tmp:
            args, amendment_path = amended_selection_case(Path(tmp))
            result = MODULE.select_tasks(args)

            self.assertEqual("passed", result["status"])
            selection = MODULE.load_json(args.output / "selection.json")
            protocol = MODULE.load_json(args.output / "confirm_materials" / "protocol.json")
            binding = {
                "path": str(amendment_path.resolve()),
                "sha256": MODULE.sha256_file(amendment_path),
            }
            self.assertEqual(binding, selection["candidate_amendment"])
            self.assertEqual(binding, protocol["candidate_amendment"])
            self.assertEqual(
                str((amendment_path.parent / "effective_candidate_pool" / "P").resolve()),
                protocol["candidate_pools"]["P"],
            )
            sec_hash = next(
                row["P_skills_sha256"]
                for row in protocol["candidate_hashes"]
                if row["task_id"] == "sec-financial-report"
            )
            self.assertEqual(
                MODULE.sha256_tree_contents(
                    amendment_path.parent
                    / "effective_candidate_pool"
                    / "P"
                    / "sec-financial-report"
                    / "skills"
                ),
                sec_hash,
            )
            self.assertTrue(protocol["evidence_boundary"]["candidate_frozen_before_confirmatory"])
            self.assertFalse(protocol["evidence_boundary"]["candidate_frozen_before_screening"])

    def test_selection_rejects_tampered_amendment_or_reused_reviewer(self):
        with tempfile.TemporaryDirectory() as tmp:
            args, amendment_path = amended_selection_case(Path(tmp))
            amendment = MODULE.load_json(amendment_path)
            amendment["generator"]["stage"] = 2
            MODULE.atomic_json(amendment_path, amendment)
            with self.assertRaisesRegex(RuntimeError, "not stage 1"):
                MODULE.select_tasks(args)

        with tempfile.TemporaryDirectory() as tmp:
            args, _ = amended_selection_case(Path(tmp))
            blind_labels(
                args.blind_labels,
                reviewers=("original-a", "fresh-b"),
                sec_p_label="intended-preserving",
            )
            with self.assertRaisesRegex(RuntimeError, "reused an original SEC reviewer"):
                MODULE.select_tasks(args)

    def test_final_hard_checks_evidence_and_reports_deferrals(self):
        with tempfile.TemporaryDirectory() as tmp:
            args, _, _ = confirm_case(Path(tmp))
            report = MODULE.analyze_confirmatory(args)

            self.assertEqual(report["status"], "complete")
            self.assertEqual(report["deferrals"], 2)
            self.assertEqual(
                sum(1 for row in report["decisions"] if row["deferred"]), 2
            )
            self.assertIn("Deferred candidate decisions: 2", (args.output / "REPORT.md").read_text())

    def test_final_rejects_stale_selection_and_blind_label_hashes(self):
        with tempfile.TemporaryDirectory() as tmp:
            args, _, selection_path = confirm_case(Path(tmp))
            selection = MODULE.load_json(selection_path)
            selection["tampered"] = True
            MODULE.atomic_json(selection_path, selection)
            with self.assertRaisesRegex(RuntimeError, "selection record hash"):
                MODULE.analyze_confirmatory(args)

        with tempfile.TemporaryDirectory() as tmp:
            args, labels_path, _ = confirm_case(Path(tmp))
            labels = MODULE.load_json(labels_path)
            labels["tampered"] = True
            MODULE.atomic_json(labels_path, labels)
            with self.assertRaisesRegex(RuntimeError, "blind-label hash"):
                MODULE.analyze_confirmatory(args)

    def test_final_rejects_duplicate_repetition_even_when_gate_claims_passed(self):
        with tempfile.TemporaryDirectory() as tmp:
            args, _, _ = confirm_case(Path(tmp))
            run_state = args.confirm_run / "run_state.jsonl"
            rows = [json.loads(line) for line in run_state.read_text().splitlines()]
            target = next(
                row
                for row in rows
                if row["event"] == "finish"
                and row["task_id"] == TASKS[0]
                and row["condition"] == "B"
                and row["repetition"] == 2
            )
            target["repetition"] = 1
            run_state.write_text(
                "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(RuntimeError, "scheduled cell changed"):
                MODULE.analyze_confirmatory(args)

    def test_final_requires_matching_manifest_and_passed_audit(self):
        with tempfile.TemporaryDirectory() as tmp:
            args, _, _ = confirm_case(Path(tmp))
            manifest_path = args.confirm_run / "manifest.json"
            manifest = MODULE.load_json(manifest_path)
            manifest["protocol_sha256"] = "0" * 64
            MODULE.atomic_json(manifest_path, manifest)
            with self.assertRaisesRegex(RuntimeError, "manifest protocol hash"):
                MODULE.analyze_confirmatory(args)

        with tempfile.TemporaryDirectory() as tmp:
            args, _, _ = confirm_case(Path(tmp))
            audit_path = args.confirm_run / "audit_report.json"
            audit = MODULE.load_json(audit_path)
            audit["status"] = "failed"
            MODULE.atomic_json(audit_path, audit)
            with self.assertRaisesRegex(RuntimeError, "audit did not pass"):
                MODULE.analyze_confirmatory(args)

    def test_final_rejects_tampered_candidate_source_or_run_mirror(self):
        with tempfile.TemporaryDirectory() as tmp:
            args, _, _ = confirm_case(Path(tmp))
            protocol = MODULE.load_json(args.protocol)
            candidate = (
                Path(protocol["candidate_pools"]["P"])
                / TASKS[0]
                / "skills"
                / "core"
                / "SKILL.md"
            )
            candidate.write_text(candidate.read_text(encoding="utf-8") + "tampered\n", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "frozen source hash mismatch"):
                MODULE.analyze_confirmatory(args)

        with tempfile.TemporaryDirectory() as tmp:
            args, _, _ = confirm_case(Path(tmp))
            mirror = (
                args.confirm_run
                / "work"
                / "D"
                / TASKS[0]
                / "environment"
                / "skills"
                / "core"
                / "SKILL.md"
            )
            mirror.write_text(mirror.read_text(encoding="utf-8") + "tampered\n", encoding="utf-8")
            with self.assertRaisesRegex(
                RuntimeError, "run mirror differs|mirror fingerprint mismatch"
            ):
                MODULE.analyze_confirmatory(args)

    def test_final_rejects_non_skill_mirror_drift_and_repair_overlap(self):
        with tempfile.TemporaryDirectory() as tmp:
            args, _, _ = confirm_case(Path(tmp))
            task_md = args.confirm_run / "work" / "F" / TASKS[0] / "task.md"
            task_md.write_text("drift\n", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "mirror fingerprint mismatch"):
                MODULE.analyze_confirmatory(args)

        with tempfile.TemporaryDirectory() as tmp:
            args, _, _ = confirm_case(Path(tmp))
            ledger_path = args.confirm_run / "platform_repairs.json"
            ledger = MODULE.load_json(ledger_path)
            target = args.confirm_run / "work" / "F" / TASKS[0] / "task.md"
            payload = target.read_bytes()
            ledger["events"] = [
                {
                    "created_at": "2026-07-27T00:00:30+00:00",
                    "repaired_file_count": 1,
                    "repairs": [
                        {
                            "condition": "F",
                            "task_id": TASKS[0],
                            "path": "task.md",
                            "after_sha256": MODULE.sha256_file(target),
                        }
                    ],
                }
            ]
            ledger["event_count"] = 1
            ledger["repaired_file_count"] = 1
            MODULE.atomic_json(ledger_path, ledger)
            manifest_path = args.confirm_run / "manifest.json"
            manifest = MODULE.load_json(manifest_path)
            manifest["platform_repairs_sha256"] = MODULE.sha256_file(ledger_path)
            MODULE.atomic_json(manifest_path, manifest)
            with self.assertRaisesRegex(RuntimeError, "overlapped a mirror repair"):
                MODULE.analyze_confirmatory(args)


if __name__ == "__main__":
    unittest.main()
