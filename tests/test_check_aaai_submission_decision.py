import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_aaai_submission_decision.py"
sys.path.insert(0, str(ROOT / "scripts"))

import check_aaai_submission_decision as decision  # noqa: E402


class CheckAAAISubmissionDecisionTest(unittest.TestCase):
    def test_current_preflight_has_recorded_wait_decision_without_failures(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_json = Path(tmp) / "decision.json"
            output_md = Path(tmp) / "decision.md"
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
            self.assertEqual("recorded", report["decision_status"])
            self.assertEqual("wait_for_external_evidence", report["selected_option"])
            self.assertEqual(0, report["status_counts"]["fail"])
            statuses = {check["id"]: check["status"] for check in report["checks"]}
            self.assertEqual("ready", statuses["aaai_submission_decision_input_decision_generator"])
            self.assertEqual("ready", statuses["aaai_submission_decision_local_gates_ready"])
            self.assertEqual("ready", statuses["aaai_submission_decision_pending_evidence_state_current"])
            self.assertEqual("ready", statuses["aaai_submission_decision_external_packet_ready"])
            self.assertEqual("ready", statuses["aaai_submission_decision_boundaries_declared"])
            self.assertEqual("ready", statuses["aaai_submission_decision_human_decision_recorded"])
            option_statuses = {option["id"]: option["status"] for option in report["options"]}
            self.assertEqual(
                {
                    "submit_now_deterministic_offline": "available_for_human_decision",
                    "wait_for_external_evidence": "available_for_human_decision",
                },
                option_statuses,
            )
            self.assertTrue(output_md.exists())
            self.assertIn("generate_aaai_submission_decision.py", output_md.read_text(encoding="utf-8"))

    def test_missing_inputs_fail_preflight(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = decision.build_report(Path(tmp))
            self.assertEqual("fail", report["overall_status"])
            checks = {check["id"]: check for check in report["checks"]}
            self.assertEqual("fail", checks["aaai_submission_decision_input_aaai_package"]["status"])

    def test_valid_human_decision_record_is_parsed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            decision_path = root / decision.DECISION_RECORD
            decision_path.parent.mkdir(parents=True)
            decision_path.write_text(
                "\n".join(
                    [
                        "# AAAI Submission Decision",
                        "",
                        "Selected option: submit_now_deterministic_offline",
                        "Decision owner: Research Lead",
                        "Decision date: 2026-06-20",
                        "Claim boundary: deterministic/offline system paper",
                        "Evidence policy: submit with explicit pending-evidence limitations",
                    ]
                ),
                encoding="utf-8",
            )

            parsed = decision.parse_decision_record(root)
            self.assertEqual("valid", parsed["status"])
            self.assertEqual("submit_now_deterministic_offline", parsed["selected_option"])

    def test_self_referential_goal_failure_keeps_final_submission_pending(self):
        goal = {
            "overall_status": "fail",
            "checks": [
                {
                    "id": "aaai_submission_decision_preflight_ready",
                    "status": "fail",
                    "detail": "overall=fail",
                },
                {
                    "id": "aaai_final_submission_ready",
                    "status": "fail",
                    "detail": "one or more paper-package gates failed",
                },
                {
                    "id": "active_goal_complete",
                    "status": "fail",
                    "detail": "failed_requirements=aaai_submission_decision_preflight_ready",
                },
            ],
        }

        pending = decision.effective_pending_goal_requirements(goal)

        self.assertIn("aaai_final_submission_ready", pending)
        self.assertTrue(decision.self_referential_goal_failure(goal))


if __name__ == "__main__":
    unittest.main()
