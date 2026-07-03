import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PREPARE_SCRIPT = ROOT / "scripts" / "prepare_real_reuse_reflexion_fixture.py"
SCORE_SCRIPT = ROOT / "scripts" / "score_real_reuse_reflexion.py"


class ScoreRealReuseReflexionTest(unittest.TestCase):
    def test_ref_t1_scores_exact_answer(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            answer_key = tmp_path / "answer_key.json"
            prediction = tmp_path / "prediction.json"
            output = tmp_path / "metric.json"
            answer_key.write_text(json.dumps({"answer": "yes", "aliases": ["yes"], "f1_success_threshold": 1.0}), encoding="utf-8")
            prediction.write_text(json.dumps({"final_answer": "Yes."}), encoding="utf-8")

            subprocess.run(
                [
                    sys.executable,
                    str(SCORE_SCRIPT),
                    "--task",
                    "REF-T1",
                    "--prediction",
                    str(prediction),
                    "--answer-key",
                    str(answer_key),
                    "--output-json",
                    str(output),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            metric = json.loads(output.read_text(encoding="utf-8"))
            self.assertTrue(metric["success"])
            self.assertEqual(1.0, metric["task_score"])
            self.assertTrue(metric["exact_match"])

    def test_ref_t1_wrong_answer_is_scored_not_crashed(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            answer_key = tmp_path / "answer_key.json"
            prediction = tmp_path / "prediction.txt"
            output = tmp_path / "metric.json"
            answer_key.write_text(json.dumps({"answer": "yes", "aliases": ["yes"], "f1_success_threshold": 1.0}), encoding="utf-8")
            prediction.write_text("Final answer: no", encoding="utf-8")

            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCORE_SCRIPT),
                    "--task",
                    "REF-T1",
                    "--prediction",
                    str(prediction),
                    "--answer-key",
                    str(answer_key),
                    "--output-json",
                    str(output),
                ],
                capture_output=True,
                text=True,
            )

            self.assertEqual(0, completed.returncode)
            metric = json.loads(output.read_text(encoding="utf-8"))
            self.assertFalse(metric["success"])
            self.assertEqual(0.0, metric["task_score"])

    def test_ref_t2_executes_candidate_against_hidden_tests(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            fixture_dir = tmp_path / "REF-T2"
            subprocess.run(
                [
                    sys.executable,
                    str(PREPARE_SCRIPT),
                    "--task",
                    "REF-T2",
                    "--dataset",
                    "humaneval",
                    "--output-dir",
                    str(fixture_dir),
                    "--condition-dir",
                    str(tmp_path / "conditions"),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            candidate = tmp_path / "candidate.py"
            output = tmp_path / "metric.json"
            candidate.write_text(
                """from typing import List


def has_close_elements(numbers: List[float], threshold: float) -> bool:
    for idx, left in enumerate(numbers):
        for right in numbers[idx + 1:]:
            if abs(left - right) < threshold:
                return True
    return False
""",
                encoding="utf-8",
            )

            subprocess.run(
                [
                    sys.executable,
                    str(SCORE_SCRIPT),
                    "--task",
                    "REF-T2",
                    "--candidate",
                    str(candidate),
                    "--tests",
                    str(fixture_dir / "tests.json"),
                    "--output-json",
                    str(output),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            metric = json.loads(output.read_text(encoding="utf-8"))
            self.assertTrue(metric["success"])
            self.assertEqual(1.0, metric["task_score"])

    def test_ref_t2_failed_candidate_is_scored_not_crashed(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            fixture_dir = tmp_path / "REF-T2"
            subprocess.run(
                [
                    sys.executable,
                    str(PREPARE_SCRIPT),
                    "--task",
                    "REF-T2",
                    "--dataset",
                    "humaneval",
                    "--output-dir",
                    str(fixture_dir),
                    "--condition-dir",
                    str(tmp_path / "conditions"),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            candidate = tmp_path / "candidate.py"
            output = tmp_path / "metric.json"
            candidate.write_text((fixture_dir / "failed_first_attempt.py").read_text(encoding="utf-8"), encoding="utf-8")

            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCORE_SCRIPT),
                    "--task",
                    "REF-T2",
                    "--candidate",
                    str(candidate),
                    "--tests",
                    str(fixture_dir / "tests.json"),
                    "--output-json",
                    str(output),
                ],
                capture_output=True,
                text=True,
            )

            self.assertEqual(0, completed.returncode)
            metric = json.loads(output.read_text(encoding="utf-8"))
            self.assertFalse(metric["success"])
            self.assertEqual(0.0, metric["task_score"])


if __name__ == "__main__":
    unittest.main()
