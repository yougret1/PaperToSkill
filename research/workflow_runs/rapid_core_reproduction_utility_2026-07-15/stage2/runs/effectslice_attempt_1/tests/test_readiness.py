import json
import sys
import tempfile
import unittest
from pathlib import Path


RUN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RUN_ROOT / "src"))

from effectslice.readiness import audit_project  # noqa: E402


@unittest.skip("Superseded by read-only static fixture tests in test_readiness_static.py")
class ReadinessAuditTest(unittest.TestCase):
    def test_aggregate_summary_and_skill_rows_are_not_certificate_ready(self):
        with tempfile.TemporaryDirectory(dir=RUN_ROOT, delete=False) as tmp:
            root = Path(tmp)
            self.write_json(
                root / "benchmarks/real_reuse/real_reuse_v0.json",
                {
                    "tasks": [
                        {
                            "id": "T1",
                            "source_paper_id": "paper_one",
                            "conditions": ["summary", "papertoskill"],
                            "metric": {"name": "score", "direction": "higher_is_better"},
                        }
                    ]
                },
            )
            self.write_json(
                root / "results/real_reuse/main_run_selection.json",
                {
                    "rows": [
                        {"task_id": "T1", "condition": "summary", "run_id": "r1"},
                        {"task_id": "T1", "condition": "papertoskill", "run_id": "r1"},
                    ]
                },
            )
            raw = root / "results/real_reuse/raw_rows.jsonl"
            raw.parent.mkdir(parents=True, exist_ok=True)
            raw.write_text(
                "\n".join(
                    json.dumps(row)
                    for row in [
                        {"task_id": "T1", "condition": "summary", "run_id": "r1", "task_score": 0.4},
                        {
                            "task_id": "T1",
                            "condition": "papertoskill",
                            "run_id": "r1",
                            "task_score": 0.6,
                        },
                    ]
                ),
                encoding="utf-8",
            )
            self.write_json(
                root / "generated_skills/paper_one/references/source_map.json",
                {
                    "workflow_steps": ["Run the method. Source anchors: lines 1-2."],
                    "source_map": {"sections": [{"title": "Methods", "line": 1}]},
                },
            )
            config = {
                "task_spec": "benchmarks/real_reuse/real_reuse_v0.json",
                "main_row_selection": "results/real_reuse/main_run_selection.json",
                "raw_rows": "results/real_reuse/raw_rows.jsonl",
                "source_maps": {
                    "paper_one": "generated_skills/paper_one/references/source_map.json"
                },
                "statistics": {"minimum_eligibility_pairs": 3},
                "task_adapters": {},
            }
            config_path = root / "config.json"
            self.write_json(config_path, config)

            report = audit_project(root, config_path)

            self.assertEqual(report["task_count"], 1)
            self.assertEqual(report["ready_task_count"], 0)
            missing = set(report["tasks"][0]["missing_requirements"])
            self.assertIn("missing_same_scaffold_no_skill_baseline", missing)
            self.assertIn("insufficient_eligibility_pairs", missing)
            self.assertIn("missing_case_level_pairs", missing)
            self.assertIn("missing_cost_conversion", missing)
            self.assertIn("missing_four_way_atoms", missing)
            self.assertIn("missing_dependency_graph", missing)
            self.assertIn("missing_contract_guardrail_predicates", missing)

    def test_shallow_truthy_fields_are_not_certificate_ready(self):
        with tempfile.TemporaryDirectory(dir=RUN_ROOT, delete=False) as tmp:
            root = Path(tmp)
            config_path = self.write_probe(root, valid=False)

            report = audit_project(root, config_path)

            self.assertEqual(report["ready_task_count"], 0)
            missing = set(report["tasks"][0]["missing_requirements"])
            self.assertIn("missing_case_level_pairs", missing)
            self.assertIn("missing_score_bounds", missing)
            self.assertIn("missing_cost_conversion", missing)
            self.assertIn("missing_contract_guardrail_predicates", missing)
            self.assertIn("missing_four_way_atoms", missing)
            self.assertIn("missing_dependency_graph", missing)
            self.assertIn("missing_complete_neighbor_budget", missing)

    def test_strict_task_adapter_and_paired_rows_are_certificate_ready(self):
        with tempfile.TemporaryDirectory(dir=RUN_ROOT, delete=False) as tmp:
            root = Path(tmp)
            config_path = self.write_probe(root, valid=True)

            report = audit_project(root, config_path)

            self.assertEqual(report["task_count"], 1)
            self.assertEqual(report["ready_task_count"], 1)
            self.assertEqual(report["tasks"][0]["paired_case_count"], 3)
            self.assertEqual(report["tasks"][0]["missing_requirements"], [])

    def write_probe(self, root: Path, valid: bool) -> Path:
        self.write_json(
            root / "benchmarks/real_reuse/real_reuse_v0.json",
            {
                "tasks": [
                    {
                        "id": "T1",
                        "source_paper_id": "paper_one",
                        "conditions": ["papertoskill", "no_skill"],
                        "metric": {"name": "score", "direction": "higher_is_better"},
                    }
                ]
            },
        )
        self.write_json(
            root / "results/real_reuse/main_run_selection.json",
            {
                "rows": [
                    {"task_id": "T1", "condition": condition, "run_id": "r1"}
                    for condition in ("papertoskill", "no_skill")
                ]
            },
        )
        raw = root / "results/real_reuse/raw_rows.jsonl"
        raw.parent.mkdir(parents=True, exist_ok=True)
        rows = []
        for index in range(3):
            for condition, score in (("papertoskill", 0.8), ("no_skill", 0.2)):
                row = {
                    "task_id": "T1",
                    "condition": condition,
                    "run_id": "r1",
                    "pair_id": f"pair-{index}",
                    "case_id": f"case-{index}",
                    "seed_block_id": "eligibility:001",
                }
                if valid:
                    row.update({"status": "completed", "task_score": score})
                rows.append(row)
        raw.write_text("\n".join(json.dumps(row) for row in rows), encoding="utf-8")

        digest = "a" * 64
        if valid:
            atom = {
                "atom_id": "A",
                "workflow_step": "step-1",
                "source_span": {
                    "file_digest": digest,
                    "byte_start": 0,
                    "byte_end": 10,
                    "line_start": 1,
                    "line_end": 2,
                },
                "executable_region": {
                    "file_digest": digest,
                    "symbol": "run",
                    "byte_start": 0,
                    "byte_end": 5,
                },
                "contract_role": "primary",
            }
            source_map = {
                "atoms": [atom],
                "dependency_nodes": ["A"],
                "dependency_edges": [],
            }
            predicate = {
                "id": "predicate-1",
                "callable": "adapter:predicate",
                "digest": digest,
                "missing_value_policy": "fail",
            }
            adapter = {
                "score_bounds": [-1.0, 1.0],
                "cost_weights": {
                    "api": 0.25,
                    "compute": 0.25,
                    "guardrail": 0.25,
                    "labor": 0.25,
                },
                "contracts": [predicate],
                "guardrails": [{**predicate, "id": "guardrail-1"}],
                "query_budget": {"Q": 24, "N": 1},
            }
        else:
            source_map = {
                "atoms": [
                    {
                        "atom_id": "A",
                        "workflow_step": "step-1",
                        "source_span": "lines 1-2",
                        "executable_region": "run",
                        "contract_role": ["primary", "guardrail"],
                    }
                ],
                "dependency_edges": [],
            }
            adapter = {
                "score_bounds": [0, 0],
                "cost_weights": {"compute": 0},
                "contracts": ["passes"],
                "guardrails": ["passes"],
            }

        self.write_json(
            root / "generated_skills/paper_one/references/source_map.json", source_map
        )
        config = {
            "task_spec": "benchmarks/real_reuse/real_reuse_v0.json",
            "main_row_selection": "results/real_reuse/main_run_selection.json",
            "raw_rows": "results/real_reuse/raw_rows.jsonl",
            "source_maps": {
                "paper_one": "generated_skills/paper_one/references/source_map.json"
            },
            "statistics": {"minimum_eligibility_pairs": 3},
            "search": {"Q": 24, "N": 16},
            "task_adapters": {"T1": adapter},
        }
        config_path = root / "config.json"
        self.write_json(config_path, config)
        return config_path

    @staticmethod
    def write_json(path: Path, payload: dict):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload), encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
