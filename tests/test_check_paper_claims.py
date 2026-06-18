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
DRAFT_MD = ROOT / "paper" / "draft.md"
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
            self.assertEqual(20, report["status_counts"]["ready"])
            self.assertEqual(0, report["status_counts"]["fail"])
            ready_ids = {check["id"] for check in report["checks"] if check["status"] == "ready"}
            self.assertIn("paper_claim_boundary_curated_scope", ready_ids)
            self.assertIn("paper_claim_boundary_live_transfer_saved_response_boundary", ready_ids)
            self.assertIn("paper_claim_boundary_model_ablation_partial_boundary", ready_ids)
            self.assertTrue(output_md.exists())

    def test_unbounded_live_transfer_claim_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            tmp_aaai = tmp_root / "paper" / "aaai" / "papertoskill_aaai2027.tex"
            tmp_draft = tmp_root / "paper" / "draft.md"
            tmp_aaai.parent.mkdir(parents=True)
            shutil.copyfile(AAAI_TEX, tmp_aaai)
            shutil.copyfile(DRAFT_MD, tmp_draft)

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


if __name__ == "__main__":
    unittest.main()
