import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "evaluate_skill.py"
RUBRIC = ROOT / "benchmarks" / "rubric_v0.json"


class EvaluateSkillTest(unittest.TestCase):
    def test_cli_scores_minimal_skill(self):
        skill_text = """---
name: sample
description: sample
---

# Sample

## Source
Source anchors: lines 1-2.

## Paper Snapshot
Snapshot.

## Central Contribution
Contribution.

## Inputs
- Input.

## Workflow
1. Use generalized idea generation and an Experiment Progress Manager with four stages.
2. Run parallelized agentic tree search, mark buggy and non-buggy nodes, and use replications plus aggregation. Source anchors: lines 3-4.

## Validation
- Source anchors: lines 5-6.

## Failure Cases
- This is workshop-level, one of three, not top-tier conference; note citation inaccuracies, IRB, and withdrawal.

## Transfer Notes
- Transfer.
"""
        with tempfile.TemporaryDirectory() as tmp:
            skill = Path(tmp) / "SKILL.md"
            skill.write_text(skill_text, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--skill", str(skill), "--rubric", str(RUBRIC)],
                check=True,
                capture_output=True,
                text=True,
            )
            report = json.loads(result.stdout)
            self.assertGreaterEqual(report["score"], 18)


if __name__ == "__main__":
    unittest.main()
