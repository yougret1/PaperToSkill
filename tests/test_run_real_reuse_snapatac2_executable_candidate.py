import gzip
import json
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_real_reuse_snapatac2_executable_candidate.py"


class RunRealReuseSnapATAC2ExecutableCandidateTest(unittest.TestCase):
    def test_cli_executes_candidate_scripts_without_main_raw_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            root = tmp_path / "root"
            make_asset(root, "SNAP-T1")
            make_asset(root, "SNAP-T2")
            candidate_dir = tmp_path / "candidates"
            candidate_dir.mkdir()
            for task_id in ("SNAP-T1", "SNAP-T2"):
                for condition in ("summary", "papertoskill"):
                    write_candidate(candidate_dir / f"{task_id}_{condition}.py", success=True)

            output_json = tmp_path / "report.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--root",
                    str(root),
                    "--candidate-dir",
                    str(candidate_dir),
                    "--run-id",
                    "unit_snap_exec_candidate",
                    "--output-dir",
                    str(tmp_path / "runs"),
                    "--output-json",
                    str(output_json),
                    "--output-md",
                    str(tmp_path / "report.md"),
                    "--output-csv",
                    str(tmp_path / "report.csv"),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            self.assertIn("unit_snap_exec_candidate", completed.stdout)
            report = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertEqual("complete", report["overall_status"])
            self.assertEqual("not_appended_to_main_raw_rows", report["raw_rows_policy"])
            self.assertTrue(report["main_rows_unchanged"])
            self.assertEqual(4, len(report["rows"]))
            self.assertTrue(all(row["success"] for row in report["rows"]))
            self.assertFalse((root / "results" / "real_reuse" / "raw_rows.jsonl").exists())
            for row in report["rows"]:
                candidate_output = root / row["candidate_output"]
                resource_record = root / row["resource_record"]
                artifact_manifest = root / row["artifact_manifest"]
                self.assertTrue(candidate_output.exists())
                self.assertTrue(resource_record.exists())
                self.assertTrue(artifact_manifest.exists())
                payload = json.loads(candidate_output.read_text(encoding="utf-8"))
                self.assertTrue(payload["completed"])
                self.assertEqual("runner_after_execution", payload["notes"]["completed_field_owner"])

    def test_runner_ignores_model_authored_completed_without_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            root = tmp_path / "root"
            make_asset(root, "SNAP-T1")
            candidate_dir = tmp_path / "candidates"
            candidate_dir.mkdir()
            write_candidate(candidate_dir / "SNAP-T1_summary.py", success=False)
            output_json = tmp_path / "report.json"

            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--root",
                    str(root),
                    "--task",
                    "SNAP-T1",
                    "--condition",
                    "summary",
                    "--candidate-dir",
                    str(candidate_dir),
                    "--run-id",
                    "unit_snap_exec_candidate_failure",
                    "--output-dir",
                    str(tmp_path / "runs"),
                    "--output-json",
                    str(output_json),
                    "--output-md",
                    str(tmp_path / "report.md"),
                    "--output-csv",
                    str(tmp_path / "report.csv"),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            report = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertEqual("complete", report["overall_status"])
            row = report["rows"][0]
            self.assertFalse(row["success"])
            payload = json.loads((root / row["candidate_output"]).read_text(encoding="utf-8"))
            self.assertFalse(payload["completed"])
            self.assertTrue(payload["notes"]["candidate_authored_completed_ignored"])


def make_asset(root: Path, task_id: str) -> None:
    asset_dir = root / "benchmarks" / "real_reuse" / "assets" / task_id
    asset_dir.mkdir(parents=True)
    fragment = asset_dir / "miniature_fragment.tsv.gz"
    with gzip.open(fragment, "wt", encoding="utf-8") as handle:
        handle.write("chr1\t10\t20\tcell_a\t1\t+\nchr1\t30\t40\tcell_b\t1\t-\n")
    resource_budget = asset_dir / "resource_budget.json"
    scorer_thresholds = asset_dir / "scorer_thresholds.json"
    resource_budget.write_text(json.dumps({"max_runtime_seconds": 1800, "max_peak_memory_mb": 8192}), encoding="utf-8")
    scorer_thresholds.write_text(json.dumps({"success_threshold": 0.8}), encoding="utf-8")
    files = [
        {"slot": "miniature_fragment", "path": fragment.as_posix()},
        {"slot": "resource_budget", "path": resource_budget.as_posix()},
        {"slot": "scorer_thresholds", "path": scorer_thresholds.as_posix()},
    ]
    (asset_dir / "asset_manifest.json").write_text(json.dumps({"files": files}), encoding="utf-8")


def write_candidate(path: Path, *, success: bool) -> None:
    path.write_text(
        textwrap.dedent(
            f"""
            import argparse
            import json
            from pathlib import Path

            parser = argparse.ArgumentParser()
            parser.add_argument("--task-id", required=True)
            parser.add_argument("--condition", required=True)
            parser.add_argument("--fragment", required=True)
            parser.add_argument("--artifact-dir", required=True)
            parser.add_argument("--result-json", required=True)
            args = parser.parse_args()
            artifact_dir = Path(args.artifact_dir)
            artifact_dir.mkdir(parents=True, exist_ok=True)
            if {str(success)}:
                if args.task_id == "SNAP-T1":
                    for name in ["embedding.csv", "cell_features.csv", "fragment_summary.json"]:
                        (artifact_dir / name).write_text("ok\\n", encoding="utf-8")
                else:
                    for name in ["clusters.csv", "marker_summary.json", "embedding.csv"]:
                        (artifact_dir / name).write_text("ok\\n", encoding="utf-8")
            result = {{
                "completed": True,
                "method_steps": ["Use SnapATAC2 spectral embedding before artifact scoring"],
                "quality_metrics": {{"proxy_quality_score": 1.0}},
            }}
            Path(args.result_json).write_text(json.dumps(result), encoding="utf-8")
            """
        ).lstrip(),
        encoding="utf-8",
    )


if __name__ == "__main__":
    unittest.main()
