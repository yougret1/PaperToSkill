import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "score_real_reuse_snapatac2.py"
sys.path.insert(0, str(ROOT / "scripts"))

from score_real_reuse_snapatac2 import score_artifact  # noqa: E402


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


class ScoreRealReuseSnapATAC2Test(unittest.TestCase):
    def test_scores_valid_snap_t1_embedding_artifact(self):
        with tempfile.TemporaryDirectory() as tmp:
            artifact_dir = Path(tmp) / "artifact"
            write_json(
                artifact_dir / "candidate_output.json",
                {
                    "completed": True,
                    "method_steps": ["Run SnapATAC2 matrix-free spectral embedding"],
                    "embedding_artifacts": ["embedding.csv", "neighbors.json"],
                    "runtime_seconds": 12.5,
                    "peak_memory_mb": 512,
                },
            )

            result = score_artifact("SNAP-T1", artifact_dir)

            self.assertEqual(1.0, result["task_score"])
            self.assertTrue(result["success"])
            self.assertEqual("runtime_memory_quality", result["metric_name"])

    def test_scores_valid_snap_t2_with_reference_labels(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            artifact_dir = tmp_path / "artifact"
            labels_path = tmp_path / "reference_labels_or_proxy.json"
            budget_path = tmp_path / "resource_budget.json"
            manifest_path = tmp_path / "asset_manifest.json"
            write_json(labels_path, {"labels": ["a", "a", "b", "b"]})
            write_json(budget_path, {"max_runtime_seconds": 100, "max_peak_memory_mb": 2048})
            write_json(
                manifest_path,
                {
                    "files": [
                        {"slot": "resource_budget", "path": str(budget_path), "visibility": "model_visible"},
                        {"slot": "reference_labels_or_proxy", "path": str(labels_path), "visibility": "scorer_only"},
                    ]
                },
            )
            write_json(
                artifact_dir / "candidate_output.json",
                {
                    "completed": True,
                    "method_steps": ["Use SnapATAC2 spectral embedding before clustering"],
                    "clustering_artifacts": {"clusters": "clusters.csv"},
                    "predicted_labels": ["a", "a", "b", "b"],
                    "quality_metrics": {},
                    "runtime_seconds": 10,
                    "peak_memory_mb": 1024,
                },
            )

            result = score_artifact("SNAP-T2", artifact_dir, manifest_path, tmp_path)

            self.assertEqual(1.0, result["task_score"])
            self.assertTrue(result["success"])
            self.assertEqual("computed_from_reference_labels", result["quality_detail"]["source"])
            self.assertEqual(1.0, result["quality_detail"]["ari"])
            self.assertEqual(1.0, result["quality_detail"]["nmi"])

    def test_invalid_or_missing_json_is_scored_not_crashed(self):
        with tempfile.TemporaryDirectory() as tmp:
            artifact_dir = Path(tmp) / "artifact"
            artifact_dir.mkdir()

            result = score_artifact("SNAP-T1", artifact_dir)

            self.assertEqual(0.0, result["task_score"])
            self.assertFalse(result["success"])
            self.assertIn("missing candidate_output.json", result["failure_reason"])

    def test_cli_writes_metric_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            artifact_dir = tmp_path / "artifact"
            output = tmp_path / "metric.json"
            write_json(
                artifact_dir / "candidate_output.json",
                {
                    "completed": True,
                    "method_steps": ["Run SnapATAC2 spectral embedding"],
                    "embedding_artifacts": ["embedding.csv"],
                    "runtime_seconds": 1,
                    "peak_memory_mb": 128,
                },
            )

            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--task",
                    "SNAP-T1",
                    "--artifact-dir",
                    str(artifact_dir),
                    "--output-json",
                    str(output),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            self.assertEqual(1.0, json.loads(output.read_text(encoding="utf-8"))["task_score"])


if __name__ == "__main__":
    unittest.main()
