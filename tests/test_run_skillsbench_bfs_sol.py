import argparse
import asyncio
import importlib.util
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "run_skillsbench_bfs_sol.py"
SPEC = importlib.util.spec_from_file_location("run_skillsbench_bfs_sol", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def write_task(root: Path, skill_body: str = "source") -> Path:
    task = root / "task"
    (task / "environment" / "skills" / "alpha").mkdir(parents=True)
    (task / "environment" / "skills" / "alpha" / "SKILL.md").write_text(
        skill_body, encoding="utf-8"
    )
    (task / "task.md").write_text("prompt\n", encoding="utf-8")
    (task / "environment" / "Dockerfile").write_text(
        "FROM ubuntu:24.04\nCOPY skills /skills\nCOPY data /root/data\n",
        encoding="utf-8",
    )
    return task


def phase_jobs(root: Path, phase: str, task_count: int, repetitions: int) -> list:
    jobs = []
    task_position = 0
    for task_index in range(1, task_count + 1):
        task_id = f"{phase}-task-{task_index:02d}"
        (root / "work" / "B" / task_id).mkdir(parents=True, exist_ok=True)
        task_position += 1
        for repetition in range(1, repetitions + 1):
            block_id = f"{phase}-{task_id}-r{repetition}"
            for condition_position, condition in enumerate(MODULE.CONDITIONS, 1):
                execution_id = f"{block_id}-{condition}"
                jobs.append(
                    MODULE.Job(
                        execution_id=execution_id,
                        block_id=block_id,
                        phase=phase,
                        repetition=repetition,
                        task_id=task_id,
                        condition=condition,
                        condition_position=condition_position,
                        task_position=task_position,
                        source_task_dir=str(root / "source" / task_id),
                        mirror_task_dir=str(root / "work" / condition / task_id),
                        skills_dir=None,
                        jobs_dir=str(root / "jobs" / execution_id),
                    )
                )
    return jobs


def finish_event(job, **overrides):
    payload = {
        "schema_version": MODULE.SCHEMA_VERSION,
        "event": "finish",
        "timestamp": "2026-07-27T00:00:00Z",
        "execution_id": job.execution_id,
        "task_id": job.task_id,
        "condition": job.condition,
        "phase": job.phase,
        "repetition": job.repetition,
        "attempt_number": 1,
        "status": "scored",
        "invalid": False,
        "invalid_reasons": [],
        "return_code": 0,
        "infra_error": False,
        "error": None,
        "verifier_error": None,
        "official_reward": 1.0,
        "official_result_path": "result.json",
        "official_reward_path": None,
        "b_contaminated": False,
        "b_contamination_markers": [],
        "credential_reflection_detected": False,
        "credential_values_recorded": False,
    }
    payload.update(overrides)
    return payload


class SkillsBenchRunnerTests(unittest.TestCase):
    def test_condition_order_is_position_balanced_across_three_repetitions(self):
        orders = [
            MODULE.condition_order("seed", "main", "task", repetition)
            for repetition in range(1, 4)
        ]
        self.assertEqual({tuple(order) for order in orders}.__len__(), 3)
        for position in range(3):
            self.assertEqual({order[position] for order in orders}, set(MODULE.CONDITIONS))

    def test_four_condition_order_rotates_every_arm_through_every_position(self):
        conditions = ("B", "F", "P", "D")
        orders = [
            MODULE.condition_order("seed", "main", "task", repetition, conditions)
            for repetition in range(1, 5)
        ]
        for position in range(4):
            self.assertEqual({order[position] for order in orders}, set(conditions))

    def test_condition_mirrors_are_isolated(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = write_task(root)
            candidate = root / "candidate"
            (candidate / "alpha").mkdir(parents=True)
            (candidate / "alpha" / "SKILL.md").write_text("reduced", encoding="utf-8")
            (candidate / "alpha" / "template.txt").write_text("asset", encoding="utf-8")

            mirrors = {condition: root / condition for condition in MODULE.CONDITIONS}
            MODULE.prepare_mirror(source, mirrors["B"], "B", None, rebuild=False)
            MODULE.prepare_mirror(source, mirrors["F"], "F", None, rebuild=False)
            MODULE.prepare_mirror(source, mirrors["S"], "S", candidate, rebuild=False)

            self.assertFalse((mirrors["B"] / "environment" / "skills").exists())
            self.assertEqual(MODULE.audit_b_mirror(mirrors["B"]), [])
            self.assertEqual(
                (mirrors["F"] / "environment" / "skills" / "alpha" / "SKILL.md").read_text(),
                "source",
            )
            self.assertEqual(
                (mirrors["S"] / "environment" / "skills" / "alpha" / "SKILL.md").read_text(),
                "reduced",
            )
            self.assertTrue(
                (mirrors["S"] / "environment" / "skills" / "alpha" / "template.txt").is_file()
            )
            self.assertEqual((source / "environment" / "skills" / "alpha" / "SKILL.md").read_text(), "source")

    def test_named_candidate_arm_uses_its_registered_skill_tree(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = write_task(root)
            candidate = root / "candidate"
            (candidate / "alpha").mkdir(parents=True)
            (candidate / "alpha" / "SKILL.md").write_text("negative", encoding="utf-8")
            destination = root / "D"
            MODULE.prepare_mirror(source, destination, "D", candidate, rebuild=False)
            self.assertEqual(
                (destination / "environment" / "skills" / "alpha" / "SKILL.md").read_text(),
                "negative",
            )

    def test_mirror_normalizes_shells_without_mutating_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = write_task(root)
            source_script = source / "environment" / "download_papers.sh"
            skill_script = source / "environment" / "skills" / "alpha" / "helper.sh"
            source_script.write_bytes(b"#!/bin/sh\r\nset -eu\r\n")
            skill_script.write_bytes(b"#!/bin/sh\r\necho skill\r\n")

            destination = root / "F"
            MODULE.prepare_mirror(source, destination, "F", None, rebuild=False)

            self.assertEqual(source_script.read_bytes(), b"#!/bin/sh\r\nset -eu\r\n")
            self.assertEqual(skill_script.read_bytes(), b"#!/bin/sh\r\necho skill\r\n")
            self.assertEqual(
                (destination / "environment" / "download_papers.sh").read_bytes(),
                b"#!/bin/sh\nset -eu\n",
            )
            self.assertEqual(
                (destination / "environment" / "skills" / "alpha" / "helper.sh").read_bytes(),
                b"#!/bin/sh\necho skill\n",
            )
            self.assertIsNotNone(MODULE.mirror_fingerprint(destination)["task_tree_sha256"])

    def test_command_uses_locked_benchflow_python_and_exact_model(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            python = root / "python.exe"
            python.write_text("", encoding="utf-8")
            task = write_task(root)
            job = MODULE.Job(
                execution_id="e",
                block_id="b",
                phase="pilot",
                repetition=1,
                task_id="task",
                condition="S",
                condition_position=1,
                task_position=1,
                source_task_dir=str(task),
                mirror_task_dir=str(task),
                skills_dir=str(task / "environment" / "skills"),
                jobs_dir=str(root / "jobs"),
            )
            args = argparse.Namespace(benchflow_python=str(python))
            command = MODULE.command_for(job, args, root)
            self.assertEqual(command[0], str(python.resolve()))
            self.assertEqual(Path(command[1]).name, "benchflow_windows_compat.py")
            self.assertEqual(command[2:4], ["eval", "run"])
            self.assertEqual(command[command.index("--model") + 1], "gpt-5.6-sol")
            self.assertEqual(command[command.index("--skill-mode") + 1], "with-skill")
            self.assertIn("--skills-dir", command)

    def test_run_environment_maps_names_without_persisting_values(self):
        args = argparse.Namespace(api_key_env="TEST_API_KEY", base_url_env="TEST_BASE_URL")
        with mock.patch.dict(
            os.environ,
            {"TEST_API_KEY": "sk-secret-value-123456", "TEST_BASE_URL": "https://example.test/v1/"},
            clear=False,
        ):
            run_env, redactor = MODULE.build_run_env(args)
        self.assertEqual(run_env["OPENAI_BASE_URL"], "https://example.test/v1")
        self.assertEqual(run_env["PYTHONUTF8"], "1")
        self.assertEqual(run_env["PYTHONIOENCODING"], "utf-8")
        self.assertNotIn("sk-secret-value-123456", redactor.text("token=sk-secret-value-123456"))

    def test_reward_parser_accepts_benchflow_shapes(self):
        self.assertEqual(MODULE.parse_reward({"rewards": {"reward": 0.75}}), 0.75)
        self.assertEqual(MODULE.parse_reward({"verifier_result": {"reward": 1}}), 1.0)
        self.assertIsNone(MODULE.parse_reward({"reward": True}))

    def test_rerun_invalid_selects_only_latest_terminal_invalid(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            jobs = [
                MODULE.Job(
                    execution_id=execution_id,
                    block_id=execution_id,
                    phase="pilot",
                    repetition=1,
                    task_id=execution_id,
                    condition="B",
                    condition_position=1,
                    task_position=index,
                    source_task_dir=str(root),
                    mirror_task_dir=str(root),
                    skills_dir=None,
                    jobs_dir=str(root / "jobs" / execution_id),
                )
                for index, execution_id in enumerate(("scored", "invalid", "running", "new"), 1)
            ]
            for execution_id, event, status in (
                ("scored", "finish", "scored"),
                ("invalid", "finish", "invalid"),
                ("running", "start", "running"),
            ):
                MODULE.append_jsonl(
                    root / "run_state.jsonl",
                    {"execution_id": execution_id, "event": event, "status": status},
                )
            MODULE.append_jsonl(
                root / "run_state.jsonl",
                {
                    "execution_id": "invalid",
                    "event": "start",
                    "status": "running",
                    "attempt_number": 2,
                },
            )
            args = argparse.Namespace(rerun=False, rerun_invalid=True, concurrency=1)
            with mock.patch.object(MODULE, "run_one", new=mock.AsyncMock()) as run_one:
                records = asyncio.run(
                    MODULE.run_selected(jobs, args, root, root, root, {}, MODULE.Redactor({}))
                )
            self.assertEqual(run_one.await_count, 1)
            self.assertEqual(run_one.await_args.args[0].execution_id, "invalid")
            self.assertEqual(len(records), 1)

    def test_latest_finish_remains_canonical_after_orphan_start(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            job = phase_jobs(root, "pilot", 1, 1)[0]
            MODULE.append_jsonl(root / "run_state.jsonl", finish_event(job))
            MODULE.append_jsonl(
                root / "run_state.jsonl",
                {
                    "event": "start",
                    "execution_id": job.execution_id,
                    "status": "running",
                    "attempt_number": 2,
                },
            )

            self.assertEqual(MODULE.latest_events(root)[job.execution_id]["event"], "start")
            self.assertEqual(
                MODULE.latest_finish_events(root)[job.execution_id]["status"],
                "scored",
            )
            self.assertIn(job.execution_id, MODULE.terminal_execution_ids(root))
            self.assertIn(job.execution_id, MODULE.orphan_start_events(root))
            self.assertEqual(len(MODULE.finish_rows(root)), 1)

    def test_main_preflight_recomputes_stale_pilot_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            jobs = [
                *phase_jobs(root, "pilot", 5, 1),
                *phase_jobs(root, "main", 24, 3),
            ]
            MODULE.atomic_json(root / "pilot_gate.json", {"status": "passed"})

            with self.assertRaises(MODULE.RunnerError):
                MODULE.enforce_main_prerequisites(
                    root,
                    jobs,
                    allow_without_pilot=False,
                )

            current = MODULE.load_json(root / "pilot_gate.json")
            self.assertEqual(current["status"], "blocked")
            self.assertEqual(len(current["missing_execution_ids"]), 15)

    def test_main_bypass_is_persistently_protocol_invalid(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            jobs = [
                *phase_jobs(root, "pilot", 5, 1),
                *phase_jobs(root, "main", 24, 3),
            ]

            preflight = MODULE.enforce_main_prerequisites(
                root,
                jobs,
                allow_without_pilot=True,
            )

            self.assertTrue(preflight["protocol_invalid"])
            self.assertEqual(
                MODULE.protocol_invalid_reasons(root),
                ["allow_main_without_pilot_used"],
            )
            gate = MODULE.main_gate(root, jobs)
            self.assertEqual(gate["status"], "protocol-invalid")
            self.assertFalse(gate["final_reportable"])

    def test_main_gate_requires_all_strict_canonical_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            jobs = phase_jobs(root, "main", 24, 3)
            (root / "result.json").write_text('{"reward": 1.0}\n', encoding="utf-8")
            for job in jobs:
                MODULE.append_jsonl(root / "run_state.jsonl", finish_event(job))

            passed = MODULE.main_gate(root, jobs)
            self.assertEqual(len(jobs), 216)
            self.assertEqual(passed["status"], "passed")
            self.assertTrue(passed["final_reportable"])

            first = jobs[0]
            MODULE.append_jsonl(
                root / "run_state.jsonl",
                {
                    "event": "start",
                    "execution_id": first.execution_id,
                    "attempt_number": 2,
                    "status": "running",
                },
            )
            after_orphan = MODULE.main_gate(root, jobs)
            self.assertEqual(after_orphan["status"], "passed")
            self.assertIn(first.execution_id, after_orphan["orphan_start_execution_ids"])

            MODULE.append_jsonl(
                root / "run_state.jsonl",
                finish_event(
                    first,
                    attempt_number=3,
                    credential_reflection_detected=True,
                ),
            )
            reflected = MODULE.main_gate(root, jobs)
            self.assertEqual(reflected["status"], "blocked")
            self.assertIn(
                "credential_reflection_not_cleared",
                reflected["invalid_details"][first.execution_id],
            )

            MODULE.append_jsonl(
                root / "run_state.jsonl",
                finish_event(
                    first,
                    attempt_number=4,
                    official_reward=True,
                    official_result_path="missing/result.json",
                ),
            )
            invalid_reward = MODULE.main_gate(root, jobs)
            reasons = invalid_reward["invalid_details"][first.execution_id]
            self.assertIn("invalid_official_reward", reasons)
            self.assertIn("missing_official_result_provenance", reasons)

    def test_main_preflight_blocks_static_b_contamination_even_with_bypass(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            jobs = [
                *phase_jobs(root, "pilot", 5, 1),
                *phase_jobs(root, "main", 24, 3),
            ]
            task_id = next(job.task_id for job in jobs if job.phase == "main")
            (root / "work" / "B" / task_id / "environment" / "skills").mkdir(
                parents=True
            )

            with self.assertRaises(MODULE.RunnerError):
                MODULE.enforce_main_prerequisites(
                    root,
                    jobs,
                    allow_without_pilot=True,
                )


if __name__ == "__main__":
    unittest.main()
