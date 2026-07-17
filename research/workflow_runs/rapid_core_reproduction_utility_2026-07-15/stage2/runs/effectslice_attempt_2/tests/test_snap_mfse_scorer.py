import difflib
import json
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


RUN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RUN_ROOT / "src"))

from effectslice.snap_mfse_scorer import (  # noqa: E402
    SnapMFSEScorerBridge,
    score_snap_mfse_patch,
)


CORRECT_BODY = """
    matrix = np.asarray(counts, dtype=np.float64)
    if matrix.ndim != 2 or matrix.shape[0] < 3 or matrix.shape[1] < 2:
        raise ValueError("counts must be two-dimensional")
    if not np.isfinite(matrix).all() or np.any(matrix < 0):
        raise ValueError("counts must be finite and nonnegative")
    if isinstance(n_components, bool) or not isinstance(n_components, (int, np.integer)):
        raise ValueError("invalid n_components")
    if n_components < 1 or n_components >= matrix.shape[0]:
        raise ValueError("invalid n_components")
    if np.any(np.linalg.norm(matrix, axis=1) == 0):
        raise ValueError("all-zero row")
    n_cells = matrix.shape[0]
    df = np.count_nonzero(matrix, axis=0)
    idf = np.log(n_cells / (1.0 + df))
    x = matrix * idf
    row_norm = np.linalg.norm(x, axis=1)
    if np.any(row_norm <= 0) or not np.isfinite(row_norm).all():
        raise ValueError("non-normalizable row")
    x = x / row_norm[:, None]
    degree = x @ (x.T @ np.ones(n_cells)) - np.ones(n_cells)
    if np.any(degree <= 0) or not np.isfinite(degree).all():
        raise ValueError("nonpositive degree")
    d_inv = 1.0 / degree
    x_tilde = x * np.sqrt(d_inv)[:, None]
    from scipy.sparse.linalg import LinearOperator, eigsh
    operator = LinearOperator(
        (n_cells, n_cells),
        matvec=lambda v: x_tilde @ (x_tilde.T @ v) - d_inv * v,
        dtype=np.float64,
    )
    rng = np.random.default_rng(random_state)
    values, vectors = eigsh(operator, k=n_components, which="LA", v0=rng.random(n_cells))
    order = np.argsort(values)[::-1]
    return values[order], vectors[:, order]
"""


def patch_with_body(workspace: Path, body: str) -> str:
    starter = (workspace / "snap_core.py").read_text(encoding="utf-8")
    indented_body = textwrap.indent(textwrap.dedent(body).strip("\n"), "    ")
    updated = starter.replace(
        '    raise NotImplementedError("implement the paper-core reproduction task")\n',
        indented_body + "\n",
    )
    return "".join(
        difflib.unified_diff(
            starter.splitlines(keepends=True),
            updated.splitlines(keepends=True),
            fromfile="a/snap_core.py",
            tofile="b/snap_core.py",
        )
    )


class SnapMFSEScorerTest(unittest.TestCase):
    def setUp(self):
        self.workspace = RUN_ROOT / "task_workspaces" / "snap_mfse_v1"
        self.registry = RUN_ROOT / "artifacts" / "snap_mfse" / "case_registry.json"

    def score(self, patch: str):
        return score_snap_mfse_patch(
            diff_text=patch,
            workspace=self.workspace,
            case_registry_path=self.registry,
            block="development",
        )

    def test_correct_matrix_free_patch_passes_all_development_cases(self):
        metric = self.score(patch_with_body(self.workspace, CORRECT_BODY))

        self.assertTrue(metric["patch_applied"])
        self.assertTrue(metric["matrix_free_guard_passed"])
        self.assertTrue(metric["contract_passed"])
        self.assertEqual(metric["case_scores"], [1, 1, 1, 1])
        self.assertEqual(metric["task_score"], 1.0)
        self.assertTrue(metric["success"])

    def test_wrong_idf_patch_fails_numerical_cases(self):
        wrong = CORRECT_BODY.replace(
            "np.log(n_cells / (1.0 + df))",
            "np.log(n_cells / np.maximum(df, 1.0))",
        )

        metric = self.score(patch_with_body(self.workspace, wrong))

        self.assertTrue(metric["matrix_free_guard_passed"])
        self.assertLess(metric["task_score"], 1.0)
        self.assertFalse(metric["success"])

    def test_dense_similarity_patch_is_rejected_by_hard_guard(self):
        dense = CORRECT_BODY.replace(
            "from scipy.sparse.linalg import LinearOperator, eigsh",
            "full_similarity = x_tilde @ x_tilde.T\n    from scipy.sparse.linalg import LinearOperator, eigsh",
        )

        metric = self.score(patch_with_body(self.workspace, dense))

        self.assertFalse(metric["matrix_free_guard_passed"])
        self.assertIn("dense_similarity_matmul", metric["guard_violations"])
        self.assertEqual(metric["task_score"], 0.0)
        self.assertFalse(metric["success"])

    def test_bridge_sanitizes_feedback_and_preserves_private_metric(self):
        patch = patch_with_body(self.workspace, CORRECT_BODY)
        with tempfile.TemporaryDirectory() as tmp:
            bridge = SnapMFSEScorerBridge(
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
        self.assertNotIn(str(self.workspace), evaluation.model_feedback)
        self.assertEqual(evaluation.metric["case_scores"], [1, 1, 1, 1])

    def test_malformed_patch_fails_without_exposing_git_details(self):
        metric = self.score("not a unified diff")

        self.assertFalse(metric["patch_applied"])
        self.assertEqual(metric["failure_reason"], "patch_apply_failed")
        self.assertNotIn("stderr", metric["public_summary"])


if __name__ == "__main__":
    unittest.main()
