import json
import sys
import tempfile
import unittest
from pathlib import Path


RUN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RUN_ROOT))

from build_stage2_summaries import build_summaries  # noqa: E402


class BuildStage2SummariesTest(unittest.TestCase):
    def test_consolidates_success_failure_and_abstention_without_general_claim(self):
        with tempfile.TemporaryDirectory(dir=RUN_ROOT) as tmp:
            result = build_summaries(RUN_ROOT, Path(tmp))
            summaries = {
                name: json.loads(Path(path).read_text(encoding="utf-8"))
                for name, path in result.items()
            }

        baseline = summaries["baseline"]
        research = summaries["research"]
        ablation = summaries["ablation"]
        self.assertEqual(baseline["metric"]["name"], "eligible_full_artifact_tasks")
        self.assertEqual(baseline["metric"]["value"], 2)
        self.assertEqual(
            research["metric"]["name"], "sealed_confirmed_task_local_slices"
        )
        self.assertEqual(research["metric"]["value"], 1)
        self.assertFalse(research["general_effectslice_claim_ready"])
        self.assertEqual(
            ablation["metric"]["name"], "sealed_false_discovery_rejections"
        )
        self.assertEqual(ablation["metric"]["value"], 1)

        rows = {row["task_id"]: row for row in research["task_rows"]}
        self.assertEqual(rows["SNAP-MFSE"]["confirmation"], "passed")
        self.assertEqual(rows["TOOLFORMER-FILTER"]["confirmation"], "failed")
        self.assertEqual(rows["AIDE-T2"]["disposition"], "development_only")
        self.assertEqual(rows["SWE-T2"]["disposition"], "abstain")
        self.assertEqual(
            rows["TOOLFORMER-FILTER"]["preservation_violations"], 15
        )

        eligibility_rows = {
            row["task_id"]: row for row in baseline["full_artifact_rows"]
        }
        self.assertEqual(
            eligibility_rows["SNAP-MFSE"]["classification"],
            "eligible_full_artifact",
        )
        self.assertEqual(eligibility_rows["SNAP-MFSE"]["beneficial_cases"], 21)
        self.assertEqual(eligibility_rows["SNAP-MFSE"]["total_cases"], 21)

    def test_every_declared_evidence_file_exists_and_rebuild_is_identical(self):
        with tempfile.TemporaryDirectory(dir=RUN_ROOT) as first, tempfile.TemporaryDirectory(
            dir=RUN_ROOT
        ) as second:
            first_result = build_summaries(RUN_ROOT, Path(first))
            second_result = build_summaries(RUN_ROOT, Path(second))
            for key in ("baseline", "research", "ablation"):
                first_bytes = Path(first_result[key]).read_bytes()
                second_bytes = Path(second_result[key]).read_bytes()
                self.assertEqual(first_bytes, second_bytes)
                payload = json.loads(first_bytes.decode("utf-8"))
                for relative in payload["exp_results_data_files"]:
                    self.assertTrue((RUN_ROOT / relative).is_file(), relative)


if __name__ == "__main__":
    unittest.main()
