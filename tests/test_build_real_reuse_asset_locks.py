import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_real_reuse_asset_locks.py"
TASK_DIR = ROOT / "benchmarks" / "real_reuse" / "tasks"
FIXTURE_DIR = ROOT / "benchmarks" / "real_reuse" / "fixtures"
CANDIDATE_DIR = ROOT / "benchmarks" / "real_reuse" / "fixture_candidates"


class BuildRealReuseAssetLocksTest(unittest.TestCase):
    def test_cli_materializes_all_asset_locks(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp) / "asset_locks"
            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--task-dir",
                    str(TASK_DIR),
                    "--fixture-dir",
                    str(FIXTURE_DIR),
                    "--candidate-dir",
                    str(CANDIDATE_DIR),
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
            self.assertEqual("asset_lock_ready_preparation_pending", swe_t1["status"])
            self.assertEqual("sqlfluff__sqlfluff-1625", swe_t1["locked_task_instance"]["instance_id"])
            self.assertEqual("D:/a_work/gitee", swe_t1["local_materialization_targets"]["external_project_root"])
            self.assertEqual("not_started", swe_t1["preparation_contract"]["status"])
            self.assertTrue(swe_t1["preparation_contract"]["hidden_from_model"])
            self.assertTrue(any(lock["observed_revision"] for lock in swe_t1["source_revision_locks"]))
            self.assertTrue(
                all(lock["materialization_status"] == "not_materialized" for lock in swe_t1["asset_slot_locks"])
            )

    def test_current_asset_locks_are_present(self):
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
        lock_dir = ROOT / "benchmarks" / "real_reuse" / "asset_locks"
        present = {path.name for path in lock_dir.glob("*.json")}
        self.assertEqual(expected, present)


if __name__ == "__main__":
    unittest.main()
