import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_paper_tables.py"
TABLES_TEX = ROOT / "paper" / "aaai" / "papertoskill_tables.tex"
sys.path.insert(0, str(ROOT / "scripts"))

from check_paper_tables import build_report  # noqa: E402


class CheckPaperTablesTest(unittest.TestCase):
    def test_current_paper_tables_are_ready(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_json = Path(tmp) / "paper_table_report.json"
            output_md = Path(tmp) / "paper_table_report.md"
            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
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

            report = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertEqual("ready", report["overall_status"])
            self.assertEqual(302, report["status_counts"]["ready"])
            self.assertEqual(0, report["status_counts"]["fail"])
            ready_ids = {check["id"] for check in report["checks"] if check["status"] == "ready"}
            self.assertIn("paper_table_real_reuse_aide_t1_papertoskill_score", ready_ids)
            self.assertIn("paper_table_real_reuse_failure_aide_t1_boundary_mode", ready_ids)
            self.assertIn("paper_table_real_reuse_failure_swe_t2_papertoskill_outcome", ready_ids)
            self.assertIn("paper_table_swe_t1_source_context_followup_summary_followup_patch_applied", ready_ids)
            self.assertIn("paper_table_swe_t1_issue_aligned_followup_summary_issue_aligned_score", ready_ids)
            self.assertIn("paper_table_swe_t1_issue_aligned_followup_papertoskill_interpretation", ready_ids)
            self.assertIn("paper_table_snap_exec_snap_t1_summary_task_score", ready_ids)
            self.assertIn("paper_table_snap_exec_snap_t2_papertoskill_peak_memory_mb", ready_ids)
            self.assertIn("paper_table_full_excerpt_sanity_swe_t1_full_excerpt_tokens", ready_ids)
            self.assertIn("paper_table_full_excerpt_sanity_aide_t1_full_excerpt_score", ready_ids)
            self.assertIn("paper_table_main_aide_skill_coverage", ready_ids)
            self.assertIn("paper_table_cost_toolformer_reduction", ready_ids)
            self.assertIn("paper_table_auto_aide_automatic_extracted_text_note_scaffold_transfer", ready_ids)
            self.assertTrue(output_md.exists())

    def test_modified_table_value_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_tables = Path(tmp) / "papertoskill_tables.tex"
            shutil.copyfile(TABLES_TEX, tmp_tables)
            text = tmp_tables.read_text(encoding="utf-8")
            tmp_tables.write_text(text.replace("AIDE & 20/20 & 9.1/10", "AIDE & 20/20 & 8.1/10", 1), encoding="utf-8")

            report = build_report(ROOT, tmp_tables)

            statuses = {check["id"]: check["status"] for check in report["checks"]}
            self.assertEqual("fail", report["overall_status"])
            self.assertEqual("fail", statuses["paper_table_main_aide_skill_coverage"])


if __name__ == "__main__":
    unittest.main()
