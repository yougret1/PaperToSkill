import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "evaluate_model_response_costs.py"


def read_csv(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


class EvaluateModelResponseCostsTest(unittest.TestCase):
    def test_generates_output_token_proxy_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            response_dir = tmp_path / "responses"
            response_dir.mkdir()
            response_path = response_dir / "model__case.md"
            response_path.write_text("A short saved response with validation and logging.", encoding="utf-8")
            missing_path = response_dir / "missing.md"
            index = tmp_path / "index.json"
            index.write_text(
                json.dumps(
                    {
                        "task": "test",
                        "prompts": [
                            {
                                "model_id": "model",
                                "model_alias": "configured-model",
                                "case_id": "case",
                                "expected_response_path": str(response_path),
                            },
                            {
                                "model_id": "deepseek_followup_slot",
                                "model_alias": "deepseek-to-be-filled",
                                "case_id": "case",
                                "expected_response_path": str(missing_path),
                            },
                        ],
                    }
                ),
                encoding="utf-8",
            )
            run_report = tmp_path / "run_report.json"
            run_report.write_text(
                json.dumps(
                    {
                        "results": [
                            {
                                "model_id": "model",
                                "case_id": "case",
                                "status": "success",
                                "alias_used": "actual-model",
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            output_json = tmp_path / "model_response_cost_proxy.json"
            output_md = tmp_path / "model_response_cost_proxy.md"
            output_csv = tmp_path / "model_response_cost_proxy.csv"

            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--root",
                    str(ROOT),
                    "--index",
                    str(index),
                    "--run-report",
                    str(run_report),
                    "--output-json",
                    str(output_json),
                    "--output-md",
                    str(output_md),
                    "--output-csv",
                    str(output_csv),
                    "--tokenizer",
                    "",
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            report = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertEqual(2, report["summary"]["total_rows"])
            self.assertEqual(1, report["summary"]["measured_rows"])
            self.assertEqual(1, report["summary"]["pending_rows"])
            self.assertGreater(report["summary"]["total_character_proxy_output_tokens"], 0)

            rows = read_csv(output_csv)
            by_model = {row["Model ID"]: row for row in rows}
            self.assertEqual("actual-model", by_model["model"]["Actual alias"])
            self.assertEqual("measured", by_model["model"]["Status"])
            self.assertEqual("pending", by_model["deepseek_followup_slot"]["Status"])
            self.assertIn("not provider bills", output_md.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
