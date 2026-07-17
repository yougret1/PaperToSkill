import json
import sys
import unittest
from pathlib import Path


RUN_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = RUN_ROOT.parents[5]
sys.path.insert(0, str(RUN_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from effectslice.swe_scorer_bridge import (  # noqa: E402
    ScorerBridgeError,
    SWEScorerBridge,
)
from score_real_reuse_swe import score_patch  # noqa: E402


PASSING_PATCH = """--- a/buggy.py
+++ b/buggy.py
@@ -1,2 +1,2 @@
 def add(a, b):
-    return a - b
+    return a + b
"""

FAILING_PATCH = """--- a/buggy.py
+++ b/buggy.py
@@ -1,2 +1,2 @@
 def missing(a, b):
-    return a - b
+    return a + b
"""


class SWEScorerBridgeTest(unittest.TestCase):
    def setUp(self):
        self.fixture_root = RUN_ROOT / "tests" / "fixtures" / "swe_scorer_bridge"
        self.output_root = self.fixture_root / "generated"

    def bridge(self, score_function=score_patch):
        return SWEScorerBridge(
            task_id="SWE-T2",
            workspace=self.fixture_root / "workspace",
            test_command="python -m pytest test_hidden.py -q",
            test_patch_path=self.fixture_root / "scorer_only" / "hidden_test.patch",
            output_dir=self.output_root,
            timeout_seconds=30.0,
            score_function=score_function,
        )

    def test_evaluates_passing_patch_and_hides_scorer_only_details(self):
        evaluation = self.bridge().evaluate(PASSING_PATCH, evaluation_id="passing")

        feedback = json.loads(evaluation.model_feedback)
        self.assertEqual(feedback["status"], "passed")
        self.assertEqual(feedback["task_score"], 1.0)
        self.assertTrue(feedback["patch_applied"])
        self.assertTrue(feedback["test_passed"])
        self.assertEqual(feedback["failure_reason"], "")
        self.assertTrue(evaluation.metric["success"])
        self.assertEqual(evaluation.patch_path.read_text(encoding="utf-8"), PASSING_PATCH)
        for forbidden in (
            "hidden_test.patch",
            "test_hidden.py",
            "assert add(20, 22) == 42",
            str(self.fixture_root / "scorer_only"),
        ):
            self.assertNotIn(forbidden, evaluation.model_feedback)

    def test_preserves_full_failed_metric_but_returns_only_sanitized_feedback(self):
        evaluation = self.bridge().evaluate(FAILING_PATCH, evaluation_id="failing")

        feedback = json.loads(evaluation.model_feedback)
        self.assertEqual(feedback["status"], "failed")
        self.assertEqual(feedback["task_score"], 0.0)
        self.assertFalse(feedback["patch_applied"])
        self.assertEqual(feedback["failure_reason"], "patch_apply_failed")
        self.assertIn("apply_result", evaluation.metric)
        self.assertNotIn("apply_result", feedback)
        self.assertNotIn("stderr", feedback)

    def test_calls_injected_scorer_with_frozen_arguments(self):
        calls = []

        def fake_score(**kwargs):
            calls.append(kwargs)
            return {
                "task_score": 0.25,
                "success": False,
                "patch_applied": True,
                "test_passed": False,
                "failure_reason": "test_command_failed",
                "private": "not model visible",
            }

        evaluation = self.bridge(fake_score).evaluate(PASSING_PATCH, evaluation_id="fake-1")

        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0]["task_id"], "SWE-T2")
        self.assertEqual(calls[0]["workspace"], (self.fixture_root / "workspace").resolve())
        self.assertEqual(calls[0]["test_patch_path"], (self.fixture_root / "scorer_only" / "hidden_test.patch").resolve())
        self.assertEqual(calls[0]["timeout_seconds"], 30.0)
        self.assertNotIn("private", evaluation.model_feedback)

    def test_normalizes_unknown_failure_text_and_rejects_malformed_metric_types(self):
        hidden_path = str(self.fixture_root / "scorer_only" / "hidden_test.patch")

        def private_failure(**kwargs):
            return {
                "task_score": 0.0,
                "success": False,
                "patch_applied": False,
                "test_passed": False,
                "failure_reason": hidden_path,
            }

        feedback = json.loads(
            self.bridge(private_failure).evaluate(
                PASSING_PATCH,
                evaluation_id="private-failure",
            ).model_feedback
        )
        self.assertEqual(feedback["failure_reason"], "scorer_failure")
        self.assertNotIn(hidden_path, json.dumps(feedback))

        malformed_metrics = [
            {
                "task_score": float("nan"),
                "success": False,
                "patch_applied": False,
                "test_passed": False,
                "failure_reason": "test_command_failed",
            },
            {
                "task_score": 0.0,
                "success": "false",
                "patch_applied": False,
                "test_passed": False,
                "failure_reason": "test_command_failed",
            },
        ]
        for index, metric in enumerate(malformed_metrics):
            with self.subTest(index=index), self.assertRaises(ScorerBridgeError):
                self.bridge(lambda **kwargs: metric).evaluate(
                    PASSING_PATCH,
                    evaluation_id=f"malformed-{index}",
                )

    def test_rejects_empty_diff_unsafe_evaluation_ids_and_missing_inputs(self):
        bridge = self.bridge(lambda **kwargs: {})
        for diff in ("", "   "):
            with self.subTest(diff=diff), self.assertRaises(ScorerBridgeError):
                bridge.evaluate(diff, evaluation_id="empty")
        for evaluation_id in ("", "../escape", "a/b", "bad id", "a" * 129):
            with self.subTest(evaluation_id=evaluation_id), self.assertRaises(ScorerBridgeError):
                bridge.evaluate(PASSING_PATCH, evaluation_id=evaluation_id)
        with self.assertRaises(ScorerBridgeError):
            SWEScorerBridge(
                task_id="SWE-T2",
                workspace=self.fixture_root / "missing",
                test_command="pytest",
                test_patch_path=None,
                output_dir=self.output_root,
                timeout_seconds=1,
                score_function=lambda **kwargs: {},
            )


if __name__ == "__main__":
    unittest.main()
