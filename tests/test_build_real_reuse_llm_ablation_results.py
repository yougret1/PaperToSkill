import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.build_real_reuse_llm_ablation_plan import build_plan
from scripts.build_real_reuse_llm_ablation_results import build_summary


ROOT = Path(__file__).resolve().parents[1]


class BuildRealReuseLLMAblationResultsTest(unittest.TestCase):
    def test_current_summary_finds_phase109_ref_t2_rows(self):
        plan = build_plan(
            ROOT,
            Path("benchmarks/real_reuse/llm_ablation_v0.json"),
            Path("results/real_reuse/main_results_plan.csv"),
        )
        raw_rows = [
            json.loads(line)
            for line in (ROOT / "results" / "real_reuse" / "raw_rows.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        summary = build_summary(plan, raw_rows)
        self.assertEqual(18, summary["expected_rows"])
        self.assertGreaterEqual(summary["collected_rows"], 2)
        ref_pair = [
            row
            for row in summary["pairs"]
            if row["task_id"] == "REF-T2" and row["model_slot"] == "gpt_5_5"
        ][0]
        self.assertEqual("complete", ref_pair["pair_status"])
        self.assertEqual("1.000", ref_pair["summary_score"])
        self.assertEqual("1.000", ref_pair["papertoskill_score"])

    def test_current_summary_finds_phase109_aide_t2_rows(self):
        plan = build_plan(
            ROOT,
            Path("benchmarks/real_reuse/llm_ablation_v0.json"),
            Path("results/real_reuse/main_results_plan.csv"),
        )
        raw_rows = [
            json.loads(line)
            for line in (ROOT / "results" / "real_reuse" / "raw_rows.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        summary = build_summary(plan, raw_rows)
        self.assertGreaterEqual(summary["collected_rows"], 4)
        aide_pair = [
            row
            for row in summary["pairs"]
            if row["task_id"] == "AIDE-T2" and row["model_slot"] == "gpt_5_5"
        ][0]
        self.assertEqual("complete", aide_pair["pair_status"])
        self.assertEqual("0.814", aide_pair["summary_score"])
        self.assertEqual("0.000", aide_pair["papertoskill_score"])

    def test_current_summary_finds_phase109_swe_t2_rows(self):
        plan = build_plan(
            ROOT,
            Path("benchmarks/real_reuse/llm_ablation_v0.json"),
            Path("results/real_reuse/main_results_plan.csv"),
        )
        raw_rows = [
            json.loads(line)
            for line in (ROOT / "results" / "real_reuse" / "raw_rows.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        summary = build_summary(plan, raw_rows)
        self.assertGreaterEqual(summary["collected_rows"], 6)
        swe_pair = [
            row
            for row in summary["pairs"]
            if row["task_id"] == "SWE-T2" and row["model_slot"] == "gpt_5_5"
        ][0]
        self.assertEqual("complete", swe_pair["pair_status"])
        self.assertEqual("0.000", swe_pair["summary_score"])
        self.assertEqual("0.000", swe_pair["papertoskill_score"])

    def test_current_summary_finds_phase109_deepseek_rows(self):
        plan = build_plan(
            ROOT,
            Path("benchmarks/real_reuse/llm_ablation_v0.json"),
            Path("results/real_reuse/main_results_plan.csv"),
        )
        raw_rows = [
            json.loads(line)
            for line in (ROOT / "results" / "real_reuse" / "raw_rows.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        summary = build_summary(plan, raw_rows)
        self.assertGreaterEqual(summary["collected_rows"], 12)
        expected_scores = {
            "AIDE-T2": ("0.500", "0.500"),
            "SWE-T2": ("0.000", "0.000"),
            "REF-T2": ("1.000", "1.000"),
        }
        for task_id, (summary_score, papertoskill_score) in expected_scores.items():
            pair = [
                row
                for row in summary["pairs"]
                if row["task_id"] == task_id and row["model_slot"] == "deepseek_v4_flash"
            ][0]
            self.assertEqual("complete", pair["pair_status"])
            self.assertEqual(summary_score, pair["summary_score"])
            self.assertEqual(papertoskill_score, pair["papertoskill_score"])

    def test_cli_writes_summary_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_csv = Path(tmp) / "rows.csv"
            output_json = Path(tmp) / "summary.json"
            output_md = Path(tmp) / "summary.md"
            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "build_real_reuse_llm_ablation_results.py"),
                    "--output-csv",
                    str(output_csv),
                    "--output-json",
                    str(output_json),
                    "--output-md",
                    str(output_md),
                ],
                cwd=ROOT,
                check=True,
                stdout=subprocess.PIPE,
                text=True,
            )
            payload = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertIn("pending_rows", payload)
            self.assertIn("Real-Reuse LLM Ablation Summary", output_md.read_text(encoding="utf-8"))
            self.assertIn("task_id", output_csv.read_text(encoding="utf-8").splitlines()[0])


if __name__ == "__main__":
    unittest.main()
