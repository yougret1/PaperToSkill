import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_real_reuse_paper_tables.py"


class BuildRealReusePaperTablesTest(unittest.TestCase):
    def test_cli_builds_main_result_scaffold(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            status_root = tmp_path / "status_root"
            (status_root / "scripts").mkdir(parents=True)
            for script in (
                "prepare_real_reuse_aide_fixture.py",
                "score_real_reuse_aide.py",
                "run_real_reuse_aide.py",
            ):
                (status_root / "scripts" / script).write_text("# placeholder\n", encoding="utf-8")
            output_csv = tmp_path / "main_results_plan.csv"
            output_md = tmp_path / "main_results_plan.md"
            output_json = tmp_path / "main_results_plan.json"
            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--raw-rows",
                    str(tmp_path / "missing_raw_rows.jsonl"),
                    "--status-root",
                    str(status_root),
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
            self.assertEqual(8, len(rows))
            self.assertEqual("AIDE-T1", rows[0]["Task ID"])
            self.assertEqual("Pending", rows[0]["Summary Score"])
            self.assertEqual("Pending", rows[0]["PaperToSkill Score"])
            self.assertEqual("Awaiting dataset", rows[0]["Status"])
            rows_by_id = {row["Task ID"]: row for row in rows}
            self.assertEqual("Skill pending", rows_by_id["SWE-T1"]["Status"])
            self.assertTrue(output_md.exists())
            self.assertTrue(output_json.exists())
            output_md_text = output_md.read_text(encoding="utf-8")
            self.assertIn("selected by the row-selection file", output_md_text)
            self.assertIn("Pending scaffold/pre-run cells mark missing scored raw rows", output_md_text)
            self.assertNotIn("future unfilled cells", output_md_text)
            self.assertNotIn("planning placeholders", output_md_text)
            output_json_payload = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertIn("selected by the row-selection file", output_json_payload["evidence_boundary"])
            self.assertIn("Pending scaffold/pre-run cells mark missing scored raw rows", output_json_payload["evidence_boundary"])
            self.assertNotIn("future unfilled cells", output_json_payload["evidence_boundary"])
            self.assertNotIn("planning placeholders", output_json_payload["evidence_boundary"])

    def test_cli_marks_swe_runner_pending_after_skill_exists(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            status_root = tmp_path / "status_root"
            (status_root / "generated_skills" / "real_reuse" / "swe_agent").mkdir(parents=True)
            (status_root / "generated_skills" / "real_reuse" / "swe_agent" / "SKILL.md").write_text(
                "# SWE-agent\n",
                encoding="utf-8",
            )
            output_csv = tmp_path / "main_results_plan.csv"
            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--raw-rows",
                    str(tmp_path / "missing_raw_rows.jsonl"),
                    "--status-root",
                    str(status_root),
                    "--output-csv",
                    str(output_csv),
                    "--output-md",
                    str(tmp_path / "main_results_plan.md"),
                    "--output-json",
                    str(tmp_path / "main_results_plan.json"),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            with output_csv.open("r", encoding="utf-8", newline="") as handle:
                rows = {row["Task ID"]: row for row in csv.DictReader(handle)}
            self.assertEqual("Runner pending", rows["SWE-T1"]["Status"])

    def test_cli_marks_swe_fixture_pending_after_runner_exists_without_assets(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            status_root = tmp_path / "status_root"
            (status_root / "generated_skills" / "real_reuse" / "swe_agent").mkdir(parents=True)
            (status_root / "generated_skills" / "real_reuse" / "swe_agent" / "SKILL.md").write_text(
                "# SWE-agent\n",
                encoding="utf-8",
            )
            (status_root / "scripts").mkdir(parents=True)
            (status_root / "scripts" / "run_real_reuse_swe.py").write_text("# placeholder\n", encoding="utf-8")
            output_csv = tmp_path / "main_results_plan.csv"
            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--raw-rows",
                    str(tmp_path / "missing_raw_rows.jsonl"),
                    "--status-root",
                    str(status_root),
                    "--output-csv",
                    str(output_csv),
                    "--output-md",
                    str(tmp_path / "main_results_plan.md"),
                    "--output-json",
                    str(tmp_path / "main_results_plan.json"),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            with output_csv.open("r", encoding="utf-8", newline="") as handle:
                rows = {row["Task ID"]: row for row in csv.DictReader(handle)}
            self.assertEqual("Fixture pending", rows["SWE-T1"]["Status"])

    def test_cli_marks_snapatac2_runner_pending_after_skill_exists(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            status_root = tmp_path / "status_root"
            (status_root / "generated_skills" / "real_reuse" / "snapatac2").mkdir(parents=True)
            (status_root / "generated_skills" / "real_reuse" / "snapatac2" / "SKILL.md").write_text(
                "# SnapATAC2\n",
                encoding="utf-8",
            )
            output_csv = tmp_path / "main_results_plan.csv"
            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--raw-rows",
                    str(tmp_path / "missing_raw_rows.jsonl"),
                    "--status-root",
                    str(status_root),
                    "--output-csv",
                    str(output_csv),
                    "--output-md",
                    str(tmp_path / "main_results_plan.md"),
                    "--output-json",
                    str(tmp_path / "main_results_plan.json"),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            with output_csv.open("r", encoding="utf-8", newline="") as handle:
                rows = {row["Task ID"]: row for row in csv.DictReader(handle)}
            self.assertEqual("Runner pending", rows["SNAP-T1"]["Status"])

    def test_cli_marks_snapatac2_fixture_pending_after_runner_exists_without_assets(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            status_root = tmp_path / "status_root"
            (status_root / "generated_skills" / "real_reuse" / "snapatac2").mkdir(parents=True)
            (status_root / "generated_skills" / "real_reuse" / "snapatac2" / "SKILL.md").write_text(
                "# SnapATAC2\n",
                encoding="utf-8",
            )
            (status_root / "scripts").mkdir(parents=True)
            (status_root / "scripts" / "run_real_reuse_snapatac2.py").write_text("# placeholder\n", encoding="utf-8")
            output_csv = tmp_path / "main_results_plan.csv"
            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--raw-rows",
                    str(tmp_path / "missing_raw_rows.jsonl"),
                    "--status-root",
                    str(status_root),
                    "--output-csv",
                    str(output_csv),
                    "--output-md",
                    str(tmp_path / "main_results_plan.md"),
                    "--output-json",
                    str(tmp_path / "main_results_plan.json"),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            with output_csv.open("r", encoding="utf-8", newline="") as handle:
                rows = {row["Task ID"]: row for row in csv.DictReader(handle)}
            self.assertEqual("Fixture pending", rows["SNAP-T1"]["Status"])

    def test_cli_fills_scores_from_raw_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            raw_rows = tmp_path / "raw_rows.jsonl"
            raw_rows.write_text(
                "\n".join(
                    [
                        json_line(
                            task_id="REF-T1",
                            condition="summary",
                            task_score=1.0,
                        ),
                        json_line(
                            task_id="REF-T1",
                            condition="papertoskill",
                            task_score=0.5,
                        ),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            output_csv = tmp_path / "main_results_plan.csv"
            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--raw-rows",
                    str(raw_rows),
                    "--output-csv",
                    str(output_csv),
                    "--output-md",
                    str(tmp_path / "main_results_plan.md"),
                    "--output-json",
                    str(tmp_path / "main_results_plan.json"),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            with output_csv.open("r", encoding="utf-8", newline="") as handle:
                rows = {row["Task ID"]: row for row in csv.DictReader(handle)}
            self.assertEqual("1.000", rows["REF-T1"]["Summary Score"])
            self.assertEqual("0.500", rows["REF-T1"]["PaperToSkill Score"])
            self.assertEqual("Scored (GPT-family)", rows["REF-T1"]["Status"])

    def test_cli_row_selection_keeps_followup_out_of_main_table(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            raw_rows = tmp_path / "raw_rows.jsonl"
            raw_rows.write_text(
                "\n".join(
                    [
                        json_line(
                            task_id="SWE-T1",
                            condition="summary",
                            task_score=0.0,
                            run_id="phase97_summary",
                        ),
                        json_line(
                            task_id="SWE-T1",
                            condition="papertoskill",
                            task_score=0.0,
                            run_id="phase97_papertoskill",
                        ),
                        json_line(
                            task_id="SWE-T1",
                            condition="summary",
                            task_score=1.0,
                            run_id="phase107_followup",
                        ),
                        json_line(
                            task_id="SWE-T1",
                            condition="papertoskill",
                            task_score=1.0,
                            run_id="phase107_followup",
                        ),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            selection = tmp_path / "main_run_selection.json"
            selection.write_text(
                json.dumps(
                    {
                        "rows": [
                            {"task_id": "SWE-T1", "condition": "summary", "run_id": "phase97_summary"},
                            {
                                "task_id": "SWE-T1",
                                "condition": "papertoskill",
                                "run_id": "phase97_papertoskill",
                            },
                        ]
                    }
                ),
                encoding="utf-8",
            )
            output_csv = tmp_path / "main_results_plan.csv"

            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--raw-rows",
                    str(raw_rows),
                    "--row-selection",
                    str(selection),
                    "--output-csv",
                    str(output_csv),
                    "--output-md",
                    str(tmp_path / "main_results_plan.md"),
                    "--output-json",
                    str(tmp_path / "main_results_plan.json"),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            with output_csv.open("r", encoding="utf-8", newline="") as handle:
                rows = {row["Task ID"]: row for row in csv.DictReader(handle)}
            self.assertEqual("0.000", rows["SWE-T1"]["Summary Score"])
            self.assertEqual("0.000", rows["SWE-T1"]["PaperToSkill Score"])
            output_md_text = (tmp_path / "main_results_plan.md").read_text(encoding="utf-8")
            self.assertIn(f"Row selection file: {selection}", output_md_text)
            self.assertIn("Row selection entries: 2", output_md_text)
            self.assertIn("diagnostic follow-up rows remain auditable", output_md_text)
            output_json_payload = json.loads((tmp_path / "main_results_plan.json").read_text(encoding="utf-8"))
            self.assertEqual(str(selection), output_json_payload["row_selection"]["path"])
            self.assertEqual(2, output_json_payload["row_selection"]["entries"])
            self.assertIn(
                "diagnostic follow-up rows remain auditable",
                output_json_payload["row_selection"]["boundary"],
            )

    def test_current_main_results_reports_default_row_selection_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            output_md = tmp_path / "main_results_plan.md"
            output_json = tmp_path / "main_results_plan.json"

            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--output-csv",
                    str(tmp_path / "main_results_plan.csv"),
                    "--output-md",
                    str(output_md),
                    "--output-json",
                    str(output_json),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            output_md_text = output_md.read_text(encoding="utf-8")
            expected_selection = str(ROOT / "results" / "real_reuse" / "main_run_selection.json")
            self.assertIn(f"Row selection file: {expected_selection}", output_md_text)
            self.assertIn("Row selection entries: 16", output_md_text)
            payload = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertEqual(expected_selection, payload["row_selection"]["path"])
            self.assertEqual(16, payload["row_selection"]["entries"])
            self.assertIn("diagnostic follow-up rows remain auditable", payload["row_selection"]["boundary"])


def json_line(task_id: str, condition: str, task_score: float, run_id: str = "run") -> str:
    import json

    return json.dumps(
        {
            "run_id": run_id,
            "task_id": task_id,
            "condition": condition,
            "status": "scored",
            "task_score": task_score,
            "model_family": "GPT-family",
        }
    )


if __name__ == "__main__":
    unittest.main()
