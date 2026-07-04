import gzip
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_real_reuse_snapatac2_executable_followup.py"


class RunRealReuseSnapATAC2ExecutableFollowupTest(unittest.TestCase):
    def test_cli_runs_paired_executable_followup_without_main_raw_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            root = tmp_path / "root"
            make_asset(root, "SNAP-T1", include_strand=True)
            make_asset(root, "SNAP-T2", include_strand=False)
            output_json = tmp_path / "followup.json"
            output_md = tmp_path / "followup.md"
            output_csv = tmp_path / "followup.csv"

            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--root",
                    str(root),
                    "--run-id",
                    "unit_snap_exec_followup",
                    "--output-dir",
                    str(tmp_path / "runs"),
                    "--output-json",
                    str(output_json),
                    "--output-md",
                    str(output_md),
                    "--output-csv",
                    str(output_csv),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            self.assertIn("unit_snap_exec_followup", completed.stdout)
            report = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertEqual("complete", report["overall_status"])
            self.assertTrue(report["main_rows_unchanged"])
            self.assertEqual("not_appended_to_main_raw_rows", report["raw_rows_policy"])
            self.assertEqual(4, len(report["rows"]))
            self.assertEqual({"summary", "papertoskill"}, {row["condition"] for row in report["rows"]})
            self.assertTrue(all(row["success"] for row in report["rows"]))
            self.assertFalse((root / "results" / "real_reuse" / "raw_rows.jsonl").exists())
            for row in report["rows"]:
                candidate = root / row["candidate_output"]
                metric = root / row["metric_path"]
                self.assertTrue(candidate.exists())
                self.assertTrue(metric.exists())
                payload = json.loads(candidate.read_text(encoding="utf-8"))
                self.assertTrue(payload["completed"])
                self.assertGreaterEqual(payload["runtime_seconds"], 0)
                self.assertGreaterEqual(payload["peak_memory_mb"], 0)


def make_asset(root: Path, task_id: str, include_strand: bool) -> None:
    asset_dir = root / "benchmarks" / "real_reuse" / "assets" / task_id
    asset_dir.mkdir(parents=True)
    fragment = asset_dir / "miniature_fragment.tsv.gz"
    lines = [
        "chr1\t10\t20\tcell_a\t1\t+",
        "chr1\t30\t45\tcell_a\t1\t-",
        "chr2\t50\t70\tcell_b\t1\t+",
        "chr2\t80\t100\tcell_c\t1\t-",
    ]
    if not include_strand:
        lines = ["\t".join(line.split("\t")[:5]) for line in lines]
    with gzip.open(fragment, "wt", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")
    resource_budget = asset_dir / "resource_budget.json"
    scorer_thresholds = asset_dir / "scorer_thresholds.json"
    resource_budget.write_text(
        json.dumps({"max_runtime_seconds": 1800, "max_peak_memory_mb": 8192}),
        encoding="utf-8",
    )
    scorer_thresholds.write_text(json.dumps({"success_threshold": 0.8}), encoding="utf-8")
    (asset_dir / "asset_manifest.json").write_text(
        json.dumps(
            {
                "files": [
                    {"slot": "miniature_fragment", "path": fragment.as_posix()},
                    {"slot": "resource_budget", "path": resource_budget.as_posix()},
                    {"slot": "scorer_thresholds", "path": scorer_thresholds.as_posix()},
                ]
            }
        ),
        encoding="utf-8",
    )


if __name__ == "__main__":
    unittest.main()
