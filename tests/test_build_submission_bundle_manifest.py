import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_submission_bundle_manifest.py"


def write_json(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


class BuildSubmissionBundleManifestTest(unittest.TestCase):
    def test_cli_records_hashes_and_external_boundary(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for raw_path in [
                "paper/aaai/papertoskill_aaai2027.pdf",
                "paper/aaai/papertoskill_aaai2027.tex",
                "paper/aaai/papertoskill_tables.tex",
                "paper/aaai/papertoskill_supporting_tables.tex",
                "paper/aaai/papertoskill_refs.bib",
                "paper/aaai/README.md",
                "paper/aaai/aaai2027.sty",
                "paper/aaai/aaai2027.bst",
                "paper/aaai/AuthorKit27.zip",
                "README.md",
                "research/artifact_map.md",
                "research/runbook.md",
                "research/goal_completion_audit.md",
                "research/submission_checklist.md",
                "research/review_report.md",
                "research/rebuttal_bank.md",
            ]:
                path = root / raw_path
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(raw_path, encoding="utf-8")

            ready_report = {"overall_status": "ready", "status_counts": {"ready": 1, "fail": 0}, "checks": []}
            write_json(root / "results/reproducibility/aaai_package_report.json", ready_report)
            write_json(root / "results/reproducibility/paper_claim_report.json", ready_report)
            write_json(root / "results/reproducibility/paper_table_report.json", ready_report)
            write_json(root / "results/reproducibility/submission_review_report.json", ready_report)
            write_json(
                root / "results/reproducibility/package_report.json",
                {"overall_status": "ready_with_pending_external_evidence", "status_counts": {}, "checks": []},
            )
            write_json(
                root / "results/reproducibility/goal_completion_report.json",
                {"overall_status": "not_complete_pending_external_evidence", "status_counts": {}, "checks": []},
            )
            write_json(
                root / "results/external_evidence_closure/closure.json",
                {"overall_status": "pending_external_evidence", "status_counts": {}, "checks": []},
            )
            write_json(root / "results/external_evidence_packets/packets.json", ready_report)
            write_json(
                root / "results/aaai_submission_decision/decision.json",
                {"overall_status": "ready", "selected_option": "wait_for_external_evidence", "checks": []},
            )
            write_json(
                root / "results/human_fidelity_packets/annotation_summary.json",
                {"annotation_status": "pending"},
            )

            output_json = root / "results/reproducibility/submission_bundle_manifest.json"
            output_md = root / "results/reproducibility/submission_bundle_manifest.md"
            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--root",
                    str(root),
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
            self.assertEqual("ready_with_pending_external_evidence", report["overall_status"])
            file_by_id = {entry["id"]: entry for entry in report["files"]}
            self.assertIn("sha256", file_by_id["aaai_pdf"])
            self.assertIn("sha256", file_by_id["runbook"])
            checks = {check["id"]: check for check in report["checks"]}
            self.assertEqual("ready", checks["submission_bundle_external_evidence_boundary_current"]["status"])
            self.assertTrue(output_md.exists())

    def test_current_manifest_is_ready_with_pending_external_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_json = Path(tmp) / "submission_bundle_manifest.json"
            output_md = Path(tmp) / "submission_bundle_manifest.md"
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
            self.assertEqual("ready_with_pending_external_evidence", report["overall_status"])
            self.assertEqual(0, report["status_counts"]["fail"])
            file_ids = {entry["id"] for entry in report["files"] if entry.get("present")}
            self.assertIn("aaai_pdf", file_ids)
            self.assertIn("human_fidelity_summary", file_ids)
            self.assertIn("runbook", file_ids)


if __name__ == "__main__":
    unittest.main()
