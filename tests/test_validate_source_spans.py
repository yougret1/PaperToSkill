import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_source_spans.py"


class ValidateSourceSpansTest(unittest.TestCase):
    def test_valid_span_scores_supported_and_invalid_range_is_flagged(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            source = tmp_path / "source.txt"
            source.write_text(
                "\n".join(
                    [
                        "The method uses generalized idea generation.",
                        "It then runs parallelized agentic tree search.",
                        "Unrelated filler line.",
                    ]
                ),
                encoding="utf-8",
            )
            skill = tmp_path / "skill.md"
            skill.write_text(
                """# Skill

## Workflow
1. Use generalized idea generation and parallelized agentic tree search. Source anchors: lines 1-2.
2. Cite a missing span. Source anchors: lines 10-12.
""",
                encoding="utf-8",
            )
            task = tmp_path / "task.json"
            task.write_text(
                json.dumps(
                    {
                        "id": "span_test",
                        "sections": ["Workflow"],
                        "min_overlap_score": 0.35,
                        "items": [
                            {"id": "skill", "skill_path": str(skill), "source_text": str(source)}
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
            item = report["results"][0]
            statuses = [claim["status"] for claim in item["claims"]]
            self.assertIn("supported", statuses)
            self.assertIn("invalid_range", statuses)
            self.assertEqual(item["invalid_ranges"], 1)

    def test_form_feed_does_not_shift_newline_based_anchors(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            source = tmp_path / "source.txt"
            source.write_text(
                "Cover page\f still line one\n"
                "The method uses generalized idea generation.\n"
                "It then runs parallelized agentic tree search.\n",
                encoding="utf-8",
            )
            skill = tmp_path / "skill.md"
            skill.write_text(
                """# Skill

## Workflow
1. Use generalized idea generation and parallelized agentic tree search. Source anchors: lines 2-3.
""",
                encoding="utf-8",
            )
            task = tmp_path / "task.json"
            task.write_text(
                json.dumps(
                    {
                        "id": "span_test_form_feed",
                        "sections": ["Workflow"],
                        "min_overlap_score": 0.35,
                        "items": [
                            {"id": "skill", "skill_path": str(skill), "source_text": str(source)}
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
            self.assertEqual(report["results"][0]["claims"][0]["status"], "supported")


if __name__ == "__main__":
    unittest.main()
