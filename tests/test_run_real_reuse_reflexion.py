import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_real_reuse_reflexion.py"
sys.path.insert(0, str(ROOT / "scripts"))

from run_real_reuse_reflexion import build_prompt  # noqa: E402


REF_T2_SUCCESS = """Reflection: The first attempt always returns False, so it misses pairs whose distance is below the threshold.

```python
from typing import List


def has_close_elements(numbers: List[float], threshold: float) -> bool:
    for idx, left in enumerate(numbers):
        for right in numbers[idx + 1:]:
            if abs(left - right) < threshold:
                return True
    return False
```
"""


class RunRealReuseReflexionTest(unittest.TestCase):
    def test_fixture_responses_produce_scored_raw_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            fixture_dir = tmp_path / "fixture_responses"
            fixture_dir.mkdir()
            for condition in ("summary", "papertoskill"):
                (fixture_dir / f"REF-T1_{condition}.json").write_text(
                    json.dumps(
                        {
                            "first_attempt": "Scott Derrickson and Ed Wood are both American.",
                            "reflection": "The context states each person is American, so the nationality comparison should be yes.",
                            "final_answer": "yes",
                        }
                    ),
                    encoding="utf-8",
                )
                (fixture_dir / f"REF-T2_{condition}.md").write_text(REF_T2_SUCCESS, encoding="utf-8")

            raw_rows = tmp_path / "raw_rows.jsonl"
            output_json = tmp_path / "run_report.json"
            output_md = tmp_path / "run_report.md"

            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--root",
                    str(ROOT),
                    "--task",
                    "REF-T1",
                    "--task",
                    "REF-T2",
                    "--condition",
                    "summary",
                    "--condition",
                    "papertoskill",
                    "--fixture-response-dir",
                    str(fixture_dir),
                    "--run-id",
                    "unit_fixture_run",
                    "--output-dir",
                    str(tmp_path / "runs"),
                    "--raw-rows-output",
                    str(raw_rows),
                    "--output-json",
                    str(output_json),
                    "--output-md",
                    str(output_md),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            self.assertIn("unit_fixture_run", completed.stdout)
            report = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertEqual("complete", report["overall_status"])
            self.assertEqual({"scored": 4}, report["status_counts"])
            rows = [json.loads(line) for line in raw_rows.read_text(encoding="utf-8").splitlines()]
            self.assertEqual(4, len(rows))
            self.assertTrue(all(row["success"] for row in rows))
            self.assertEqual({"summary", "papertoskill"}, {row["condition"] for row in rows})
            self.assertTrue((tmp_path / "runs" / "REF-T2" / "papertoskill" / "unit_fixture_run" / "metric.json").exists())
            self.assertTrue(output_md.exists())

    def test_missing_credentials_records_pending_without_raw_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            raw_rows = tmp_path / "raw_rows.jsonl"
            output_json = tmp_path / "run_report.json"

            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--root",
                    str(ROOT),
                    "--task",
                    "REF-T1",
                    "--condition",
                    "summary",
                    "--base-url-env",
                    "PAPERTOSKILL_UNITTEST_MISSING_BASE_URL",
                    "--api-key-env",
                    "PAPERTOSKILL_UNITTEST_MISSING_API_KEY",
                    "--run-id",
                    "unit_missing_credentials",
                    "--output-dir",
                    str(tmp_path / "runs"),
                    "--raw-rows-output",
                    str(raw_rows),
                    "--output-json",
                    str(output_json),
                    "--output-md",
                    str(tmp_path / "run_report.md"),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            report = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertEqual("pending", report["overall_status"])
            self.assertEqual({"skipped": 1}, report["status_counts"])
            self.assertFalse(raw_rows.exists())
            self.assertIn("missing_base_url_or_api_key_env", report["results"][0]["failure_reason"])

    def test_prompt_uses_condition_context_without_scorer_only_paths(self):
        prompt = build_prompt(ROOT, "REF-T1", "summary")

        self.assertIn("Real-Reuse Condition: summary", prompt)
        self.assertIn("Generic Summary: Reflexion", prompt)
        self.assertIn("REF-T1 Locked Task Prompt", prompt)
        self.assertNotIn("answer_key.json", prompt)
        self.assertNotIn("tests.json", prompt)
        self.assertNotIn("canonical_solution.py", prompt)


if __name__ == "__main__":
    unittest.main()
