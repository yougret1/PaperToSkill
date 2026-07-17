import json
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


RUN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RUN_ROOT))
sys.path.insert(0, str(RUN_ROOT / "src"))

from effectslice.aci_runner import DEFAULT_COMMON_SCAFFOLD, ModelTurnResult  # noqa: E402
from build_confirmation_v2 import build_family  # noqa: E402
from run_swe_effectslice import sha256_file, sha256_text, workspace_tree_digest  # noqa: E402
from run_toolformer_filter_effectslice import (  # noqa: E402
    NO_ARTIFACT_CONTEXT,
    build_pair_manifest,
    build_toolformer_context,
    evidence_boundary_for_block,
    load_confirmation_binding,
    load_slice_binding,
    normalize_condition_order,
    require_new_output_dir,
    run_condition,
)


CORRECT_EDIT = """
    arrays = [np.asarray(value, dtype=np.float64) for value in (
        logp_with_result, logp_call_only, logp_no_call
    )]
    if any(array.ndim != 2 or min(array.shape) < 1 for array in arrays):
        raise ValueError("inputs must be nonempty matrices")
    if any(array.shape != arrays[0].shape for array in arrays[1:]):
        raise ValueError("input shapes must match")
    if any(not np.isfinite(array).all() or np.any(array > 0) for array in arrays):
        raise ValueError("log probabilities must be finite and nonpositive")
    if isinstance(tau_filter, bool) or not isinstance(tau_filter, (int, float, np.integer, np.floating)):
        raise ValueError("invalid threshold")
    tau = float(tau_filter)
    if not np.isfinite(tau) or tau < 0:
        raise ValueError("invalid threshold")
    raw = np.maximum(0.0, 1.0 - 0.2 * np.arange(arrays[0].shape[1]))
    weights = raw / raw.sum()
    losses = [-(array * weights).sum(axis=1) for array in arrays]
    margins = np.minimum(losses[1], losses[2]) - losses[0]
    return margins >= tau, margins
"""


class SequenceTransport:
    def __init__(self, response_texts):
        self.response_texts = list(response_texts)
        self.calls = []

    def __call__(self, *, prompt, retry_lineage_id, turn_index):
        self.calls.append(
            {
                "prompt": prompt,
                "retry_lineage_id": retry_lineage_id,
                "turn_index": turn_index,
            }
        )
        return ModelTurnResult(
            status="success",
            response_text=self.response_texts.pop(0),
            attempts=1,
            input_tokens=100,
            output_tokens=20,
        )


