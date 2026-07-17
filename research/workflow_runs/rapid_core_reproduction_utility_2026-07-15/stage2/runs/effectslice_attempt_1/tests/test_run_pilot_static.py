import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


RUN_ROOT = Path(__file__).resolve().parents[1]
PROJECT_FIXTURE = RUN_ROOT / "tests" / "fixtures" / "readiness" / "aggregate"
RUN_FIXTURE = RUN_ROOT / "tests" / "fixtures" / "runner_output"
sys.path.insert(0, str(RUN_ROOT))
sys.path.insert(0, str(RUN_ROOT / "src"))

from run_pilot import build_summaries, run_pilot  # noqa: E402


class StaticPilotRunnerTest(unittest.TestCase):
    def test_records_invalid_format_before_reraising(self):
        with patch("run_pilot.audit_project", side_effect=ValueError("invalid task schema")), patch(
            "run_pilot._write_json"
        ) as write_json:
            with self.assertRaisesRegex(ValueError, "invalid task schema"):
                run_pilot(PROJECT_FIXTURE, RUN_FIXTURE)

        error_path, payload = write_json.call_args.args
        self.assertEqual(error_path, RUN_FIXTURE / "logs" / "execution_error.json")
        self.assertEqual(payload["failure_class"], "invalid_format")
        self.assertEqual(payload["error_type"], "ValueError")

    def test_ready_audit_is_not_described_as_missing_paired_evidence(self):
        summaries = build_summaries(
            {
                "task_count": 1,
                "ready_task_count": 1,
                "blocker_counts": {},
                "evidence_boundary": (
                    "Read-only development readiness audit; this is not EffectSlice effectiveness evidence."
                ),
            },
            "experiment_results/pilot/readiness_report.json",
        )

        ablation = summaries["ablation"]
        self.assertEqual(ablation["status"], "not_run_route_a_scope")
        self.assertNotIn("zero current tasks", ablation["entries"][0]["analysis"])

    def test_writes_readiness_and_three_bounded_summaries(self):
        outputs = run_pilot(PROJECT_FIXTURE, RUN_FIXTURE)

        expected = {
            "readiness": RUN_FIXTURE / "experiment_results/pilot/readiness_report.json",
            "baseline": RUN_FIXTURE / "logs/baseline_summary.json",
            "research": RUN_FIXTURE / "logs/research_summary.json",
            "ablation": RUN_FIXTURE / "logs/ablation_summary.json",
        }
        self.assertEqual(outputs, {key: str(path) for key, path in expected.items()})
        for path in expected.values():
            payload = json.loads(path.read_text(encoding="utf-8"))
            self.assertIn("evidence_boundary", payload)
            self.assertIn("not EffectSlice effectiveness evidence", payload["evidence_boundary"])
        readiness = json.loads(expected["readiness"].read_text(encoding="utf-8"))
        self.assertEqual(readiness["ready_task_count"], 0)
        for summary_name in ("baseline", "research", "ablation"):
            summary = json.loads(expected[summary_name].read_text(encoding="utf-8"))
            self.assertEqual(len(summary["entries"]), 1)
            self.assertIn("metric", summary["entries"][0])


if __name__ == "__main__":
    unittest.main()
