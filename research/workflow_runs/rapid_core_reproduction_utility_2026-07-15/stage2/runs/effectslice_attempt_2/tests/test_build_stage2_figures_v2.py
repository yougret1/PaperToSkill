import json
import sys
import tempfile
import unittest
from pathlib import Path


RUN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RUN_ROOT))

from build_stage2_figures_v2 import (  # noqa: E402
    build_stage2_figures,
    collect_figure_data,
)


class BuildStage2FiguresV2Test(unittest.TestCase):
    def _write_summaries(self, root):
        logs = root / "logs"
        logs.mkdir(parents=True)
        ablation = {
            "schema_version": "effectslice-stage2-ablation-summary.v2",
            "statistical_unit": "independent_agent_run",
            "replicate_denominator_per_task": 18,
            "clustered_hidden_checks_per_run": 64,
            "task_rows": [
                {
                    "task_key": "snap_mfse",
                    "condition_successes": {"B": 2, "F": 14, "S": 11},
                },
                {
                    "task_key": "toolformer_filter",
                    "condition_successes": {"B": 1, "F": 18, "S": 18},
                },
            ],
        }
        research = {
            "schema_version": "effectslice-stage2-research-summary.v2",
            "statistical_unit": "independent_agent_run",
            "task_rows": [
                {
                    "task_key": "snap_mfse",
                    "full_benefit": {
                        "successes": 12,
                        "total": 18,
                        "one_sided_cp_lower": 0.51,
                        "minimum_prevalence": 0.8,
                    },
                    "slice_preservation": {
                        "successes": 10,
                        "total": 18,
                        "one_sided_cp_lower": 0.40,
                        "minimum_prevalence": 0.8,
                    },
                    "slice_benefit": {
                        "successes": 9,
                        "total": 18,
                        "one_sided_cp_lower": 0.35,
                        "minimum_prevalence": 0.8,
                    },
                },
                {
                    "task_key": "toolformer_filter",
                    "full_benefit": {
                        "successes": 17,
                        "total": 18,
                        "one_sided_cp_lower": 0.716,
                        "minimum_prevalence": 0.8,
                    },
                    "slice_preservation": {
                        "successes": 18,
                        "total": 18,
                        "one_sided_cp_lower": 0.805,
                        "minimum_prevalence": 0.8,
                    },
                    "slice_benefit": {
                        "successes": 17,
                        "total": 18,
                        "one_sided_cp_lower": 0.716,
                        "minimum_prevalence": 0.8,
                    },
                },
            ],
        }
        (logs / "ablation_summary.json").write_text(
            json.dumps(ablation), encoding="utf-8"
        )
        (logs / "research_summary.json").write_text(
            json.dumps(research), encoding="utf-8"
        )

    def test_collects_only_run_level_summary_values(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._write_summaries(root)

            data = collect_figure_data(root)

        self.assertEqual(data["replicate_denominator"], 18)
        self.assertEqual(data["clustered_hidden_checks_per_run"], 64)
        self.assertEqual(data["condition_successes"]["snap_mfse"], [2, 14, 11])
        self.assertEqual(
            data["indicator_successes"]["toolformer_filter"], [17, 18, 17]
        )
        self.assertEqual(
            data["cp_lowers"]["toolformer_filter"], [0.716, 0.805, 0.716]
        )

    def test_builds_png_and_traceability_report(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._write_summaries(root)

            outputs = build_stage2_figures(root, root / "figures")

            figure = Path(outputs["figure"])
            report = json.loads(Path(outputs["report"]).read_text(encoding="utf-8"))
            figure_size = figure.stat().st_size

        self.assertGreater(figure_size, 1000)
        self.assertEqual(
            report["data_sources"],
            ["logs/ablation_summary.json", "logs/research_summary.json"],
        )
        self.assertEqual(report["statistical_unit"], "independent_agent_run")
        self.assertIn("figure_data_sha256", report)


if __name__ == "__main__":
    unittest.main()
