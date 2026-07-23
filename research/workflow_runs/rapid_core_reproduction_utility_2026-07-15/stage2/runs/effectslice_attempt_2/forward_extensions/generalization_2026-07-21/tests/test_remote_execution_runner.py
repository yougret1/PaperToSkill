from __future__ import annotations

import io
import json
import re
import sys
import urllib.error
from pathlib import Path

import pytest


FORWARD_ROOT = Path(__file__).resolve().parents[1]
MATERIALIZATION = FORWARD_ROOT / "materialization_remote_only_2026-07-23"
sys.path.insert(0, str(FORWARD_ROOT))

import remote_execution_runner as runner  # noqa: E402


def test_frozen_anchor_sha_is_well_formed_and_matches_manifest() -> None:
    assert re.fullmatch(r"[0-9a-f]{64}", runner.EXPECTED_ANCHOR_BUNDLE_SHA256)
    anchor = runner.load_json(MATERIALIZATION / "final_anchor_manifest.json")
    assert anchor["bundle_sha256"] == runner.EXPECTED_ANCHOR_BUNDLE_SHA256


class FakeResponse:
    def __init__(self, body: bytes, status: int = 200):
        self.body = body
        self.status = status
        self.headers = {"x-request-id": "safe-request-id"}

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def read(self) -> bytes:
        return self.body

    def getcode(self) -> int:
        return self.status


class FakeOpener:
    def __init__(self, outcomes: list[object]):
        self.outcomes = outcomes

    def open(self, request: object, timeout: int) -> FakeResponse:
        del request, timeout
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, BaseException):
            raise outcome
        assert isinstance(outcome, FakeResponse)
        return outcome


class FakeClock:
    def __init__(self) -> None:
        self.value = 0.0

    def monotonic(self) -> float:
        self.value += 0.001
        return self.value

    def sleep(self, seconds: float) -> None:
        self.value += seconds


def schedule_row(index: int = 0) -> dict[str, object]:
    schedule = runner.load_json(MATERIALIZATION / "global_remote_schedule.json")
    return schedule["rows"][index]


def test_credentials_are_selected_in_memory_without_value_metadata(tmp_path: Path) -> None:
    first = "sk-" + "a" * 64
    second = "sk-" + "b" * 64
    deepseek = "sk-" + "c" * 32
    (tmp_path / "gpt.md").write_text(
        "https://coderxiaoc.com/v1/responses\n"
        "gpt-5.5 gpt-5.6-sol gpt-5.6-terra gpt-5.6-luna\n"
        f"API-Key: {first}\nBearer {first}\n",
        encoding="utf-8",
    )
    (tmp_path / "claude.md").write_text(
        "https://coderxiaoc.com/v1/messages\nclaude-opus-4-7\n"
        f"regular API-Key: {first}\ndesktop direct: {second}\n",
        encoding="utf-8",
    )
    (tmp_path / "deepseek.md").write_text(
        "https://api.deepseek.com/chat/completions\ndeepseek-v4-flash\n"
        f"Bearer {deepseek}\n",
        encoding="utf-8",
    )
    values, metadata = runner.load_credentials(tmp_path)
    assert values["claude_opus_4_7"] == first
    assert values["deepseek_primary"] == deepseek
    serialized = json.dumps(metadata)
    assert first not in serialized
    assert second not in serialized
    assert deepseek not in serialized
    assert metadata["claude_opus_4_7"]["unique_candidate_count"] == 2


def test_transport_retries_503_with_registered_delay() -> None:
    error = urllib.error.HTTPError(
        "https://example.invalid",
        503,
        "busy",
        {"Retry-After": "0", "x-request-id": "retry-id"},
        io.BytesIO(b'{"error":"busy"}'),
    )
    opener = FakeOpener([error, FakeResponse(b'{"ok":true}')])
    clock = FakeClock()
    spec = runner.PROVIDER_SPECS["gpt_5_5"]
    result = runner.dispatch_request(
        spec,
        "secret-not-logged",
        "fg1-test-retry",
        b"{}",
        sleep=clock.sleep,
        monotonic=clock.monotonic,
        opener_factory=lambda: opener,
    )
    assert result.state == "completed_body"
    assert len(result.attempts) == 2
    assert result.attempts[0]["attempt_status_class"] == "http_503"
    assert result.attempts[0]["retry_sleep_after_attempt_ms"] >= 2000
    assert result.attempts[-1]["retry_sleep_after_attempt_ms"] == 0
    assert result.terminal_body == b'{"ok":true}'


