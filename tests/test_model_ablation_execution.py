import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "run_model_ablation_prompts.py"
EVALUATOR = ROOT / "scripts" / "evaluate_model_ablation_responses.py"
sys.path.insert(0, str(ROOT / "scripts"))

import run_model_ablation_prompts as runner_module  # noqa: E402
from run_model_ablation_prompts import (  # noqa: E402
    build_wire_request,
    model_ids_from_response,
    select_model_alias,
    wire_endpoint,
)


class ModelAblationExecutionTest(unittest.TestCase):
    def test_model_ids_accepts_object_and_string_model_lists(self):
        self.assertEqual(
            ["claude-opus-4-8", "gpt-5"],
            model_ids_from_response(
                {"models": ["gpt-5", {"id": "claude-opus-4-8"}]}
            ),
        )

    def test_gpt_slot_falls_back_to_available_gpt_family_model(self):
        alias, reason = select_model_alias(
            {"id": "gpt_5_5_or_gpt_family", "model_alias": "gpt-5.5"},
            ["claude-opus-4-8", "gpt-5", "gpt-4.1"],
        )
        self.assertEqual("gpt-5", alias)
        self.assertEqual("fallback_from_gpt-5.5", reason)

    def test_alias_candidates_select_available_claude_variant(self):
        alias, reason = select_model_alias(
            {
                "id": "claude_opus_4_8",
                "model_alias": "claude-opus-4-8",
                "model_aliases": ["claude-opus-4-8", "claude-opus-4.8", "claude-opus-4-7"],
            },
            ["claude-opus-4-7"],
        )
        self.assertEqual("claude-opus-4-7", alias)
        self.assertEqual("exact", reason)

    def test_gpt_slot_prefers_gpt_5_4_when_5_5_missing(self):
        alias, reason = select_model_alias(
            {
                "id": "gpt_5_5_or_gpt_family",
                "model_alias": "gpt-5.5",
                "model_aliases": ["gpt-5.5", "gpt-5.4"],
            },
            ["gpt-5.4", "gpt-5"],
        )
        self.assertEqual("gpt-5.4", alias)
        self.assertEqual("exact", reason)

    def test_wire_endpoint_matches_local_api_docs(self):
        self.assertEqual(
            "https://coderxiaoc.com/v1/messages",
            wire_endpoint("https://coderxiaoc.com", "anthropic_messages"),
        )
        self.assertEqual(
            "https://coderxiaoc.com/v1/responses",
            wire_endpoint("https://coderxiaoc.com/v1", "openai_responses"),
        )
        self.assertEqual(
            "https://api.deepseek.com/chat/completions",
            wire_endpoint("https://api.deepseek.com", "openai_chat_completions"),
        )

    def test_builds_gpt_responses_request_shape(self):
        body, headers = build_wire_request(
            wire_api="openai_responses",
            model="gpt-5.5",
            prompt_text="prompt",
            max_tokens=32,
            anthropic_version="2023-06-01",
        )

        self.assertEqual({"model", "input", "max_output_tokens"}, set(body))
        self.assertEqual("gpt-5.5", body["model"])
        self.assertIn("prompt", body["input"])
        self.assertEqual(32, body["max_output_tokens"])
        self.assertEqual({}, headers)

    def test_builds_claude_messages_request_shape(self):
        body, headers = build_wire_request(
            wire_api="anthropic_messages",
            model="claude-opus-4-8",
            prompt_text="prompt",
            max_tokens=32,
            anthropic_version="2023-06-01",
        )

        self.assertEqual("claude-opus-4-8", body["model"])
        self.assertEqual("prompt", body["messages"][0]["content"])
        self.assertEqual(32, body["max_tokens"])
        self.assertNotIn("max_output_tokens", body)
        self.assertEqual({"anthropic-version": "2023-06-01"}, headers)

    def test_builds_deepseek_chat_completions_request_shape(self):
        body, headers = build_wire_request(
            wire_api="openai_chat_completions",
            model="deepseek-v4-flash",
            prompt_text="prompt",
            max_tokens=32,
            anthropic_version="2023-06-01",
        )

        self.assertEqual("deepseek-v4-flash", body["model"])
        self.assertEqual("prompt", body["messages"][1]["content"])
        self.assertEqual(0, body["temperature"])
        self.assertEqual(32, body["max_tokens"])
        self.assertEqual({}, headers)

    def test_evaluator_scores_saved_response_and_marks_missing_pending(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            response = tmp_path / "response.md"
            response.write_text(
                """Sufficient context.

Files and commands:
- Use the local tool.

Step-by-step plan:
1. Run the plan.

Source-backed steps:
- Keep the method.

Inferred adaptations:
- Mock external APIs.

Validation checks and stop conditions:
- Stop on failed tests.

Failure branch:
- Log the failed branch.
""",
                encoding="utf-8",
            )
            index = tmp_path / "index.json"
            index.write_text(
                json.dumps(
                    {
                        "task": "test_task",
                        "prompts": [
                            {
                                "model_id": "m1",
                                "model_alias": "model-one",
                                "case_id": "case_one",
                                "expected_response_path": str(response),
                            },
                            {
                                "model_id": "m2",
                                "model_alias": "model-two",
                                "case_id": "case_two",
                                "expected_response_path": str(tmp_path / "missing.md"),
                            },
                        ],
                    }
                ),
                encoding="utf-8",
            )
            output_json = tmp_path / "eval.json"
            output_md = tmp_path / "eval.md"

            subprocess.run(
                [
                    sys.executable,
                    str(EVALUATOR),
                    "--index",
                    str(index),
                    "--output-json",
                    str(output_json),
                    "--output-md",
                    str(output_md),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            report = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertEqual(1, report["summary"]["scored_rows"])
            self.assertEqual(1, report["summary"]["pending_rows"])
            self.assertEqual(1.0, report["results"][0]["normalized_score"])
            self.assertEqual("pending", report["results"][1]["status"])

    def test_runner_skips_missing_environment_without_network(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            prompt = tmp_path / "prompt.md"
            prompt.write_text("Prompt", encoding="utf-8")
            task = tmp_path / "task.json"
            task.write_text(
                json.dumps(
                    {
                        "id": "test_task",
                        "model_slots": [
                            {
                                "id": "claude_opus_4_8",
                                "model_alias": "claude-opus-4-8",
                                "auth_env": "MISSING_KEY",
                                "base_url_env": "MISSING_BASE",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            index = tmp_path / "index.json"
            index.write_text(
                json.dumps(
                    {
                        "task": "test_task",
                        "prompts": [
                            {
                                "model_id": "claude_opus_4_8",
                                "case_id": "case_one",
                                "prompt_path": str(prompt),
                                "expected_response_path": str(tmp_path / "response.md"),
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            output_json = tmp_path / "run.json"
            output_md = tmp_path / "run.md"

            subprocess.run(
                [
                    sys.executable,
                    str(RUNNER),
                    "--task",
                    str(task),
                    "--index",
                    str(index),
                    "--output-json",
                    str(output_json),
                    "--output-md",
                    str(output_md),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            report = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertEqual("pending", report["overall_status"])
            self.assertEqual("skipped", report["results"][0]["status"])

    def test_runner_keeps_catalogs_for_same_base_url_different_auth_envs(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            prompt = tmp_path / "prompt.md"
            prompt.write_text("Prompt", encoding="utf-8")
            task = tmp_path / "task.json"
            task.write_text(
                json.dumps(
                    {
                        "id": "test_task",
                        "model_slots": [
                            {
                                "id": "claude_opus_4_8",
                                "model_alias": "claude-opus-4-8",
                                "auth_env": "TEST_CLAUDE_KEY",
                                "base_url_env": "TEST_SHARED_BASE",
                            },
                            {
                                "id": "gpt_5_5_or_gpt_family",
                                "model_alias": "gpt-5.5",
                                "model_aliases": ["gpt-5.5", "gpt-5.4"],
                                "auth_env": "TEST_GPT_KEY",
                                "base_url_env": "TEST_SHARED_BASE",
                            },
                        ],
                    }
                ),
                encoding="utf-8",
            )
            index = tmp_path / "index.json"
            index.write_text(
                json.dumps(
                    {
                        "task": "test_task",
                        "prompts": [
                            {
                                "model_id": "claude_opus_4_8",
                                "case_id": "case_one",
                                "prompt_path": str(prompt),
                                "expected_response_path": str(tmp_path / "claude.md"),
                            },
                            {
                                "model_id": "gpt_5_5_or_gpt_family",
                                "case_id": "case_one",
                                "prompt_path": str(prompt),
                                "expected_response_path": str(tmp_path / "gpt.md"),
                            },
                        ],
                    }
                ),
                encoding="utf-8",
            )

            original_request_json = runner_module.request_json
            original_env = {
                "TEST_SHARED_BASE": os.environ.get("TEST_SHARED_BASE"),
                "TEST_CLAUDE_KEY": os.environ.get("TEST_CLAUDE_KEY"),
                "TEST_GPT_KEY": os.environ.get("TEST_GPT_KEY"),
            }

            def fake_request_json(url, api_key, method="GET", body=None, **kwargs):
                if url.endswith("/models"):
                    if api_key == "claude-key":
                        return 200, {"data": [{"id": "claude-opus-4-8"}]}
                    if api_key == "gpt-key":
                        return 200, {"data": [{"id": "gpt-5.5"}]}
                raise RuntimeError("simulated chat failure")

            try:
                os.environ["TEST_SHARED_BASE"] = "https://example.test/v1"
                os.environ["TEST_CLAUDE_KEY"] = "claude-key"
                os.environ["TEST_GPT_KEY"] = "gpt-key"
                runner_module.request_json = fake_request_json
                report = runner_module.run(
                    SimpleNamespace(
                        task=task,
                        index=index,
                        model_id=None,
                        base_url=None,
                        api_key=None,
                        max_tokens=20,
                        timeout_seconds=1,
                        anthropic_version="2023-06-01",
                        include_placeholder_models=False,
                    )
                )
            finally:
                runner_module.request_json = original_request_json
                for key, value in original_env.items():
                    if value is None:
                        os.environ.pop(key, None)
                    else:
                        os.environ[key] = value

            catalogs = {(item["base_url"], item["auth_env"], item["wire_api"]): item for item in report["model_catalogs"]}
            self.assertIn(("https://example.test/v1", "TEST_CLAUDE_KEY", "openai_chat_completions"), catalogs)
            self.assertIn(("https://example.test/v1", "TEST_GPT_KEY", "openai_chat_completions"), catalogs)
            self.assertEqual(
                ["claude-opus-4-8"],
                catalogs[("https://example.test/v1", "TEST_CLAUDE_KEY", "openai_chat_completions")]["model_ids"],
            )
            self.assertEqual(
                ["gpt-5.5"],
                catalogs[("https://example.test/v1", "TEST_GPT_KEY", "openai_chat_completions")]["model_ids"],
            )

    def test_runner_retries_next_alias_when_chat_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            prompt = tmp_path / "prompt.md"
            prompt.write_text("Prompt", encoding="utf-8")
            response_path = tmp_path / "response.md"
            task = tmp_path / "task.json"
            task.write_text(
                json.dumps(
                    {
                        "id": "test_task",
                        "model_slots": [
                            {
                                "id": "claude_opus_4_8",
                                "model_alias": "claude-opus-4-8",
                                "model_aliases": ["claude-opus-4-8", "claude-opus-4-7"],
                                "auth_env": "TEST_CLAUDE_KEY",
                                "base_url_env": "TEST_SHARED_BASE",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            index = tmp_path / "index.json"
            index.write_text(
                json.dumps(
                    {
                        "task": "test_task",
                        "prompts": [
                            {
                                "model_id": "claude_opus_4_8",
                                "case_id": "case_one",
                                "prompt_path": str(prompt),
                                "expected_response_path": str(response_path),
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            original_request_json = runner_module.request_json
            original_env = {
                "TEST_SHARED_BASE": os.environ.get("TEST_SHARED_BASE"),
                "TEST_CLAUDE_KEY": os.environ.get("TEST_CLAUDE_KEY"),
            }

            def fake_request_json(url, api_key, method="GET", body=None, **kwargs):
                if url.endswith("/models"):
                    return 200, {
                        "data": [
                            {"id": "claude-opus-4-8"},
                            {"id": "claude-opus-4-7"},
                        ]
                    }
                if body["model"] == "claude-opus-4-8":
                    raise RuntimeError("simulated capacity failure")
                return 200, {"choices": [{"message": {"content": "fallback response"}}]}

            try:
                os.environ["TEST_SHARED_BASE"] = "https://example.test/v1"
                os.environ["TEST_CLAUDE_KEY"] = "claude-key"
                runner_module.request_json = fake_request_json
                report = runner_module.run(
                    SimpleNamespace(
                        task=task,
                        index=index,
                        model_id=None,
                        base_url=None,
                        api_key=None,
                        max_tokens=20,
                        timeout_seconds=1,
                        anthropic_version="2023-06-01",
                        include_placeholder_models=False,
                    )
                )
            finally:
                runner_module.request_json = original_request_json
                for key, value in original_env.items():
                    if value is None:
                        os.environ.pop(key, None)
                    else:
                        os.environ[key] = value

            result = report["results"][0]
            self.assertEqual("complete", report["overall_status"])
            self.assertEqual("success", result["status"])
            self.assertEqual("claude-opus-4-7", result["alias_used"])
            self.assertEqual(["error", "success"], [item["status"] for item in result["attempted_aliases"]])
            self.assertEqual("fallback response\n", response_path.read_text(encoding="utf-8"))

    def test_runner_retries_same_alias_before_fallback(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            prompt = tmp_path / "prompt.md"
            prompt.write_text("Prompt", encoding="utf-8")
            response_path = tmp_path / "response.md"
            task = tmp_path / "task.json"
            task.write_text(
                json.dumps(
                    {
                        "id": "test_task",
                        "model_slots": [
                            {
                                "id": "claude_opus_4_8",
                                "model_alias": "claude-opus-4-8",
                                "model_aliases": ["claude-opus-4-8", "claude-opus-4-7"],
                                "wire_api": "anthropic_messages",
                                "auth_env": "TEST_CLAUDE_KEY",
                                "base_url_env": "TEST_CLAUDE_BASE",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            index = tmp_path / "index.json"
            index.write_text(
                json.dumps(
                    {
                        "task": "test_task",
                        "prompts": [
                            {
                                "model_id": "claude_opus_4_8",
                                "case_id": "case_one",
                                "prompt_path": str(prompt),
                                "expected_response_path": str(response_path),
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            original_request_json = runner_module.request_json
            original_env = {
                "TEST_CLAUDE_BASE": os.environ.get("TEST_CLAUDE_BASE"),
                "TEST_CLAUDE_KEY": os.environ.get("TEST_CLAUDE_KEY"),
            }
            calls = []

            def fake_request_json(url, api_key, method="GET", body=None, **kwargs):
                calls.append(body["model"])
                if len(calls) == 1:
                    raise RuntimeError("temporary 502")
                return 200, {"content": [{"type": "text", "text": "retried response"}]}

            try:
                os.environ["TEST_CLAUDE_BASE"] = "https://example.test"
                os.environ["TEST_CLAUDE_KEY"] = "claude-key"
                runner_module.request_json = fake_request_json
                report = runner_module.run(
                    SimpleNamespace(
                        task=task,
                        index=index,
                        model_id=None,
                        base_url=None,
                        api_key=None,
                        max_tokens=20,
                        timeout_seconds=1,
                        max_attempts=2,
                        retry_delay_seconds=0,
                        anthropic_version="2023-06-01",
                        include_placeholder_models=False,
                    )
                )
            finally:
                runner_module.request_json = original_request_json
                for key, value in original_env.items():
                    if value is None:
                        os.environ.pop(key, None)
                    else:
                        os.environ[key] = value

            result = report["results"][0]
            self.assertEqual("complete", report["overall_status"])
            self.assertEqual(["claude-opus-4-8", "claude-opus-4-8"], calls)
            self.assertEqual("claude-opus-4-8", result["alias_used"])
            self.assertEqual("success", result["attempted_aliases"][0]["status"])
            self.assertEqual(2, result["attempted_aliases"][0]["attempts"])
            self.assertEqual("retried response\n", response_path.read_text(encoding="utf-8"))

    def test_runner_uses_claude_messages_without_model_catalog(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            prompt = tmp_path / "prompt.md"
            prompt.write_text("Prompt", encoding="utf-8")
            response_path = tmp_path / "response.md"
            task = tmp_path / "task.json"
            task.write_text(
                json.dumps(
                    {
                        "id": "test_task",
                        "model_slots": [
                            {
                                "id": "claude_opus_4_8",
                                "model_alias": "claude-opus-4-8",
                                "wire_api": "anthropic_messages",
                                "auth_env": "TEST_CLAUDE_KEY",
                                "base_url_env": "TEST_CLAUDE_BASE",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            index = tmp_path / "index.json"
            index.write_text(
                json.dumps(
                    {
                        "task": "test_task",
                        "prompts": [
                            {
                                "model_id": "claude_opus_4_8",
                                "case_id": "case_one",
                                "prompt_path": str(prompt),
                                "expected_response_path": str(response_path),
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            original_request_json = runner_module.request_json
            original_env = {
                "TEST_CLAUDE_BASE": os.environ.get("TEST_CLAUDE_BASE"),
                "TEST_CLAUDE_KEY": os.environ.get("TEST_CLAUDE_KEY"),
            }

            def fake_request_json(url, api_key, method="GET", body=None, **kwargs):
                self.assertFalse(url.endswith("/models"))
                self.assertEqual("https://example.test/v1/messages", url)
                self.assertEqual({"anthropic-version": "2023-06-01"}, kwargs["extra_headers"])
                self.assertEqual("claude-opus-4-8", body["model"])
                return 200, {"content": [{"type": "text", "text": "claude response"}]}

            try:
                os.environ["TEST_CLAUDE_BASE"] = "https://example.test"
                os.environ["TEST_CLAUDE_KEY"] = "claude-key"
                runner_module.request_json = fake_request_json
                report = runner_module.run(
                    SimpleNamespace(
                        task=task,
                        index=index,
                        model_id=None,
                        base_url=None,
                        api_key=None,
                        max_tokens=20,
                        timeout_seconds=1,
                        anthropic_version="2023-06-01",
                        include_placeholder_models=False,
                    )
                )
            finally:
                runner_module.request_json = original_request_json
                for key, value in original_env.items():
                    if value is None:
                        os.environ.pop(key, None)
                    else:
                        os.environ[key] = value

            self.assertEqual("complete", report["overall_status"])
            self.assertEqual("anthropic_messages", report["results"][0]["wire_api"])
            self.assertEqual("claude response\n", response_path.read_text(encoding="utf-8"))

    def test_runner_attempts_configured_deepseek_slot_when_env_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            prompt = tmp_path / "prompt.md"
            prompt.write_text("Prompt", encoding="utf-8")
            task = tmp_path / "task.json"
            task.write_text(
                json.dumps(
                    {
                        "id": "test_task",
                        "model_slots": [
                            {
                                "id": "deepseek_followup_slot",
                                "model_alias": "deepseek-reasoner",
                                "auth_env": "MISSING_DEEPSEEK_KEY",
                                "base_url_env": "MISSING_DEEPSEEK_BASE",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            index = tmp_path / "index.json"
            index.write_text(
                json.dumps(
                    {
                        "task": "test_task",
                        "prompts": [
                            {
                                "model_id": "deepseek_followup_slot",
                                "case_id": "case_one",
                                "prompt_path": str(prompt),
                                "expected_response_path": str(tmp_path / "response.md"),
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            output_json = tmp_path / "run.json"
            output_md = tmp_path / "run.md"

            subprocess.run(
                [
                    sys.executable,
                    str(RUNNER),
                    "--task",
                    str(task),
                    "--index",
                    str(index),
                    "--output-json",
                    str(output_json),
                    "--output-md",
                    str(output_md),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            report = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertEqual("missing_base_url_or_api_key_env", report["results"][0]["selection_reason"])

    def test_runner_skips_placeholder_deepseek_slot_by_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            prompt = tmp_path / "prompt.md"
            prompt.write_text("Prompt", encoding="utf-8")
            task = tmp_path / "task.json"
            task.write_text(
                json.dumps(
                    {
                        "id": "test_task",
                        "model_slots": [
                            {
                                "id": "deepseek_followup_slot",
                                "model_alias": "deepseek-to-be-filled",
                                "auth_env": "MISSING_DEEPSEEK_KEY",
                                "base_url_env": "MISSING_DEEPSEEK_BASE",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            index = tmp_path / "index.json"
            index.write_text(
                json.dumps(
                    {
                        "task": "test_task",
                        "prompts": [
                            {
                                "model_id": "deepseek_followup_slot",
                                "case_id": "case_one",
                                "prompt_path": str(prompt),
                                "expected_response_path": str(tmp_path / "response.md"),
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            output_json = tmp_path / "run.json"
            output_md = tmp_path / "run.md"

            subprocess.run(
                [
                    sys.executable,
                    str(RUNNER),
                    "--task",
                    str(task),
                    "--index",
                    str(index),
                    "--output-json",
                    str(output_json),
                    "--output-md",
                    str(output_md),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            report = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertEqual("placeholder_model_slot", report["results"][0]["selection_reason"])


if __name__ == "__main__":
    unittest.main()
