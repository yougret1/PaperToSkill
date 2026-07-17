import importlib.util
import inspect
import sys
import unittest
from pathlib import Path


RUN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RUN_ROOT / "src"))

from effectslice.aci_workspace import OverlayWorkspace  # noqa: E402
from run_swe_effectslice import workspace_tree_digest  # noqa: E402


class SnapMFSEWorkspaceTest(unittest.TestCase):
    def setUp(self):
        self.workspace = RUN_ROOT / "task_workspaces" / "snap_mfse_v1"
        self.module_path = self.workspace / "snap_core.py"
        self.public_test = self.workspace / "test_snap_core_public.py"
        self.task_prompt = RUN_ROOT / "artifacts" / "snap_mfse" / "task_prompt.md"

    def test_starter_exposes_incomplete_required_api_without_oracle_details(self):
        self.assertTrue(self.module_path.is_file())
        spec = importlib.util.spec_from_file_location("snap_mfse_starter", self.module_path)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)

        signature = inspect.signature(module.matrix_free_spectral_embedding)
        self.assertEqual(
            list(signature.parameters), ["counts", "n_components", "random_state"]
        )
        with self.assertRaises(NotImplementedError):
            module.matrix_free_spectral_embedding([[1, 0], [0, 1], [1, 1]], 1)

        visible_text = self.module_path.read_text(encoding="utf-8") + self.public_test.read_text(
            encoding="utf-8"
        )
        self.assertNotIn("log(n / (1 + df))", visible_text)
        self.assertNotIn("X_tilde", visible_text)
        self.assertNotIn("D_inv", visible_text)

    def test_prompt_locks_contract_and_budget_without_method_equations(self):
        prompt = self.task_prompt.read_text(encoding="utf-8")

        self.assertIn("matrix_free_spectral_embedding", prompt)
        self.assertIn("16-action", prompt)
        self.assertIn("python -m pytest test_snap_core_public.py", prompt)
        self.assertIn("must not materialize", prompt)
        self.assertNotIn("log(n / (1 + df))", prompt)
        self.assertNotIn("X_tilde", prompt)
        self.assertNotIn("D_inv", prompt)

    def test_workspace_is_two_visible_files_and_overlay_read_only(self):
        digest = workspace_tree_digest(self.workspace)

        self.assertEqual(digest["file_count"], 2)
        self.assertGreater(digest["total_bytes"], 0)
        overlay = OverlayWorkspace(self.workspace)
        self.assertIn("matrix_free_spectral_embedding", "\n".join(overlay.open_lines("snap_core.py", 1, 80)))


if __name__ == "__main__":
    unittest.main()
