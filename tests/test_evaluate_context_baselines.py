import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "evaluate_context_baselines.py"
TASK = ROOT / "benchmarks" / "tasks" / "ai_scientist_v2_research_run.json"


class EvaluateContextBaselinesTest(unittest.TestCase):
    def test_skill_scores_above_abstract(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--task", str(TASK)],
            check=True,
            capture_output=True,
            text=True,
        )
        report = json.loads(result.stdout)
        scores = {item["id"]: item["score"] for item in report["results"]}
        self.assertGreater(scores["skill"], scores["abstract_only"])
        self.assertGreater(scores["skill"], scores["generic_summary"])


if __name__ == "__main__":
    unittest.main()
