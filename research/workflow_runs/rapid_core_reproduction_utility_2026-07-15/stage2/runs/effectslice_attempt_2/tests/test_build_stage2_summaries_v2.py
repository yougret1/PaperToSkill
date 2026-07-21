import json
import sys
import tempfile
import unittest
from pathlib import Path


RUN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RUN_ROOT))

from build_stage2_summaries_v2 import build_summaries  # noqa: E402


def task_summary(
    task_key,
    *,
    baseline_successes,
    full_successes,
    slice_successes,
    full_benefit,
    preservation,
    slice_benefit,
    admitted,
):
    replicates = []
    for index in range(18):
        replicates.append(
            {
                "replicate_id": f"r{index + 1:03d}",
                "conditions": {
                    "B": {"success": index < baseline_successes},
                    "F": {"success": index < full_successes},
                    "S": {"success": index < slice_successes},
                },
                "integrity_violations": [],
            }
        )
    return {
        "schema_version": "effectslice-confirmation-v2-task-summary.v1",
        "task_key": task_key,
        "selected_candidate_id": "prefix_03",
        "confirmation_family_sha256": task_key[0] * 64,
        "classification": (
            "task_local_admission_passed"
            if admitted
            else "task_local_admission_rejected"
        ),
        "statistical_unit": "independent_agent_run",
        "replicate_denominator": 18,
        "clustered_hidden_checks_per_run": 64,
        "schedule_complete": True,
        "integrity_passed": True,
        "hard_constraints_passed": admitted,
        "hypotheses": {
            "H_full_benefit_run_level": {
                "successes": full_benefit,
                "total": 18,
                "one_sided_cp_lower": full_benefit / 20,
                "minimum_prevalence": 0.8,
            },
            "H_slice_preservation_run_level": {
                "successes": preservation,
                "total": 18,
                "one_sided_cp_lower": preservation / 20,
                "minimum_prevalence": 0.8,
            },
            "H_slice_benefit_run_level": {
                "successes": slice_benefit,
                "total": 18,
                "one_sided_cp_lower": slice_benefit / 20,
                "minimum_prevalence": 0.8,
            },
        },
        "replicates": replicates,
        "task_local_admission_ready": admitted,
        "general_effectslice_claim_ready": False,
        "prior_confirmation_status": "contaminated_development_excluded",
    }


class BuildStage2SummariesV2Test(unittest.TestCase):
    def test_builds_all_required_summaries_from_run_level_json(self):
        snap = task_summary(
            "snap_mfse",
            baseline_successes=2,
            full_successes=14,
            slice_successes=11,
            full_benefit=12,
            preservation=10,
            slice_benefit=9,
            admitted=False,
        )
        tool = task_summary(
            "toolformer_filter",
            baseline_successes=1,
            full_successes=18,
            slice_successes=18,
            full_benefit=17,
            preservation=18,
            slice_benefit=17,
            admitted=True,
        )
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            snap_path = root / "snap.json"
            tool_path = root / "tool.json"
            snap_path.write_text(json.dumps(snap), encoding="utf-8")
            tool_path.write_text(json.dumps(tool), encoding="utf-8")

            paths = build_summaries([snap_path, tool_path], root / "logs")

            baseline = json.loads(Path(paths["baseline"]).read_text(encoding="utf-8"))
            research = json.loads(Path(paths["research"]).read_text(encoding="utf-8"))
            ablation = json.loads(Path(paths["ablation"]).read_text(encoding="utf-8"))

        self.assertEqual(
            [row["full_benefit_successes"] for row in baseline["task_rows"]],
            [12, 17],
        )
        self.assertEqual(baseline["statistical_unit"], "independent_agent_run")
        self.assertEqual(baseline["metric"]["value"], 29)
        self.assertEqual(research["metric"]["value"], 1)
        self.assertFalse(research["general_effectslice_claim_ready"])
        self.assertEqual(
            ablation["task_rows"][0]["condition_successes"],
            {"B": 2, "F": 14, "S": 11},
        )
        self.assertEqual(
            ablation["task_rows"][1]["condition_successes"],
            {"B": 1, "F": 18, "S": 18},
        )
        self.assertEqual(ablation["replicate_denominator_per_task"], 18)
        self.assertEqual(ablation["clustered_hidden_checks_per_run"], 64)

    def test_rejects_incomplete_or_non_run_level_inputs(self):
        invalid = task_summary(
            "snap_mfse",
            baseline_successes=0,
            full_successes=18,
            slice_successes=18,
            full_benefit=18,
            preservation=18,
            slice_benefit=18,
            admitted=True,
        )
        invalid["schedule_complete"] = False
        invalid["statistical_unit"] = "hidden_case"
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "invalid.json"
            path.write_text(json.dumps(invalid), encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "independent_agent_run"):
                build_summaries([path], Path(temporary) / "logs")


if __name__ == "__main__":
    unittest.main()
