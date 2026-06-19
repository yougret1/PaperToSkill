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
