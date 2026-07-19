import hashlib
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


RUN_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = RUN_ROOT.parents[5]
sys.path.insert(0, str(RUN_ROOT))
sys.path.insert(0, str(RUN_ROOT / "src"))

from effectslice.aci_runner import DEFAULT_COMMON_SCAFFOLD, ModelTurnResult  # noqa: E402
from run_swe_effectslice import (  # noqa: E402
    NO_SKILL_CONTEXT,
    ProviderTransport,
    RunnerInputError,
    build_condition_context,
    build_pair_manifest,
    sha256_file,
    sha256_text,
    workspace_tree_digest,
)


class FakeRequester:
    def __init__(self, outcomes):
        self.outcomes = list(outcomes)
        self.calls = []

    def __call__(self, url, api_key, **kwargs):
        self.calls.append({"url": url, "api_key": api_key, **kwargs})
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


class SWEffectSliceRunnerTest(unittest.TestCase):
    def setUp(self):
        self.full_skill = PROJECT_ROOT / "generated_skills" / "real_reuse" / "swe_agent" / "SKILL.md"
        self.slice_path = RUN_ROOT / "artifacts" / "swe_t2" / "slice_v0.md"
        self.atom_map = RUN_ROOT / "artifacts" / "swe_t2" / "source_atom_map.json"
        self.asset_manifest = PROJECT_ROOT / "benchmarks" / "real_reuse" / "assets" / "SWE-T2" / "asset_manifest.json"
        self.task_prompt = PROJECT_ROOT / "benchmarks" / "real_reuse" / "assets" / "SWE-T2" / "task_prompt.md"
        self.scorer = PROJECT_ROOT / "scripts" / "score_real_reuse_swe.py"
        self.test_patch = PROJECT_ROOT / "benchmarks" / "real_reuse" / "assets" / "SWE-T2" / "scorer_only" / "test.patch"

    def test_builds_b_f_s_contexts_without_changing_common_scaffold(self):
        contexts = {
            condition: build_condition_context(
                condition,
                full_skill_path=self.full_skill,
                slice_path=self.slice_path,
            )
            for condition in ("B", "F", "S")
        }

        self.assertEqual(contexts["B"], NO_SKILL_CONTEXT)
        self.assertEqual(contexts["F"], self.full_skill.read_text(encoding="utf-8").strip())
        self.assertEqual(contexts["S"], self.slice_path.read_text(encoding="utf-8").strip())
        self.assertNotEqual(sha256_text(contexts["B"]), sha256_text(contexts["F"]))
        self.assertEqual(sha256_text(DEFAULT_COMMON_SCAFFOLD.strip()), sha256_text(DEFAULT_COMMON_SCAFFOLD.strip()))
        with self.assertRaises(RunnerInputError):
            build_condition_context("X", full_skill_path=self.full_skill, slice_path=self.slice_path)

    def test_pair_manifest_binds_inputs_and_never_persists_credentials(self):
        contexts = {
            condition: build_condition_context(
                condition,
                full_skill_path=self.full_skill,
                slice_path=self.slice_path,
            )
            for condition in ("B", "F", "S")
        }
        secret = "secret-token-must-not-persist"

        manifest = build_pair_manifest(
            pair_id="swe-t2:dev:triage:001",
            case_id="astropy__astropy-12907",
            seed_block_id="development:aci:001",
            model_family="GPT-family",
            model_alias="gpt-5.6",
            wire_api="openai_responses",
            source_commit="d16bfe05a744909de4b27f5875fe0d4ed41ce607",
            condition_contexts=contexts,
            common_scaffold=DEFAULT_COMMON_SCAFFOLD,
            task_prompt=self.task_prompt.read_text(encoding="utf-8").strip(),
            full_skill_path=self.full_skill,
            atom_map_path=self.atom_map,
            scorer_path=self.scorer,
            test_patch_path=self.test_patch,
            max_actions=8,
            maximum_transport_attempts=5,
            authorization_evidence="user-confirmed trusted endpoint",
        )

        self.assertEqual(manifest["comparison_role"], "development_triage")
        self.assertEqual(manifest["source_commit"], "d16bfe05a744909de4b27f5875fe0d4ed41ce607")
        self.assertEqual(manifest["common_scaffold_sha256"], sha256_text(DEFAULT_COMMON_SCAFFOLD.strip()))
        self.assertEqual(manifest["full_artifact_sha256"], sha256_file(self.full_skill))
        self.assertEqual(manifest["atom_map_sha256"], sha256_file(self.atom_map))
        self.assertEqual(manifest["scorer_sha256"], sha256_file(self.scorer))
        self.assertEqual(manifest["test_patch_sha256"], sha256_file(self.test_patch))
        self.assertEqual(manifest["harness_protocol_version"], "effectslice-swe-aci.v2")
        self.assertTrue(manifest["action_budget_visible_to_model"])
        self.assertEqual(set(manifest["conditions"]), {"B", "F", "S"})
        self.assertTrue(all(item["max_actions"] == 8 for item in manifest["conditions"].values()))
        serialized = json.dumps(manifest, sort_keys=True)
        self.assertNotIn(secret, serialized)
        self.assertNotIn("api_key", serialized.lower())
        self.assertNotIn("authorization_header", serialized.lower())

    def test_pair_manifest_rejects_role_mismatches_and_invalid_digests(self):
        context = build_condition_context(
            "F",
            full_skill_path=self.full_skill,
            slice_path=self.slice_path,
        )
        kwargs = dict(
            pair_id="pair",
            case_id="case",
            seed_block_id="development:001",
            model_family="GPT-family",
            model_alias="gpt-5.6",
            wire_api="openai_responses",
            source_commit="bad",
            condition_contexts={"F": context},
            common_scaffold=DEFAULT_COMMON_SCAFFOLD,
            task_prompt="task",
            full_skill_path=self.full_skill,
            atom_map_path=self.atom_map,
            scorer_path=self.scorer,
            test_patch_path=self.test_patch,
            max_actions=8,
            maximum_transport_attempts=5,
            authorization_evidence="trusted",
        )
        with self.assertRaises(RunnerInputError):
            build_pair_manifest(**kwargs)
        kwargs["source_commit"] = "d" * 40
        with self.assertRaises(RunnerInputError):
            build_pair_manifest(**kwargs)

    def test_workspace_tree_digest_matches_scorer_copy_exclusions(self):
        source = RUN_ROOT / "tests" / "fixtures" / "aci_workspace" / "locked_source"
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp) / "locked_source"
            shutil.copytree(source, workspace)
            git_config = workspace / ".git" / "config"
            git_config.parent.mkdir(exist_ok=True)
            git_config.write_text("[core]\n\trepositoryformatversion = 0\n", encoding="utf-8")
            included = [
                workspace / "alpha.txt",
                workspace / "binary.dat",
                workspace / "large.txt",
                workspace / "pkg" / "main.py",
                workspace / "pkg" / "unchanged.py",
            ]

            first = workspace_tree_digest(workspace)
            second = workspace_tree_digest(workspace)

            self.assertEqual(first, second)
            self.assertEqual(first["file_count"], 5)
            self.assertEqual(
                first["total_bytes"], sum(path.stat().st_size for path in included)
            )
            self.assertEqual(len(first["sha256"]), 64)
            self.assertNotEqual(first["sha256"], sha256_file(git_config))

    def test_gpt_responses_transport_normalizes_usage_and_public_config(self):
        requester = FakeRequester(
            [
                (
                    200,
                    {
                        "output_text": '{"action":"submit"}',
                        "usage": {"input_tokens": 12, "output_tokens": 3},
                    },
                )
            ]
        )
        transport = ProviderTransport(
            base_url="https://example.invalid/v1",
            api_key="private-gpt-key",
            model_alias="gpt-5.6",
            wire_api="openai_responses",
            max_tokens=2048,
            timeout_seconds=30,
            max_attempts=5,
            retry_delay_seconds=0,
            request_function=requester,
        )

        result = transport(prompt="prompt", retry_lineage_id="pair:F:turn-001", turn_index=1)

        self.assertEqual(result, ModelTurnResult("success", '{"action":"submit"}', 1, 12, 3))
        self.assertTrue(requester.calls[0]["url"].endswith("/responses"))
        self.assertEqual(requester.calls[0]["body"]["max_output_tokens"], 2048)
        public = json.dumps(transport.public_config(), sort_keys=True)
        self.assertNotIn("private-gpt-key", public)
        self.assertNotIn("api_key", public.lower())

    def test_deepseek_transport_retries_503_and_empty_content_then_succeeds(self):
        requester = FakeRequester(
            [
                RuntimeError('{"http_error":503}'),
                (
                    200,
                    {
                        "choices": [{"message": {"content": ""}}],
                        "usage": {"prompt_tokens": 7, "completion_tokens": 64},
                    },
                ),
                (
                    200,
                    {
                        "choices": [{"message": {"content": '{"action":"test"}'}}],
                        "usage": {"prompt_tokens": 20, "completion_tokens": 4},
                        "model": "deepseek-v3.2-exp-20260717",
                        "id": "response-test-001",
                        "created": 1784246400,
                    },
                ),
            ]
        )
        transport = ProviderTransport(
            base_url="https://api.deepseek.com",
            api_key="private-deepseek-key",
            model_alias="deepseek-v4-flash",
            wire_api="openai_chat_completions",
            max_tokens=4096,
            timeout_seconds=60,
            max_attempts=5,
            retry_delay_seconds=0,
            request_function=requester,
        )

        result = transport(prompt="prompt", retry_lineage_id="pair:F:turn-001", turn_index=1)

        self.assertEqual(
            result,
            ModelTurnResult(
                "success",
                '{"action":"test"}',
                3,
                27,
                68,
                provider_model_id="deepseek-v3.2-exp-20260717",
                provider_response_id="response-test-001",
                provider_created=1784246400,
            ),
        )
        self.assertEqual(result.provider_model_id, "deepseek-v3.2-exp-20260717")
        self.assertEqual(result.provider_response_id, "response-test-001")
        self.assertEqual(result.provider_created, 1784246400)
        self.assertEqual(len(requester.calls), 3)
        body = requester.calls[-1]["body"]
        self.assertEqual(body["model"], "deepseek-v4-flash")
        self.assertEqual(body["temperature"], 0)
        self.assertEqual(body["max_tokens"], 4096)
        self.assertEqual(transport.public_config()["temperature"], 0)
        self.assertTrue(requester.calls[-1]["url"].endswith("/chat/completions"))

    def test_transport_does_not_retry_deterministic_401(self):
        requester = FakeRequester([RuntimeError('{"http_error":401}')])
        transport = ProviderTransport(
            base_url="https://example.invalid/v1",
            api_key="private-key",
            model_alias="gpt-5.6",
            wire_api="openai_responses",
            max_tokens=1024,
            timeout_seconds=30,
            max_attempts=5,
            retry_delay_seconds=0,
            request_function=requester,
        )

        result = transport(prompt="prompt", retry_lineage_id="pair:F:turn-001", turn_index=1)

        self.assertEqual(result.status, "error")
        self.assertEqual(result.attempts, 1)
        self.assertEqual(result.error_message, "deterministic_provider_error")
        self.assertEqual(len(requester.calls), 1)


if __name__ == "__main__":
    unittest.main()
