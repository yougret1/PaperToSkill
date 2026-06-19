import json
import sys
import tempfile
import time
import types
import unittest
from argparse import Namespace
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import run_ai_scientist_v2_smoke as smoke  # noqa: E402


class AIScientistV2SmokeTest(unittest.TestCase):
    def tearDown(self):
        for name in ["ai_scientist", "ai_scientist.llm"]:
            sys.modules.pop(name, None)

    def install_fake_ai_scientist(
        self,
        response_text=None,
        error=None,
        delay_seconds=0,
        responses_by_model=None,
        errors_by_model=None,
    ):
        package = types.ModuleType("ai_scientist")
        llm = types.ModuleType("ai_scientist.llm")

        def create_client(model):
            return object(), model

        def get_response_from_llm(prompt, client, model, system_message, temperature=0):
            if delay_seconds:
                time.sleep(delay_seconds)
            if errors_by_model and model in errors_by_model:
                raise RuntimeError(errors_by_model[model])
            if error:
                raise RuntimeError(error)
            if responses_by_model and model in responses_by_model:
                return responses_by_model[model], []
            return response_text, []

        llm.create_client = create_client
        llm.get_response_from_llm = get_response_from_llm
        sys.modules["ai_scientist"] = package
        sys.modules["ai_scientist.llm"] = llm

    def test_smoke_run_saves_contract_response(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            self.install_fake_ai_scientist(
                "PAPERTOSKILL_SMOKE_OK from ai-scientist-v2 for paper-to-skill."
            )
            report = smoke.run(
                Namespace(
                    ai_scientist_root=tmp_path,
                    model="claude-opus-4-8",
                    prompt="prompt",
                    system_message="system",
                    response_output=tmp_path / "response.md",
                    timeout_seconds=1,
                    model_aliases=None,
                )
            )

            self.assertEqual("complete", report["overall_status"])
            self.assertTrue((tmp_path / "response.md").exists())
            statuses = {check["id"]: check["status"] for check in report["checks"]}
            self.assertEqual("ready", statuses["ai_scientist_v2_llm_response_saved"])
            self.assertEqual("ready", statuses["ai_scientist_v2_smoke_marker_papertoskill_smoke_ok"])
            self.assertEqual("ready", statuses["ai_scientist_v2_smoke_marker_ai_scientist_v2"])
            self.assertEqual("ready", statuses["ai_scientist_v2_smoke_marker_paper_to_skill"])
            self.assertEqual(0, smoke.exit_code(report, strict=True, require_complete=True))
            self.assertIn("overall_status=complete", smoke.status_summary(report))

    def test_smoke_error_is_redacted_and_pending(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            fake_secret = "sk-" + "a" * 24
            self.install_fake_ai_scientist(error=f"bad key {fake_secret}")
            response_path = tmp_path / "response.md"
            response_path.write_text("stale response\n", encoding="utf-8")
            report = smoke.run(
                Namespace(
                    ai_scientist_root=tmp_path,
                    model="claude-opus-4-8",
                    prompt="prompt",
                    system_message="system",
                    response_output=response_path,
                    timeout_seconds=1,
                    model_aliases=None,
                )
            )

            self.assertEqual("blocked_by_provider_or_model_availability", report["overall_status"])
            self.assertFalse(response_path.exists())
            self.assertIn("sk-REDACTED", json.dumps(report))
            self.assertNotIn(fake_secret, json.dumps(report))
            self.assertEqual(0, smoke.exit_code(report, strict=True, require_complete=False))
            self.assertEqual(1, smoke.exit_code(report, strict=True, require_complete=True))
            self.assertIn("overall_status=blocked_by_provider_or_model_availability", smoke.status_summary(report))

    def test_smoke_timeout_is_reported_as_provider_blocker(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            self.install_fake_ai_scientist(
                "PAPERTOSKILL_SMOKE_OK from ai-scientist-v2 for paper-to-skill.",
                delay_seconds=0.2,
            )
            response_path = tmp_path / "response.md"
            response_path.write_text("stale response\n", encoding="utf-8")
            report = smoke.run(
                Namespace(
                    ai_scientist_root=tmp_path,
                    model="claude-opus-4-8",
                    prompt="prompt",
                    system_message="system",
                    response_output=response_path,
                    timeout_seconds=0.01,
                    model_aliases=None,
                )
            )

            self.assertEqual("blocked_by_provider_or_model_availability", report["overall_status"])
            self.assertFalse(response_path.exists())
            details = [check["detail"] for check in report["checks"]]
            self.assertTrue(any("Timed out after" in detail for detail in details))
            self.assertEqual(1, smoke.exit_code(report, strict=True, require_complete=True))

    def test_smoke_tries_model_aliases_until_success(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            self.install_fake_ai_scientist(
                responses_by_model={
                    "claude-opus-4-7": "PAPERTOSKILL_SMOKE_OK from ai-scientist-v2 for paper-to-skill."
                },
                errors_by_model={"claude-opus-4-8": "alias unavailable"},
            )
            report = smoke.run(
                Namespace(
                    ai_scientist_root=tmp_path,
                    model="claude-opus-4-8",
                    prompt="prompt",
                    system_message="system",
                    response_output=tmp_path / "response.md",
                    timeout_seconds=1,
                    model_aliases=["claude-opus-4-8", "claude-opus-4-7", "claude-opus-4-6"],
                )
            )

            self.assertEqual("complete", report["overall_status"])
            attempts = report["attempted_models"]
            self.assertEqual(["claude-opus-4-8", "claude-opus-4-7"], [item["model"] for item in attempts])
            self.assertEqual(["blocked", "success"], [item["status"] for item in attempts])
            checks = {check["id"]: check for check in report["checks"]}
            self.assertEqual("ready", checks["ai_scientist_v2_llm_alias_attempt_1"]["status"])
            self.assertIn("blocked", checks["ai_scientist_v2_llm_alias_attempt_1"]["detail"])
            self.assertEqual("ready", checks["ai_scientist_v2_llm_alias_attempt_2"]["status"])
            self.assertTrue((tmp_path / "response.md").exists())


if __name__ == "__main__":
    unittest.main()
