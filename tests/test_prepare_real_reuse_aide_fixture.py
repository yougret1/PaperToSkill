import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "prepare_real_reuse_aide_fixture.py"


def write_train_csv(path: Path) -> None:
    path.write_text(
        "\n".join(
            [
                "PassengerId,HomePlanet,CryoSleep,Age,Transported",
                "0001_01,Earth,False,18,False",
                "0002_01,Mars,True,44,True",
                "0003_01,Europa,False,55,True",
                "0004_01,Earth,False,22,False",
                "0005_01,Mars,True,36,True",
                "0006_01,Earth,False,28,False",
                "0007_01,Europa,True,61,True",
                "0008_01,Earth,False,19,False",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


class PrepareRealReuseAIDEFixtureTest(unittest.TestCase):
    def test_prepare_aide_t1_writes_visible_assets_and_hidden_labels(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            train_csv = tmp_path / "train.csv"
            write_train_csv(train_csv)
            output_dir = tmp_path / "AIDE-T1"
            condition_dir = tmp_path / "conditions"

            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--task",
                    "AIDE-T1",
                    "--train-csv",
                    str(train_csv),
                    "--output-dir",
                    str(output_dir),
                    "--condition-dir",
                    str(condition_dir),
                    "--validation-fraction",
                    "0.25",
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            manifest = json.loads((output_dir / "asset_manifest.json").read_text(encoding="utf-8"))
            self.assertEqual("AIDE-T1", manifest["task_id"])
            self.assertEqual("prepared_assets_ready_for_dry_scoring", manifest["status"])
            files = {row["slot"]: row for row in manifest["files"]}
            self.assertEqual("scorer_only", files["validation_labels"]["visibility"])
            self.assertEqual([files["validation_labels"]["path"]], manifest["hidden_from_model"])
            self.assertTrue((output_dir / "starter_workspace" / "train.csv").exists())
            self.assertTrue((output_dir / "task_prompt.md").exists())
            self.assertTrue((condition_dir / "AIDE-T1_summary.md").exists())
            prompt = (output_dir / "task_prompt.md").read_text(encoding="utf-8")
            self.assertIn("submission.csv", prompt)
            self.assertNotIn("validation_labels.csv", prompt)

    def test_prepare_aide_t2_writes_weak_script_and_feedback(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            train_csv = tmp_path / "train.csv"
            write_train_csv(train_csv)
            output_dir = tmp_path / "AIDE-T2"

            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--task",
                    "AIDE-T2",
                    "--train-csv",
                    str(train_csv),
                    "--output-dir",
                    str(output_dir),
                    "--condition-dir",
                    str(tmp_path / "conditions"),
                    "--validation-fraction",
                    "0.25",
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            manifest = json.loads((output_dir / "asset_manifest.json").read_text(encoding="utf-8"))
            files = {row["slot"]: row for row in manifest["files"]}
            self.assertIn("weak_script", files)
            self.assertIn("error_or_score_feedback", files)
            self.assertTrue((output_dir / "starter_workspace" / "weak_script.py").exists())
            feedback = (output_dir / "error_or_score_feedback.md").read_text(encoding="utf-8")
            self.assertIn("objective validation score", feedback)


if __name__ == "__main__":
    unittest.main()
