import contextlib
import importlib.util
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "aggregate_skillsbench_bfs_sol.py"
SPEC = importlib.util.spec_from_file_location("aggregate_skillsbench_bfs_sol", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def aggregate(manifests, states, results):
    return MODULE.aggregate(
        manifests,
        states,
        results,
        bootstrap_samples=100,
        bootstrap_seed_value=MODULE.DEFAULT_BOOTSTRAP_SEED,
        b_warning_threshold=MODULE.DEFAULT_B_WARNING_THRESHOLD,
        success_threshold=1.0,
    )


class SkillsBenchAggregateTests(unittest.TestCase):
    def test_canonical_finish_blocks_old_result_fallback_for_same_cell(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = root / "manifest.json"
            manifest.write_text(
                json.dumps(
                    {
                        "phase": "main",
                        "tasks": ["task-a"],
                        "conditions": ["F"],
                        "repetitions": 1,
                    }
                ),
                encoding="utf-8",
            )
            state = root / "run_state.jsonl"
            state.write_text(
                json.dumps(
                    {
                        "event": "finish",
                        "execution_id": "canonical",
                        "phase": "main",
                        "task_id": "task-a",
                        "condition": "F",
                        "repetition": 1,
                        "status": "invalid",
                        "invalid": True,
                        "invalid_reasons": ["runner_process_timeout"],
                        "official_reward": None,
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            old_result = root / "old-attempt" / "result.json"
            old_result.parent.mkdir()
            old_result.write_text(
                json.dumps(
                    {
                        "execution_id": "old-attempt",
                        "phase": "main",
                        "task_id": "task-a",
                        "condition": "F",
                        "repetition": 1,
                        "status": "scored",
                        "reward": 0.0,
                    }
                ),
                encoding="utf-8",
            )

            summary = aggregate([manifest], [state], [old_result])

            self.assertEqual(len(summary["observations"]), 1)
            self.assertEqual(summary["observations"][0]["execution_id"], "canonical")
            self.assertFalse(summary["observations"][0]["valid"])
            self.assertNotIn("duplicate_schedule_cell", json.dumps(summary))
            self.assertTrue(
                any("canonical schedule cell" in warning for warning in summary["warnings"])
            )

    def test_external_error_details_are_reduced_to_categories(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = Path(tmp) / "run_state.jsonl"
            secret_detail = "bad key sk-unit-secret-value-123456"
            state.write_text(
                json.dumps(
                    {
                        "event": "finish",
                        "execution_id": "invalid-run",
                        "phase": "main",
                        "task_id": "task-a",
                        "condition": "B",
                        "repetition": 1,
                        "status": "error",
                        "invalid": True,
                        "invalid_reasons": ["runner_process_timeout", secret_detail],
                        "error": secret_detail,
                        "official_reward": None,
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            summary = aggregate([], [state], [])
            encoded = json.dumps(summary)

            self.assertNotIn(secret_detail, encoded)
            reasons = summary["observations"][0]["invalid_reasons"]
            self.assertIn("runner_process_timeout", reasons)
            self.assertIn("reported_invalid_reason", reasons)
            self.assertIn("error", reasons)

    def test_s_identity_is_explicitly_non_official(self):
        summary = aggregate([], [], [])
        identity = summary["evidence_boundary"]["candidate_identity"]
        self.assertIn("independently generated heuristic candidate inspired by SkillReducer", identity)
        self.assertIn("not the official SkillReducer implementation or artifact", identity)
        self.assertIn("not an official head-to-head comparison", identity)
        self.assertNotIn("an independent SkillReducer implementation", json.dumps(summary))

    def test_cli_redacts_reflected_credentials_and_returns_nonzero(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = root / "result.json"
            output = root / "output"
            api_key = "sk-unit-secret-value-123456789"
            base_url = "https://unit-api.example.invalid/v1"
            result.write_text(
                json.dumps(
                    {
                        "task_id": f"task-{api_key}-{base_url}",
                        "condition": "S",
                        "phase": "main",
                        "repetition": 1,
                        "reward": 1.0,
                        "status": "scored",
                    }
                ),
                encoding="utf-8",
            )
            argv = [
                str(SCRIPT),
                "--result",
                str(result),
                "--output-dir",
                str(output),
                "--bootstrap-samples",
                "10",
                "--api-key-env",
                "UNIT_API_KEY",
                "--base-url-env",
                "UNIT_BASE_URL",
            ]
            stdout = io.StringIO()
            stderr = io.StringIO()
            with mock.patch.dict(
                os.environ,
                {"UNIT_API_KEY": api_key, "UNIT_BASE_URL": base_url},
                clear=False,
            ), mock.patch.object(sys, "argv", argv), contextlib.redirect_stdout(
                stdout
            ), contextlib.redirect_stderr(stderr):
                return_code = MODULE.main()

            self.assertEqual(return_code, 2)
            self.assertIn("credential_reflection_detected", stderr.getvalue())
            persisted = "\n".join(
                path.read_text(encoding="utf-8") for path in output.iterdir() if path.is_file()
            )
            visible = stdout.getvalue() + stderr.getvalue() + persisted
            self.assertNotIn(api_key, visible)
            self.assertNotIn(base_url, visible)
            security = json.loads((output / "summary.json").read_text(encoding="utf-8"))[
                "output_security"
            ]
            self.assertTrue(security["credential_reflection_detected"])
            self.assertFalse(security["credential_values_recorded"])


if __name__ == "__main__":
    unittest.main()
