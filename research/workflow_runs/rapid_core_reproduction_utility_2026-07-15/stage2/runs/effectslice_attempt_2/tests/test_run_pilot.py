import json
import sys
import tempfile
import unittest
from pathlib import Path


RUN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RUN_ROOT))
sys.path.insert(0, str(RUN_ROOT / "src"))

from run_pilot import run_pilot  # noqa: E402


@unittest.skip("Superseded by the static run fixture test in test_run_pilot_static.py")
class PilotRunnerTest(unittest.TestCase):
    def test_writes_readiness_and_three_bounded_summaries(self):
        with tempfile.TemporaryDirectory(
            dir=RUN_ROOT, delete=False
        ) as project_tmp, tempfile.TemporaryDirectory(
            dir=RUN_ROOT, delete=False
        ) as run_tmp:
            project = Path(project_tmp)
            run = Path(run_tmp)
            self.write_json(
                project / "benchmarks/real_reuse/real_reuse_v0.json",
                {
                    "tasks": [
                        {
                            "id": "T1",
                            "source_paper_id": "p1",
                            "conditions": ["summary", "papertoskill"],
                            "metric": {"name": "score"},
                        }
                    ]
                },
            )
            self.write_json(
                project / "results/real_reuse/main_run_selection.json",
                {
                    "rows": [
                        {"task_id": "T1", "condition": "summary", "run_id": "r1"},
                        {"task_id": "T1", "condition": "papertoskill", "run_id": "r1"},
                    ]
                },
            )
            raw = project / "results/real_reuse/raw_rows.jsonl"
            raw.parent.mkdir(parents=True, exist_ok=True)
            raw.write_text(
                json.dumps(
                    {"task_id": "T1", "condition": "papertoskill", "run_id": "r1", "task_score": 0.6}
                ),
                encoding="utf-8",
            )
            self.write_json(
                project / "generated_skills/p1/references/source_map.json",
                {"workflow_steps": ["Run one step."], "source_map": {"sections": []}},
            )
            self.write_json(
                run / "configs/experiment_config.json",
                {
                    "task_spec": "benchmarks/real_reuse/real_reuse_v0.json",
                    "main_row_selection": "results/real_reuse/main_run_selection.json",
                    "raw_rows": "results/real_reuse/raw_rows.jsonl",
                    "source_maps": {"p1": "generated_skills/p1/references/source_map.json"},
                    "statistics": {"minimum_eligibility_pairs": 3},
                    "search": {"Q": 24, "N": 16},
                    "task_adapters": {},
                },
            )

            outputs = run_pilot(project, run)

            expected = {
                "readiness": run / "experiment_results/pilot/readiness_report.json",
                "baseline": run / "logs/baseline_summary.json",
                "research": run / "logs/research_summary.json",
                "ablation": run / "logs/ablation_summary.json",
            }
            self.assertEqual(outputs, {key: str(path) for key, path in expected.items()})
            for path in expected.values():
                payload = json.loads(path.read_text(encoding="utf-8"))
                self.assertIn("evidence_boundary", payload)
                self.assertIn("not EffectSlice effectiveness evidence", payload["evidence_boundary"])
            readiness = json.loads(expected["readiness"].read_text(encoding="utf-8"))
            self.assertEqual(readiness["ready_task_count"], 0)
            for summary_name in ("baseline", "research", "ablation"):
                summary = json.loads(expected[summary_name].read_text(encoding="utf-8"))
                self.assertEqual(len(summary["entries"]), 1)
                self.assertIn("metric", summary["entries"][0])

    @staticmethod
    def write_json(path: Path, payload: dict):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload), encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
