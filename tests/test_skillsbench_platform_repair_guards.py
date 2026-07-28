import contextlib
import importlib.util
import io
import shutil
import sys
import tempfile
import unittest
from dataclasses import asdict
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "run_skillsbench_bfs_sol.py"
SPEC = importlib.util.spec_from_file_location(
    "run_skillsbench_bfs_sol_platform_repair_guards", SCRIPT
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


NON_SKILL_CRLF = b"#!/bin/sh\r\nset -eu\r\n"
SKILL_CRLF = b"#!/bin/sh\r\necho skill\r\n"


def create_prepared_run(root: Path, task_ids=("task-a",)) -> dict[str, dict[str, Path]]:
    jobs = []
    paths: dict[str, dict[str, Path]] = {}
    for position, task_id in enumerate(task_ids, start=1):
        source = root / "source" / task_id
        source_environment = source / "environment"
        source_skill = source_environment / "skills" / "alpha"
        source_skill.mkdir(parents=True)
        (source / "task.md").write_text("prompt\n", encoding="utf-8")
        (source_environment / "Dockerfile").write_text(
            "FROM ubuntu:24.04\nCOPY skills /skills\n", encoding="utf-8"
        )
        source_script = source_environment / "setup.sh"
        source_skill_script = source_skill / "helper.sh"
        source_script.write_bytes(NON_SKILL_CRLF)
        source_skill_script.write_bytes(SKILL_CRLF)

        mirror = root / "work" / "F" / task_id
        mirror.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source, mirror)
        jobs.append(
            MODULE.Job(
                execution_id=f"exec-{task_id}",
                block_id=f"block-{task_id}",
                phase="main",
                repetition=1,
                task_id=task_id,
                condition="F",
                condition_position=1,
                task_position=position,
                source_task_dir=str(source),
                mirror_task_dir=str(mirror),
                skills_dir=str(mirror / "environment" / "skills"),
                jobs_dir=str(root / "jobs" / task_id),
            )
        )
        paths[task_id] = {
            "source_script": source_script,
            "source_skill_script": source_skill_script,
            "mirror": mirror,
            "mirror_script": mirror / "environment" / "setup.sh",
            "mirror_skill_script": mirror
            / "environment"
            / "skills"
            / "alpha"
            / "helper.sh",
        }

    schedule_path = root / "schedule.json"
    MODULE.atomic_json(
        schedule_path,
        {
            "schema_version": "skillsbench-bfs-schedule-v1",
            "jobs": [asdict(job) for job in jobs],
        },
    )
    initial_event = {
        "created_at": "2026-07-28T00:00:00+00:00",
        "include_skill_shells": False,
        "checked_mirrors": len(jobs),
        "selected_conditions": ["F"],
        "selected_tasks": list(task_ids),
        "repaired_file_count": 0,
        "repairs": [],
    }
    repairs_path = root / "platform_repairs.json"
    MODULE.atomic_json(
        repairs_path,
        {
            "schema_version": "skillsbench-bfs-platform-repairs-v2",
            "created_at": initial_event["created_at"],
            "scope": "prepared task mirrors; each event records whether skill trees were included",
            "event_count": 1,
            "repaired_file_count": 0,
            "events": [initial_event],
        },
    )
    MODULE.atomic_json(
        root / "manifest.json",
        {
            "schema_version": MODULE.SCHEMA_VERSION,
            "planned_jobs": len(jobs),
            "schedule_sha256": MODULE.sha256_file(schedule_path),
            "mirror_fingerprints": {
                "F": {
                    task_id: MODULE.mirror_fingerprint(paths[task_id]["mirror"])
                    for task_id in task_ids
                }
            },
            "platform_repairs_path": str(repairs_path),
            "platform_repairs_sha256": MODULE.sha256_file(repairs_path),
        },
    )
    return paths


def run_repair(root: Path, *extra_args: str) -> tuple[int, str, str]:
    stdout = io.StringIO()
    stderr = io.StringIO()
    argv = ["repair-windows-shells", "--run-root", str(root), *extra_args]
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        result = MODULE.main(argv)
    return result, stdout.getvalue(), stderr.getvalue()


