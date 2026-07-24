from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import output_contract_successor as successor  # noqa: E402


FG4_ROOT = successor.fg1.windows_extended_path(
    ROOT / "interface_contract_successor_2026-07-24"
)


def _visible(value: dict[str, object]) -> str:
    if isinstance(value.get("input"), str):
        return str(value["input"])
    messages = value["messages"]
    assert isinstance(messages, list) and len(messages) == 1
    return str(messages[0]["content"])


def test_transformation_inserts_only_task_specific_output_contract() -> None:
    registry = json.loads(successor.DEFAULT_CONTRACTS.read_text(encoding="utf-8"))
    prompts = {row["task_id"]: row["prompt"] for row in registry["tasks"]}
    schedule = successor.load_json(FG4_ROOT / "global_remote_schedule.json")["rows"]
    row = schedule[0]
    source_path = FG4_ROOT / "requests" / f"{row['execution_id']}.json"
    source = json.loads(source_path.read_text(encoding="utf-8"))
    transformed = json.loads(
        successor.transformed_request_bytes(
            source_path.read_bytes(),
            task_id=row["task_id"],
            prompt=prompts[row["task_id"]],
        )
    )
    before = _visible(source)
    after = _visible(transformed)
    assert before.startswith(successor.fg4.INTERFACE_INSTRUCTION)
    assert after == (
        successor.fg4.INTERFACE_INSTRUCTION
        + prompts[row["task_id"]]
        + before[len(successor.fg4.INTERFACE_INSTRUCTION) :]
    )
    source_without_visible = dict(source)
    transformed_without_visible = dict(transformed)
    if "input" in source:
        source_without_visible.pop("input")
        transformed_without_visible.pop("input")
    else:
        source_without_visible.pop("messages")
        transformed_without_visible.pop("messages")
    assert transformed_without_visible == source_without_visible


def test_execution_ids_bind_parent_and_contract_registry() -> None:
    parent = "fg4-exec-0123456789abcdef01234567"
    first = successor.execution_id(parent, "a" * 64)
    assert first == successor.execution_id(parent, "a" * 64)
    assert first.startswith("fg5-exec-")
    assert first != successor.execution_id(parent, "b" * 64)
    assert first != successor.execution_id(parent + "x", "a" * 64)


def test_run_cli_requires_an_explicit_bound() -> None:
    args = successor.parse_args(["run", "--docs-dir", "."])
    assert args.max_new_rows is None
    try:
        successor.main(["run", "--docs-dir", "."])
    except successor.OutputContractSuccessorError as exc:
        assert "bounded --max-new-rows is required" in str(exc)
    else:
        raise AssertionError("unbounded FG5 run was accepted")


def test_worker_bound_is_explicit_and_bounded() -> None:
    args = successor.parse_args(
        ["run", "--docs-dir", ".", "--max-new-rows", "3", "--workers", "5"]
    )
    assert args.workers == 5


def test_manifest_files_excludes_mutable_manifest_and_freeze_record(
    tmp_path: Path,
) -> None:
    (tmp_path / "request.json").write_text("{}", encoding="utf-8")
    (tmp_path / "successor_manifest.json").write_text("{}", encoding="utf-8")
    (tmp_path / "freeze.json").write_text("{}", encoding="utf-8")
    files = successor.manifest_files(tmp_path)
    assert [item["path"] for item in files] == ["request.json"]