class ToolformerFilterRunnerTest(unittest.TestCase):
    def setUp(self):
        self.workspace = RUN_ROOT / "task_workspaces" / "toolformer_filter_v1"
        self.card = RUN_ROOT / "artifacts" / "toolformer_filter" / "full_artifact.md"
        self.atom_map = (
            RUN_ROOT / "artifacts" / "toolformer_filter" / "source_atom_map.json"
        )
        self.registry = (
            RUN_ROOT / "artifacts" / "toolformer_filter" / "case_registry.json"
        )
        self.task_prompt = (
            RUN_ROOT / "artifacts" / "toolformer_filter" / "task_prompt.md"
        )
        self.scorer = (
            RUN_ROOT / "src" / "effectslice" / "toolformer_filter_scorer.py"
        )
        self.slice_registry = (
            RUN_ROOT
            / "artifacts"
            / "toolformer_filter"
            / "slices"
            / "slice_registry.json"
        )
        self.confirmation_family = (
            RUN_ROOT
            / "artifacts"
            / "toolformer_filter"
            / "confirmation_family.json"
        )

    def test_contexts_separate_no_artifact_full_and_slice(self):
        self.assertEqual(
            build_toolformer_context(
                "B", full_artifact_path=self.card, slice_path=None
            ),
            NO_ARTIFACT_CONTEXT,
        )
        expected = self.card.read_text(encoding="utf-8").strip()
        self.assertEqual(
            build_toolformer_context(
                "F", full_artifact_path=self.card, slice_path=None
            ),
            expected,
        )
        self.assertEqual(
            build_toolformer_context(
                "S", full_artifact_path=self.card, slice_path=self.card
            ),
            expected,
        )
        with self.assertRaises(ValueError):
            build_toolformer_context(
                "S", full_artifact_path=self.card, slice_path=None
            )

    def test_condition_order_is_preserved_while_comparison_set_is_canonical(self):
        execution_order, canonical = normalize_condition_order(["F", "S", "B", "F"])
        self.assertEqual(execution_order, ("F", "S", "B"))
        self.assertEqual(canonical, ("B", "F", "S"))

    def test_evidence_boundary_tracks_registered_case_block(self):
        self.assertEqual(
            evidence_boundary_for_block("development"),
            "development_only_not_confirmation",
        )
        self.assertEqual(
            evidence_boundary_for_block("confirmation"), "contaminated_development"
        )
        self.assertEqual(
            evidence_boundary_for_block("confirmation_v2"),
            "registered_final_only_confirmation",
        )
        with self.assertRaises(ValueError):
            evidence_boundary_for_block("unknown")

    def test_manifest_binds_all_scientific_inputs_without_credentials(self):
        contexts = {
            condition: build_toolformer_context(
                condition, full_artifact_path=self.card, slice_path=None
            )
            for condition in ("B", "F")
        }
        manifest = build_pair_manifest(
            pair_id="toolformer-filter:dev:deepseek:bf:001",
            seed_block_id="development:deepseek:001",
            model_family="DeepSeek-family",
            model_alias="deepseek-v4-flash",
            wire_api="openai_chat_completions",
            case_block="development",
            condition_contexts=contexts,
            task_prompt=self.task_prompt.read_text(encoding="utf-8"),
            full_artifact_path=self.card,
            atom_map_path=self.atom_map,
            case_registry_path=self.registry,
            scorer_path=self.scorer,
            workspace_state=workspace_tree_digest(self.workspace),
            max_actions=16,
            maximum_transport_attempts=5,
            harness_protocol_version="effectslice-toolformer-filter-aci.v2",
            provider_protocol_version="effectslice-deepseek-output-budget.v2",
            authorization_evidence="user-provided-deepseek-endpoint-2026-07-16",
        )

        self.assertEqual(
            manifest["schema_version"], "effectslice-toolformer-filter-pair.v2"
        )
        self.assertEqual(manifest["task_id"], "TOOLFORMER-FILTER")
        self.assertEqual(manifest["full_artifact_sha256"], sha256_file(self.card))
        self.assertEqual(manifest["atom_map_sha256"], sha256_file(self.atom_map))
        self.assertEqual(manifest["case_registry_sha256"], sha256_file(self.registry))
        self.assertEqual(manifest["scorer_sha256"], sha256_file(self.scorer))
        self.assertEqual(
            manifest["common_scaffold_sha256"],
            sha256_text(DEFAULT_COMMON_SCAFFOLD.strip()),
        )
        serialized = json.dumps(manifest).lower()
        self.assertNotIn("api_key", serialized)
        self.assertNotIn("authorization_header", serialized)
        self.assertNotIn("secret", serialized)

    def test_slice_binding_requires_registered_candidate_and_digest(self):
        slice_path = self.slice_registry.parent / "candidates" / "prefix_03.md"
        binding = load_slice_binding(
            slice_path=slice_path,
            registry_path=self.slice_registry,
            candidate_id="prefix_03",
        )

        self.assertEqual(binding["slice_candidate_id"], "prefix_03")
        self.assertEqual(binding["retained_atom_ids"], ["T01", "T02", "T03"])
        self.assertEqual(binding["slice_artifact_sha256"], sha256_file(slice_path))
        self.assertEqual(
            binding["slice_registry_sha256"], sha256_file(self.slice_registry)
        )
        with self.assertRaises(ValueError):
            load_slice_binding(
                slice_path=slice_path,
                registry_path=self.slice_registry,
                candidate_id="prefix_02",
            )

    def test_confirmation_binding_matches_locked_prefix_and_family(self):
        slice_path = self.slice_registry.parent / "candidates" / "prefix_01.md"
        slice_binding = load_slice_binding(
            slice_path=slice_path,
            registry_path=self.slice_registry,
            candidate_id="prefix_01",
        )
        confirmation = load_confirmation_binding(
            family_path=self.confirmation_family,
            slice_binding=slice_binding,
            conditions=("B", "F", "S"),
            case_block="confirmation",
        )

        self.assertEqual(confirmation["confirmation_case_count"], 59)
        self.assertEqual(
            confirmation["confirmation_family_sha256"],
            sha256_file(self.confirmation_family),
        )
        self.assertEqual(
            confirmation["confirmation_hypothesis_ids"],
            ["H_preserve_F", "H_benefit_over_B", "H_hard_constraints"],
        )
        with self.assertRaises(ValueError):
            load_confirmation_binding(
                family_path=self.confirmation_family,
                slice_binding={**slice_binding, "slice_candidate_id": "prefix_02"},
                conditions=("B", "F", "S"),
                case_block="confirmation",
            )

    def test_confirmation_binding_rejects_every_registered_file_digest_mutation(self):
        slice_path = self.slice_registry.parent / "candidates" / "prefix_01.md"
        slice_binding = load_slice_binding(
            slice_path=slice_path,
            registry_path=self.slice_registry,
            candidate_id="prefix_01",
        )
        discovery = RUN_ROOT / "derived" / "toolformer_filter_discovery_summary.json"
        registered = {
            "selected_artifact": slice_path,
            "discovery_summary": discovery,
            "slice_registry": self.slice_registry,
            "case_registry": self.registry,
            "source_map": self.atom_map,
            "task_prompt": self.task_prompt,
            "scorer": self.scorer,
        }

        for name, source in registered.items():
            with self.subTest(binding=name), tempfile.TemporaryDirectory() as tmp:
                temp_root = Path(tmp)
                family = json.loads(self.confirmation_family.read_text(encoding="utf-8"))
                for extra_name, extra_source in registered.items():
                    family[f"{extra_name}_path"] = extra_source.as_posix()
                    family[f"{extra_name}_sha256"] = sha256_file(extra_source)
                mutated = temp_root / source.name
                mutated.write_bytes(source.read_bytes() + b"\nmutated")
                family[f"{name}_path"] = mutated.as_posix()
                family_path = temp_root / "family.json"
                family_path.write_text(json.dumps(family), encoding="utf-8")

                with self.assertRaises(ValueError):
                    load_confirmation_binding(
                        family_path=family_path,
                        slice_binding=slice_binding,
                        conditions=("B", "F", "S"),
                        case_block="confirmation",
                    )

    def test_confirmation_v2_binding_and_final_only_run(self):
        slice_path = self.slice_registry.parent / "candidates" / "prefix_01.md"
        slice_binding = load_slice_binding(
            slice_path=slice_path,
            registry_path=self.slice_registry,
            candidate_id="prefix_01",
        )
        new_text = textwrap.indent(textwrap.dedent(CORRECT_EDIT).strip("\n"), "    ")
        transport = SequenceTransport(
            [
                json.dumps(
                    {
                        "action": "edit",
                        "path": "toolformer_filter.py",
                        "old_text": '    raise NotImplementedError("implement the paper-core reproduction task")',
                        "new_text": new_text,
                    }
                ),
                '{"action":"test"}',
                '{"action":"submit"}',
            ]
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            case_path = root / "case_registry_v2.json"
            family_path = root / "confirmation_v2_family.json"
            build_family(
                task_key="toolformer_filter",
                case_registry_output=case_path,
                family_output=family_path,
            )
            binding = load_confirmation_binding(
                family_path=family_path,
                slice_binding=slice_binding,
                conditions=("B", "F", "S"),
                case_block="confirmation_v2",
                workspace_state=workspace_tree_digest(self.workspace),
            )
            with self.assertRaisesRegex(ValueError, "workspace tree"):
                load_confirmation_binding(
                    family_path=family_path,
                    slice_binding=slice_binding,
                    conditions=("B", "F", "S"),
                    case_block="confirmation_v2",
                    workspace_state={"sha256": "0" * 64},
                )
            result, public = run_condition(
                condition="F",
                context=self.card.read_text(encoding="utf-8"),
                task_prompt=self.task_prompt.read_text(encoding="utf-8"),
                workspace=self.workspace,
                case_registry_path=case_path,
                case_block="confirmation_v2",
                output_dir=root / "run",
                transport=transport,
                retry_lineage_prefix="toolformer:v2:F",
                max_actions=16,
                private_score_policy="final_only",
            )

        self.assertEqual(binding["confirmation_case_count"], 64)
        self.assertGreaterEqual(len(binding["verified_family_inputs"]), 10)
        self.assertEqual(result.private_score_count, 1)
        self.assertFalse(result.private_feedback_exposed)
        self.assertEqual(public["private_score_count"], 1)
        self.assertFalse(public["private_feedback_exposed"])
        self.assertNotIn("passed_cases", transport.calls[-1]["prompt"])

    def test_scripted_edit_test_submit_scores_without_hidden_feedback(self):
        new_text = textwrap.indent(textwrap.dedent(CORRECT_EDIT).strip("\n"), "    ")
        transport = SequenceTransport(
            [
                json.dumps(
                    {
                        "action": "edit",
                        "path": "toolformer_filter.py",
                        "old_text": '    raise NotImplementedError("implement the paper-core reproduction task")',
                        "new_text": new_text,
                    }
                ),
                '{"action":"test"}',
                '{"action":"submit"}',
            ]
        )
        with tempfile.TemporaryDirectory(dir=RUN_ROOT) as tmp:
            result, public = run_condition(
                condition="F",
                context=self.card.read_text(encoding="utf-8"),
                task_prompt=self.task_prompt.read_text(encoding="utf-8"),
                workspace=self.workspace,
                case_registry_path=self.registry,
                case_block="development",
                output_dir=Path(tmp),
                transport=transport,
                retry_lineage_prefix="toolformer-filter:F",
                max_actions=16,
            )
            transcript = (Path(tmp) / "F" / "transcript.json").read_text(
                encoding="utf-8"
            )

        self.assertEqual(result.status, "scored")
        self.assertEqual(result.task_score, 1.0)
        self.assertTrue(result.success)
        self.assertEqual(public["actions_used"], 3)
        self.assertIn("Total action budget: 16", transport.calls[0]["prompt"])
        self.assertNotIn("seed", transcript.lower())
        self.assertNotIn("case_scores", transcript)
        self.assertNotIn(str(self.registry), transcript)

    def test_output_directory_is_reserved_once(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fresh = root / "fresh-run"
            require_new_output_dir(fresh)
            self.assertTrue(fresh.is_dir())

            with self.assertRaisesRegex(ValueError, "already exists"):
                require_new_output_dir(fresh)


if __name__ == "__main__":
    unittest.main()