class SkillsBenchPlatformRepairGuardTests(unittest.TestCase):
    def test_repeated_repairs_append_events_instead_of_overwriting_history(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            create_prepared_run(root)

            first_result, _, first_stderr = run_repair(root)
            self.assertEqual(first_result, 0, first_stderr)
            first_report = MODULE.load_json(root / "platform_repairs.json")
            retained_events = first_report["events"][:]
            self.assertEqual(first_report["event_count"], 2)
            self.assertEqual(first_report["events"][1]["repaired_file_count"], 1)

            second_result, _, second_stderr = run_repair(root)
            self.assertEqual(second_result, 0, second_stderr)
            second_report = MODULE.load_json(root / "platform_repairs.json")

            self.assertEqual(second_report["event_count"], 3)
            self.assertEqual(second_report["events"][:2], retained_events)
            self.assertEqual(second_report["events"][2]["repaired_file_count"], 0)
            self.assertEqual(second_report["repaired_file_count"], 1)

    def test_latest_unfinished_start_for_selected_mirror_blocks_repair(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = create_prepared_run(root)
            before_manifest = (root / "manifest.json").read_bytes()
            before_repairs = (root / "platform_repairs.json").read_bytes()
            MODULE.append_jsonl(
                root / "run_state.jsonl",
                {
                    "event": "finish",
                    "execution_id": "exec-task-a",
                    "attempt_number": 1,
                    "status": "scored",
                },
            )
            MODULE.append_jsonl(
                root / "run_state.jsonl",
                {
                    "event": "start",
                    "execution_id": "exec-task-a",
                    "attempt_number": 2,
                    "status": "running",
                },
            )

            result, _, stderr = run_repair(
                root, "--condition", "F", "--task", "task-a"
            )

            self.assertEqual(result, 2)
            self.assertIn("cannot repair mirrors with active executions", stderr)
            self.assertEqual(paths["task-a"]["mirror_script"].read_bytes(), NON_SKILL_CRLF)
            self.assertEqual((root / "manifest.json").read_bytes(), before_manifest)
            self.assertEqual((root / "platform_repairs.json").read_bytes(), before_repairs)

    def test_skill_shells_require_explicit_flag_and_sources_stay_unchanged(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = create_prepared_run(root)
            task = paths["task-a"]

            default_result, _, default_stderr = run_repair(root)
            self.assertEqual(default_result, 0, default_stderr)
            self.assertEqual(
                task["mirror_script"].read_bytes(),
                NON_SKILL_CRLF.replace(b"\r\n", b"\n"),
            )
            self.assertEqual(task["mirror_skill_script"].read_bytes(), SKILL_CRLF)
            self.assertEqual(task["source_script"].read_bytes(), NON_SKILL_CRLF)
            self.assertEqual(task["source_skill_script"].read_bytes(), SKILL_CRLF)

            flagged_result, _, flagged_stderr = run_repair(
                root, "--include-skill-shells"
            )
            self.assertEqual(flagged_result, 0, flagged_stderr)
            self.assertEqual(
                task["mirror_skill_script"].read_bytes(),
                SKILL_CRLF.replace(b"\r\n", b"\n"),
            )
            self.assertEqual(task["source_script"].read_bytes(), NON_SKILL_CRLF)
            self.assertEqual(task["source_skill_script"].read_bytes(), SKILL_CRLF)

    def test_manifest_binds_repair_ledger_and_updated_mirror_fingerprints(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = create_prepared_run(root, task_ids=("task-a", "task-b"))
            task_b_before = MODULE.mirror_fingerprint(paths["task-b"]["mirror"])

            result, _, stderr = run_repair(
                root, "--condition", "F", "--task", "task-a"
            )
            self.assertEqual(result, 0, stderr)
            manifest = MODULE.load_json(root / "manifest.json")

            self.assertEqual(
                manifest["platform_repairs_sha256"],
                MODULE.sha256_file(root / "platform_repairs.json"),
            )
            self.assertEqual(
                manifest["mirror_fingerprints"]["F"]["task-a"],
                MODULE.mirror_fingerprint(paths["task-a"]["mirror"]),
            )
            self.assertEqual(
                manifest["mirror_fingerprints"]["F"]["task-b"], task_b_before
            )
            prepared_manifest, prepared_jobs = MODULE.read_prepared(root)
            self.assertEqual(prepared_manifest, manifest)
            self.assertEqual(len(prepared_jobs), 2)


if __name__ == "__main__":
    unittest.main()
