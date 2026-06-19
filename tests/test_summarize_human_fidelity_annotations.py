import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "summarize_human_fidelity_annotations.py"
TEMPLATE = ROOT / "results" / "human_fidelity_packets" / "annotation_template.csv"


class SummarizeHumanFidelityAnnotationsTest(unittest.TestCase):
    def test_pending_template_summarizes_without_scores(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_json = Path(tmp) / "summary.json"
            output_md = Path(tmp) / "summary.md"
            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--annotations",
                    str(TEMPLATE),
                    "--output-json",
                    str(output_json),
                    "--output-md",
                    str(output_md),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            summary = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertEqual("pending", summary["annotation_status"])
            self.assertEqual(24, summary["total_rows"])
            self.assertEqual(0, summary["scored_rows"])
            self.assertEqual(24, summary["pending_rows"])
            self.assertIsNone(summary["average_confidence"])
            self.assertEqual(0, summary["discussion_rows"])
            self.assertEqual([], summary["errors"])
            self.assertIn("Annotation status: pending", output_md.read_text(encoding="utf-8"))

    def test_scored_rows_require_required_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            annotations = Path(tmp) / "annotations.csv"
            rows = []
            with TEMPLATE.open(encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle))
                fieldnames = handle.readline()
            rows[0]["score_0_to_3"] = "3"
            with annotations.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=[
                    "paper_id",
                    "paper",
                    "packet_path",
                    "criterion_id",
                    "criterion_label",
                    "score_0_to_3",
                    "evidence_locator",
                    "evidence_note",
                    "confidence_0_to_1",
                    "reviewer_id",
                    "review_date",
                    "needs_discussion",
                ])
                writer.writeheader()
                writer.writerows(rows)

            output_json = Path(tmp) / "summary.json"
            output_md = Path(tmp) / "summary.md"
            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--annotations",
                    str(annotations),
                    "--output-json",
                    str(output_json),
                    "--output-md",
                    str(output_md),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            summary = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertEqual(1, summary["scored_rows"])
            self.assertEqual(5, len(summary["errors"]))

    def test_complete_scored_rows_compute_confidence_and_discussion(self):
        with tempfile.TemporaryDirectory() as tmp:
            annotations = Path(tmp) / "annotations.csv"
            with TEMPLATE.open(encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle))
                fieldnames = list(rows[0].keys())
            for row in rows:
                row["score_0_to_3"] = "3"
                row["evidence_locator"] = "source note line 1"
                row["evidence_note"] = "faithful to source"
                row["confidence_0_to_1"] = "0.8"
                row["reviewer_id"] = "reviewer-a"
                row["review_date"] = "2026-06-19"
                row["needs_discussion"] = "false"
            rows[0]["needs_discussion"] = "true"
            with annotations.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)

            output_json = Path(tmp) / "summary.json"
            output_md = Path(tmp) / "summary.md"
            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--annotations",
                    str(annotations),
                    "--output-json",
                    str(output_json),
                    "--output-md",
                    str(output_md),
                    "--strict",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            summary = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertEqual("complete", summary["annotation_status"])
            self.assertEqual(24, summary["scored_rows"])
            self.assertEqual(0, summary["pending_rows"])
            self.assertEqual(0.8, summary["average_confidence"])
            self.assertEqual(1, summary["discussion_rows"])
            self.assertEqual([], summary["errors"])


if __name__ == "__main__":
    unittest.main()
