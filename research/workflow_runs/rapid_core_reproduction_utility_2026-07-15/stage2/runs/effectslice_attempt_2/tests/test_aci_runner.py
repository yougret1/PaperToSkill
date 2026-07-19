import json
import sys
import unittest
from pathlib import Path


RUN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RUN_ROOT / "src"))

from effectslice.aci_protocol import ActionLimits  # noqa: E402
from effectslice.aci_runner import (  # noqa: E402
    DEFAULT_COMMON_SCAFFOLD,
    InteractiveACIRunner,
    ModelTurnResult,
    RunnerConfigurationError,
)
from effectslice.aci_workspace import OverlayWorkspace  # noqa: E402
from effectslice.swe_scorer_bridge import ScorerEvaluation  # noqa: E402


class SequenceTransport:
    def __init__(self, turns):
        self.turns = list(turns)
        self.calls = []

    def __call__(self, *, prompt, retry_lineage_id, turn_index):
        self.calls.append(
            {
                "prompt": prompt,
                "retry_lineage_id": retry_lineage_id,
                "turn_index": turn_index,
            }
        )
        return self.turns.pop(0)


class FakeScorerBridge:
    def __init__(self, *, score=1.0, raises=None):
        self.score = score
        self.raises = raises
        self.calls = []

    def evaluate(self, diff_text, *, evaluation_id):
        self.calls.append({"diff_text": diff_text, "evaluation_id": evaluation_id})
        if self.raises is not None:
            raise self.raises
        success = self.score == 1.0
        metric = {
            "task_score": self.score,
            "success": success,
            "patch_applied": True,
            "test_passed": success,
            "failure_reason": "" if success else "test_command_failed",
            "private_output": "never enter model prompt",
        }
        feedback = json.dumps(
            {
                "failure_reason": metric["failure_reason"],
                "patch_applied": True,
                "status": "passed" if success else "failed",
                "task_score": self.score,
                "test_passed": success,
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        return ScorerEvaluation(feedback, metric, Path("candidate.patch"))


class FakePublicTestBridge:
    def __init__(self, feedback='{"status":"passed","stdout":"1 passed"}'):
        self.feedback = feedback
        self.calls = []

    def evaluate(self, diff_text, *, evaluation_id):
        self.calls.append({"diff_text": diff_text, "evaluation_id": evaluation_id})
        return type(
            "PublicResult",
            (),
            {"feedback": self.feedback, "passed": True, "returncode": 0},
        )()


def success_turn(text, *, attempts=1, input_tokens=10, output_tokens=5):
    return ModelTurnResult(
        status="success",
        response_text=text,
        attempts=attempts,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
    )


class InteractiveACIRunnerTest(unittest.TestCase):
    def setUp(self):
        self.source_root = RUN_ROOT / "tests" / "fixtures" / "aci_workspace" / "locked_source"
        self.limits = ActionLimits(
            max_query_chars=100,
            max_path_chars=100,
            max_edit_chars=200,
            max_open_lines=20,
            max_search_results=5,
        )

    def runner(
        self,
        transport,
        bridge,
        *,
        context="paper procedure",
        max_actions=6,
        score_final_state_on_exhaustion=False,
        private_score_policy="interactive",
        public_test_bridge=None,
    ):
        return InteractiveACIRunner(
            workspace=OverlayWorkspace(self.source_root),
            scorer_bridge=bridge,
            model_transport=transport,
            common_scaffold=DEFAULT_COMMON_SCAFFOLD,
            condition_context=context,
            task_prompt="Repair pkg/main.py so value returns new.",
            action_limits=self.limits,
            max_actions=max_actions,
            max_response_chars=2000,
            max_observation_chars=2000,
            score_final_state_on_exhaustion=score_final_state_on_exhaustion,
            private_score_policy=private_score_policy,
            public_test_bridge=public_test_bridge,
        )

    def test_runs_search_open_edit_test_submit_and_preserves_private_metrics(self):
        transport = SequenceTransport(
            [
                success_turn('{"action":"search","query":"return \'old\'","path":"pkg"}'),
                success_turn('{"action":"open","path":"pkg/main.py","start_line":1,"end_line":2}'),
                success_turn(
                    '{"action":"edit","path":"pkg/main.py",'
                    '"old_text":"return \'old\'","new_text":"return \'new\'"}'
                ),
                success_turn('{"action":"test"}', attempts=2),
                success_turn('{"action":"submit"}'),
            ]
        )
        bridge = FakeScorerBridge(score=1.0)

        result = self.runner(transport, bridge).run(retry_lineage_prefix="pair:F")

        self.assertEqual(result.status, "scored")
        self.assertEqual(result.terminal_reason, "submitted")
        self.assertTrue(result.submitted)
        self.assertEqual(result.task_score, 1.0)
        self.assertTrue(result.success)
        self.assertEqual(result.state.actions_used, 5)
        self.assertIn("return 'new'", result.diff_text)
        self.assertEqual([call["evaluation_id"] for call in bridge.calls], ["step-04", "submit-05"])
        self.assertEqual(result.input_tokens, 50)
        self.assertEqual(result.output_tokens, 25)
        self.assertEqual(result.transport_attempts, 6)
        self.assertEqual(len(result.scorer_metrics), 2)
        self.assertIn("private_output", result.scorer_metrics[0])
        self.assertNotIn("private_output", "\n".join(call["prompt"] for call in transport.calls))
        self.assertIn("pkg/main.py:2", transport.calls[1]["prompt"])
        self.assertEqual(
            [call["retry_lineage_id"] for call in transport.calls],
            [f"pair:F:turn-{index:03d}" for index in range(1, 6)],
        )

    def test_malformed_action_and_edit_error_consume_budget_with_feedback(self):
        transport = SequenceTransport(
            [
                success_turn("I will inspect the file"),
                success_turn(
                    '{"action":"edit","path":"pkg/main.py",'
                    '"old_text":"missing","new_text":"new"}'
                ),
            ]
        )

        result = self.runner(transport, FakeScorerBridge(), max_actions=2).run(
            retry_lineage_prefix="pair:B"
        )

        self.assertEqual(result.status, "failed")
        self.assertEqual(result.terminal_reason, "action_budget_exhausted")
        self.assertEqual(result.state.actions_used, 2)
        self.assertEqual(result.state.observations[0].status, "invalid_action")
        self.assertEqual(result.state.observations[1].status, "workspace_error")
        self.assertIn("return exactly one JSON action", transport.calls[1]["prompt"])

    def test_prompts_expose_total_and_remaining_action_horizon(self):
        transport = SequenceTransport(
            [
                success_turn("not-json"),
                success_turn('{"action":"submit"}'),
            ]
        )

        self.runner(transport, FakeScorerBridge(), max_actions=2).run(
            retry_lineage_prefix="pair:B"
        )

        self.assertIn("Total action budget: 2", transport.calls[0]["prompt"])
        self.assertIn("Actions remaining before this turn: 2", transport.calls[0]["prompt"])
        self.assertIn("Actions remaining before this turn: 1", transport.calls[1]["prompt"])

    def test_budget_exhaustion_preserves_last_objective_test_score(self):
        transport = SequenceTransport(
            [
                success_turn(
                    '{"action":"edit","path":"pkg/main.py",'
                    '"old_text":"return \'old\'","new_text":"return \'new\'"}'
                ),
                success_turn('{"action":"test"}'),
            ]
        )

        result = self.runner(transport, FakeScorerBridge(score=1.0), max_actions=2).run(
            retry_lineage_prefix="pair:B"
        )

        self.assertEqual(result.status, "scored")
        self.assertEqual(result.terminal_reason, "action_budget_exhausted_after_scored_test")
        self.assertFalse(result.submitted)
        self.assertEqual(result.task_score, 1.0)
        self.assertTrue(result.success)
        self.assertIn("return 'new'", result.diff_text)

    def test_protocol_v2_scores_the_final_edited_state_at_budget_exhaustion(self):
        transport = SequenceTransport(
            [
                success_turn(
                    '{"action":"edit","path":"pkg/main.py",'
                    '"old_text":"return \'old\'","new_text":"return \'new\'"}'
                ),
                success_turn('{"action":"test"}'),
                success_turn(
                    '{"action":"edit","path":"pkg/main.py",'
                    '"old_text":"return \'new\'","new_text":"return \'newer\'"}'
                ),
            ]
        )
        bridge = FakeScorerBridge(score=1.0)

        result = self.runner(
            transport,
            bridge,
            max_actions=3,
            score_final_state_on_exhaustion=True,
        ).run(retry_lineage_prefix="pair:B")

        self.assertEqual(result.status, "scored")
        self.assertEqual(
            result.terminal_reason,
            "action_budget_exhausted_after_final_score",
        )
        self.assertFalse(result.submitted)
        self.assertEqual(
            [call["evaluation_id"] for call in bridge.calls],
            ["step-02", "budget-final"],
        )
        self.assertIn("return 'newer'", bridge.calls[-1]["diff_text"])
        self.assertEqual(result.scorer_metrics[-1]["task_score"], 1.0)

    def test_final_only_policy_hides_test_score_and_scores_submit_once(self):
        transport = SequenceTransport(
            [
                success_turn(
                    '{"action":"edit","path":"pkg/main.py",'
                    '"old_text":"return \'old\'","new_text":"return \'new\'"}'
                ),
                success_turn('{"action":"test"}'),
                success_turn('{"action":"submit"}'),
            ]
        )
        bridge = FakeScorerBridge(score=1.0)

        result = self.runner(
            transport,
            bridge,
            private_score_policy="final_only",
        ).run(retry_lineage_prefix="confirmation:F")

        self.assertEqual(result.status, "scored")
        self.assertEqual(result.terminal_reason, "submitted")
        self.assertEqual(
            [call["evaluation_id"] for call in bridge.calls],
            ["submit-03"],
        )
        self.assertEqual(len(result.scorer_metrics), 1)
        self.assertEqual(result.private_score_policy, "final_only")
        self.assertEqual(result.private_score_count, 1)
        self.assertFalse(result.private_feedback_exposed)
        self.assertEqual(len(transport.calls), 3)
        self.assertIn("private scoring is unavailable", transport.calls[2]["prompt"])
        self.assertNotIn("task_score", transport.calls[2]["prompt"])
        self.assertNotIn("test_passed", transport.calls[2]["prompt"])

    def test_final_only_policy_exposes_public_test_but_not_private_score(self):
        transport = SequenceTransport(
            [
                success_turn(
                    '{"action":"edit","path":"pkg/main.py",'
                    '"old_text":"return \'old\'","new_text":"return \'new\'"}'
                ),
                success_turn('{"action":"test"}'),
                success_turn('{"action":"submit"}'),
            ]
        )
        private_bridge = FakeScorerBridge(score=1.0)
        public_bridge = FakePublicTestBridge()

        result = self.runner(
            transport,
            private_bridge,
            private_score_policy="final_only",
            public_test_bridge=public_bridge,
        ).run(retry_lineage_prefix="confirmation:F")

        self.assertEqual(result.status, "scored")
        self.assertEqual(
            [call["evaluation_id"] for call in public_bridge.calls],
            ["step-02"],
        )
        self.assertEqual(
            [call["evaluation_id"] for call in private_bridge.calls],
            ["submit-03"],
        )
        self.assertEqual(result.private_score_count, 1)
        self.assertFalse(result.private_feedback_exposed)
        self.assertIn("locked public test", transport.calls[0]["prompt"])
        self.assertIn("1 passed", transport.calls[2]["prompt"])
        self.assertNotIn("task_score", transport.calls[2]["prompt"])

    def test_provider_failure_is_terminal_and_not_scored(self):
        transport = SequenceTransport(
            [
                ModelTurnResult(
                    status="error",
                    response_text=None,
                    attempts=5,
                    input_tokens=0,
                    output_tokens=0,
                    error_message="transport unavailable",
                )
            ]
        )
        bridge = FakeScorerBridge()

        result = self.runner(transport, bridge).run(retry_lineage_prefix="pair:F")

        self.assertEqual(result.status, "error")
        self.assertEqual(result.terminal_reason, "provider_error")
        self.assertEqual(result.transport_attempts, 5)
        self.assertEqual(result.state.actions_used, 0)
        self.assertEqual(bridge.calls, [])

    def test_submit_without_changes_fails_without_calling_scorer(self):
        transport = SequenceTransport([success_turn('{"action":"submit"}')])
        bridge = FakeScorerBridge()

        result = self.runner(transport, bridge).run(retry_lineage_prefix="pair:S")

        self.assertEqual(result.status, "failed")
        self.assertEqual(result.terminal_reason, "submitted_without_changes")
        self.assertEqual(result.task_score, 0.0)
        self.assertFalse(result.success)
        self.assertEqual(bridge.calls, [])

    def test_scorer_exception_is_sanitized_and_terminal(self):
        transport = SequenceTransport(
            [
                success_turn(
                    '{"action":"edit","path":"pkg/main.py",'
                    '"old_text":"return \'old\'","new_text":"return \'new\'"}'
                ),
                success_turn('{"action":"test"}'),
            ]
        )
        bridge = FakeScorerBridge(raises=RuntimeError("hidden scorer path"))

        result = self.runner(transport, bridge).run(retry_lineage_prefix="pair:F")

        self.assertEqual(result.status, "error")
        self.assertEqual(result.terminal_reason, "scorer_error")
        self.assertEqual(result.state.actions_used, 2)
        self.assertEqual(len(result.turns), 2)
        self.assertEqual(result.turns[-1].action.action, "test")
        self.assertEqual(result.turns[-1].observation_status, "scorer_error")
        self.assertNotIn("hidden scorer path", result.public_error)
        self.assertNotIn("hidden scorer path", "\n".join(call["prompt"] for call in transport.calls))

    def test_common_scaffold_digest_is_condition_invariant_but_prompts_are_not(self):
        first_transport = SequenceTransport([success_turn('{"action":"submit"}')])
        second_transport = SequenceTransport([success_turn('{"action":"submit"}')])

        first = self.runner(first_transport, FakeScorerBridge(), context="no skill").run(
            retry_lineage_prefix="pair:B"
        )
        second = self.runner(second_transport, FakeScorerBridge(), context="full skill").run(
            retry_lineage_prefix="pair:F"
        )

        self.assertEqual(first.common_scaffold_sha256, second.common_scaffold_sha256)
        self.assertNotEqual(first.condition_context_sha256, second.condition_context_sha256)
        self.assertNotEqual(first.turns[0].prompt_sha256, second.turns[0].prompt_sha256)

    def test_rejects_invalid_configuration_and_model_turns(self):
        with self.assertRaises(RunnerConfigurationError):
            self.runner(SequenceTransport([]), FakeScorerBridge(), max_actions=0)
        with self.assertRaises(RunnerConfigurationError):
            ModelTurnResult(
                status="success",
                response_text=None,
                attempts=1,
                input_tokens=0,
                output_tokens=0,
            )
        with self.assertRaises(RunnerConfigurationError):
            ModelTurnResult(
                status="error",
                response_text="unexpected",
                attempts=True,
                input_tokens=0,
                output_tokens=0,
            )


if __name__ == "__main__":
    unittest.main()
