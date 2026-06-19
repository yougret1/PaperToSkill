import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_external_evidence_packets.py"
sys.path.insert(0, str(ROOT / "scripts"))

import check_external_evidence_packets as packets  # noqa: E402


class CheckExternalEvidencePacketsTest(unittest.TestCase):
    def test_current_packets_are_ready_and_cover_closure_items(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_json = Path(tmp) / "packets.json"
            output_md = Path(tmp) / "packets.md"
            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--output-json",
                    str(output_json),
                    "--output-md",
                    str(output_md),
                    "--strict",
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            report = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertEqual("ready", report["overall_status"])
            self.assertEqual(0, report["status_counts"]["fail"])
            packet_ids = {packet["id"] for packet in report["packets"]}
            self.assertEqual(packets.EXPECTED_PACKET_IDS, packet_ids)
            self.assertTrue(output_md.exists())

            for packet in report["packets"]:
                self.assertTrue(packet["run_commands"], packet["id"])
                self.assertTrue(packet["validation_commands"], packet["id"])
                self.assertTrue(packet["completion_criteria"], packet["id"])
                self.assertIn("does not complete external evidence", packet["evidence_boundary"])

            smoke_packet = next(
                packet for packet in report["packets"] if packet["id"] == "ai_scientist_v2_smoke_completion"
            )
            smoke_text = json.dumps(smoke_packet)
            self.assertIn("scripts/run_openai_compatible_direct_probe.py", smoke_text)
            self.assertIn("results\\\\openai_compatible_direct_probe\\\\claude_family\\\\run_report.json", smoke_text)
            self.assertIn("results\\\\openai_compatible_direct_probe\\\\gpt_family\\\\run_report.json", smoke_text)
            self.assertIn("Run the direct OpenAI-compatible probe first", smoke_text)
            self.assertIn("At least one direct OpenAI-compatible probe report is complete", smoke_text)
            run_commands = smoke_packet["run_commands"]
            first_direct = run_commands.index("# Claude-family direct endpoint preflight")
            first_smoke = run_commands.index("# Claude-family credential profile")
            self.assertLess(first_direct, first_smoke)
            self.assertIn("  --model-alias claude-opus-4-8 `", run_commands)
            self.assertIn("  --model-alias claude-opus-4.8 `", run_commands)
            self.assertIn("  --model-alias gpt-5.5 `", run_commands)

            deepseek_packet = next(
                packet for packet in report["packets"] if packet["id"] == "deepseek_followup_responses"
            )
            deepseek_text = json.dumps(deepseek_packet)
            self.assertIn("scripts/configure_deepseek_followup.py", deepseek_text)
            self.assertIn("--model-alias <deepseek-model-alias>", deepseek_text)
            self.assertIn("without storing secrets", deepseek_text)
            self.assertEqual(
                "python scripts\\configure_deepseek_followup.py --model-alias <deepseek-model-alias> --auth-env DEEPSEEK_API_KEY --base-url-env DEEPSEEK_BASE_URL",
                deepseek_packet["run_commands"][0],
            )

            aaai_packet = next(
                packet for packet in report["packets"] if packet["id"] == "aaai_submission_decision"
            )
            aaai_text = json.dumps(aaai_packet)
            self.assertIn("scripts/generate_aaai_submission_decision.py", aaai_text)
            self.assertIn("results/aaai_submission_decision/decision.json", aaai_text)
            self.assertIn("--selected-option submit_now_deterministic_offline", aaai_text)
            self.assertIn("--selected-option wait_for_external_evidence", aaai_text)
            self.assertIn("research/aaai_submission_decision.md exists", aaai_text)
            self.assertIn("scripts/check_aaai_submission_decision.py --strict validates", aaai_text)
            self.assertIn("# Select exactly one human decision record command", aaai_packet["run_commands"])
            self.assertIn("# Final validation after the selected decision record exists", aaai_packet["run_commands"])
            self.assertLess(
                aaai_packet["run_commands"].index("# Select exactly one human decision record command"),
                aaai_packet["run_commands"].index(
                    "python scripts\\generate_aaai_submission_decision.py --selected-option submit_now_deterministic_offline --decision-owner \"<name or role>\" --decision-date YYYY-MM-DD --claim-boundary \"<accepted bounded claim scope>\" --evidence-policy \"submit with explicit pending-evidence limitations\""
                ),
            )
            self.assertLess(
                aaai_packet["run_commands"].index(
                    "python scripts\\generate_aaai_submission_decision.py --selected-option wait_for_external_evidence --decision-owner \"<name or role>\" --decision-date YYYY-MM-DD --claim-boundary \"<claims deferred until named evidence is complete>\" --evidence-policy \"wait for named external evidence rows\""
                ),
                aaai_packet["run_commands"].index("# Final validation after the selected decision record exists"),
            )

    def test_missing_closure_report_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = packets.build_report(root)
            checks = {check["id"]: check for check in report["checks"]}

            self.assertEqual("fail", report["overall_status"])
            self.assertEqual("fail", checks["external_evidence_packets_closure_present"]["status"])
            self.assertEqual("fail", checks["external_evidence_packets_match_closure"]["status"])

    def test_secret_like_material_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            closure_path = root / packets.CLOSURE_REPORT
            closure_path.parent.mkdir(parents=True, exist_ok=True)
            fake_secret = "sk-" + ("1" * 24)
            closure_path.write_text(
                json.dumps(
                    {
                        "overall_status": "pending_external_evidence",
                        "items": [
                            {
                                "id": "ai_scientist_v2_smoke_completion",
                                "status": "pending_provider",
                                "goal_requirements": ["ai_scientist_v2_live_llm_smoke_complete"],
                                "evidence": "results/ai_scientist_v2_smoke/run_report.json",
                                "detail": "blocked",
                                "next_commands": [f"echo {fake_secret}"],
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            report = packets.build_report(root)
            checks = {check["id"]: check for check in report["checks"]}
            self.assertEqual("fail", report["overall_status"])
            self.assertEqual("fail", checks["external_evidence_packets_no_secret_material"]["status"])


if __name__ == "__main__":
    unittest.main()
