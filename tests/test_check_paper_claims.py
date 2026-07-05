import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_paper_claims.py"
AAAI_TEX = ROOT / "paper" / "aaai" / "papertoskill_aaai2027.tex"
AAAI_TABLES = ROOT / "paper" / "aaai" / "papertoskill_tables.tex"
DRAFT_MD = ROOT / "paper" / "draft.md"
OUTLINE_MD = ROOT / "paper" / "outline.md"
LIMITATIONS_MD = ROOT / "paper" / "limitations.md"
sys.path.insert(0, str(ROOT / "scripts"))

from check_paper_claims import build_report  # noqa: E402


class CheckPaperClaimsTest(unittest.TestCase):
    def test_current_paper_claims_are_ready(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_json = Path(tmp) / "paper_claim_report.json"
            output_md = Path(tmp) / "paper_claim_report.md"
            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--output-json",
                    str(output_json),
                    "--output-md",
                    str(output_md),
                    "--strict",
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            report = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertEqual("ready", report["overall_status"])
            self.assertEqual(56, report["status_counts"]["ready"])
            self.assertEqual(0, report["status_counts"]["fail"])
            ready_ids = {check["id"] for check in report["checks"] if check["status"] == "ready"}
            self.assertIn("paper_claim_boundary_curated_scope", ready_ids)
            self.assertIn("paper_claim_boundary_live_transfer_saved_response_boundary", ready_ids)
            self.assertIn("paper_claim_boundary_model_ablation_saved_response_boundary", ready_ids)
            self.assertIn("paper_claim_no_aaai_tables_draft_planning_language", ready_ids)
            self.assertIn("paper_claim_no_outline_md_draft_planning_language", ready_ids)
            self.assertIn("paper_claim_target_limitations_md", ready_ids)
            self.assertIn("paper_claim_no_limitations_md_stale_claude_completion", ready_ids)
            self.assertIn("paper_claim_no_outline_md_stale_model_response_cost_scope", ready_ids)
            self.assertTrue(output_md.exists())

    def test_unbounded_live_transfer_claim_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            tmp_aaai = tmp_root / "paper" / "aaai" / "papertoskill_aaai2027.tex"
            tmp_tables = tmp_root / "paper" / "aaai" / "papertoskill_tables.tex"
            tmp_draft = tmp_root / "paper" / "draft.md"
            tmp_outline = tmp_root / "paper" / "outline.md"
            tmp_limitations = tmp_root / "paper" / "limitations.md"
            tmp_aaai.parent.mkdir(parents=True)
            shutil.copyfile(AAAI_TEX, tmp_aaai)
            shutil.copyfile(AAAI_TABLES, tmp_tables)
            shutil.copyfile(DRAFT_MD, tmp_draft)
            shutil.copyfile(OUTLINE_MD, tmp_outline)
            shutil.copyfile(LIMITATIONS_MD, tmp_limitations)

            text = tmp_aaai.read_text(encoding="utf-8")
            text = text.replace(
                r"\begin{abstract}",
                "\\begin{abstract}\nLive cross-harness execution has completed successfully.",
                1,
            )
            tmp_aaai.write_text(text, encoding="utf-8")

            report = build_report(tmp_root)

            statuses = {check["id"]: check["status"] for check in report["checks"]}
            self.assertEqual("fail", report["overall_status"])
            self.assertEqual("fail", statuses["paper_claim_no_aaai_tex_live_transfer_success"])

    def test_draft_language_in_aaai_tables_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            tmp_aaai = tmp_root / "paper" / "aaai" / "papertoskill_aaai2027.tex"
            tmp_tables = tmp_root / "paper" / "aaai" / "papertoskill_tables.tex"
            tmp_draft = tmp_root / "paper" / "draft.md"
            tmp_outline = tmp_root / "paper" / "outline.md"
            tmp_limitations = tmp_root / "paper" / "limitations.md"
            tmp_aaai.parent.mkdir(parents=True)
            shutil.copyfile(AAAI_TEX, tmp_aaai)
            shutil.copyfile(AAAI_TABLES, tmp_tables)
            shutil.copyfile(DRAFT_MD, tmp_draft)
            shutil.copyfile(OUTLINE_MD, tmp_outline)
            shutil.copyfile(LIMITATIONS_MD, tmp_limitations)

            text = tmp_tables.read_text(encoding="utf-8")
            text = text.replace(
                "Scores come from the eight locked local raw rows",
                "Filled scores come from local raw rows; future reruns or additional rows may be added. Scores come from the eight locked local raw rows",
                1,
            )
            tmp_tables.write_text(text, encoding="utf-8")

            report = build_report(tmp_root)

            statuses = {check["id"]: check["status"] for check in report["checks"]}
            self.assertEqual("fail", report["overall_status"])
            self.assertEqual("fail", statuses["paper_claim_no_aaai_tables_draft_planning_language"])

    def test_stale_planned_llm_ablation_outline_row_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            tmp_aaai = tmp_root / "paper" / "aaai" / "papertoskill_aaai2027.tex"
            tmp_tables = tmp_root / "paper" / "aaai" / "papertoskill_tables.tex"
            tmp_draft = tmp_root / "paper" / "draft.md"
            tmp_outline = tmp_root / "paper" / "outline.md"
            tmp_limitations = tmp_root / "paper" / "limitations.md"
            tmp_aaai.parent.mkdir(parents=True)
            shutil.copyfile(AAAI_TEX, tmp_aaai)
            shutil.copyfile(AAAI_TABLES, tmp_tables)
            shutil.copyfile(DRAFT_MD, tmp_draft)
            shutil.copyfile(OUTLINE_MD, tmp_outline)
            shutil.copyfile(LIMITATIONS_MD, tmp_limitations)

            text = tmp_outline.read_text(encoding="utf-8")
            text = text.replace(
                "Auxiliary: real-reuse LLM ablation",
                "Planned: LLM real-reuse ablation",
                1,
            )
            tmp_outline.write_text(text, encoding="utf-8")

            report = build_report(tmp_root)

            statuses = {check["id"]: check["status"] for check in report["checks"]}
            self.assertEqual("fail", report["overall_status"])
            self.assertEqual("fail", statuses["paper_claim_no_outline_md_draft_planning_language"])

    def test_stale_claude_completion_in_limitations_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            tmp_aaai = tmp_root / "paper" / "aaai" / "papertoskill_aaai2027.tex"
            tmp_tables = tmp_root / "paper" / "aaai" / "papertoskill_tables.tex"
            tmp_draft = tmp_root / "paper" / "draft.md"
            tmp_outline = tmp_root / "paper" / "outline.md"
            tmp_limitations = tmp_root / "paper" / "limitations.md"
            tmp_aaai.parent.mkdir(parents=True)
            shutil.copyfile(AAAI_TEX, tmp_aaai)
            shutil.copyfile(AAAI_TABLES, tmp_tables)
            shutil.copyfile(DRAFT_MD, tmp_draft)
            shutil.copyfile(OUTLINE_MD, tmp_outline)
            shutil.copyfile(LIMITATIONS_MD, tmp_limitations)

            text = tmp_limitations.read_text(encoding="utf-8")
            text = text.replace(
                "The latest Claude-family protocol\nrefresh used Anthropic Messages but was blocked by provider HTTP 502",
                "The latest live recheck completed both Claude Opus 4.8 prompt rows",
                1,
            )
            tmp_limitations.write_text(text, encoding="utf-8")

            report = build_report(tmp_root)

            statuses = {check["id"]: check["status"] for check in report["checks"]}
            self.assertEqual("fail", report["overall_status"])
            self.assertEqual("fail", statuses["paper_claim_no_limitations_md_stale_claude_completion"])

    def test_stale_model_response_cost_scope_in_outline_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            tmp_aaai = tmp_root / "paper" / "aaai" / "papertoskill_aaai2027.tex"
            tmp_tables = tmp_root / "paper" / "aaai" / "papertoskill_tables.tex"
            tmp_draft = tmp_root / "paper" / "draft.md"
            tmp_outline = tmp_root / "paper" / "outline.md"
            tmp_limitations = tmp_root / "paper" / "limitations.md"
            tmp_aaai.parent.mkdir(parents=True)
            shutil.copyfile(AAAI_TEX, tmp_aaai)
            shutil.copyfile(AAAI_TABLES, tmp_tables)
            shutil.copyfile(DRAFT_MD, tmp_draft)
            shutil.copyfile(OUTLINE_MD, tmp_outline)
            shutil.copyfile(LIMITATIONS_MD, tmp_limitations)

            text = tmp_outline.read_text(encoding="utf-8")
            text = text.replace(
                "Local output-token proxy for saved Claude/GPT-family/DeepSeek model-ablation responses",
                "Local output-token proxy for saved Claude/GPT-family model-ablation responses",
                1,
            )
            tmp_outline.write_text(text, encoding="utf-8")

            report = build_report(tmp_root)

            statuses = {check["id"]: check["status"] for check in report["checks"]}
            self.assertEqual("fail", report["overall_status"])
            self.assertEqual("fail", statuses["paper_claim_no_outline_md_stale_model_response_cost_scope"])


if __name__ == "__main__":
    unittest.main()
