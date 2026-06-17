import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "audit_skill_source_map.py"


class AuditSkillSourceMapTest(unittest.TestCase):
    def test_supported_skill_scores_better_than_abstract_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            good_note = tmp_path / "good_note.md"
            good_note.write_text(
                """# Title

## Methods
1. Use generalized idea generation.
2. Manage four stages and parallelized tree search.

## Experiments
- Run replications and aggregation with figures reviewed by VLM.

## Limitations
- Warn about workshop-level results and disclosure.

## Transfer Notes
- Keep source-backed steps separate.
""",
                encoding="utf-8",
            )
            bad_note = tmp_path / "bad_note.md"
            bad_note.write_text(
                """# Title

## Abstract
We propose a skill system.
""",
                encoding="utf-8",
            )

            good_skill = tmp_path / "good_skill"
            good_skill.mkdir()
            (good_skill / "SKILL.md").write_text(
                """---
name: good
description: good
---

## Workflow
1. Use generalized idea generation. Source anchors: lines 1-2.
2. Manage four stages and parallelized tree search. Source anchors: lines 3-4.

## Validation
- Run replications and aggregation with figures reviewed by VLM. Source anchors: lines 5-6.

## Failure Cases
- Warn about workshop-level results and disclosure. Source anchors: lines 7-8.

## Transfer Notes
- Keep source-backed steps separate. Source anchors: lines 9-10.
""",
                encoding="utf-8",
            )
            (good_skill / "references").mkdir()
            (good_skill / "references" / "source_map.json").write_text(
                json.dumps({"source": str(good_note), "source_map": {"selected_groups": {"method": ["Methods"], "experiment": ["Experiments"], "limitation": ["Limitations"], "transfer notes": ["Transfer Notes"]}}}),
                encoding="utf-8",
            )

            bad_skill = tmp_path / "bad_skill"
            bad_skill.mkdir()
            (bad_skill / "SKILL.md").write_text(
                """---
name: bad
description: bad
---

## Workflow
1. Use generalized idea generation.

## Validation
- Run replications.
""",
                encoding="utf-8",
            )
            (bad_skill / "references").mkdir()
            (bad_skill / "references" / "source_map.json").write_text(
                json.dumps({"source": str(bad_note), "source_map": {"selected_groups": {"workflow": ["Abstract"], "validation": ["Abstract"], "failure cases": ["Abstract"], "transfer notes": ["Abstract"]}}}),
                encoding="utf-8",
            )

            task = tmp_path / "task.json"
            task.write_text(
                json.dumps(
                    {
                        "id": "audit",
                        "skills": [
                            {"id": "good", "path": str(good_skill)},
                            {"id": "bad", "path": str(bad_skill)},
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
            scores = {item["id"]: item["unsupported_rate"] for item in report["results"]}
            self.assertLess(scores["good"], scores["bad"])


if __name__ == "__main__":
    unittest.main()
