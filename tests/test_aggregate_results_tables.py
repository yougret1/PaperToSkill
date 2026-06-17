import csv
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "aggregate_results_tables.py"
RESULTS_DIR = ROOT / "results" / "evaluations"


def read_csv(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


class AggregateResultsTablesTest(unittest.TestCase):
    def test_generates_expected_paper_ready_tables(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp) / "tables"
            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--results-dir",
                    str(RESULTS_DIR),
                    "--output-dir",
                    str(output_dir),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            expected = [
                "main_results.md",
                "main_results.csv",
                "transfer_ablation.md",
                "transfer_ablation.csv",
                "compactness_source_grounding.md",
                "compactness_source_grounding.csv",
                "auto_note_comparison.md",
                "auto_note_comparison.csv",
                "paper_ready_summary.md",
            ]
            for name in expected:
                self.assertTrue((output_dir / name).exists(), name)

            main_rows = read_csv(output_dir / "main_results.csv")
            self.assertEqual(["AI Scientist-v2", "Reflexion", "AIDE", "Toolformer"], [row["Paper"] for row in main_rows])
            ai_row = main_rows[0]
            self.assertEqual("20/20", ai_row["Skill rubric"])
            self.assertEqual("7.867/9", ai_row["Skill coverage"])
            self.assertEqual("6.134", ai_row["Skill vs generic delta"])
            aide_row = main_rows[2]
            self.assertEqual("20/20", aide_row["Skill rubric"])
            self.assertEqual("9.1/10", aide_row["Skill coverage"])
            toolformer_row = main_rows[3]
            self.assertEqual("20/20", toolformer_row["Skill rubric"])
            self.assertEqual("8.9/10", toolformer_row["Skill coverage"])
            self.assertEqual("10/10", toolformer_row["Transfer readiness"])

            transfer_rows = read_csv(output_dir / "transfer_ablation.csv")
            self.assertEqual(12, len(transfer_rows))
            reflexion = {
                row["Variant"]: row
                for row in transfer_rows
                if row["Paper"] == "Reflexion"
            }
            self.assertEqual("10/10", reflexion["Full skill"]["Average readiness"])
            self.assertEqual("7.6/10", reflexion["No transfer notes"]["Average readiness"])
            toolformer = {
                row["Variant"]: row
                for row in transfer_rows
                if row["Paper"] == "Toolformer"
            }
            self.assertEqual("10/10", toolformer["Full skill"]["Average readiness"])
            self.assertEqual("7.6/10", toolformer["No transfer notes"]["Average readiness"])

            grounding_rows = read_csv(output_dir / "compactness_source_grounding.csv")
            grounding = {row["Paper"]: row for row in grounding_rows}
            self.assertEqual("0.938", grounding["AI Scientist-v2"]["Source support rate"])
            self.assertEqual("n/a", grounding["Reflexion"]["Unsupported instruction rate"])
            self.assertEqual("927", grounding["AIDE"]["Skill words"])
            self.assertEqual("1", grounding["Toolformer"]["Source support rate"])

            auto_rows = read_csv(output_dir / "auto_note_comparison.csv")
            self.assertEqual(
                ["Curated source-anchored note", "Automatic extracted-text note scaffold"],
                [row["Input"] for row in auto_rows],
            )
            self.assertEqual("Toolformer", auto_rows[1]["Paper"])
            self.assertEqual("20/20", auto_rows[1]["Skill rubric"])
            self.assertEqual("1", auto_rows[1]["Source support rate"])


if __name__ == "__main__":
    unittest.main()
