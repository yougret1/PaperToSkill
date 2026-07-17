import importlib.util
import inspect
import sys
import unittest
from pathlib import Path


RUN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RUN_ROOT / "src"))

from effectslice.aci_workspace import OverlayWorkspace  # noqa: E402
from run_swe_effectslice import workspace_tree_digest  # noqa: E402


class ToolformerFilterWorkspaceTest(unittest.TestCase):
    def setUp(self):
        self.workspace = RUN_ROOT / "task_workspaces" / "toolformer_filter_v1"
        self.module_path = self.workspace / "toolformer_filter.py"
        self.public_test = self.workspace / "test_toolformer_filter_public.py"
        self.task_prompt = (
            RUN_ROOT / "artifacts" / "toolformer_filter" / "task_prompt.md"
        )

    def test_starter_exposes_only_the_incomplete_required_api(self):
        self.assertTrue(self.module_path.is_file())
        spec = importlib.util.spec_from_file_location(
            "toolformer_filter_starter", self.module_path
        )
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)

        signature = inspect.signature(module.filter_api_calls)
        self.assertEqual(
            list(signature.parameters),
            [
                "logp_with_result",
                "logp_call_only",
                "logp_no_call",
                "tau_filter",
            ],
        )
        with self.assertRaises(NotImplementedError):
            module.filter_api_calls([[-1.0]], [[-2.0]], [[-3.0]], 0.1)

        visible_text = self.module_path.read_text(
            encoding="utf-8"
        ) + self.public_test.read_text(encoding="utf-8")
        self.assertNotIn("1 - 0.2", visible_text)
        self.assertNotIn("minimum", visible_text)
        self.assertNotIn("tau_filter", self.public_test.read_text(encoding="utf-8"))

    def test_prompt_locks_contract_and_budget_without_paper_equations(self):
        prompt = self.task_prompt.read_text(encoding="utf-8")

        self.assertIn("filter_api_calls", prompt)
        self.assertIn("16-action", prompt)
        self.assertIn("python -m pytest test_toolformer_filter_public.py", prompt)
        self.assertIn("preserve candidate order", prompt)
        self.assertIn("Boolean values are invalid thresholds", prompt)
        self.assertNotIn("1 - 0.2", prompt)
        self.assertNotIn("L_minus", prompt)
        self.assertNotIn("minimum", prompt)

    def test_workspace_is_two_visible_files_and_overlay_read_only(self):
        digest = workspace_tree_digest(self.workspace)

        self.assertEqual(digest["file_count"], 2)
        self.assertGreater(digest["total_bytes"], 0)
        overlay = OverlayWorkspace(self.workspace)
        visible = "\n".join(overlay.open_lines("toolformer_filter.py", 1, 80))
        self.assertIn("filter_api_calls", visible)


if __name__ == "__main__":
    unittest.main()
