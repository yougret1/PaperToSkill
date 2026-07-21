import json
import sys
import tempfile
import unittest
from pathlib import Path


RUN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RUN_ROOT))

from build_paper_results_v2 import build_paper_results  # noqa: E402


class BuildPaperResultsV2Test(unittest.TestCase):
    def test_generates_latex_macros_only_from_v2_summaries(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            logs = root / "logs"
            logs.mkdir()
            research = {
                "schema_version": "effectslice-stage2-research-summary.v2",
                "statistical_unit": "independent_agent_run",
                "task_rows": [
                    {
                        "task_key": "snap_mfse",
                        "classification": "task_local_admission_rejected",
                        "full_benefit": {
                            "successes": 12,
                            "total": 18,
                            "one_sided_cp_lower": 0.510123,
                        },
                        "slice_preservation": {
                            "successes": 10,
                            "total": 18,
                            "one_sided_cp_lower": 0.401234,
                        },
                        "slice_benefit": {
                            "successes": 9,
                            "total": 18,
                            "one_sided_cp_lower": 0.351234,
                        },
                    },
                    {
                        "task_key": "toolformer_filter",
                        "classification": "task_local_admission_passed",
                        "full_benefit": {
                            "successes": 18,
                            "total": 18,
                            "one_sided_cp_lower": 0.804661,
                        },
                        "slice_preservation": {
                            "successes": 18,
                            "total": 18,
                            "one_sided_cp_lower": 0.804661,
                        },
                        "slice_benefit": {
                            "successes": 18,
                            "total": 18,
                            "one_sided_cp_lower": 0.804661,
                        },
                    },
                ],
            }
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
            research_path = logs / "research_summary.json"
            ablation_path = logs / "ablation_summary.json"
            research_path.write_text(json.dumps(research), encoding="utf-8")
            ablation_path.write_text(json.dumps(ablation), encoding="utf-8")
            output_tex = root / "generated_results.tex"
            output_manifest = root / "generated_results_manifest.json"

            build_paper_results(
                research_path=research_path,
                ablation_path=ablation_path,
                output_tex=output_tex,
                output_manifest=output_manifest,
            )

            latex = output_tex.read_text(encoding="utf-8")
            manifest = json.loads(output_manifest.read_text(encoding="utf-8"))

        self.assertIn(r"\newcommand{\EffectSliceProviderConversations}{108}", latex)
        self.assertIn(r"\newcommand{\EffectSliceAdmissions}{1}", latex)
        self.assertIn(r"\newcommand{\SnapMFSEFSuccesses}{14}", latex)
        self.assertIn(r"\newcommand{\SnapMFSEFullBenefitSuccesses}{12}", latex)
        self.assertIn(r"\newcommand{\SnapMFSEFullBenefitCPLower}{0.510}", latex)
        self.assertIn(r"\newcommand{\SnapMFSEDecision}{Reject}", latex)
        self.assertIn(r"\newcommand{\ToolformerFilterDecision}{Admit}", latex)
        self.assertEqual(manifest["statistical_unit"], "independent_agent_run")
        self.assertEqual(manifest["replicates_per_task"], 18)
        self.assertEqual(manifest["hidden_checks_per_run"], 64)
        self.assertEqual(len(manifest["source_sha256"]), 2)


if __name__ == "__main__":
    unittest.main()
