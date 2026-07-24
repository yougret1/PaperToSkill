from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import build_fg5_output_contracts as contracts  # noqa: E402


EXPECTED_KEYS = {
    "AGENT-RA-01": {"error_line", "trajectory", "valid"},
    "AGENT-RA-02": {"final", "status", "trace"},
    "AGENT-RF-01": {"memory", "signatures"},
    "AGENT-RF-02": {"decision", "memory_append", "next_attempt"},
    "AGENT-TF-01": {"accepted_call_ids", "diagnostics"},
    "AGENT-TF-02": {"selected_call_ids", "tokens"},
    "DATA-HDB-01": {"mst_edges", "total_weight"},
    "DATA-HDB-02": {"clusters", "selected_cluster_ids"},
    "DATA-LEI-01": {"communities", "moves"},
    "DATA-LEI-02": {"aggregate_edges", "members"},
    "DATA-SNAP-01": {"idf", "row_degree", "weighted_matrix"},
    "DATA-SNAP-02": {"degree", "result"},
    "NLP-CSE-01": {"ranking", "scores"},
    "NLP-CSE-02": {"selected_indices", "tokens_used", "total_score"},
    "NLP-LL2-01": {"kept_indices", "token_labels"},
    "NLP-LL2-02": {"retained_token_indices", "selected_words", "tokens_used"},
    "NLP-LLM-01": {"allocations", "by_name", "total"},
    "NLP-LLM-02": {"history", "retained_indices"},
    "SE-CR-01": {"applications", "fixed_point", "text"},
    "SE-CR-02": {"attempts", "one_minimal", "reduced_items"},
    "SE-DD-01": {"minimal_failure", "outcome", "tests"},
    "SE-DD-02": {"isolated_difference", "tests"},
    "SE-PE-01": {"removed_node_ids", "retained_node_ids"},
    "SE-PE-02": {"retained_node_ids", "visit_order"},
}


def _by_task(value: dict[str, object]) -> dict[str, dict[str, object]]:
    return {str(row["task_id"]): row for row in value["tasks"]}


def test_registry_covers_all_public_tasks_and_exact_top_level_keys() -> None:
    value = contracts.build_registry_value()
    rows = _by_task(value)
    assert value["task_count"] == len(rows) == 24
    assert value["probes_per_task"] == 64
    assert set(rows) == set(EXPECTED_KEYS)
    for task_id, expected in EXPECTED_KEYS.items():
        shape = rows[task_id]["output_shape"]
        assert shape["type"] == "object"
        assert set(shape["properties"]) == expected
        assert set(shape["required"]) == expected
        assert shape["additionalProperties"] is False


def test_registry_persists_hashes_shapes_and_prompts_but_not_probe_values() -> None:
    value = contracts.build_registry_value()
    for row in value["tasks"]:
        assert set(row) == {
            "task_id",
            "input_set_sha256",
            "output_set_sha256",
            "output_shape",
            "prompt",
            "prompt_sha256",
        }
        assert re.fullmatch(r"[0-9a-f]{64}", row["input_set_sha256"])
        assert re.fullmatch(r"[0-9a-f]{64}", row["output_set_sha256"])
        assert re.fullmatch(r"[0-9a-f]{64}", row["prompt_sha256"])
        assert "cases" not in row and "outputs" not in row and "expected" not in row
        assert "[EXACT OUTPUT CONTRACT]" in row["prompt"]
        assert "never parse, coerce, numerically validate" in row["prompt"]


def test_dynamic_maps_and_nullable_fields_are_explicit() -> None:
    rows = _by_task(contracts.build_registry_value())
    assert rows["NLP-LLM-01"]["output_shape"]["properties"]["by_name"] == {
        "type": "object",
        "dynamicKeysFrom": "case.segments[*].name",
        "additionalProperties": {"type": "integer"},
    }
    assert rows["DATA-LEI-01"]["output_shape"]["properties"]["communities"][
        "dynamicKeysFrom"
    ] == "case.communities.keys()"
    assert rows["DATA-LEI-02"]["output_shape"]["properties"]["members"][
        "dynamicKeysFrom"
    ] == "case.refinement.values()"
    assert rows["AGENT-RF-02"]["output_shape"]["properties"]["memory_append"][
        "anyOf"
    ][0] == {"type": "null"}
    assert rows["AGENT-RA-02"]["output_shape"]["properties"]["final"]["anyOf"][
        0
    ] == {"type": "null"}


def test_build_and_verify_are_reproducible(tmp_path: Path) -> None:
    path = tmp_path / "registry.json"
    first = contracts.build_registry(path)
    first_bytes = path.read_bytes()
    second = contracts.build_registry(path)
    assert first == second
    assert path.read_bytes() == first_bytes
    result = contracts.verify_registry(path)
    assert result["status"] == "passed"
    assert result["task_count"] == 24
    assert json.loads(path.read_text(encoding="utf-8")) == first


def test_shape_validator_handles_exact_objects_dynamic_maps_tuples_and_nulls() -> None:
    rows = _by_task(contracts.build_registry_value())
    nlp_shape = rows["NLP-LLM-01"]["output_shape"]
    assert contracts.shape_violations(
        {"allocations": [1, 2], "by_name": {"arbitrary-name": 1}, "total": 3},
        nlp_shape,
    ) == []
    assert "unexpected key" in contracts.shape_violations(
        {
            "allocations": [1],
            "by_name": {"x": 1},
            "total": 1,
            "renamed_total": 1,
        },
        nlp_shape,
    )[0]
    tuple_shape = rows["DATA-HDB-01"]["output_shape"]
    assert contracts.shape_violations(
        {"mst_edges": [["a", "b", 0.5]], "total_weight": 0.5}, tuple_shape
    ) == []
    assert contracts.shape_violations(
        {"mst_edges": [["a", 1, "bad"]], "total_weight": 0.5}, tuple_shape
    )
    nullable_shape = rows["AGENT-RA-02"]["output_shape"]
    assert contracts.shape_violations(
        {"final": None, "status": "tool_error", "trace": []}, nullable_shape
    ) == []
