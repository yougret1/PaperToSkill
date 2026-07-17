import json
import sys
import unittest
from pathlib import Path


RUN_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = RUN_ROOT.parents[5]
sys.path.insert(0, str(RUN_ROOT))

from run_aide_effectslice import (  # noqa: E402
    build_pair_manifest,
    build_prompt,
    sha256_text,
)


class AideEffectSlicePromptTest(unittest.TestCase):
    def test_b_and_f_share_exact_scaffold_outside_context(self):
        b_prompt, b_context = build_prompt(PROJECT_ROOT, "B")
        f_prompt, f_context = build_prompt(PROJECT_ROOT, "F")

        b_prefix, b_suffix = b_prompt.split(b_context)
        f_prefix, f_suffix = f_prompt.split(f_context)
        self.assertEqual(b_prefix, f_prefix)
        self.assertEqual(b_suffix, f_suffix)
        self.assertIn("No paper-derived procedural context", b_context)
        self.assertIn("AIDE: AI-Driven Exploration", f_context)

    def test_f_and_s_share_scaffold_and_s_uses_generated_slice(self):
        slice_path = RUN_ROOT / "artifacts" / "aide_t2" / "slice_v0.md"
        f_prompt, f_context = build_prompt(PROJECT_ROOT, "F")
        s_prompt, s_context = build_prompt(PROJECT_ROOT, "S", slice_path)

        f_prefix, f_suffix = f_prompt.split(f_context)
        s_prefix, s_suffix = s_prompt.split(s_context)
        self.assertEqual(f_prefix, s_prefix)
        self.assertEqual(f_suffix, s_suffix)
        self.assertEqual(s_context, slice_path.read_text(encoding="utf-8").strip())
        self.assertLess(len(s_context), len(f_context))

    def test_pair_manifest_binds_prompts_without_credentials(self):
        b_prompt, b_context = build_prompt(PROJECT_ROOT, "B")
        f_prompt, f_context = build_prompt(PROJECT_ROOT, "F")
        manifest = build_pair_manifest(
            pair_id="aide-t2:dev:0001",
            case_id="spaceship-titanic:split:20260703",
            seed_block_id="development:001",
            model_alias="gpt-5.6",
            prompts={"B": b_prompt, "F": f_prompt},
            contexts={"B": b_context, "F": f_context},
            artifact_digest="a" * 64,
            authorization_evidence="user message confirming trusted endpoint",
            comparison_role="eligibility",
        )
        serialized = json.dumps(manifest, sort_keys=True)

        self.assertEqual(manifest["conditions"]["B"]["prompt_sha256"], sha256_text(b_prompt))
        self.assertEqual(manifest["conditions"]["F"]["context_sha256"], sha256_text(f_context))
        self.assertNotIn("api_key", serialized.lower())
        self.assertNotIn("authorization_header", serialized.lower())
        self.assertEqual(manifest["evidence_boundary"], "development_only_not_confirmation")
        self.assertEqual(manifest["comparison_role"], "eligibility")

    def test_rejects_condition_pair_with_wrong_comparison_role(self):
        b_prompt, b_context = build_prompt(PROJECT_ROOT, "B")
        slice_path = RUN_ROOT / "artifacts" / "aide_t2" / "slice_v2.md"
        s_prompt, s_context = build_prompt(PROJECT_ROOT, "S", slice_path)

        with self.assertRaisesRegex(ValueError, "comparison_role"):
            build_pair_manifest(
                pair_id="aide-t2:dev:neighbor:0001",
                case_id="spaceship-titanic:split:20260703",
                seed_block_id="development:001",
                model_alias="gpt-5.6",
                prompts={"B": b_prompt, "S": s_prompt},
                contexts={"B": b_context, "S": s_context},
                artifact_digest="a" * 64,
                authorization_evidence="user message confirming trusted endpoint",
                comparison_role="preservation",
            )

    def test_accepts_explicit_development_triage_bundle(self):
        slice_path = RUN_ROOT / "artifacts" / "aide_t2" / "slice_v2.md"
        prompts = {}
        contexts = {}
        for condition in ("B", "F", "S"):
            prompt, context = build_prompt(PROJECT_ROOT, condition, slice_path)
            prompts[condition] = prompt
            contexts[condition] = context

        manifest = build_pair_manifest(
            pair_id="aide-t2:dev:triage:0001",
            case_id="spaceship-titanic:split:20260703",
            seed_block_id="development:002",
            model_alias="gpt-5.6",
            prompts=prompts,
            contexts=contexts,
            artifact_digest="a" * 64,
            authorization_evidence="user message confirming trusted endpoint",
            comparison_role="development_triage",
        )

        self.assertEqual(tuple(manifest["conditions"]), ("B", "F", "S"))
        self.assertEqual(manifest["comparison_role"], "development_triage")


if __name__ == "__main__":
    unittest.main()
