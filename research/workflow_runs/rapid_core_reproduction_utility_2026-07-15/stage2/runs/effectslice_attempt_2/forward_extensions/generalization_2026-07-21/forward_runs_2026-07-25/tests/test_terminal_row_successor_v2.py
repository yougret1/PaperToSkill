from __future__ import annotations

from pathlib import Path

import pytest

import terminal_row_successor_v2 as successor


def install_writer_fakes(monkeypatch: pytest.MonkeyPatch, calls: list[str]) -> None:
    def base_write(
        run_dir: Path,
        row: dict[str, object],
        value: dict[str, object],
        materialization: Path,
    ) -> None:
        del materialization
        calls.append(str(row["execution_id"]))
        successor.v1.atomic_json(
            run_dir / "rows" / f"{row['execution_id']}.json", value
        )

    monkeypatch.setattr(successor.fg1, "write_row", base_write)
    monkeypatch.setattr(successor.fg1, "validate_result_row", lambda *args: None)
    monkeypatch.setattr(
        successor.v1,
        "core_result",
        lambda value: dict(value),
    )
    monkeypatch.setattr(
        successor.v1,
        "metadata_document",
        lambda *args, **kwargs: {"schema_version": "test-metadata.v1"},
    )


def test_patched_writer_calls_captured_base_once_without_recursion(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[str] = []
    install_writer_fakes(monkeypatch, calls)
    row = {"execution_id": "test-row", "model_slot_id": "test-model"}
    value = {
        "execution_id": "test-row",
        "terminal_outcome": "completed",
        "preflight_status": "passed",
    }

    with successor.patched_runner_schema():
        successor.fg1.write_row(
            tmp_path, row, value, successor.fg5.DEFAULT_PARENT
        )

    assert calls == ["test-row"]
    assert (tmp_path / "rows" / "test-row.json").is_file()
    metadata = successor.v1.load_json(tmp_path / "metadata" / "test-row.json")
    assert metadata["writer_successor"] == successor.SCHEMA_VERSION
    assert metadata["result_row_sha256"] == successor.v1.sha256_file(
        tmp_path / "rows" / "test-row.json"
    )


def test_retryable_network_result_cannot_become_terminal(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[str] = []
    install_writer_fakes(monkeypatch, calls)
    row = {"execution_id": "network-row", "model_slot_id": "test-model"}
    value = {
        "execution_id": "network-row",
        "terminal_outcome": "transport_terminal_failure",
        "attempts": [{"attempt_status_class": "read_timeout"}],
    }

    with successor.patched_runner_schema():
        with pytest.raises(successor.v1.DeferredTransportError):
            successor.fg1.write_row(
                tmp_path, row, value, successor.fg5.DEFAULT_PARENT
            )

    assert calls == []
    assert not (tmp_path / "rows" / "network-row.json").exists()


def test_registered_counts_remain_frozen() -> None:
    controls_by_id, grid_by_id = successor.v1.schedule_maps()
    assert len(controls_by_id) == 96
    assert len(grid_by_id) == 3 * 1296
    assert {
        repeat_id: sum(
            row["repeat_id"] == repeat_id for row in grid_by_id.values()
        )
        for repeat_id in successor.grid.REPEAT_IDS
    } == {"FG6": 1296, "FG7": 1296, "FG8": 1296}
