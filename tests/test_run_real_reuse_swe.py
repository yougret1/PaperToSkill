import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PREP_SCRIPT = ROOT / "scripts" / "prepare_real_reuse_swe_fixture.py"
RUN_SCRIPT = ROOT / "scripts" / "run_real_reuse_swe.py"
sys.path.insert(0, str(ROOT / "scripts"))

from run_real_reuse_swe import build_prompt  # noqa: E402


PATCH_RESPONSE = """```diff
diff --git a/buggy.py b/buggy.py
--- a/buggy.py
+++ b/buggy.py
@@ -1,2 +1,2 @@
 def add(a, b):
-    return a - b
+    return a + b
```
"""


def write_tiny_repo(path: Path) -> None:
    path.mkdir(parents=True)
    (path / "buggy.py").write_text("def add(a, b):\n    return a - b\n", encoding="utf-8")
    (path / "test_buggy.py").write_text(
        "\n".join(
            [
                "import unittest",
                "from buggy import add",
                "",
                "class BuggyTest(unittest.TestCase):",
                "    def test_add(self):",
                "        self.assertEqual(add(2, 3), 5)",
                "",
                "if __name__ == '__main__':",
                "    unittest.main()",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def prepare_temp_root(tmp_path: Path, task_id: str = "SWE-T2") -> Path:
    root = tmp_path / "root"
    for relative_dir in [
        "benchmarks/real_reuse/tasks",
        "benchmarks/real_reuse/asset_locks",
        "generated_skills/real_reuse/swe_agent",
        "baselines/real_reuse",
        "papers/extracted",
    ]:
        (root / relative_dir).mkdir(parents=True)
    shutil.copy2(ROOT / "benchmarks" / "real_reuse" / "tasks" / f"{task_id}.json", root / "benchmarks" / "real_reuse" / "tasks" / f"{task_id}.json")
    shutil.copy2(ROOT / "benchmarks" / "real_reuse" / "asset_locks" / f"{task_id}.json", root / "benchmarks" / "real_reuse" / "asset_locks" / f"{task_id}.json")
    (root / "generated_skills" / "real_reuse" / "swe_agent" / "SKILL.md").write_text(
        "# SWE-agent Skill\n\nUse search, edit command, linter feedback, and tests.\n",
        encoding="utf-8",
    )
    (root / "papers" / "extracted" / "swe_agent.txt").write_text(
        "Full SWE-agent paper excerpt with repository inspection, edit commands, and test verification.\n",
        encoding="utf-8",
    )
    repo = tmp_path / "repo"
    write_tiny_repo(repo)
    subprocess.run(
        [
            sys.executable,
            str(PREP_SCRIPT),
            "--root",
            str(root),
            "--task",
            task_id,
            "--repo-source",
            str(repo),
            "--issue-text",
            "The add helper fails the target unit test.",
            "--test-command",
            "python -m unittest discover -s .",
            "--output-dir",
            str(root / "benchmarks" / "real_reuse" / "assets" / task_id),
            "--condition-dir",
            str(root / "baselines" / "real_reuse"),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return root


class RunRealReuseSWETest(unittest.TestCase):
    def test_fixture_response_produces_scored_raw_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            root = prepare_temp_root(tmp_path)
            fixture_dir = tmp_path / "fixture_responses"
            fixture_dir.mkdir()
            for condition in ("summary", "papertoskill"):
                (fixture_dir / f"SWE-T2_{condition}.diff").write_text(PATCH_RESPONSE, encoding="utf-8")
            raw_rows = tmp_path / "raw_rows.jsonl"
            output_json = tmp_path / "swe_report.json"

            completed = subprocess.run(
                [
                    sys.executable,
                    str(RUN_SCRIPT),
                    "--root",
                    str(root),
                    "--task",
                    "SWE-T2",
                    "--condition",
                    "summary",
                    "--condition",
                    "papertoskill",
                    "--fixture-response-dir",
                    str(fixture_dir),
                    "--run-id",
                    "unit_swe_fixture_run",
                    "--output-dir",
                    str(tmp_path / "runs"),
                    "--raw-rows-output",
                    str(raw_rows),
                    "--output-json",
                    str(output_json),
                    "--output-md",
                    str(tmp_path / "swe_report.md"),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            self.assertIn("unit_swe_fixture_run", completed.stdout)
            report = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertEqual("complete", report["overall_status"])
            rows = [json.loads(line) for line in raw_rows.read_text(encoding="utf-8").splitlines()]
            self.assertEqual(2, len(rows))
            self.assertEqual({"summary", "papertoskill"}, {row["condition"] for row in rows})
            self.assertTrue(all(row["success"] for row in rows))
            self.assertTrue((tmp_path / "runs" / "SWE-T2" / "summary" / "unit_swe_fixture_run" / "metric.json").exists())

    def test_missing_credentials_records_pending_without_raw_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            root = prepare_temp_root(tmp_path)
            raw_rows = tmp_path / "raw_rows.jsonl"
            output_json = tmp_path / "swe_report.json"

            subprocess.run(
                [
                    sys.executable,
                    str(RUN_SCRIPT),
                    "--root",
                    str(root),
                    "--task",
                    "SWE-T2",
                    "--condition",
                    "summary",
                    "--base-url-env",
                    "PAPERTOSKILL_UNITTEST_MISSING_BASE_URL",
                    "--api-key-env",
                    "PAPERTOSKILL_UNITTEST_MISSING_API_KEY",
                    "--run-id",
                    "unit_swe_missing_credentials",
                    "--output-dir",
                    str(tmp_path / "runs"),
                    "--raw-rows-output",
                    str(raw_rows),
                    "--output-json",
                    str(output_json),
                    "--output-md",
                    str(tmp_path / "swe_report.md"),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            report = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertEqual("pending", report["overall_status"])
            self.assertFalse(raw_rows.exists())
            self.assertIn("missing_base_url_or_api_key_env", report["results"][0]["failure_reason"])

    def test_missing_fixture_records_pending_without_raw_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            root = tmp_path / "root"
            for relative_dir in [
                "benchmarks/real_reuse/tasks",
                "benchmarks/real_reuse/asset_locks",
                "generated_skills/real_reuse/swe_agent",
                "baselines/real_reuse",
            ]:
                (root / relative_dir).mkdir(parents=True)
            shutil.copy2(ROOT / "benchmarks" / "real_reuse" / "tasks" / "SWE-T2.json", root / "benchmarks" / "real_reuse" / "tasks" / "SWE-T2.json")
            raw_rows = tmp_path / "raw_rows.jsonl"
            output_json = tmp_path / "swe_report.json"

            subprocess.run(
                [
                    sys.executable,
                    str(RUN_SCRIPT),
                    "--root",
                    str(root),
                    "--task",
                    "SWE-T2",
                    "--condition",
                    "summary",
                    "--run-id",
                    "unit_swe_missing_fixture",
                    "--output-dir",
                    str(tmp_path / "runs"),
                    "--raw-rows-output",
                    str(raw_rows),
                    "--output-json",
                    str(output_json),
                    "--output-md",
                    str(tmp_path / "swe_report.md"),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            report = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertEqual("pending", report["overall_status"])
            self.assertFalse(raw_rows.exists())
            self.assertEqual("missing_fixture_assets", report["results"][0]["failure_reason"])

    def test_prompt_uses_condition_context_without_hidden_assets(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = prepare_temp_root(Path(tmp))
            prompt = build_prompt(root, "SWE-T2", "summary")

            self.assertIn("Real-Reuse Condition: summary", prompt)
            self.assertIn("Summary Baseline", prompt)
            self.assertIn("SWE-T2 Locked SWE-agent Task Prompt", prompt)
            self.assertIn("unified diff patch", prompt)
            self.assertNotIn("gold_patch", prompt)
            self.assertNotIn("hidden_from_model", prompt)

    def test_full_excerpt_fixture_response_for_sanity_task(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            root = prepare_temp_root(tmp_path, "SWE-T1")
            fixture_dir = tmp_path / "fixture_responses"
            fixture_dir.mkdir()
            (fixture_dir / "SWE-T1_full_excerpt.diff").write_text(PATCH_RESPONSE, encoding="utf-8")
            raw_rows = tmp_path / "raw_rows.jsonl"
            output_json = tmp_path / "swe_report.json"

            subprocess.run(
                [
                    sys.executable,
                    str(RUN_SCRIPT),
                    "--root",
                    str(root),
                    "--task",
                    "SWE-T1",
                    "--condition",
                    "full_excerpt",
                    "--fixture-response-dir",
                    str(fixture_dir),
                    "--run-id",
                    "unit_swe_full_excerpt",
                    "--output-dir",
                    str(tmp_path / "runs"),
                    "--raw-rows-output",
                    str(raw_rows),
                    "--output-json",
                    str(output_json),
                    "--output-md",
                    str(tmp_path / "swe_report.md"),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            report = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertEqual("complete", report["overall_status"])
            rows = [json.loads(line) for line in raw_rows.read_text(encoding="utf-8").splitlines()]
            self.assertEqual(["full_excerpt"], [row["condition"] for row in rows])
            self.assertTrue(rows[0]["success"])
            prompt = (tmp_path / "runs" / "SWE-T1" / "full_excerpt" / "unit_swe_full_excerpt" / "prompt.md").read_text(encoding="utf-8")
            self.assertIn("Full SWE-agent paper excerpt", prompt)


if __name__ == "__main__":
    unittest.main()
