import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_real_reuse_full_excerpt_sanity.py"


class BuildRealReuseFullExcerptSanityTest(unittest.TestCase):
    def test_cli_builds_current_sanity_table(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            output_csv = tmp_path / "full_excerpt_sanity.csv"
            output_md = tmp_path / "full_excerpt_sanity.md"
            output_json = tmp_path / "full_excerpt_sanity.json"
            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--output-csv",
                    str(output_csv),
                    "--output-md",
                    str(output_md),
                    "--output-json",
                    str(output_json),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            with output_csv.open("r", encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(["AIDE-T1", "SWE-T1", "SNAP-T1"], [row["Task ID"] for row in rows])
            rows_by_id = {row["Task ID"]: row for row in rows}
            self.assertEqual("0.000", rows_by_id["AIDE-T1"]["Summary Score"])
            self.assertEqual("0.000", rows_by_id["AIDE-T1"]["PaperToSkill Score"])
            self.assertEqual("0.000", rows_by_id["AIDE-T1"]["Full Excerpt Score"])
            self.assertEqual("0.000", rows_by_id["SWE-T1"]["Full Excerpt Score"])
            self.assertEqual("0.250", rows_by_id["SNAP-T1"]["Full Excerpt Score"])
            self.assertEqual("Scored (GPT-family)", rows_by_id["AIDE-T1"]["Status"])
            self.assertGreater(
                int(rows_by_id["SWE-T1"]["Full Excerpt Tokens"]),
                int(rows_by_id["SWE-T1"]["PaperToSkill Tokens"]),
            )
            self.assertIn("Token counts are local whitespace context proxies", output_md.read_text(encoding="utf-8"))
            payload = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertEqual(3, len(payload["rows"]))
            self.assertIn("Missing Full Excerpt score cells", payload["evidence_boundary"])

    def test_full_excerpt_score_is_filled_from_raw_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            raw_rows = tmp_path / "raw_rows.jsonl"
            raw_rows.write_text(
                json.dumps(
                    {
                        "task_id": "AIDE-T1",
                        "condition": "full_excerpt",
                        "status": "scored",
                        "task_score": 0.25,
                        "model_family": "GPT-family",
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            output_csv = tmp_path / "full_excerpt_sanity.csv"
            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--raw-rows",
                    str(raw_rows),
                    "--output-csv",
                    str(output_csv),
                    "--output-md",
                    str(tmp_path / "full_excerpt_sanity.md"),
                    "--output-json",
                    str(tmp_path / "full_excerpt_sanity.json"),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            with output_csv.open("r", encoding="utf-8", newline="") as handle:
                rows = {row["Task ID"]: row for row in csv.DictReader(handle)}
            self.assertEqual("0.250", rows["AIDE-T1"]["Full Excerpt Score"])
            self.assertEqual("Scored (GPT-family)", rows["AIDE-T1"]["Status"])


if __name__ == "__main__":
    unittest.main()
