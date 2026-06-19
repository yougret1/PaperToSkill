import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "generate_aaai_submission_decision.py"
sys.path.insert(0, str(ROOT / "scripts"))

import generate_aaai_submission_decision as generator  # noqa: E402


class GenerateAAAISubmissionDecisionTest(unittest.TestCase):
    def write_preflight(self, root: Path, *, option_status: str = "available_for_human_decision") -> Path:
        path = root / "decision.json"
        path.write_text(
            json.dumps(
                {
                    "overall_status": "pending_human_decision",
                    "options": [
                        {
                            "id": "submit_now_deterministic_offline",
                            "status": option_status,
                        },
                        {
                            "id": "wait_for_external_evidence",
                            "status": "available_for_human_decision",
                        },
                    ],
                }
            ),
            encoding="utf-8",
        )
        return path

    def test_writes_valid_decision_record(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            output = tmp_path / "aaai_submission_decision.md"
            preflight = self.write_preflight(tmp_path)

            generator.write_decision_record(
                output_path=output,
                selected_option="submit_now_deterministic_offline",
                decision_owner="Research Lead",
                decision_date="2026-06-20",
                claim_boundary="deterministic/offline system paper with pending-evidence limitations",
                evidence_policy="submit with explicit limitations and no external-evidence overclaims",
                preflight_path=preflight,
            )

            text = output.read_text(encoding="utf-8")
            self.assertIn("Selected option: submit_now_deterministic_offline", text)
            self.assertIn("Decision owner: Research Lead", text)
            self.assertIn("Claim boundary:", text)

    def test_rejects_unavailable_preflight_option(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            preflight = self.write_preflight(tmp_path, option_status="blocked_by_local_gate")

            with self.assertRaisesRegex(ValueError, "not currently available"):
                generator.write_decision_record(
                    output_path=tmp_path / "decision.md",
                    selected_option="submit_now_deterministic_offline",
                    decision_owner="Research Lead",
                    decision_date="2026-06-20",
                    claim_boundary="bounded claim",
                    evidence_policy="bounded policy",
                    preflight_path=preflight,
                )

    def test_rejects_secret_like_material(self):
        with self.assertRaisesRegex(ValueError, "raw API-key-like"):
            generator.render_decision_record(
                selected_option="wait_for_external_evidence",
                decision_owner="Research Lead",
                decision_date="2026-06-20",
                claim_boundary="sk-" + "a" * 24,
                evidence_policy="wait for evidence",
            )

    def test_cli_can_write_to_explicit_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            output = tmp_path / "decision.md"
            preflight = self.write_preflight(tmp_path)

            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--selected-option",
                    "wait_for_external_evidence",
                    "--decision-owner",
                    "Research Lead",
                    "--decision-date",
                    "2026-06-20",
                    "--claim-boundary",
                    "wait before claiming live evidence",
                    "--evidence-policy",
                    "wait for named external evidence rows",
                    "--preflight-json",
                    str(preflight),
                    "--output",
                    str(output),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            self.assertTrue(output.exists())
            self.assertIn("Selected option: wait_for_external_evidence", output.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
