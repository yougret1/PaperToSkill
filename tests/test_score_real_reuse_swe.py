import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "score_real_reuse_swe.py"


def write_workspace(path: Path) -> None:
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


VALID_PATCH = """diff --git a/buggy.py b/buggy.py
--- a/buggy.py
+++ b/buggy.py
@@ -1,2 +1,2 @@
 def add(a, b):
-    return a - b
+    return a + b
"""

TEST_PATCH = """diff --git a/test_buggy.py b/test_buggy.py
new file mode 100644
--- /dev/null
+++ b/test_buggy.py
@@ -0,0 +1,9 @@
+import unittest
+from buggy import add
+
+class BuggyTest(unittest.TestCase):
+    def test_add(self):
+        self.assertEqual(add(2, 3), 5)
+
+if __name__ == '__main__':
+    unittest.main()
"""


class ScoreRealReuseSWETest(unittest.TestCase):
    def test_valid_patch_applies_and_passes_tests(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            workspace = tmp_path / "workspace"
            write_workspace(workspace)
            patch = tmp_path / "candidate.patch"
            patch.write_text(VALID_PATCH, encoding="utf-8")
            output = tmp_path / "metric.json"

            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--task",
                    "SWE-T2",
                    "--patch",
                    str(patch),
                    "--workspace",
                    str(workspace),
                    "--test-command",
                    "python -m unittest discover -s .",
                    "--output-json",
                    str(output),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            self.assertIn('"success": true', completed.stdout.lower())
            metric = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(1.0, metric["task_score"])
            self.assertTrue(metric["success"])
            self.assertTrue(metric["patch_applied"])
            self.assertTrue(metric["test_passed"])

    def test_invalid_patch_is_scored_not_crashed(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            workspace = tmp_path / "workspace"
            write_workspace(workspace)
            patch = tmp_path / "candidate.patch"
            patch.write_text("this is not a unified diff\n", encoding="utf-8")

            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--task",
                    "SWE-T2",
                    "--patch",
                    str(patch),
                    "--workspace",
                    str(workspace),
                    "--test-command",
                    "python -m unittest discover -s .",
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            metric = json.loads(completed.stdout)
            self.assertEqual(0.0, metric["task_score"])
            self.assertFalse(metric["success"])
            self.assertEqual("patch_apply_failed", metric["failure_reason"])

    def test_hidden_test_patch_is_applied_before_scoring(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            workspace = tmp_path / "workspace"
            workspace.mkdir(parents=True)
            (workspace / "buggy.py").write_text("def add(a, b):\n    return a - b\n", encoding="utf-8")
            patch = tmp_path / "candidate.patch"
            patch.write_text(VALID_PATCH, encoding="utf-8")
            test_patch = tmp_path / "test.patch"
            test_patch.write_text(TEST_PATCH, encoding="utf-8")
            output = tmp_path / "metric.json"

            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--task",
                    "SWE-T2",
                    "--patch",
                    "candidate.patch",
                    "--workspace",
                    "workspace",
                    "--test-command",
                    "python -m unittest discover -s .",
                    "--test-patch",
                    "test.patch",
                    "--output-json",
                    "metric.json",
                ],
                check=True,
                capture_output=True,
                text=True,
                cwd=tmp_path,
            )

            metric = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(1.0, metric["task_score"])
            self.assertTrue(metric["success"])
            self.assertTrue(metric["test_patch_applied"])
            self.assertEqual(str(test_patch).replace("\\", "/"), metric["test_patch_path"])


if __name__ == "__main__":
    unittest.main()
