from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import build_fg5_selection_batch as batches  # noqa: E402


def test_batch_skips_terminal_rows_and_preserves_source_order(tmp_path: Path) -> None:
    source = tmp_path / "source.json"
    run_dir = tmp_path / "run"
    rows = [
        {"execution_id": "e1", "task_id": "t1"},
        {"execution_id": "e2", "task_id": "t2"},
        {"execution_id": "e3", "task_id": "t3"},
    ]
    source.write_text(
        json.dumps(
            {
                "selection_name": "all",
                "row_count": 3,
                "execution_ids": ["e1", "e2", "e3"],
                "rows": rows,
            }
        ),
        encoding="utf-8",
    )
    (run_dir / "rows").mkdir(parents=True)
    (run_dir / "rows" / "e1.json").write_text("{}", encoding="utf-8")
    value = batches.build_batch(source, run_dir, limit=1, batch_name="batch-1")
    assert value["pending_before_batch"] == 2
    assert value["execution_ids"] == ["e2"]
    assert value["rows"] == [rows[1]]
