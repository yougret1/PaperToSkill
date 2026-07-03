import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PREP_SCRIPT = ROOT / "scripts" / "prepare_real_reuse_snapatac2_fixture.py"
RUN_SCRIPT = ROOT / "scripts" / "run_real_reuse_snapatac2.py"
sys.path.insert(0, str(ROOT / "scripts"))

from run_real_reuse_snapatac2 import build_prompt  # noqa: E402


VALID_SNAP_T2_RESPONSE = """{
  "completed": true,
  "method_steps": ["Use SnapATAC2 spectral embedding before clustering"],
  "clustering_artifacts": {"clusters": "clusters.csv"},
  "predicted_labels": ["a", "a", "b", "b"],
  "quality_metrics": {},
  "runtime_seconds": 10,
  "peak_memory_mb": 1024
}
"""


def prepare_temp_root(tmp_path: Path) -> Path:
    root = tmp_path / "root"
    for relative_dir in [
        "benchmarks/real_reuse/tasks",
        "benchmarks/real_reuse/asset_locks",
        "generated_skills/real_reuse/snapatac2",
        "baselines/real_reuse",
    ]:
        (root / relative_dir).mkdir(parents=True)
    shutil.copy2(
        ROOT / "benchmarks" / "real_reuse" / "tasks" / "SNAP-T2.json",
        root / "benchmarks" / "real_reuse" / "tasks" / "SNAP-T2.json",
    )
    shutil.copy2(
        ROOT / "benchmarks" / "real_reuse" / "asset_locks" / "SNAP-T2.json",
        root / "benchmarks" / "real_reuse" / "asset_locks" / "SNAP-T2.json",
    )
    (root / "generated_skills" / "real_reuse" / "snapatac2" / "SKILL.md").write_text(
        "# SnapATAC2 Skill\n\nUse matrix-free spectral embedding, clustering, ARI, NMI, runtime, and memory.\n",
        encoding="utf-8",
    )
    labels = tmp_path / "reference_labels.json"
    labels.write_text(json.dumps({"labels": ["a", "a", "b", "b"]}), encoding="utf-8")
    subprocess.run(
        [
            sys.executable,
            str(PREP_SCRIPT),
            "--root",
            str(root),
            "--task",
            "SNAP-T2",
            "--reference-labels",
            str(labels),
            "--output-dir",
            str(root / "benchmarks" / "real_reuse" / "assets" / "SNAP-T2"),
            "--condition-dir",
            str(root / "baselines" / "real_reuse"),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return root


class RunRealReuseSnapATAC2Test(unittest.TestCase):
    def test_fixture_response_produces_scored_raw_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            root = prepare_temp_root(tmp_path)
            fixture_dir = tmp_path / "fixture_responses"
            fixture_dir.mkdir()
            for condition in ("summary", "papertoskill"):
                (fixture_dir / f"SNAP-T2_{condition}.json").write_text(VALID_SNAP_T2_RESPONSE, encoding="utf-8")
            raw_rows = tmp_path / "raw_rows.jsonl"
            output_json = tmp_path / "snap_report.json"

            completed = subprocess.run(
                [
                    sys.executable,
                    str(RUN_SCRIPT),
                    "--root",
                    str(root),
                    "--task",
                    "SNAP-T2",
                    "--condition",
                    "summary",
                    "--condition",
                    "papertoskill",
                    "--fixture-response-dir",
                    str(fixture_dir),
                    "--run-id",
                    "unit_snap_fixture_run",
                    "--output-dir",
                    str(tmp_path / "runs"),
                    "--raw-rows-output",
                    str(raw_rows),
                    "--output-json",
                    str(output_json),
                    "--output-md",
                    str(tmp_path / "snap_report.md"),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            self.assertIn("unit_snap_fixture_run", completed.stdout)
            report = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertEqual("complete", report["overall_status"])
            rows = [json.loads(line) for line in raw_rows.read_text(encoding="utf-8").splitlines()]
            self.assertEqual(2, len(rows))
            self.assertEqual({"summary", "papertoskill"}, {row["condition"] for row in rows})
            self.assertTrue(all(row["success"] for row in rows))
            self.assertTrue((tmp_path / "runs" / "SNAP-T2" / "summary" / "unit_snap_fixture_run" / "metric.json").exists())

    def test_missing_credentials_records_pending_without_raw_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            root = prepare_temp_root(tmp_path)
            raw_rows = tmp_path / "raw_rows.jsonl"
            output_json = tmp_path / "snap_report.json"

            subprocess.run(
                [
                    sys.executable,
                    str(RUN_SCRIPT),
                    "--root",
                    str(root),
                    "--task",
                    "SNAP-T2",
                    "--condition",
                    "summary",
                    "--base-url-env",
                    "PAPERTOSKILL_UNITTEST_MISSING_BASE_URL",
                    "--api-key-env",
                    "PAPERTOSKILL_UNITTEST_MISSING_API_KEY",
                    "--run-id",
                    "unit_snap_missing_credentials",
                    "--output-dir",
                    str(tmp_path / "runs"),
                    "--raw-rows-output",
                    str(raw_rows),
                    "--output-json",
                    str(output_json),
                    "--output-md",
                    str(tmp_path / "snap_report.md"),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            report = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertEqual("pending", report["overall_status"])
            self.assertFalse(raw_rows.exists())
            self.assertIn("missing_base_url_or_api_key_env", report["results"][0]["failure_reason"])

    def test_missing_fixture_records_pending_without_raw_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            root = tmp_path / "root"
            (root / "benchmarks" / "real_reuse" / "tasks").mkdir(parents=True)
            shutil.copy2(
                ROOT / "benchmarks" / "real_reuse" / "tasks" / "SNAP-T2.json",
                root / "benchmarks" / "real_reuse" / "tasks" / "SNAP-T2.json",
            )
            raw_rows = tmp_path / "raw_rows.jsonl"
            output_json = tmp_path / "snap_report.json"

            subprocess.run(
                [
                    sys.executable,
                    str(RUN_SCRIPT),
                    "--root",
                    str(root),
                    "--task",
                    "SNAP-T2",
                    "--condition",
                    "summary",
                    "--run-id",
                    "unit_snap_missing_fixture",
                    "--output-dir",
                    str(tmp_path / "runs"),
                    "--raw-rows-output",
                    str(raw_rows),
                    "--output-json",
                    str(output_json),
                    "--output-md",
                    str(tmp_path / "snap_report.md"),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            report = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertEqual("pending", report["overall_status"])
            self.assertFalse(raw_rows.exists())
            self.assertEqual("missing_fixture_assets", report["results"][0]["failure_reason"])

    def test_prompt_uses_condition_context_without_hidden_assets(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = prepare_temp_root(Path(tmp))
            prompt = build_prompt(root, "SNAP-T2", "summary")

            self.assertIn("Real-Reuse Condition: summary", prompt)
            self.assertIn("Real-Reuse Summary Baseline", prompt)
            self.assertIn("SNAP-T2 Locked SnapATAC2 Task Prompt", prompt)
            self.assertIn("expected_artifact_schema", prompt)
            self.assertNotIn("reference_labels_or_proxy.json", prompt)
            self.assertNotIn("hidden_from_model", prompt)
            self.assertNotIn("cell_a", prompt)


if __name__ == "__main__":
    unittest.main()
