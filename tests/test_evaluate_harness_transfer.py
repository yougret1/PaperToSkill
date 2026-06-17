import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "evaluate_harness_transfer.py"


class EvaluateHarnessTransferTest(unittest.TestCase):
    def test_transfer_notes_improve_readiness(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            skill = tmp_path / "skill.md"
            skill.write_text(
                """# Paper Skill

## Inputs
- A paper.

## Workflow
1. Use generalized idea generation and parallelized agentic tree search.

## Validation
- Check three complete manuscripts and a 6.33/10 review outcome. Source anchors: lines 1-2.

## Failure Cases
- Record citation inaccuracies and top-tier limitations. Source anchors: lines 3-4.

## Transfer Notes
- Check the target harness.
- Replace framework-specific commands with local equivalents.
- Keep source-backed steps separate from inferred adaptations.
- Record any failed branch.
""",
                encoding="utf-8",
            )
            summary = tmp_path / "summary.md"
            summary.write_text(
                """# Summary

The paper uses tree search and generated manuscripts.
""",
                encoding="utf-8",
            )
            task = tmp_path / "task.json"
            task.write_text(
                json.dumps(
                    {
                        "id": "transfer_test",
                        "context_variants": [
                            {"id": "full", "path": str(skill)},
                            {
                                "id": "no_transfer",
                                "path": str(skill),
                                "drop_sections": ["Transfer Notes"],
                            },
                            {"id": "summary", "path": str(summary)},
                        ],
                        "core_signal_groups": [
                            {
                                "id": "method",
                                "keywords": ["generalized idea generation", "parallelized agentic tree search"],
                            },
                            {
                                "id": "validation",
                                "keywords": ["three complete manuscripts", "6.33/10"],
                            },
                        ],
                        "target_harnesses": [
                            {
                                "id": "codex",
                                "required_sections": ["Inputs", "Workflow", "Validation", "Failure Cases", "Transfer Notes"],
                                "transfer_checks": [
                                    "target harness",
                                    "framework-specific commands",
                                    "local equivalents",
                                    "source-backed steps",
                                    "failed branch",
                                ],
                                "source_anchor_min": 2,
                                "max_words": 250,
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--task", str(task)],
                check=True,
                capture_output=True,
                text=True,
            )
            report = json.loads(result.stdout)
            scores = {item["id"]: item["average_normalized_score"] for item in report["results"]}
            self.assertGreater(scores["full"], scores["no_transfer"])
            self.assertGreater(scores["no_transfer"], scores["summary"])


if __name__ == "__main__":
    unittest.main()
