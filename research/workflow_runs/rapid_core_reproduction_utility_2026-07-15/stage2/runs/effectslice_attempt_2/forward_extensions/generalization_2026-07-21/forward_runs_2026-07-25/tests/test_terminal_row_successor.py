from __future__ import annotations

from pathlib import Path

import pytest

import terminal_row_successor as successor


def dispatch(
    state: str,
    status_class: str,
    *,
    http_status: int | None = None,
    body: bytes | None = None,
) -> object:
    return successor.fg1.DispatchResult(
        state=state,
        attempts=[
            {
                "attempt_index": 1,
                "attempt_status_class": status_class,
                "attempt_elapsed_ms": 10,
                "retry_sleep_after_attempt_ms": 0,
                "http_status": http_status,
                "request_ids": {},
                "error_type": None,
            }
        ],
        terminal_body=body,
        terminal_http_status=http_status,
        terminal_headers={},
        attempt_bodies=[] if body is None else [(1, body)],
        total_execution_elapsed_ms=10,
        failure_class=None if state == "completed_body" else status_class,
    )


def test_registered_counts_are_per_repeat() -> None:
    controls_by_id, grid_by_id = successor.schedule_maps()
    assert len(controls_by_id) == 96
    assert len(grid_by_id) == 3 * 1296
    assert {
        repeat_id: sum(row["repeat_id"] == repeat_id for row in grid_by_id.values())
        for repeat_id in successor.grid.REPEAT_IDS
    } == {"FG6": 1296, "FG7": 1296, "FG8": 1296}


def test_started_rows_have_expected_forward_recovery_classes() -> None:
    controls_by_id, grid_by_id = successor.schedule_maps()
    classified: list[tuple[str, str]] = []
    for label, rows, run_dir in (
        ("Controls-v2", controls_by_id, successor.controls.DEFAULT_RUN),
        ("FG6", grid_by_id, successor.grid.DEFAULT_RUNS / "FG6"),
    ):
        for execution_id in successor.started_ids(run_dir):
            assert execution_id in rows
            classified.append(
                (label, successor.classify_started_row(run_dir, execution_id))
            )
    assert sum(label == "Controls-v2" for label, _ in classified) == 12
    assert sum(label == "FG6" for label, _ in classified) == 18
    assert sum(kind == "persisted_response" for _, kind in classified) == 26
    assert sum(kind == "started_marker_only" for _, kind in classified) == 4


def test_resilient_dispatch_retries_and_preserves_one_semantic_id() -> None:
    sequence = [
        dispatch("transport_terminal_failure", "read_timeout"),
        dispatch("http_terminal_failure", "http_503", http_status=503, body=b"busy"),
        dispatch("completed_body", "completed_body", http_status=200, body=b"ok"),
    ]
    calls: list[tuple[tuple[object, ...], dict[str, object]]] = []

    def original(*args: object, **kwargs: object) -> object:
        calls.append((args, kwargs))
        return sequence[len(calls) - 1]

    result = successor.resilient_dispatch(original, "spec", "token", "same-id", b"request")
    assert len(calls) == 3
    assert all(call[0][2] == "same-id" for call in calls)
    assert result.state == "completed_body"
    assert [row["attempt_index"] for row in result.attempts] == [1, 2, 3]
    assert result.total_execution_elapsed_ms == 30


def test_retryable_transport_is_not_a_terminal_result() -> None:
    base = {"terminal_outcome": "transport_terminal_failure", "attempts": []}
    assert successor.retryable_result(base)
    assert successor.retryable_result(
        {
            "terminal_outcome": "integrity_or_digest_failure",
            "attempts": [{"attempt_status_class": "http_503"}],
        }
    )
    assert not successor.retryable_result(
        {
            "terminal_outcome": "malformed_or_no_submission",
            "attempts": [{"attempt_status_class": "completed_body"}],
        }
    )


def test_core_result_rejects_unknown_extensions() -> None:
    value = {field: None for field in successor.RESULT_FIELDS}
    value["repeat_id"] = "FG6"
    assert set(successor.core_result(value)) == set(successor.RESULT_FIELDS)
    value["unknown_extension"] = True
    with pytest.raises(successor.SuccessorError):
        successor.core_result(value)


def test_one_persisted_response_reprojects_without_source_changes() -> None:
    controls_by_id, _ = successor.schedule_maps()
    execution_id = next(
        item
        for item in successor.started_ids(successor.controls.DEFAULT_RUN)
        if successor.classify_started_row(successor.controls.DEFAULT_RUN, item)
        == "persisted_response"
    )
    row = controls_by_id[execution_id]
    resolver = successor.controls.ControlResolver(
        successor.controls.DEFAULT_REGISTRATION
    )
    before = successor.artifact_manifest(successor.controls.DEFAULT_RUN, execution_id)
    result, regenerated = successor.reproject_persisted_response(
        row,
        successor.controls.DEFAULT_RUN,
        resolver.resolve(row),
    )
    assert result["execution_id"] == execution_id
    assert regenerated == before
    assert successor.artifact_manifest(successor.controls.DEFAULT_RUN, execution_id) == before
