import gzip
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_real_reuse_snapatac2_artifact_followup.py"


class BuildRealReuseSnapATAC2ArtifactFollowupTest(unittest.TestCase):
    def test_cli_reports_execution_gap_for_plan_only_snap_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "root"
            make_snap_fixture(root, "SNAP-T1", "chr1\t1\t2\tcell_a\t1\t+\n")
            make_snap_fixture(root, "SNAP-T2", "chr1\t1\t2\tcell_a\t1\n")
            run_dir = root / "results" / "real_reuse" / "runs"
            invalid_candidate = run_dir / "SNAP-T1" / "summary" / "unit" / "candidate_output.json"
            plan_candidate = run_dir / "SNAP-T1" / "papertoskill" / "unit" / "candidate_output.json"
            invalid_candidate.parent.mkdir(parents=True)
            plan_candidate.parent.mkdir(parents=True)
            invalid_candidate.write_text('{"cmd":"probe"}{"completed":false}\n', encoding="utf-8")
            plan_candidate.write_text(
                json.dumps(
                    {
                        "completed": False,
                        "method_steps": ["Use SnapATAC2 spectral embedding"],
                        "embedding_artifacts": [{"status": "planned"}],
                        "runtime_seconds": None,
                        "peak_memory_mb": None,
                    }
                ),
                encoding="utf-8",
            )
            raw_rows = root / "results" / "real_reuse" / "raw_rows.jsonl"
            raw_rows.parent.mkdir(parents=True, exist_ok=True)
            raw_rows.write_text(
                "\n".join(
                    [
                        raw_row("SNAP-T1", "summary", "unit", 0.0, "Extra data", invalid_candidate, root),
                        raw_row(
                            "SNAP-T1",
                            "papertoskill",
                            "unit",
                            0.5,
                            "missing_required_artifacts_or_metrics",
                            plan_candidate,
                            root,
                        ),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            selection = root / "results" / "real_reuse" / "main_run_selection.json"
            selection.write_text(
                json.dumps(
                    {
                        "rows": [
                            {"task_id": "SNAP-T1", "condition": "summary", "run_id": "unit"},
                            {"task_id": "SNAP-T1", "condition": "papertoskill", "run_id": "unit"},
                        ]
                    }
                ),
                encoding="utf-8",
            )
            output_json = root / "results" / "real_reuse" / "snapatac2_artifact_followup.json"

            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--root",
                    str(root),
                    "--raw-rows",
                    str(raw_rows),
                    "--row-selection",
                    str(selection),
                    "--output-json",
                    str(output_json),
                    "--output-md",
                    str(root / "results" / "real_reuse" / "snapatac2_artifact_followup.md"),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            report = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertEqual("pre_registered_followup_needed", report["overall_status"])
            rows = {(row["task_id"], row["condition"]): row for row in report["rows"]}
            self.assertEqual("invalid_json", rows[("SNAP-T1", "summary")]["candidate_probe"]["status"])
            self.assertTrue(rows[("SNAP-T1", "summary")]["candidate_probe"]["starts_with_command_probe"])
            self.assertTrue(rows[("SNAP-T1", "papertoskill")]["candidate_probe"]["execution_gap"])
            self.assertTrue(report["followup_contract"]["main_rows_unchanged"])
            fixture_statuses = {probe["task_id"]: probe["status"] for probe in report["environment"]["fixture_probes"]}
            self.assertEqual("readable", fixture_statuses["SNAP-T1"])
            self.assertEqual("readable", fixture_statuses["SNAP-T2"])


def make_snap_fixture(root: Path, task_id: str, line: str) -> None:
    asset_dir = root / "benchmarks" / "real_reuse" / "assets" / task_id
    asset_dir.mkdir(parents=True)
    fragment = asset_dir / "miniature_fragment.tsv.gz"
    with gzip.open(fragment, "wt", encoding="utf-8") as handle:
        handle.write(line)
    (asset_dir / "asset_manifest.json").write_text(
        json.dumps({"files": [{"slot": "miniature_fragment", "path": fragment.as_posix()}]}),
        encoding="utf-8",
    )


def raw_row(task_id: str, condition: str, run_id: str, score: float, failure: str, output: Path, root: Path) -> str:
    return json.dumps(
        {
            "run_id": run_id,
            "task_id": task_id,
            "condition": condition,
            "status": "scored",
            "task_score": score,
            "success": False,
            "failure_reason": failure,
            "output_path": output.relative_to(root).as_posix(),
        }
    )


if __name__ == "__main__":
    unittest.main()
