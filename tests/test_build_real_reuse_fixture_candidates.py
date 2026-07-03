import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_real_reuse_fixture_candidates.py"
TASK_DIR = ROOT / "benchmarks" / "real_reuse" / "tasks"
FIXTURE_DIR = ROOT / "benchmarks" / "real_reuse" / "fixtures"


class BuildRealReuseFixtureCandidatesTest(unittest.TestCase):
    def test_cli_materializes_all_fixture_candidates(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp) / "fixture_candidates"
            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--task-dir",
                    str(TASK_DIR),
                    "--fixture-dir",
                    str(FIXTURE_DIR),
                    "--output-dir",
                    str(output_dir),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            paths = sorted(output_dir.glob("*.json"))
            self.assertEqual(8, len(paths))
            aide_t1 = json.loads((output_dir / "AIDE-T1.json").read_text(encoding="utf-8"))
            self.assertEqual("AIDE-T1", aide_t1["task_id"])
            self.assertEqual("candidate_assets_selected_preparation_pending", aide_t1["status"])
            self.assertEqual("D:/a_work/gitee", aide_t1["preparation_plan"]["external_project_root"])
            self.assertEqual("not_started", aide_t1["preparation_plan"]["preparation_status"])
            self.assertEqual("to_implement_next_phase", aide_t1["scoring_plan"]["scorer_status"])
            self.assertEqual("none_mid_run", aide_t1["run_controls"]["first_pass_human_intervention"])
            self.assertTrue(all(asset["materialization_status"] == "not_downloaded" for asset in aide_t1["candidate_assets"]))

    def test_current_fixture_candidates_are_present(self):
        expected = {
            "AIDE-T1.json",
            "AIDE-T2.json",
            "SWE-T1.json",
            "SWE-T2.json",
            "REF-T1.json",
            "REF-T2.json",
            "SNAP-T1.json",
            "SNAP-T2.json",
        }
        candidate_dir = ROOT / "benchmarks" / "real_reuse" / "fixture_candidates"
        present = {path.name for path in candidate_dir.glob("*.json")}
        self.assertEqual(expected, present)


if __name__ == "__main__":
    unittest.main()
