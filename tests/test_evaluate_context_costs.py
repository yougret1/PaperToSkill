import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "evaluate_context_costs.py"


def read_csv(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


class EvaluateContextCostsTest(unittest.TestCase):
    def test_generates_cost_proxy_tables(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp) / "tables"
            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--root",
                    str(ROOT),
                    "--output-dir",
                    str(output_dir),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            expected = [
                "context_cost_proxy.csv",
                "coverage_cost_efficiency.csv",
                "context_cost_proxy.md",
                "context_cost_proxy.json",
            ]
            for name in expected:
                self.assertTrue((output_dir / name).exists(), name)

            size_rows = read_csv(output_dir / "context_cost_proxy.csv")
            self.assertEqual(20, len(size_rows))
            by_key = {(row["Paper"], row["Variant"]): row for row in size_rows}
            ai_full = by_key[("AI Scientist-v2", "Full extracted paper")]
            ai_skill = by_key[("AI Scientist-v2", "Generated skill")]
            self.assertGreater(
                int(ai_full["Estimated input tokens"]),
                int(ai_skill["Estimated input tokens"]),
            )
            self.assertLess(float(ai_skill["Tokens vs full paper"]), 0.05)

            efficiency_rows = read_csv(output_dir / "coverage_cost_efficiency.csv")
            self.assertEqual(12, len(efficiency_rows))
            efficiency = {(row["Paper"], row["Variant"]): row for row in efficiency_rows}
            aide_skill = efficiency[("AIDE", "Generated skill")]
            aide_summary = efficiency[("AIDE", "Generic summary")]
            self.assertEqual("9.1/10", aide_skill["Coverage score"])
            self.assertGreater(
                float(aide_skill["Normalized coverage"]),
                float(aide_summary["Normalized coverage"]),
            )
            toolformer_skill = efficiency[("Toolformer", "Generated skill")]
            self.assertEqual("8.9/10", toolformer_skill["Coverage score"])

            tokenizer_csv = output_dir / "context_cost_proxy_tokenizer.csv"
            if tokenizer_csv.exists():
                tokenizer_rows = read_csv(tokenizer_csv)
                self.assertEqual(20, len(tokenizer_rows))
                tokenizer_by_key = {(row["Paper"], row["Variant"]): row for row in tokenizer_rows}
                tokenizer_ai_full = tokenizer_by_key[("AI Scientist-v2", "Full extracted paper")]
                tokenizer_ai_skill = tokenizer_by_key[("AI Scientist-v2", "Generated skill")]
                self.assertGreater(
                    int(tokenizer_ai_full["Estimated input tokens"]),
                    int(tokenizer_ai_skill["Estimated input tokens"]),
                )
                tokenizer_report = json.loads((output_dir / "context_cost_proxy_tokenizer.json").read_text(encoding="utf-8"))
                self.assertEqual("tokenizer", tokenizer_report["token_count_method"])
                self.assertEqual("o200k_base", tokenizer_report["tokenizer_name"])
            else:
                self.assertTrue((output_dir / "context_cost_proxy_tokenizer_unavailable.txt").exists())

    def test_can_skip_tokenizer_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp) / "tables"
            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--root",
                    str(ROOT),
                    "--output-dir",
                    str(output_dir),
                    "--tokenizer",
                    "",
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            self.assertTrue((output_dir / "context_cost_proxy.csv").exists())
            self.assertFalse((output_dir / "context_cost_proxy_tokenizer.csv").exists())


if __name__ == "__main__":
    unittest.main()
