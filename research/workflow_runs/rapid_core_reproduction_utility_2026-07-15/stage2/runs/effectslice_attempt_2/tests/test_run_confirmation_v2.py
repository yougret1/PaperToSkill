import json
import os
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch
from pathlib import Path


RUN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RUN_ROOT))
sys.path.insert(0, str(RUN_ROOT / "src"))

from build_confirmation_v2 import build_family  # noqa: E402
from run_confirmation_v2 import build_run_namespace, run_schedule  # noqa: E402
from effectslice.aci_runner import ModelTurnResult  # noqa: E402
import run_snap_mfse_effectslice  # noqa: E402


class RunConfirmationV2Test(unittest.TestCase):
    def test_namespace_preserves_registered_order_and_v2_inputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cases = root / "cases.json"
            family_path = root / "family.json"
            family = build_family(
                task_key="snap_mfse",
                case_registry_output=cases,
                family_output=family_path,
            )
            replicate = family["replicate_schedule"][0]

            args = build_run_namespace(
                family_path=family_path,
                family=family,
                replicate=replicate,
                output_root=root / "raw",
            )

        self.assertEqual(args.condition, replicate["condition_order"])
        self.assertEqual(args.case_block, "confirmation_v2")
        self.assertEqual(args.case_registry, cases.resolve())
        self.assertEqual(args.confirmation_family, family_path.resolve())
        self.assertEqual(args.harness_protocol_version, "effectslice-snap-mfse-aci.v3")
        self.assertEqual(args.max_attempts, 5)
        self.assertEqual(args.max_tokens, 8192)
        self.assertEqual(args.model_alias, "deepseek-v4-flash")

    def test_schedule_runs_missing_replicates_once_and_preserves_existing_outputs(self):
        calls = []
        lock = threading.Lock()

        def fake_runner(args):
            output = Path(args.output_dir)
            output.mkdir(parents=True, exist_ok=False)
            report = {
                "pair_id": args.pair_id,
                "condition_execution_order": args.condition,
            }
            (output / "run_report.json").write_text(
                json.dumps(report), encoding="utf-8"
            )
            with lock:
                calls.append(args.pair_id)
            return report

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cases = root / "cases.json"
            family_path = root / "family.json"
            build_family(
                task_key="snap_mfse",
                case_registry_output=cases,
                family_output=family_path,
            )
            output_root = root / "raw"
            first = run_schedule(
                family_paths=[family_path],
                output_root=output_root,
                max_workers=2,
                replicate_ids={"r001", "r002"},
                runner_by_task={"snap_mfse": fake_runner},
            )
            second = run_schedule(
                family_paths=[family_path],
                output_root=output_root,
                max_workers=2,
                replicate_ids={"r001", "r002"},
                runner_by_task={"snap_mfse": fake_runner},
            )

        self.assertEqual(first["counts"], {"completed": 2, "failed": 0, "preserved": 0})
        self.assertEqual(second["counts"], {"completed": 0, "failed": 0, "preserved": 2})
        self.assertEqual(len(calls), 2)

    def test_real_bundle_uses_registered_order_registry_and_final_only_scoring(self):
        edit = json.dumps(
            {
                "action": "edit",
                "path": "snap_core.py",
                "old_text": '    raise NotImplementedError("implement the paper-core reproduction task")',
                "new_text": "    return None",
            }
        )
        responses = [edit, '{"action":"test"}', '{"action":"submit"}'] * 3

        class FakeProvider:
            def __init__(self):
                self.responses = list(responses)

            def public_config(self):
                return {
                    "model_alias": "deepseek-v4-flash",
                    "temperature": 0,
                }

            def __call__(self, *, prompt, retry_lineage_id, turn_index):
                del prompt, retry_lineage_id, turn_index
                return ModelTurnResult(
                    status="success",
                    response_text=self.responses.pop(0),
                    attempts=1,
                    input_tokens=1,
                    output_tokens=1,
                    provider_model_id="offline-fake",
                    provider_response_id=f"fake-{len(self.responses):02d}",
                    provider_created=1784246400,
                )

        fake = FakeProvider()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cases = root / "cases.json"
            family_path = root / "family.json"
            family = build_family(
                task_key="snap_mfse",
                case_registry_output=cases,
                family_output=family_path,
            )
            replicate = next(
                row
                for row in family["replicate_schedule"]
                if row["condition_order"] != ["B", "F", "S"]
            )
            args = build_run_namespace(
                family_path=family_path,
                family=family,
                replicate=replicate,
                output_root=root / "raw",
            )
            with patch.object(
                run_snap_mfse_effectslice,
                "ProviderTransport",
                return_value=fake,
            ), patch.dict(
                os.environ,
                {
                    "EFFECTSLICE_DEEPSEEK_BASE_URL": "https://example.invalid",
                    "EFFECTSLICE_DEEPSEEK_API_KEY": "test-only-key",
                },
            ):
                report = run_snap_mfse_effectslice.run_bundle(args)
            manifest = json.loads(
                (Path(args.output_dir) / "pair_manifest.json").read_text(encoding="utf-8")
            )

        self.assertEqual(report["condition_execution_order"], replicate["condition_order"])
        self.assertEqual(manifest["case_registry_sha256"], family["case_registry_sha256"])
        for condition in ("B", "F", "S"):
            self.assertEqual(report["results"][condition]["private_score_count"], 1)
            self.assertFalse(report["results"][condition]["private_feedback_exposed"])


if __name__ == "__main__":
    unittest.main()