def test_request_resolver_rechecks_every_frozen_row_hash() -> None:
    row = schedule_row()
    resolved = runner.RowResolver(MATERIALIZATION).resolve(row)
    assert runner.sha256_bytes(resolved.request_bytes) == row[
        "serialized_wire_request_sha256"
    ]
    assert json.loads(resolved.request_bytes)["model"] == "deepseek-v4-flash"


def test_worker_runs_pure_code_and_removes_workspace(tmp_path: Path) -> None:
    source = "def solve(case):\n    return {'answer': case['value'] * 2}"
    cases = [
        {"case_id": "a", "payload": {"value": 2}},
        {"case_id": "b", "payload": {"value": 3}},
    ]
    result = runner.run_worker(source, cases, tmp_path, "worker-good")
    assert result["status"] == "completed"
    assert result["outputs"] == [
        {"case_id": "a", "output": {"answer": 4}},
        {"case_id": "b", "output": {"answer": 6}},
    ]
    assert not (tmp_path / "sandbox_tmp" / "worker-good").exists()


def test_worker_blocks_network_capable_import(tmp_path: Path) -> None:
    source = "import socket\ndef solve(case):\n    return {}"
    result = runner.run_worker(source, [], tmp_path, "worker-blocked")
    assert result["status"] == "safety_policy_violation"
    assert "socket" in result["reason"]


def test_strict_submission_rejects_fences_and_duplicate_keys() -> None:
    with pytest.raises(json.JSONDecodeError):
        runner.strict_submission("```json\n{}\n```")
    with pytest.raises(ValueError, match="duplicate JSON key"):
        runner.strict_submission(
            '{"implementation":"def solve(case): return {}",'
            '"implementation":"def solve(case): return {}"}'
        )


def test_scorer_vector_mismatch_is_preserved_as_forward_audit() -> None:
    audit = runner.scorer_contract_audit(MATERIALIZATION)
    assert audit["task_count"] == 24
    assert audit["length_mismatch_count"] == 24
    assert audit["forward_execution_policy"]["frozen_scorer_output_preserved"] is True
    assert (
        audit["forward_execution_policy"]["vector_components_relabelled_as_manifest_ids"]
        is False
    )


def test_unavailable_row_passes_frozen_schema_and_semantics() -> None:
    row = schedule_row()
    inputs = runner.RowResolver(MATERIALIZATION).resolve(row)
    result = runner.unavailable_row(row, inputs)
    runner.validate_result_row(MATERIALIZATION, result, str(row["model_slot_id"]))
    assert result["terminal_outcome"] == "provider_or_model_unavailable"
    assert result["attempts"] == []


def test_output_normalization_is_crlf_to_lf_and_nfc() -> None:
    raw = "e\u0301\r\nnext\rline"
    assert runner.normalize_output(raw).decode("utf-8") == "\u00e9\nnext\nline"


def test_completed_body_runs_worker_scores_and_validates_row(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    row = schedule_row()
    inputs = runner.RowResolver(MATERIALIZATION).resolve(row)
    implementation = "def solve(case):\n    return {}"
    response = {
        "choices": [
            {
                "message": {
                    "content": json.dumps({"implementation": implementation})
                },
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 5,
            "total_tokens": 15,
            "prompt_tokens_details": {"cached_tokens": 0},
        },
    }
    body = runner.canonical_json(response)
    dispatch = runner.DispatchResult(
        state="completed_body",
        attempts=[
            {
                "attempt_index": 1,
                "attempt_status_class": "completed_body",
                "attempt_elapsed_ms": 5,
                "retry_sleep_after_attempt_ms": 0,
                "http_status": 200,
                "request_ids": {"x-request-id": "test-id"},
                "error_type": None,
            }
        ],
        terminal_body=body,
        terminal_http_status=200,
        terminal_headers={"x-request-id": "test-id"},
        attempt_bodies=[(1, body)],
        total_execution_elapsed_ms=5,
        failure_class=None,
    )
    monkeypatch.setattr(runner, "dispatch_request", lambda *args, **kwargs: dispatch)
    run_dir = runner.windows_extended_path(tmp_path)
    result = runner.execute_row(MATERIALIZATION, run_dir, row, inputs, "not-logged")
    runner.validate_result_row(MATERIALIZATION, result, str(row["model_slot_id"]))
    assert result["terminal_outcome"] == "hard_contract_failure"
    assert result["private_score"] < 0.99
    assert result["hard_contract_vector"] == [True, False]
    assert result["raw_response_sha256"] == runner.sha256_bytes(body)
