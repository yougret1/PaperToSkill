import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_real_reuse_fixture_manifests.py"
TASK_DIR = ROOT / "benchmarks" / "real_reuse" / "tasks"


class BuildRealReuseFixtureManifestsTest(unittest.TestCase):
    def test_cli_materializes_all_fixture_manifests(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp) / "fixtures"
            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--task-dir",
                    str(TASK_DIR),
                    "--output-dir",
                    str(output_dir),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            paths = sorted(output_dir.glob("*.json"))
            self.assertEqual(8, len(paths))
            swe_t1 = json.loads((output_dir / "SWE-T1.json").read_text(encoding="utf-8"))
            self.assertEqual("SWE-T1", swe_t1["task_id"])
            self.assertEqual("fixture_manifest_ready_assets_pending", swe_t1["status"])
            self.assertEqual({"summary", "papertoskill"}, {asset["condition"] for asset in swe_t1["context_assets"]})
            self.assertEqual("none_mid_run", swe_t1["execution_budget"]["first_pass_human_intervention"])
            self.assertEqual("not_started", swe_t1["provenance_and_license"]["download_or_clone_status"])
            self.assertIn("patch_file", swe_t1["scoring_contract"]["metric_inputs"])

    def test_current_fixture_manifests_are_present(self):
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
        fixture_dir = ROOT / "benchmarks" / "real_reuse" / "fixtures"
        present = {path.name for path in fixture_dir.glob("*.json")}
        self.assertEqual(expected, present)


if __name__ == "__main__":
    unittest.main()
