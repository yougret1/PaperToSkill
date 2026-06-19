import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "summarize_provider_billing_evidence.py"
CONFIG = ROOT / "benchmarks" / "provider_billing_evidence_v0.json"


class SummarizeProviderBillingEvidenceTest(unittest.TestCase):
    def run_script(self, template, output_json, output_md, *extra_args, check=True):
        return subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--config",
                str(CONFIG),
                "--template",
                str(template),
                "--output-json",
                str(output_json),
                "--output-md",
                str(output_md),
                *extra_args,
            ],
            check=check,
            capture_output=True,
            text=True,
        )

    def test_blank_template_is_pending_without_errors(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            template = tmp_path / "billing_template.csv"
            output_json = tmp_path / "summary.json"
            output_md = tmp_path / "summary.md"

            self.run_script(template, output_json, output_md, "--init-template", "--strict")

            summary = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertEqual("pending", summary["billing_status"])
            self.assertEqual(6, summary["total_rows"])
            self.assertEqual(0, summary["measured_rows"])
            self.assertEqual(6, summary["pending_rows"])
            self.assertEqual([], summary["errors"])
            self.assertIn("Billing status: pending", output_md.read_text(encoding="utf-8"))

    def test_measured_row_requires_billing_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            template = tmp_path / "billing_template.csv"
            output_json = tmp_path / "summary.json"
            output_md = tmp_path / "summary.md"
            self.run_script(template, output_json, output_md, "--init-template")

            with template.open(encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle))
                fieldnames = list(rows[0].keys())
            rows[0]["provider"] = "coderxiaoc"
            with template.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)

            self.run_script(template, output_json, output_md)
            summary = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertEqual(1, summary["measured_rows"])
            self.assertGreaterEqual(len(summary["errors"]), 8)

    def test_complete_rows_compute_success_per_dollar(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            template = tmp_path / "billing_template.csv"
            output_json = tmp_path / "summary.json"
            output_md = tmp_path / "summary.md"
            self.run_script(template, output_json, output_md, "--init-template")

            with template.open(encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle))
                fieldnames = list(rows[0].keys())
            for row in rows:
                row["provider"] = "coderxiaoc"
                row["model_alias"] = "model-x"
                row["billing_period"] = "2026-06"
                row["input_tokens"] = "100"
                row["output_tokens"] = "50"
                row["billed_usd"] = "2"
                row["currency"] = "USD"
                row["invoice_or_usage_evidence"] = "local invoice export row"
                row["success_metric"] = "scored_rows"
                row["success_value"] = "1"
                row["reviewer_id"] = "reviewer-a"
            with template.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)

            self.run_script(template, output_json, output_md, "--strict")
            summary = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertEqual("complete", summary["billing_status"])
            self.assertEqual(6, summary["measured_rows"])
            self.assertEqual(0, summary["pending_rows"])
            self.assertEqual(12, summary["total_billed_usd"])
            self.assertEqual(0.5, summary["success_per_dollar"])
            self.assertEqual([], summary["errors"])


if __name__ == "__main__":
    unittest.main()
