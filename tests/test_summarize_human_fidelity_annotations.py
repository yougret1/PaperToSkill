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
ANNOTATION_METADATA_COLUMNS = [
    "score_1_to_5",
    "evidence_locator",
    "evidence_note",
    "confidence_0_to_1",
    "reviewer_id",
    "review_date",
    "needs_discussion",
]


def blank_template_rows():
    with TEMPLATE.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
        fieldnames = list(rows[0].keys())
    for row in rows:
        for column in ANNOTATION_METADATA_COLUMNS:
            row[column] = ""
    return rows, fieldnames


class SummarizeHumanFidelityAnnotationsTest(unittest.TestCase):
    def test_pending_template_summarizes_without_scores(self):
        with tempfile.TemporaryDirectory() as tmp:
            annotations = Path(tmp) / "annotations.csv"
            rows, fieldnames = blank_template_rows()
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
            rows, fieldnames = blank_template_rows()
            rows[0]["score_1_to_5"] = "5"
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
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            summary = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertEqual(1, summary["scored_rows"])
            self.assertEqual(6, len(summary["errors"]))
            self.assertIn("requires needs_discussion true/false", "\n".join(summary["errors"]))

    def test_complete_scored_rows_compute_confidence_and_discussion(self):
        with tempfile.TemporaryDirectory() as tmp:
            annotations = Path(tmp) / "annotations.csv"
            rows, fieldnames = blank_template_rows()
            for row in rows:
                row["score_1_to_5"] = "5"
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
            self.assertEqual(24, summary["required_cells"])
            self.assertEqual(24, summary["scored_cells"])
            self.assertEqual(0, summary["pending_rows"])
            self.assertEqual(0.8, summary["average_confidence"])
            self.assertEqual(1, summary["discussion_rows"])
            self.assertEqual([], summary["errors"])

    def test_multiple_reviewers_can_append_duplicate_cells(self):
        with tempfile.TemporaryDirectory() as tmp:
            annotations = Path(tmp) / "annotations.csv"
            rows, fieldnames = blank_template_rows()
            for row in rows:
                row["score_1_to_5"] = "5"
                row["evidence_locator"] = "source note line 1"
                row["evidence_note"] = "faithful to source"
                row["confidence_0_to_1"] = "0.8"
                row["reviewer_id"] = "R1"
                row["review_date"] = "2026-07-04"
                row["needs_discussion"] = "false"
            duplicate_reviewer_rows = []
            for row in rows:
                duplicate = dict(row)
                duplicate["score_1_to_5"] = "4"
                duplicate["evidence_note"] = "mostly faithful"
                duplicate["confidence_0_to_1"] = "0.7"
                duplicate["reviewer_id"] = "R2"
                duplicate_reviewer_rows.append(duplicate)
            with annotations.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows + duplicate_reviewer_rows)

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
            self.assertEqual(48, summary["total_rows"])
            self.assertEqual(48, summary["scored_rows"])
            self.assertEqual(24, summary["required_cells"])
            self.assertEqual(24, summary["scored_cells"])
            self.assertEqual(0, summary["pending_rows"])
            self.assertEqual(0.75, summary["average_confidence"])
            self.assertEqual([], summary["errors"])

    def test_duplicate_reviewer_for_same_cell_is_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            annotations = Path(tmp) / "annotations.csv"
            rows, fieldnames = blank_template_rows()
            first = rows[0]
            for row in [first]:
                row["score_1_to_5"] = "5"
                row["evidence_locator"] = "source note line 1"
                row["evidence_note"] = "faithful to source"
                row["confidence_0_to_1"] = "0.8"
                row["reviewer_id"] = "R1"
                row["review_date"] = "2026-07-04"
                row["needs_discussion"] = "false"
            duplicate = dict(first)
            rows.append(duplicate)
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
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            summary = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertIn("duplicate scored annotation", "\n".join(summary["errors"]))


if __name__ == "__main__":
    unittest.main()
