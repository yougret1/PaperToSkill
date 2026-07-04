import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PREP_SCRIPT = ROOT / "scripts" / "prepare_real_reuse_aide_fixture.py"
RUN_SCRIPT = ROOT / "scripts" / "run_real_reuse_aide.py"
sys.path.insert(0, str(ROOT / "scripts"))

from run_real_reuse_aide import build_prompt  # noqa: E402


CANDIDATE_RESPONSE = """```python
import csv

with open("validation_features.csv", newline="", encoding="utf-8") as handle:
    rows = list(csv.DictReader(handle))

with open("submission.csv", "w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=["PassengerId", "Transported"])
    writer.writeheader()
    for row in rows:
        writer.writerow({
            "PassengerId": row["PassengerId"],
            "Transported": "True" if float(row["Age"]) > 30 else "False",
        })
```
"""


def write_train_csv(path: Path) -> None:
    path.write_text(
        "\n".join(
            [
                "PassengerId,HomePlanet,CryoSleep,Age,Transported",
                "0001_01,Earth,False,18,False",
                "0002_01,Mars,True,44,True",
                "0003_01,Europa,False,55,True",
                "0004_01,Earth,False,22,False",
                "0005_01,Mars,True,36,True",
                "0006_01,Earth,False,28,False",
                "0007_01,Europa,True,61,True",
                "0008_01,Earth,False,19,False",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def prepare_temp_root(tmp_path: Path) -> Path:
    root = tmp_path / "root"
    (root / "benchmarks" / "real_reuse" / "tasks").mkdir(parents=True)
    (root / "generated_skills" / "aide").mkdir(parents=True)
    (root / "baselines" / "real_reuse").mkdir(parents=True)
    (root / "papers" / "extracted").mkdir(parents=True)
    shutil.copy2(ROOT / "benchmarks" / "real_reuse" / "tasks" / "AIDE-T1.json", root / "benchmarks" / "real_reuse" / "tasks" / "AIDE-T1.json")
    (root / "generated_skills" / "aide" / "SKILL.md").write_text("# AIDE Skill\n\nUse measured validation feedback.\n", encoding="utf-8")
    (root / "papers" / "extracted" / "aide.txt").write_text("Full AIDE paper excerpt with measured code search and validation feedback.\n", encoding="utf-8")
    train_csv = tmp_path / "train.csv"
    write_train_csv(train_csv)
    subprocess.run(
        [
            sys.executable,
            str(PREP_SCRIPT),
            "--root",
            str(root),
            "--task",
            "AIDE-T1",
            "--train-csv",
            str(train_csv),
            "--output-dir",
            str(root / "benchmarks" / "real_reuse" / "assets" / "AIDE-T1"),
            "--condition-dir",
            str(root / "baselines" / "real_reuse"),
            "--validation-fraction",
            "0.25",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return root


class RunRealReuseAIDETest(unittest.TestCase):
    def test_fixture_response_produces_scored_raw_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            root = prepare_temp_root(tmp_path)
            fixture_dir = tmp_path / "fixture_responses"
            fixture_dir.mkdir()
            for condition in ("summary", "papertoskill"):
                (fixture_dir / f"AIDE-T1_{condition}.md").write_text(CANDIDATE_RESPONSE, encoding="utf-8")
            raw_rows = tmp_path / "raw_rows.jsonl"
            output_json = tmp_path / "aide_report.json"

            completed = subprocess.run(
                [
                    sys.executable,
                    str(RUN_SCRIPT),
                    "--root",
                    str(root),
                    "--task",
                    "AIDE-T1",
                    "--condition",
                    "summary",
                    "--condition",
                    "papertoskill",
                    "--fixture-response-dir",
                    str(fixture_dir),
                    "--run-id",
                    "unit_aide_fixture_run",
                    "--output-dir",
                    str(tmp_path / "runs"),
                    "--raw-rows-output",
                    str(raw_rows),
                    "--output-json",
                    str(output_json),
                    "--output-md",
                    str(tmp_path / "aide_report.md"),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            self.assertIn("unit_aide_fixture_run", completed.stdout)
            report = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertEqual("complete", report["overall_status"])
            rows = [json.loads(line) for line in raw_rows.read_text(encoding="utf-8").splitlines()]
            self.assertEqual(2, len(rows))
            self.assertEqual({"summary", "papertoskill"}, {row["condition"] for row in rows})
            self.assertTrue(all(row["success"] for row in rows))
            self.assertTrue((tmp_path / "runs" / "AIDE-T1" / "summary" / "unit_aide_fixture_run" / "metric.json").exists())

    def test_full_excerpt_fixture_response_for_sanity_task(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            root = prepare_temp_root(tmp_path)
            fixture_dir = tmp_path / "fixture_responses"
            fixture_dir.mkdir()
            (fixture_dir / "AIDE-T1_full_excerpt.md").write_text(CANDIDATE_RESPONSE, encoding="utf-8")
            raw_rows = tmp_path / "raw_rows.jsonl"
            output_json = tmp_path / "aide_report.json"

            subprocess.run(
                [
                    sys.executable,
                    str(RUN_SCRIPT),
                    "--root",
                    str(root),
                    "--task",
                    "AIDE-T1",
                    "--condition",
                    "full_excerpt",
                    "--fixture-response-dir",
                    str(fixture_dir),
                    "--run-id",
                    "unit_aide_full_excerpt",
                    "--output-dir",
                    str(tmp_path / "runs"),
                    "--raw-rows-output",
                    str(raw_rows),
                    "--output-json",
                    str(output_json),
                    "--output-md",
                    str(tmp_path / "aide_report.md"),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            report = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertEqual("complete", report["overall_status"])
            rows = [json.loads(line) for line in raw_rows.read_text(encoding="utf-8").splitlines()]
            self.assertEqual(["full_excerpt"], [row["condition"] for row in rows])
            self.assertTrue(rows[0]["success"])
            prompt = (tmp_path / "runs" / "AIDE-T1" / "full_excerpt" / "unit_aide_full_excerpt" / "prompt.md").read_text(encoding="utf-8")
            self.assertIn("Full AIDE paper excerpt", prompt)
            self.assertIn("Real-Reuse Condition: full_excerpt", prompt)

    def test_default_conditions_remain_primary_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            root = prepare_temp_root(tmp_path)
            fixture_dir = tmp_path / "fixture_responses"
            fixture_dir.mkdir()
            for condition in ("summary", "papertoskill", "full_excerpt"):
                (fixture_dir / f"AIDE-T1_{condition}.md").write_text(CANDIDATE_RESPONSE, encoding="utf-8")
            raw_rows = tmp_path / "raw_rows.jsonl"
            output_json = tmp_path / "aide_report.json"

            subprocess.run(
                [
                    sys.executable,
                    str(RUN_SCRIPT),
                    "--root",
                    str(root),
                    "--task",
                    "AIDE-T1",
                    "--fixture-response-dir",
                    str(fixture_dir),
                    "--run-id",
                    "unit_aide_default_primary",
                    "--output-dir",
                    str(tmp_path / "runs"),
                    "--raw-rows-output",
                    str(raw_rows),
                    "--output-json",
                    str(output_json),
                    "--output-md",
                    str(tmp_path / "aide_report.md"),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            report = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertEqual(["summary", "papertoskill"], report["conditions"])
            rows = [json.loads(line) for line in raw_rows.read_text(encoding="utf-8").splitlines()]
            self.assertEqual({"summary", "papertoskill"}, {row["condition"] for row in rows})

    def test_missing_credentials_records_pending_without_raw_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            root = prepare_temp_root(tmp_path)
            raw_rows = tmp_path / "raw_rows.jsonl"
            output_json = tmp_path / "aide_report.json"

            subprocess.run(
                [
                    sys.executable,
                    str(RUN_SCRIPT),
                    "--root",
                    str(root),
                    "--task",
                    "AIDE-T1",
                    "--condition",
                    "summary",
                    "--base-url-env",
                    "PAPERTOSKILL_UNITTEST_MISSING_BASE_URL",
                    "--api-key-env",
                    "PAPERTOSKILL_UNITTEST_MISSING_API_KEY",
                    "--run-id",
                    "unit_aide_missing_credentials",
                    "--output-dir",
                    str(tmp_path / "runs"),
                    "--raw-rows-output",
                    str(raw_rows),
                    "--output-json",
                    str(output_json),
                    "--output-md",
                    str(tmp_path / "aide_report.md"),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            report = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertEqual("pending", report["overall_status"])
            self.assertFalse(raw_rows.exists())
            self.assertIn("missing_base_url_or_api_key_env", report["results"][0]["failure_reason"])

    def test_prompt_uses_condition_context_without_hidden_labels(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = prepare_temp_root(Path(tmp))
            prompt = build_prompt(root, "AIDE-T1", "summary")

            self.assertIn("Real-Reuse Condition: summary", prompt)
            self.assertIn("Generic Summary: AIDE", prompt)
            self.assertIn("AIDE-T1 Locked Task Prompt", prompt)
            self.assertNotIn("validation_labels.csv", prompt)
            self.assertNotIn("hidden_from_model", prompt)


if __name__ == "__main__":
    unittest.main()
