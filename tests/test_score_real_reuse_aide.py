import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "score_real_reuse_aide.py"
sys.path.insert(0, str(ROOT / "scripts"))

from score_real_reuse_aide import score_candidate, score_submission  # noqa: E402


def write_labels(path: Path) -> None:
    path.write_text(
        "PassengerId,Transported\n0001_01,False\n0002_01,True\n0003_01,True\n",
        encoding="utf-8",
    )


class ScoreRealReuseAIDETest(unittest.TestCase):
    def test_scores_valid_submission_against_baseline(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            labels = tmp_path / "validation_labels.csv"
            submission = tmp_path / "submission.csv"
            write_labels(labels)
            submission.write_text(
                "PassengerId,Transported\n0001_01,False\n0002_01,True\n0003_01,True\n",
                encoding="utf-8",
            )

            result = score_submission(
                task_id="AIDE-T1",
                submission_path=submission,
                labels_path=labels,
                baseline_score=0.5,
            )

            self.assertEqual(1.0, result["task_score"])
            self.assertTrue(result["success"])
            self.assertTrue(result["improved_over_baseline"])

    def test_invalid_submission_is_scored_not_crashed(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            labels = tmp_path / "validation_labels.csv"
            submission = tmp_path / "submission.csv"
            write_labels(labels)
            submission.write_text("PassengerId,Transported\n0001_01,False\n", encoding="utf-8")

            result = score_submission(
                task_id="AIDE-T1",
                submission_path=submission,
                labels_path=labels,
                baseline_score=0.0,
            )

            self.assertEqual(0.0, result["task_score"])
            self.assertFalse(result["success"])
            self.assertIn("submission ids do not match", result["failure_reason"])

    def test_candidate_script_runs_in_workspace(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            workspace = tmp_path / "workspace"
            workspace.mkdir()
            labels = tmp_path / "validation_labels.csv"
            write_labels(labels)
            (workspace / "validation_features.csv").write_text(
                "PassengerId,Age\n0001_01,18\n0002_01,44\n0003_01,55\n",
                encoding="utf-8",
            )
            (workspace / "train.csv").write_text(
                "PassengerId,Age,Transported\n0004_01,22,False\n0005_01,36,True\n",
                encoding="utf-8",
            )
            candidate = tmp_path / "candidate.py"
            candidate.write_text(
                """import csv

with open('validation_features.csv', newline='', encoding='utf-8') as handle:
    rows = list(csv.DictReader(handle))

with open('submission.csv', 'w', newline='', encoding='utf-8') as handle:
    writer = csv.DictWriter(handle, fieldnames=['PassengerId', 'Transported'])
    writer.writeheader()
    for row in rows:
        writer.writerow({
            'PassengerId': row['PassengerId'],
            'Transported': 'True' if float(row['Age']) > 30 else 'False',
        })
""",
                encoding="utf-8",
            )

            result = score_candidate(
                task_id="AIDE-T2",
                candidate_script=candidate,
                workspace=workspace,
                labels_path=labels,
                baseline_score=0.5,
                timeout_seconds=5,
            )

            self.assertEqual(1.0, result["task_score"])
            self.assertTrue(result["success"])
            self.assertTrue((tmp_path / "submission.csv").exists())

    def test_cli_writes_metric_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            labels = tmp_path / "validation_labels.csv"
            submission = tmp_path / "submission.csv"
            output = tmp_path / "metric.json"
            write_labels(labels)
            submission.write_text(
                "PassengerId,Transported\n0001_01,False\n0002_01,True\n0003_01,True\n",
                encoding="utf-8",
            )

            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--task",
                    "AIDE-T1",
                    "--submission",
                    str(submission),
                    "--labels",
                    str(labels),
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
