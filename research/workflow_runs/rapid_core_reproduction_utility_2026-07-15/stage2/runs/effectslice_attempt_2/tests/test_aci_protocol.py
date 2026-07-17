import sys
import unittest
from dataclasses import FrozenInstanceError
from pathlib import Path


RUN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RUN_ROOT / "src"))

from effectslice.aci_protocol import (  # noqa: E402
    ACIAction,
    ACILoopState,
    ActionBudgetExhausted,
    ActionLimits,
    ActionProtocolError,
    parse_action,
)


class ACIProtocolTest(unittest.TestCase):
    def setUp(self):
        self.limits = ActionLimits(
            max_query_chars=20,
            max_path_chars=40,
            max_edit_chars=60,
            max_open_lines=10,
            max_search_results=5,
        )

    def test_parses_plain_and_fenced_search_json_with_frozen_defaults(self):
        expected = ACIAction(
            action="search",
            query="needle",
            path=".",
            max_results=5,
        )

        self.assertEqual(parse_action('{"action":"search","query":"needle"}', self.limits), expected)
        self.assertEqual(
            parse_action(
                '```json\n{"action":"search","query":"needle",'
                '"path":"src","max_results":3}\n```',
                self.limits,
            ),
            ACIAction(
                action="search",
                query="needle",
                path="src",
                max_results=3,
            ),
        )
        with self.assertRaises(FrozenInstanceError):
            expected.path = "src"

    def test_parses_open_edit_test_and_submit(self):
        self.assertEqual(
            parse_action(
                '{"action":"open","path":"src/a.py",'
                '"start_line":2,"end_line":6}',
                self.limits,
            ),
            ACIAction(
                action="open",
                path="src/a.py",
                start_line=2,
                end_line=6,
            ),
        )
        self.assertEqual(
            parse_action(
                '{"action":"edit","path":"src/a.py",'
                '"old_text":"old","new_text":"new"}',
                self.limits,
            ),
            ACIAction(
                action="edit",
                path="src/a.py",
                old_text="old",
                new_text="new",
            ),
        )
        self.assertEqual(parse_action('{"action":"test"}', self.limits), ACIAction("test"))
        self.assertEqual(parse_action('{"action":"submit"}', self.limits), ACIAction("submit"))

    def test_rejects_non_json_multiple_objects_and_surrounding_narrative(self):
        invalid = [
            "search the repo",
            '{"action":"test"} {"action":"submit"}',
            '{"action":"test","action":"submit"}',
            '{"action":"search","query":"first","query":"second"}',
            'I will inspect. {"action":"test"}',
            "```json\n{not valid}\n```",
            "[]",
        ]
        for response in invalid:
            with self.subTest(response=response), self.assertRaises(ActionProtocolError):
                parse_action(response, self.limits)

    def test_rejects_unknown_actions_extra_fields_and_wrong_field_sets(self):
        invalid = [
            '{"action":"shell","command":"dir"}',
            '{"action":"test","path":"x"}',
            '{"action":"submit","extra":true}',
            '{"action":"open","path":"x","start_line":1}',
            '{"action":"edit","path":"x","old_text":"a"}',
            '{"action":"search","query":"x","old_text":"a"}',
        ]
        for response in invalid:
            with self.subTest(response=response), self.assertRaises(ActionProtocolError):
                parse_action(response, self.limits)

    def test_rejects_invalid_types_and_bounds(self):
        invalid = [
            '{"action":"search","query":"","max_results":1}',
            '{"action":"search","query":"xxxxxxxxxxxxxxxxxxxxx"}',
            '{"action":"search","query":"x","max_results":0}',
            '{"action":"search","query":"x","max_results":6}',
            '{"action":"search","query":"x","max_results":true}',
            '{"action":"open","path":"x","start_line":0,"end_line":1}',
            '{"action":"open","path":"x","start_line":1,"end_line":11}',
            '{"action":"open","path":"x","start_line":1,"end_line":true}',
            '{"action":"edit","path":"x","old_text":"","new_text":"n"}',
            '{"action":"edit","path":"x","old_text":1,"new_text":"n"}',
        ]
        for response in invalid:
            with self.subTest(response=response), self.assertRaises(ActionProtocolError):
                parse_action(response, self.limits)

    def test_rejects_path_and_edit_payload_limits_and_nul(self):
        long_path = "x" * 41
        long_edit = "x" * 61
        invalid = [
            f'{{"action":"open","path":"{long_path}","start_line":1,"end_line":1}}',
            '{"action":"open","path":"bad\\u0000path","start_line":1,"end_line":1}',
            f'{{"action":"edit","path":"x","old_text":"{long_edit}","new_text":"n"}}',
            f'{{"action":"edit","path":"x","old_text":"o","new_text":"{long_edit}"}}',
        ]
        for response in invalid:
            with self.subTest(response=response), self.assertRaises(ActionProtocolError):
                parse_action(response, self.limits)

    def test_loop_state_consumes_valid_and_malformed_actions(self):
        state = ACILoopState(max_actions=2)
        action = parse_action('{"action":"test"}', self.limits)

        after_valid = state.consume(action=action, status="ok", message="tests passed")
        after_invalid = after_valid.consume(
            action=None,
            status="invalid_action",
            message="return one JSON action",
        )

        self.assertEqual(state.actions_used, 0)
        self.assertEqual(after_valid.actions_used, 1)
        self.assertEqual(after_invalid.actions_used, 2)
        self.assertEqual(after_invalid.remaining_actions, 0)
        self.assertEqual(after_invalid.observations[1].step, 2)
        self.assertIsNone(after_invalid.observations[1].action)
        with self.assertRaises(ActionBudgetExhausted):
            after_invalid.consume(action=action, status="ok", message="late")
        with self.assertRaises(FrozenInstanceError):
            after_invalid.max_actions = 3

    def test_rejects_invalid_limits_and_observation_fields(self):
        for field in (
            "max_query_chars",
            "max_path_chars",
            "max_edit_chars",
            "max_open_lines",
            "max_search_results",
        ):
            values = dict(
                max_query_chars=1,
                max_path_chars=1,
                max_edit_chars=1,
                max_open_lines=1,
                max_search_results=1,
            )
            values[field] = 0
            with self.subTest(field=field), self.assertRaises(ActionProtocolError):
                ActionLimits(**values)
        with self.assertRaises(ActionProtocolError):
            ACILoopState(max_actions=True)
        with self.assertRaises(ActionProtocolError):
            ACILoopState(max_actions=1).consume(
                action=None,
                status="",
                message="bad",
            )


if __name__ == "__main__":
    unittest.main()
