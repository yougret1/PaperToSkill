import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.build_real_reuse_llm_ablation_plan import build_plan


ROOT = Path(__file__).resolve().parents[1]


class BuildRealReuseLLMAblationPlanTest(unittest.TestCase):
    def test_current_plan_selects_stabilized_subset_and_long_retries(self):
        plan = build_plan(
            ROOT,
            Path("benchmarks/real_reuse/llm_ablation_v0.json"),
            Path("results/real_reuse/main_results_plan.csv"),
        )
        self.assertEqual(["AIDE-T2", "SWE-T2", "REF-T2"], [row["task_id"] for row in plan["tasks"]])
        self.assertEqual(18, plan["expected_scored_raw_rows"])
        self.assertTrue(any(row["task_id"] == "SWE-T1" for row in plan["deferred_until_contract_fix"]))
        for command in plan["commands"]:
            self.assertIn("--condition summary --condition papertoskill", command["command"])
            self.assertIn("--timeout-seconds 300", command["command"])
            self.assertIn("--max-attempts 5", command["command"])
        claude = [row for row in plan["commands"] if row["model_slot"] == "claude_opus_4_8"]
        self.assertTrue(all("--wire-api anthropic_messages" in row["command"] for row in claude))
        deepseek = [row for row in plan["commands"] if row["model_slot"] == "deepseek_v4_flash"]
        self.assertTrue(all("--wire-api openai_chat_completions" in row["command"] for row in deepseek))

    def test_cli_writes_plan_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_json = Path(tmp) / "plan.json"
            output_md = Path(tmp) / "plan.md"
            env = os.environ.copy()
            env["PAPERTOSKILL_GPT_OPENAI_BASE_URL"] = "https://example.invalid/v1"
            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "build_real_reuse_llm_ablation_plan.py"),
                    "--output-json",
                    str(output_json),
                    "--output-md",
                    str(output_md),
                ],
                cwd=ROOT,
                check=True,
                env=env,
                stdout=subprocess.PIPE,
                text=True,
            )
            payload = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertEqual("present", payload["environment_status"]["PAPERTOSKILL_GPT_OPENAI_BASE_URL"])
            self.assertIn("Real-Reuse LLM Ablation Plan", output_md.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
