import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "prepare_real_reuse_snapatac2_fixture.py"


def prepare_temp_root(tmp_path: Path) -> Path:
    root = tmp_path / "root"
    for relative_dir in [
        "benchmarks/real_reuse/asset_locks",
        "generated_skills/real_reuse/snapatac2",
        "baselines/real_reuse",
    ]:
        (root / relative_dir).mkdir(parents=True)
    shutil.copy2(
        ROOT / "benchmarks" / "real_reuse" / "asset_locks" / "SNAP-T2.json",
        root / "benchmarks" / "real_reuse" / "asset_locks" / "SNAP-T2.json",
    )
    (root / "generated_skills" / "real_reuse" / "snapatac2" / "SKILL.md").write_text(
        "# SnapATAC2 Skill\n\nUse matrix-free spectral embedding and objective clustering metrics.\n",
        encoding="utf-8",
    )
    return root


class PrepareRealReuseSnapATAC2FixtureTest(unittest.TestCase):
    def test_prepare_snap_t2_writes_visible_assets_and_hidden_reference_labels(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            root = prepare_temp_root(tmp_path)
            reference_labels = tmp_path / "reference_labels.json"
            reference_labels.write_text(
                json.dumps({"labels": ["cell_a", "cell_a", "cell_b", "cell_b"]}),
                encoding="utf-8",
            )
            output_dir = root / "benchmarks" / "real_reuse" / "assets" / "SNAP-T2"

            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--root",
                    str(root),
                    "--task",
                    "SNAP-T2",
                    "--reference-labels",
                    str(reference_labels),
                    "--output-dir",
                    str(output_dir),
                    "--condition-dir",
                    str(root / "baselines" / "real_reuse"),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            self.assertIn("asset_manifest.json", completed.stdout)
            manifest = json.loads((output_dir / "asset_manifest.json").read_text(encoding="utf-8"))
            self.assertEqual("SNAP-T2", manifest["task_id"])
            self.assertEqual("snapatac2", manifest["source_paper_id"])
            self.assertEqual("prepared_assets_ready_for_dry_scoring", manifest["status"])
            files = {row["slot"]: row for row in manifest["files"]}
            self.assertEqual("scorer_only", files["reference_labels_or_proxy"]["visibility"])
            self.assertEqual([files["reference_labels_or_proxy"]["path"]], manifest["hidden_from_model"])
            visible_slots = {row["slot"] for row in manifest["files"] if row["visibility"] == "model_visible"}
            self.assertTrue({"dataset_manifest", "resource_budget", "expected_artifact_schema", "task_prompt"} <= visible_slots)
            self.assertTrue((root / "baselines" / "real_reuse" / "SNAP-T2_summary.md").exists())
            prompt = (output_dir / "task_prompt.md").read_text(encoding="utf-8")
            self.assertIn("Return one JSON object only", prompt)
            self.assertNotIn("cell_a", prompt)
            self.assertNotIn("reference_labels_or_proxy.json", prompt)


if __name__ == "__main__":
    unittest.main()
