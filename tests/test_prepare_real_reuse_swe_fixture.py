import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "prepare_real_reuse_swe_fixture.py"


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


def prepare_temp_root(tmp_path: Path) -> Path:
    root = tmp_path / "root"
    for relative_dir in [
        "benchmarks/real_reuse/tasks",
        "benchmarks/real_reuse/asset_locks",
        "generated_skills/real_reuse/swe_agent",
        "baselines/real_reuse",
    ]:
        (root / relative_dir).mkdir(parents=True)
    shutil.copy2(ROOT / "benchmarks" / "real_reuse" / "tasks" / "SWE-T2.json", root / "benchmarks" / "real_reuse" / "tasks" / "SWE-T2.json")
    shutil.copy2(ROOT / "benchmarks" / "real_reuse" / "asset_locks" / "SWE-T2.json", root / "benchmarks" / "real_reuse" / "asset_locks" / "SWE-T2.json")
    (root / "generated_skills" / "real_reuse" / "swe_agent" / "SKILL.md").write_text(
        "# SWE-agent Skill\n\nUse search, edit, and test feedback.\n",
        encoding="utf-8",
    )
    return root


class PrepareRealReuseSWEFixtureTest(unittest.TestCase):
    def test_prepare_swe_t2_writes_visible_assets_and_hidden_gold_patch(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            root = prepare_temp_root(tmp_path)
            repo = tmp_path / "repo"
            write_tiny_repo(repo)
            gold_patch = tmp_path / "gold.patch"
            gold_patch.write_text(
                "diff --git a/buggy.py b/buggy.py\n"
                "--- a/buggy.py\n"
                "+++ b/buggy.py\n"
                "@@ -1,2 +1,2 @@\n"
                " def add(a, b):\n"
                "-    return a - b\n"
                "+    return a + b\n",
                encoding="utf-8",
            )
            test_patch = tmp_path / "test.patch"
            test_patch.write_text(
                "diff --git a/test_buggy.py b/test_buggy.py\n"
                "--- a/test_buggy.py\n"
                "+++ b/test_buggy.py\n"
                "@@ -4,6 +4,7 @@ from buggy import add\n"
                " class BuggyTest(unittest.TestCase):\n"
                "     def test_add(self):\n"
                "         self.assertEqual(add(2, 3), 5)\n"
                "+        self.assertEqual(add(1, 1), 2)\n",
                encoding="utf-8",
            )

            output_dir = root / "benchmarks" / "real_reuse" / "assets" / "SWE-T2"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--root",
                    str(root),
                    "--task",
                    "SWE-T2",
                    "--repo-source",
                    str(repo),
                    "--issue-text",
                    "The add helper fails the target unit test.",
                    "--test-command",
                    "python -m unittest discover -s .",
                    "--gold-patch",
                    str(gold_patch),
                    "--test-patch",
                    str(test_patch),
                    "--output-dir",
                    str(output_dir),
                    "--condition-dir",
                    str(root / "baselines" / "real_reuse"),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            self.assertIn("asset_manifest.json", completed.stdout)
            manifest = json.loads((output_dir / "asset_manifest.json").read_text(encoding="utf-8"))
            self.assertEqual("prepared_assets_ready_for_dry_scoring", manifest["status"])
            self.assertEqual("swe_agent", manifest["source_paper_id"])
            self.assertTrue((output_dir / "workspace" / "buggy.py").exists())
            self.assertTrue((root / "baselines" / "real_reuse" / "SWE-T2_summary.md").exists())
            hidden = set(manifest["hidden_from_model"])
            self.assertIn("benchmarks/real_reuse/assets/SWE-T2/scorer_only/gold.patch", hidden)
            self.assertIn("benchmarks/real_reuse/assets/SWE-T2/scorer_only/test.patch", hidden)
            visible_slots = {item["slot"] for item in manifest["files"] if item["visibility"] == "model_visible"}
            hidden_slots = {item["slot"] for item in manifest["files"] if item["visibility"] == "scorer_only"}
            self.assertIn("target_test_command", visible_slots)
            self.assertIn("test_patch", hidden_slots)
            self.assertTrue((output_dir / "scorer_only" / "gold.patch").exists())
            self.assertTrue((output_dir / "scorer_only" / "test.patch").exists())
            prompt = (output_dir / "task_prompt.md").read_text(encoding="utf-8")
            self.assertIn("Return a single unified diff patch", prompt)
            self.assertNotIn("gold.patch", prompt)
            self.assertNotIn("test.patch", prompt)

    def test_external_workspace_mode_does_not_copy_repo_snapshot(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            root = prepare_temp_root(tmp_path)
            repo = tmp_path / "repo"
            write_tiny_repo(repo)
            output_dir = root / "benchmarks" / "real_reuse" / "assets" / "SWE-T2"

            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--root",
                    str(root),
                    "--task",
                    "SWE-T2",
                    "--workspace-mode",
                    "external",
                    "--repo-source",
                    str(repo),
                    "--issue-text",
                    "The add helper fails the target unit test.",
                    "--test-command",
                    "python -m unittest discover -s .",
                    "--output-dir",
                    str(output_dir),
                    "--condition-dir",
                    str(root / "baselines" / "real_reuse"),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            manifest = json.loads((output_dir / "asset_manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(str(repo.resolve()).replace("\\", "/"), manifest["workspace_dir"])
            self.assertFalse((output_dir / "workspace").exists())
            self.assertTrue((output_dir / "workspace_readme.md").exists())
            visible_slots = {item["slot"] for item in manifest["files"] if item["visibility"] == "model_visible"}
            self.assertIn("workspace_readme", visible_slots)

    def test_prepare_from_swe_bench_parquet_keeps_gold_assets_hidden(self):
        with tempfile.TemporaryDirectory() as tmp:
            import pandas as pd

            tmp_path = Path(tmp)
            root = prepare_temp_root(tmp_path)
            repo = tmp_path / "repo"
            write_tiny_repo(repo)
            parquet_path = tmp_path / "swe_lite.parquet"
            pd.DataFrame(
                [
                    {
                        "instance_id": "unit__repo-1",
                        "problem_statement": "Unit issue from SWE-bench parquet.",
                        "patch": (
                            "diff --git a/buggy.py b/buggy.py\n"
                            "--- a/buggy.py\n"
                            "+++ b/buggy.py\n"
                            "@@ -1,2 +1,2 @@\n"
                            " def add(a, b):\n"
                            "-    return a - b\n"
                            "+    return a + b\n"
                        ),
                        "test_patch": (
                            "diff --git a/test_buggy.py b/test_buggy.py\n"
                            "--- a/test_buggy.py\n"
                            "+++ b/test_buggy.py\n"
                            "@@ -4,6 +4,7 @@ from buggy import add\n"
                            " class BuggyTest(unittest.TestCase):\n"
                            "     def test_add(self):\n"
                            "         self.assertEqual(add(2, 3), 5)\n"
                            "+        self.assertEqual(add(1, 1), 2)\n"
                        ),
                    }
                ]
            ).to_parquet(parquet_path)

            output_dir = root / "benchmarks" / "real_reuse" / "assets" / "SWE-T2"
            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--root",
                    str(root),
                    "--task",
                    "SWE-T2",
                    "--repo-source",
                    str(repo),
                    "--swe-bench-parquet",
                    str(parquet_path),
                    "--instance-id",
                    "unit__repo-1",
                    "--test-command",
                    "python -m unittest discover -s .",
                    "--output-dir",
                    str(output_dir),
                    "--condition-dir",
                    str(root / "baselines" / "real_reuse"),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            manifest = json.loads((output_dir / "asset_manifest.json").read_text(encoding="utf-8"))
            prompt = (output_dir / "task_prompt.md").read_text(encoding="utf-8")
            self.assertIn("Unit issue from SWE-bench parquet.", prompt)
            self.assertTrue((output_dir / "scorer_only" / "gold.patch").exists())
            self.assertTrue((output_dir / "scorer_only" / "test.patch").exists())
            self.assertIn("benchmarks/real_reuse/assets/SWE-T2/scorer_only/gold.patch", manifest["hidden_from_model"])
            self.assertIn("benchmarks/real_reuse/assets/SWE-T2/scorer_only/test.patch", manifest["hidden_from_model"])
            self.assertNotIn("return a + b", prompt)


if __name__ == "__main__":
    unittest.main()
