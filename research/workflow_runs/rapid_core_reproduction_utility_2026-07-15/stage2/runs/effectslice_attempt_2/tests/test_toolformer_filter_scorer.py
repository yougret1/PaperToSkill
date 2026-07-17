import difflib
import json
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


RUN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RUN_ROOT / "src"))

from effectslice.toolformer_filter_scorer import (  # noqa: E402
    ToolformerFilterScorerBridge,
    score_toolformer_filter_patch,
)


CORRECT_BODY = """
    arrays = [np.asarray(value, dtype=np.float64) for value in (
        logp_with_result, logp_call_only, logp_no_call
    )]
    if any(array.ndim != 2 or min(array.shape) < 1 for array in arrays):
        raise ValueError("inputs must be nonempty matrices")
    if any(array.shape != arrays[0].shape for array in arrays[1:]):
        raise ValueError("input shapes must match")
    if any(not np.isfinite(array).all() or np.any(array > 0) for array in arrays):
        raise ValueError("log probabilities must be finite and nonpositive")
    if isinstance(tau_filter, bool) or not isinstance(tau_filter, (int, float, np.integer, np.floating)):
        raise ValueError("invalid threshold")
    tau = float(tau_filter)
    if not np.isfinite(tau) or tau < 0:
        raise ValueError("invalid threshold")
    raw = np.maximum(0.0, 1.0 - 0.2 * np.arange(arrays[0].shape[1]))
    weights = raw / raw.sum()
    losses = [-(array * weights).sum(axis=1) for array in arrays]
    margins = np.minimum(losses[1], losses[2]) - losses[0]
    return margins >= tau, margins
"""


def patch_with_body(workspace: Path, body: str) -> str:
    starter = (workspace / "toolformer_filter.py").read_text(encoding="utf-8")
    indented_body = textwrap.indent(textwrap.dedent(body).strip("\n"), "    ")
    updated = starter.replace(
        '    raise NotImplementedError("implement the paper-core reproduction task")\n',
        indented_body + "\n",
    )
    return "".join(
        difflib.unified_diff(
            starter.splitlines(keepends=True),
            updated.splitlines(keepends=True),
            fromfile="a/toolformer_filter.py",
            tofile="b/toolformer_filter.py",
        )
    )


class ToolformerFilterScorerTest(unittest.TestCase):
    def setUp(self):
        self.workspace = RUN_ROOT / "task_workspaces" / "toolformer_filter_v1"
        self.registry = (
            RUN_ROOT / "artifacts" / "toolformer_filter" / "case_registry.json"
        )

    def score(self, patch: str):
        return score_toolformer_filter_patch(
            diff_text=patch,
            workspace=self.workspace,
            case_registry_path=self.registry,
            block="development",
        )

    def test_correct_patch_passes_all_development_cases(self):
        metric = self.score(patch_with_body(self.workspace, CORRECT_BODY))

        self.assertTrue(metric["patch_applied"])
        self.assertTrue(metric["contract_passed"])
        self.assertEqual(metric["case_scores"], [1, 1, 1, 1])
        self.assertEqual(metric["task_score"], 1.0)
        self.assertTrue(metric["success"])

    def test_uniform_weights_fail_private_cases(self):
        wrong = CORRECT_BODY.replace(
            "raw = np.maximum(0.0, 1.0 - 0.2 * np.arange(arrays[0].shape[1]))\n    weights = raw / raw.sum()",
            "weights = np.full(arrays[0].shape[1], 1.0 / arrays[0].shape[1])",
        )
        metric = self.score(patch_with_body(self.workspace, wrong))

        self.assertLess(metric["task_score"], 1.0)
        self.assertEqual(metric["failure_reason"], "numerical_case_failed")

    def test_wrong_comparator_and_strict_threshold_fail(self):
        wrong_comparator = CORRECT_BODY.replace("np.minimum", "np.maximum")
        strict_threshold = CORRECT_BODY.replace("margins >= tau", "margins > tau")

        comparator_metric = self.score(
            patch_with_body(self.workspace, wrong_comparator)
        )
        strict_metric = self.score(patch_with_body(self.workspace, strict_threshold))

        self.assertLess(comparator_metric["task_score"], 1.0)
        self.assertLess(strict_metric["task_score"], 1.0)

    def test_exception_and_malformed_patch_fail_cleanly(self):
        exception_metric = self.score(
            patch_with_body(self.workspace, 'raise RuntimeError("candidate failure")')
        )
        malformed_metric = self.score("not a unified diff")

        self.assertEqual(exception_metric["task_score"], 0.0)
        self.assertEqual(
            exception_metric["failure_reason"], "candidate_load_or_contract_failed"
        )
        self.assertFalse(malformed_metric["patch_applied"])
        self.assertEqual(malformed_metric["failure_reason"], "patch_apply_failed")
        self.assertNotIn("stderr", malformed_metric["public_summary"])

    def test_bridge_sanitizes_feedback_and_preserves_private_metric(self):
        patch = patch_with_body(self.workspace, CORRECT_BODY)
        with tempfile.TemporaryDirectory(dir=RUN_ROOT) as tmp:
            bridge = ToolformerFilterScorerBridge(
                workspace=self.workspace,
                case_registry_path=self.registry,
                block="development",
                output_dir=Path(tmp),
            )
            evaluation = bridge.evaluate(patch, evaluation_id="correct")
            self.assertTrue(evaluation.patch_path.is_file())

        feedback = json.loads(evaluation.model_feedback)
        self.assertEqual(feedback["task_score"], 1.0)
        self.assertEqual(feedback["passed_cases"], 4)
        self.assertNotIn("case_scores", feedback)
        self.assertNotIn("seed", evaluation.model_feedback.lower())
        self.assertNotIn("registry", evaluation.model_feedback.lower())
        self.assertNotIn("margin", evaluation.model_feedback.lower())
        self.assertNotIn(str(self.workspace), evaluation.model_feedback)
        self.assertEqual(evaluation.metric["case_scores"], [1, 1, 1, 1])


if __name__ == "__main__":
    unittest.main()
