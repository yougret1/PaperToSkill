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
            self.assertIn(str(gold_patch.resolve()).replace("\\", "/"), hidden)
            visible_slots = {item["slot"] for item in manifest["files"] if item["visibility"] == "model_visible"}
            self.assertIn("target_test_command", visible_slots)
            prompt = (output_dir / "task_prompt.md").read_text(encoding="utf-8")
            self.assertIn("Return a single unified diff patch", prompt)
            self.assertNotIn("gold.patch", prompt)


if __name__ == "__main__":
    unittest.main()
