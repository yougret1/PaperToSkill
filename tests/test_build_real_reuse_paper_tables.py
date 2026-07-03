import csv
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


def json_line(task_id: str, condition: str, task_score: float) -> str:
    import json

    return json.dumps(
        {
            "task_id": task_id,
            "condition": condition,
            "status": "scored",
            "task_score": task_score,
            "model_family": "GPT-family",
        }
    )


if __name__ == "__main__":
    unittest.main()
