import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_real_reuse_benchmark.py"
SPEC = ROOT / "benchmarks" / "real_reuse" / "real_reuse_v0.json"
sys.path.insert(0, str(ROOT / "scripts"))

from check_real_reuse_benchmark import build_report  # noqa: E402


class CheckRealReuseBenchmarkTest(unittest.TestCase):
    def test_current_real_reuse_spec_is_ready_to_implement(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_json = Path(tmp) / "spec_preflight.json"
            output_md = Path(tmp) / "spec_preflight.md"
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
            self.assertEqual("ready_to_implement", report["overall_status"])
            self.assertEqual(8, report["task_count"])
            self.assertEqual(0, report["status_counts"]["fail"])
            ready_ids = {check["id"] for check in report["checks"] if check["status"] == "ready"}
            self.assertIn("real_reuse_expected_task_ids", ready_ids)
            self.assertIn("real_reuse_no_abstract_or_full_excerpt_main", ready_ids)
            self.assertIn("real_reuse_full_excerpt_sanity_scope", ready_ids)
            self.assertIn("real_reuse_task_specs_materialized", ready_ids)
            self.assertIn("real_reuse_fixture_manifests_materialized", ready_ids)
            self.assertIn("real_reuse_fixture_candidates_materialized", ready_ids)
            self.assertIn("real_reuse_asset_locks_materialized", ready_ids)
            self.assertIn("real_reuse_prepared_assets_reflexion_materialized", ready_ids)
            self.assertIn("real_reuse_reflexion_runner_contract_ready", ready_ids)
            self.assertIn("real_reuse_aide_runner_contract_ready", ready_ids)
            self.assertIn("real_reuse_swe_agent_skill_contract_ready", ready_ids)
            self.assertIn("real_reuse_swe_agent_rubric_ready", ready_ids)
            self.assertIn("real_reuse_swe_agent_source_span_ready", ready_ids)
            self.assertIn("real_reuse_llm_ablation_linked_to_tasks", ready_ids)
            self.assertIn("snapatac2_code_url_declared", ready_ids)
            self.assertTrue(output_md.exists())

    def test_missing_task_fails_preflight(self):
        spec = json.loads(SPEC.read_text(encoding="utf-8"))
        spec["tasks"] = spec["tasks"][:-1]
        with tempfile.TemporaryDirectory() as tmp:
            spec_path = Path(tmp) / "real_reuse_v0.json"
            spec_path.write_text(json.dumps(spec), encoding="utf-8")

            report = build_report(Path(tmp), spec_path)
            self.assertEqual("fail", report["overall_status"])
            statuses = {check["id"]: check["status"] for check in report["checks"]}
            self.assertEqual("fail", statuses["real_reuse_main_task_count"])
            self.assertEqual("fail", statuses["real_reuse_expected_task_ids"])

    def test_abstract_condition_fails_main_preflight(self):
        spec = json.loads(SPEC.read_text(encoding="utf-8"))
        spec["main_conditions"] = ["summary", "papertoskill", "abstract"]
        with tempfile.TemporaryDirectory() as tmp:
            spec_path = Path(tmp) / "real_reuse_v0.json"
            spec_path.write_text(json.dumps(spec), encoding="utf-8")

            report = build_report(Path(tmp), spec_path)
            self.assertEqual("fail", report["overall_status"])
            statuses = {check["id"]: check["status"] for check in report["checks"]}
            self.assertEqual("fail", statuses["real_reuse_main_conditions"])
            self.assertEqual("fail", statuses["real_reuse_no_abstract_or_full_excerpt_main"])

    def test_invalid_candidate_status_fails_preflight(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            candidate_dir = root / "benchmarks" / "real_reuse" / "fixture_candidates"
            task_dir = root / "benchmarks" / "real_reuse" / "tasks"
            fixture_dir = root / "benchmarks" / "real_reuse" / "fixtures"
            spec_dir = root / "benchmarks" / "real_reuse"
            candidate_dir.mkdir(parents=True)
            task_dir.mkdir(parents=True)
            fixture_dir.mkdir(parents=True)
            spec_dir.mkdir(parents=True, exist_ok=True)
            (spec_dir / "real_reuse_v0.json").write_text(SPEC.read_text(encoding="utf-8"), encoding="utf-8")
            for source_dir, dest_dir in [
                (ROOT / "benchmarks" / "real_reuse" / "tasks", task_dir),
                (ROOT / "benchmarks" / "real_reuse" / "fixtures", fixture_dir),
                (ROOT / "benchmarks" / "real_reuse" / "fixture_candidates", candidate_dir),
            ]:
                for path in source_dir.glob("*.json"):
                    (dest_dir / path.name).write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
            candidate_path = candidate_dir / "AIDE-T1.json"
            candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
            candidate["status"] = "executed"
            candidate_path.write_text(json.dumps(candidate), encoding="utf-8")

            report = build_report(root, spec_dir / "real_reuse_v0.json")
            statuses = {check["id"]: check["status"] for check in report["checks"]}
            self.assertEqual("fail", report["overall_status"])
            self.assertEqual("fail", statuses["aide_t1_fixture_candidate_status"])

    def test_missing_asset_lock_fails_preflight(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for relative_dir in [
                "benchmarks/real_reuse/tasks",
                "benchmarks/real_reuse/fixtures",
                "benchmarks/real_reuse/fixture_candidates",
                "benchmarks/real_reuse/asset_locks",
            ]:
                (root / relative_dir).mkdir(parents=True)
            spec_dir = root / "benchmarks" / "real_reuse"
            spec_dir.mkdir(parents=True, exist_ok=True)
            (spec_dir / "real_reuse_v0.json").write_text(SPEC.read_text(encoding="utf-8"), encoding="utf-8")
            for source_dir, dest_dir in [
                (ROOT / "benchmarks" / "real_reuse" / "tasks", root / "benchmarks" / "real_reuse" / "tasks"),
                (ROOT / "benchmarks" / "real_reuse" / "fixtures", root / "benchmarks" / "real_reuse" / "fixtures"),
                (ROOT / "benchmarks" / "real_reuse" / "fixture_candidates", root / "benchmarks" / "real_reuse" / "fixture_candidates"),
                (ROOT / "benchmarks" / "real_reuse" / "asset_locks", root / "benchmarks" / "real_reuse" / "asset_locks"),
            ]:
                for path in source_dir.glob("*.json"):
                    if source_dir.name == "asset_locks" and path.name == "AIDE-T1.json":
                        continue
                    (dest_dir / path.name).write_text(path.read_text(encoding="utf-8"), encoding="utf-8")

            report = build_report(root, spec_dir / "real_reuse_v0.json")
            statuses = {check["id"]: check["status"] for check in report["checks"]}
            self.assertEqual("fail", report["overall_status"])
            self.assertEqual("fail", statuses["aide_t1_asset_lock_present"])
            self.assertEqual("fail", statuses["real_reuse_asset_locks_materialized"])

    def test_missing_reflexion_prepared_assets_fail_preflight(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for relative_dir in [
                "benchmarks/real_reuse/tasks",
                "benchmarks/real_reuse/fixtures",
                "benchmarks/real_reuse/fixture_candidates",
                "benchmarks/real_reuse/asset_locks",
            ]:
                (root / relative_dir).mkdir(parents=True)
            spec_dir = root / "benchmarks" / "real_reuse"
            spec_dir.mkdir(parents=True, exist_ok=True)
            (spec_dir / "real_reuse_v0.json").write_text(SPEC.read_text(encoding="utf-8"), encoding="utf-8")
            for source_dir, dest_dir in [
                (ROOT / "benchmarks" / "real_reuse" / "tasks", root / "benchmarks" / "real_reuse" / "tasks"),
                (ROOT / "benchmarks" / "real_reuse" / "fixtures", root / "benchmarks" / "real_reuse" / "fixtures"),
                (ROOT / "benchmarks" / "real_reuse" / "fixture_candidates", root / "benchmarks" / "real_reuse" / "fixture_candidates"),
                (ROOT / "benchmarks" / "real_reuse" / "asset_locks", root / "benchmarks" / "real_reuse" / "asset_locks"),
            ]:
                for path in source_dir.glob("*.json"):
                    (dest_dir / path.name).write_text(path.read_text(encoding="utf-8"), encoding="utf-8")

            report = build_report(root, spec_dir / "real_reuse_v0.json")
            statuses = {check["id"]: check["status"] for check in report["checks"]}
            self.assertEqual("fail", report["overall_status"])
            self.assertEqual("fail", statuses["ref_t1_prepared_asset_manifest_present"])
            self.assertEqual("fail", statuses["real_reuse_prepared_assets_reflexion_materialized"])


if __name__ == "__main__":
    unittest.main()
