import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_real_reuse_task_specs.py"
MASTER = ROOT / "benchmarks" / "real_reuse" / "real_reuse_v0.json"


class BuildRealReuseTaskSpecsTest(unittest.TestCase):
    def test_cli_materializes_all_task_specs(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp) / "tasks"
            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--master",
                    str(MASTER),
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
            self.assertEqual("AIDE-T1", aide_t1["id"])
            self.assertEqual("spec_ready_assets_pending", aide_t1["status"])
            self.assertEqual({"summary", "papertoskill"}, {condition["id"] for condition in aide_t1["conditions"]})
            self.assertIn("task_score", aide_t1["raw_row_schema"])
            self.assertEqual("none_mid_run", aide_t1["run_controls"]["first_pass_human_intervention"])
            self.assertIn("reported_reference_only_until_local_reproduction", aide_t1["reference_score_policy"]["comparability"])

    def test_current_task_specs_are_present(self):
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
        task_dir = ROOT / "benchmarks" / "real_reuse" / "tasks"
        present = {path.name for path in task_dir.glob("*.json")}
        self.assertEqual(expected, present)


if __name__ == "__main__":
    unittest.main()
