from __future__ import annotations

import copy
import hashlib
import json
import sys
from pathlib import Path

import pytest


FORWARD_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FORWARD_ROOT))

from materialization_verifier_v2 import (  # noqa: E402
    MaterializationError,
    _alternate_reducer_enumerations,
    _canonical_json,
    _compose_model_visible_payload,
    _enumerate_closed_subsets,
    _execute_golden_json_transform,
    _render_subset,
    _render_wire_request,
    _select_ratio_candidate,
    _sha256,
    _token_encoder,
    _tokenizer_fingerprint_document,
    _validate_open_anchor_file_inventory,
    _validate_open_anchor_generated_token_ids,
    _validate_implementation_source_audit,
    _validate_replacement_amendments,
    _validate_result_row_semantics,
    _validate_result_row_schema_contract,
    _verify_overlap,
    audit_materialization,
    preregistrations,
    validate_task_artifacts,
)


TASK_ID = "NLP-LLM-01"


def request_template_fixture() -> dict[str, object]:
    return {
        "schema_version": "effectslice-fg1-request-template.v1",
        "model_slot_id": "deepseek_primary",
        "exact_alias": "deepseek-v4-flash",
        "base_request": {
            "model": "",
            "messages": [{"role": "user", "content": ""}],
            "temperature": None,
            "top_p": None,
            "max_tokens": None,
            "stream": False,
        },
        "model_json_pointer": "/model",
        "payload_json_pointer": "/messages/0/content",
        "decoding_field_json_pointers": {
            "temperature": "/temperature",
            "top_p": "/top_p",
            "normalized_max_output_tokens": "/max_tokens",
        },
    }


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def digest_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def build_task_fixture(root: Path) -> Path:
    task_root = root / TASK_ID
    task_root.mkdir(parents=True)
    encoder = _token_encoder()
    source_bytes = b"0123456789" * 20
    source_path = task_root / "sources" / "paper.txt"
    source_path.parent.mkdir()
    source_path.write_bytes(source_bytes)
    source_sha256 = _sha256(source_path)

    texts = [
        "alpha",
        "bravo",
        "charlie",
        "delta",
        "echo",
        "foxtrot",
        "golf",
        "hotel",
    ]
    registry_atoms = []
    dag_atoms = []
    atom_order = []
    text_by_id = {}
    dependencies = {}
    for index, rendered_text in enumerate(texts, start=1):
        source_locator = {
            "document_sha256": source_sha256,
            "byte_start": index * 10,
            "byte_end": index * 10 + len(rendered_text),
            "split_index": 0,
        }
        atom_preimage = b"\0".join(
            str(source_locator[field]).encode("ascii")
            for field in ("document_sha256", "byte_start", "byte_end", "split_index")
        )
        atom_id = "a_" + hashlib.sha256(atom_preimage).hexdigest()[:16]
        registry_atoms.append(
            {
                "atom_id": atom_id,
                "source_locator": source_locator,
                "rendered_text": rendered_text,
                "rendered_text_sha256": digest_text(rendered_text),
            }
        )
        dag_atoms.append(
            {
                "atom_id": atom_id,
                "dependency_ids": [],
                "rendered_token_count": len(encoder.encode(rendered_text)),
            }
        )
        atom_order.append(atom_id)
        text_by_id[atom_id] = rendered_text
        dependencies[atom_id] = set()

    write_json(
        task_root / "atom_registry.json",
        {"schema_version": "effectslice-fg1-atom-registry.v1", "task_id": TASK_ID, "atoms": registry_atoms},
    )
    write_json(
        task_root / "atom_dag.json",
        {"schema_version": "effectslice-fg1-atom-dag.v1", "task_id": TASK_ID, "atoms": dag_atoms},
    )
    reducer_input = {
        "schema_version": "effectslice-fg1-reducer-input.v1",
        "task_id": TASK_ID,
        "atoms": dag_atoms,
    }
    write_json(task_root / "reducer_input_manifest.json", reducer_input)

    runtime_dir = task_root / "runtime"
    runtime_dir.mkdir()
    (runtime_dir / "renderer.py").write_text("RENDERER_ID = 'effectslice_atom_renderer_v1'\n", encoding="utf-8")
    write_json(
        runtime_dir / "tokenizer_fingerprint.json",
        _tokenizer_fingerprint_document(encoder),
    )
    (runtime_dir / "reducer.py").write_text("REDUCER_ID = 'dag_ratio_60_v1'\n", encoding="utf-8")
    runtime = {
        "schema_version": "effectslice-fg1-reducer-runtime.v1",
        "task_id": TASK_ID,
        "renderer": {
            "id": "effectslice_atom_renderer_v1",
            "path": "runtime/renderer.py",
            "sha256": _sha256(runtime_dir / "renderer.py"),
            "separator": "\n\n",
            "encoding": "utf-8",
            "newline": "LF",
        },
        "tokenizer": {
            "id": "cl100k_base_asset",
            "path": "runtime/tokenizer_fingerprint.json",
            "sha256": _sha256(runtime_dir / "tokenizer_fingerprint.json"),
            "package": "tiktoken",
            "version": "0.12.0",
            "encoding": "cl100k_base",
        },
        "reducer": {
            "id": "dag_ratio_60_v1",
            "path": "runtime/reducer.py",
            "sha256": _sha256(runtime_dir / "reducer.py"),
        },
    }
    write_json(task_root / "reducer_runtime_manifest.json", runtime)

    subset_rows, subset_tokens = _enumerate_closed_subsets(
        atom_order, dependencies, text_by_id, encoder
    )
    full_bytes = _render_subset(atom_order, atom_order, text_by_id)
    full_tokens = len(encoder.encode(full_bytes.decode("utf-8")))
    eligible = [
        row
        for row in subset_rows
        if 45 * full_tokens <= 100 * row["rendered_token_count"] <= 75 * full_tokens
    ]
    selected = min(
        eligible,
        key=lambda row: (
            abs(5 * row["rendered_token_count"] - 3 * full_tokens),
            row["rendered_token_count"],
            tuple(row["atom_ids"]),
        ),
    )
    s_set = set(selected["atom_ids"])
    ladder_subsets = [
        row for row in subset_rows if s_set < set(row["atom_ids"]) < set(atom_order)
    ]
    chains = [
        {"L1_atom_ids": left["atom_ids"], "L2_atom_ids": right["atom_ids"]}
        for left in ladder_subsets
        for right in ladder_subsets
        if set(left["atom_ids"]) < set(right["atom_ids"])
    ]
    chains.sort(key=lambda row: (tuple(row["L1_atom_ids"]), tuple(row["L2_atom_ids"])))
    selected_chain = min(
        chains,
        key=lambda row: (
            -subset_tokens[tuple(row["L2_atom_ids"])],
            abs(
                2 * subset_tokens[tuple(row["L1_atom_ids"])]
                - subset_tokens[tuple(selected["atom_ids"])]
                - subset_tokens[tuple(row["L2_atom_ids"])]
            ),
            subset_tokens[tuple(row["L1_atom_ids"])],
            tuple(row["L1_atom_ids"]),
            tuple(row["L2_atom_ids"]),
        ),
    )
    greedy_rows, window_rows = _alternate_reducer_enumerations(
        atom_order, dependencies, text_by_id, encoder
    )
    selected_greedy = _select_ratio_candidate(greedy_rows, full_tokens)
    selected_window = _select_ratio_candidate(window_rows, full_tokens)

    candidate_atoms = {
        "B_empty_artifact": [],
        "F": atom_order,
        "S_dag_ratio_60_v1": selected["atom_ids"],
        "control_positive_reference": atom_order,
        "control_negative": atom_order[:1],
        "control_identity": atom_order,
        "ladder_L0": selected["atom_ids"],
        "ladder_L1": selected_chain["L1_atom_ids"],
        "ladder_L2": selected_chain["L2_atom_ids"],
        "alternate_dag_greedy": selected_greedy["atom_ids"],
        "alternate_source_window": selected_window["atom_ids"],
    }
    candidates = []
    for candidate_id, atom_ids in candidate_atoms.items():
        artifact_bytes = b"" if candidate_id == "B_empty_artifact" else _render_subset(atom_ids, atom_order, text_by_id)
        artifact_path = task_root / "artifacts" / f"{candidate_id}.txt"
        artifact_path.parent.mkdir(exist_ok=True)
        artifact_path.write_bytes(artifact_bytes)
        log_path = task_root / "logs" / f"{candidate_id}.json"
        write_json(log_path, {"candidate_id": candidate_id})
        token_count = 0 if not artifact_bytes else len(encoder.encode(artifact_bytes.decode("utf-8")))
        selected_set = set(atom_ids)
        candidates.append(
            {
                "candidate_id": candidate_id,
                "candidate_type": "registered_fixture",
                "atom_ids": atom_ids,
                "dependency_closed": True,
                "strict_subset": bool(selected_set) and selected_set < set(atom_order),
                "rendered_token_count": token_count,
                "retained_token_ratio": round(token_count / full_tokens, 12),
                "artifact_path": artifact_path.relative_to(task_root).as_posix(),
                "artifact_sha256": _sha256(artifact_path),
                "construction_log_path": log_path.relative_to(task_root).as_posix(),
                "construction_log_sha256": _sha256(log_path),
                "renderer_sha256": runtime["renderer"]["sha256"],
                "tokenizer_asset_sha256": runtime["tokenizer"]["sha256"],
                "reducer_input_manifest_sha256": _sha256(task_root / "reducer_input_manifest.json"),
            }
        )

    enumeration_sha = hashlib.sha256(_canonical_json(subset_rows)).hexdigest()
    candidate_doc = {
        "schema_version": "effectslice-fg1-candidates.v1",
        "task_id": TASK_ID,
        "candidates": candidates,
        "primary_reducer_audit": {
            "selection_rule_id": "dag_ratio_60_v1",
            "all_closed_strict_subsets": subset_rows,
            "complete_enumeration_sha256": enumeration_sha,
            "eligible_subset_count": len(eligible),
            "selected_candidate_id": "S_dag_ratio_60_v1",
        },
        "ladder_chain_audit": {
            "selection_rule_id": "complete_chain_enumeration_v1",
            "eligible_closed_subsets": ladder_subsets,
            "complete_subset_enumeration_sha256": hashlib.sha256(
                _canonical_json(ladder_subsets)
            ).hexdigest(),
            "enumerated_chain_count": len(chains),
            "all_chains": chains,
            "complete_chain_enumeration_sha256": hashlib.sha256(
                _canonical_json(chains)
            ).hexdigest(),
            "selected_chain_candidate_ids": ["ladder_L0", "ladder_L1", "ladder_L2", "F"],
        },
        "alternate_reducer_audit": {
            "dag_greedy_ratio_60_v1": {
                "selection_rule_id": "dag_greedy_ratio_60_v1",
                "enumeration": greedy_rows,
                "complete_enumeration_sha256": hashlib.sha256(
                    _canonical_json(greedy_rows)
                ).hexdigest(),
                "selected_candidate_id": "alternate_dag_greedy",
            },
            "source_window_ratio_60_v1": {
                "selection_rule_id": "source_window_ratio_60_v1",
                "enumeration": window_rows,
                "complete_enumeration_sha256": hashlib.sha256(
                    _canonical_json(window_rows)
                ).hexdigest(),
                "selected_candidate_id": "alternate_source_window",
            },
        },
    }
    write_json(task_root / "candidate_manifest.json", candidate_doc)
    write_json(
        task_root / "reducer_enumeration_manifest.json",
        {
            "schema_version": "effectslice-fg1-reducer-enumeration.v1",
            "task_id": TASK_ID,
            "all_closed_strict_subsets": subset_rows,
            "complete_enumeration_sha256": enumeration_sha,
            "eligible_subset_count": len(eligible),
            "selected_candidate_id": "S_dag_ratio_60_v1",
        },
    )

    for registry_id in ("A", "B"):
        prefix = registry_id.lower()
        write_json(
            task_root / f"private_registry_{registry_id}_manifest.json",
            {
                "schema_version": "effectslice-fg1-private-registry.v1",
                "task_id": TASK_ID,
                "registry_id": registry_id,
                "case_ids": [f"{prefix}-case-{index:03d}" for index in range(64)],
                "case_seeds": [f"{prefix}-seed-{index:03d}" for index in range(64)],
                "payload_sha256_values": sorted(
                    digest_text(f"{prefix}-payload-{index:03d}") for index in range(64)
                ),
                "expected_output_sha256": digest_text(f"{prefix}-expected"),
                "builder_identity": f"{prefix}-builder",
                "auditor_identity": f"{prefix}-auditor",
            },
        )

    write_json(
        task_root / "task_to_span_matrix.json",
        {
            "schema_version": "effectslice-fg1-task-spans.v1",
            "task_id": TASK_ID,
            "central_spans": [
                {
                    "document_sha256": source_sha256,
                    "page_or_section": "1",
                    "byte_start": 0,
                    "byte_end": 10,
                    "quoted_text_sha256": hashlib.sha256(source_bytes[0:10]).hexdigest(),
                    "atom_ids": atom_order[:3],
                },
                {
                    "document_sha256": source_sha256,
                    "page_or_section": "2",
                    "byte_start": 11,
                    "byte_end": 30,
                    "quoted_text_sha256": hashlib.sha256(source_bytes[11:30]).hexdigest(),
                    "atom_ids": atom_order[3:],
                },
            ],
        },
    )
    write_json(
        task_root / "source_manifest.json",
        {
            "schema_version": "effectslice-fg1-sources.v1",
            "task_id": TASK_ID,
            "sources": [
                {
                    "path": source_path.relative_to(task_root).as_posix(),
                    "sha256": source_sha256,
                    "license_or_access_note": "Synthetic test fixture.",
                }
            ],
        },
    )
    public_fixture_path = task_root / "fixtures" / "public.json"
    write_json(public_fixture_path, {"cases": ["public-case"]})
    write_json(
        task_root / "public_fixture_manifest.json",
        {
            "schema_version": "effectslice-fg1-public-fixture.v1",
            "task_id": TASK_ID,
            "fixture_path": public_fixture_path.relative_to(task_root).as_posix(),
            "fixture_sha256": _sha256(public_fixture_path),
        },
    )
    support_specs = (
        ("adapter_manifest.json", "effectslice-fg1-adapter.v1", "adapter.py"),
        (
            "reference_implementation_manifest.json",
            "effectslice-fg1-reference-implementation.v1",
            "reference.py",
        ),
        ("scorer_manifest.json", "effectslice-fg1-scorer.v1", "scorer.py"),
    )
    for manifest_name, schema_version, filename in support_specs:
        implementation_path = task_root / "support" / filename
        implementation_path.parent.mkdir(exist_ok=True)
        implementation_path.write_text(f"IDENTITY = {filename!r}\n", encoding="utf-8")
        manifest = {
            "schema_version": schema_version,
            "task_id": TASK_ID,
            "implementation_path": implementation_path.relative_to(task_root).as_posix(),
            "implementation_sha256": _sha256(implementation_path),
        }
        if manifest_name == "scorer_manifest.json":
            manifest["hard_contract_ids"] = [
                "hc_artifact_written",
                "hc_output_parseable",
            ]
        write_json(
            task_root / manifest_name,
            manifest,
        )
    write_json(
        task_root / "differential_test_report.json",
        {
            "schema_version": "effectslice-fg1-differential-test.v1",
            "task_id": TASK_ID,
            "passed": True,
            "comparison_count": 3,
            "failure_count": 0,
            "terminal_score_semantics_passed": True,
            "terminal_score_case_count": 5,
        },
    )
    write_json(
        task_root / "semantic_audit.json",
        {
            "schema_version": "effectslice-fg1-semantic-audit.v1",
            "task_id": TASK_ID,
            "identities": {
                "candidate_builder_identity": "candidate-builder",
                "source_auditor_identity": "source-auditor",
                "registry_A_builder_identity": "a-builder",
                "registry_A_auditor_identity": "a-auditor",
                "registry_B_builder_identity": "b-builder",
                "registry_B_auditor_identity": "b-auditor",
            },
            "reviews": [
                "task-to-span matrix",
                "atom roles and dependency edges",
                "F completeness",
                "primary reducer blindness",
                "S closure and retention",
                "scorer semantics",
                "task-specificity differential test",
            ],
            "disagreements_and_resolutions": [],
            "passed": True,
        },
    )
    task_scaffold = task_root / "task_scaffold.md"
    task_scaffold.write_text("Implement the registered task.\n", encoding="utf-8")
    fixture_a = task_root / "fixtures" / "A.json"
    write_json(fixture_a, {"cases": ["a-case"]})
    decoding = {
        "temperature": 0,
        "top_p": 1.0,
        "normalized_max_output_tokens": 1024,
    }
    decoding_path = task_root / "decoding" / "deepseek_primary.json"
    write_json(decoding_path, decoding)

    execution_id = "fixture-execution-001"
    payload_row = {
        "execution_id": execution_id,
        "registry_id": "A",
        "condition": "F",
        "candidate_id": "F",
        "model_slot_id": "deepseek_primary",
        "task_scaffold_path": "task_scaffold.md",
        "fixture_manifest_path": "public_fixture_manifest.json",
        "fixture_payload_path": "fixtures/A.json",
        "scorer_manifest_path": "scorer_manifest.json",
        "candidate_artifact_path": next(
            row["artifact_path"]
            for row in candidates
            if row["candidate_id"] == "F"
        ),
        "canonical_model_visible_payload_path": f"payloads/{execution_id}.txt",
        "serialized_wire_request_path": f"requests/{execution_id}.json",
        "decoding_config_path": "decoding/deepseek_primary.json",
        "private_registry_manifest_path": "private_registry_A_manifest.json",
    }
    _, _, _, contract = preregistrations()
    payload_bytes = _compose_model_visible_payload(task_root, payload_row, contract)
    payload_path = task_root / payload_row["canonical_model_visible_payload_path"]
    payload_path.parent.mkdir()
    payload_path.write_bytes(payload_bytes)
    wire_bytes = _render_wire_request(
        request_template_fixture(), payload_bytes, decoding
    )
    wire_path = task_root / payload_row["serialized_wire_request_path"]
    wire_path.parent.mkdir()
    wire_path.write_bytes(wire_bytes)
    for digest_field, path_field in contract["model_visible_payload_contract"][
        "digest_path_fields"
    ].items():
        payload_row[digest_field] = _sha256(task_root / payload_row[path_field])
    write_json(
        task_root / "model_visible_payload_manifest.json",
        {
            "schema_version": "effectslice-fg1-model-visible-payloads.v1",
            "task_id": TASK_ID,
            "rows": [payload_row],
        },
    )
    return task_root


def mutate_json(path: Path, mutator) -> None:
    value = json.loads(path.read_text(encoding="utf-8"))
    mutator(value)
    write_json(path, value)


def build_golden_execution_fixture(root: Path) -> tuple[Path, Path, Path, Path]:
    implementation = root / "transform.py"
    implementation.write_text(
        "import json\n"
        "import sys\n"
        "value = json.load(sys.stdin)\n"
        "sys.stdout.write(json.dumps({'value': value['value']}, "
        "sort_keys=True, separators=(',', ':'), ensure_ascii=True))\n",
        encoding="utf-8",
    )
    fixture = root / "fixture.json"
    write_json(fixture, {"value": 7})
    golden = root / "golden.json"
    golden.write_bytes(_canonical_json({"value": 7}))
    schema = root / "schema.json"
    write_json(
        schema,
        {
            "type": "object",
            "required": ["value"],
            "properties": {"value": {"type": "integer", "const": 7}},
            "additionalProperties": False,
        },
    )
    return implementation, fixture, golden, schema


def build_open_anchor_inventory_fixture(
    root: Path,
) -> tuple[Path, dict[str, object], dict[str, object]]:
    revision = "a" * 40
    model_root = root / "models--Qwen--Qwen2.5-Coder-7B-Instruct" / "snapshots" / revision
    model_root.mkdir(parents=True)
    shard_names = [
        "model-00001-of-00002.safetensors",
        "model-00002-of-00002.safetensors",
    ]
    for index, name in enumerate(shard_names, start=1):
        (model_root / name).write_bytes(f"shard-{index}".encode("ascii"))
    write_json(
        model_root / "model.safetensors.index.json",
        {"weight_map": {"layer.0": shard_names[0], "layer.1": shard_names[1]}},
    )
    write_json(
        model_root / "config.json",
        {
            "model_type": "qwen2",
            "architectures": ["Qwen2ForCausalLM"],
            "torch_dtype": "bfloat16",
            "hidden_size": 3584,
            "intermediate_size": 18944,
            "num_hidden_layers": 28,
            "num_attention_heads": 28,
            "num_key_value_heads": 4,
            "vocab_size": 152064,
            "max_position_embeddings": 131072,
        },
    )
    write_json(
        model_root / "generation_config.json",
        {"eos_token_id": [151645, 151643], "pad_token_id": 151643},
    )
    write_json(model_root / "tokenizer.json", {"version": "1.0"})
    write_json(model_root / "tokenizer_config.json", {"padding_side": "left"})

    _, _, _, contract = preregistrations()
    runtime_schema = contract["global_artifact_schemas"]["open_anchor_runtime_manifest"]

    def rows(names: list[str]) -> list[dict[str, object]]:
        return [
            {
                "path": name,
                "sha256": _sha256(model_root / name),
                "size_bytes": (model_root / name).stat().st_size,
            }
            for name in sorted(names)
        ]

    runtime: dict[str, object] = {
        "revision": revision,
        "dtype": "bfloat16",
        "quantization": "none",
        "weight_files": rows(shard_names),
        "tokenizer_files": rows(["tokenizer.json", "tokenizer_config.json"]),
        "config_files": rows(
            ["config.json", "generation_config.json", "model.safetensors.index.json"]
        ),
    }
    return model_root, runtime, runtime_schema


def refresh_inventory_row(
    model_root: Path, runtime: dict[str, object], group: str, filename: str
) -> None:
    row = next(item for item in runtime[group] if item["path"] == filename)
    row["sha256"] = _sha256(model_root / filename)
    row["size_bytes"] = (model_root / filename).stat().st_size


def test_valid_task_semantics_pass(tmp_path: Path) -> None:
    task_root = build_task_fixture(tmp_path)
    result = validate_task_artifacts(
        task_root,
        TASK_ID,
        True,
        {"deepseek_primary": request_template_fixture()},
    )
    assert len(result["candidate_hashes"]) == 11
    assert len(result["private_case_ids"]) == 128
    assert len(result["payload_rows"]) == 1


def test_result_canonicalizer_is_actually_executed(tmp_path: Path) -> None:
    implementation, fixture, golden, schema = build_golden_execution_fixture(tmp_path)
    result = _execute_golden_json_transform(
        implementation, fixture, golden, schema, 30, "result canonicalizer"
    )
    assert result == {"value": 7}
    implementation.write_text(
        "import sys\nsys.stdin.buffer.read()\nsys.stdout.write('{\"value\":8}')\n",
        encoding="utf-8",
    )
    with pytest.raises(MaterializationError, match="execution bytes differ"):
        _execute_golden_json_transform(
            implementation, fixture, golden, schema, 30, "result canonicalizer"
        )


def test_analysis_implementation_is_actually_executed(tmp_path: Path) -> None:
    implementation, fixture, golden, schema = build_golden_execution_fixture(tmp_path)
    schema_value = json.loads(schema.read_text(encoding="utf-8"))
    schema_value["properties"]["value"]["const"] = 8
    write_json(schema, schema_value)
    with pytest.raises(MaterializationError, match="schema const mismatch"):
        _execute_golden_json_transform(
            implementation, fixture, golden, schema, 30, "analysis implementation"
        )


def test_nonempty_replacement_amendment_is_rejected() -> None:
    _, _, _, contract = preregistrations()
    schema = contract["global_artifact_schemas"]["replacement_amendment_manifest"]
    document = {
        "schema_version": schema["schema_version"],
        "amendments": [{"amendment_id": "forged"}],
    }
    with pytest.raises(MaterializationError, match="successor registration"):
        _validate_replacement_amendments(document, schema)


def test_result_row_schema_weakening_is_rejected() -> None:
    _, _, _, contract = preregistrations()
    registered = contract["result_canonicalization_contract"]["result_row_json_schema"]
    weakened = copy.deepcopy(registered)
    weakened["properties"]["private_score"] = {}
    with pytest.raises(MaterializationError, match="registered typed contract"):
        _validate_result_row_schema_contract(
            weakened,
            registered,
        )


def result_row_fixture() -> dict[str, object]:
    return {
        "execution_id": "golden-operational-success",
        "terminal_outcome": "operational_success",
        "termination_reason": "provider_stop",
        "provider_finish_reason": "stop",
        "row_valid": True,
        "condition_success": True,
        "private_score": 1.0,
        "raw_response_path": "raw.json",
        "raw_response_sha256": "1" * 64,
        "canonical_output_path": "canonical.txt",
        "canonical_output_sha256": "2" * 64,
        "generated_token_ids": None,
        "hard_contract_vector": [True],
        "attempts": [
            {
                "attempt_index": 1,
                "attempt_status_class": "completed",
                "attempt_elapsed_ms": 5,
                "retry_sleep_after_attempt_ms": 0,
            }
        ],
        "candidate_artifact_bytes": 10,
        "candidate_artifact_cl100k_tokens": 3,
        "canonical_model_visible_payload_bytes": 20,
        "provider_reported_input_tokens": 2,
        "provider_reported_output_tokens": 1,
        "provider_reported_total_tokens": 3,
        "provider_reported_cached_input_tokens": 0,
        "provider_usage_missing_reason": None,
        "terminal_attempt_elapsed_ms": 5,
        "total_execution_elapsed_ms": 5,
        "retry_sleep_elapsed_ms": 0,
        "retry_overhead_ms": 0,
    }


def test_result_termination_outcome_mismatch_is_rejected() -> None:
    row = result_row_fixture()
    row["termination_reason"] = "not_dispatched"
    with pytest.raises(MaterializationError, match="completed-body termination"):
        _validate_result_row_semantics(row, "test-row")


def test_length_termination_remains_normally_scored() -> None:
    row = result_row_fixture()
    row["termination_reason"] = "length"
    row["provider_finish_reason"] = "length"
    _validate_result_row_semantics(row, "test-row")


def test_dispatched_result_requires_attempts() -> None:
    row = result_row_fixture()
    row["attempts"] = []
    with pytest.raises(MaterializationError, match="dispatched row must have attempts"):
        _validate_result_row_semantics(row, "test-row")


@pytest.mark.parametrize(
    "field",
    [
        "terminal_attempt_elapsed_ms",
        "total_execution_elapsed_ms",
        "retry_sleep_elapsed_ms",
        "retry_overhead_ms",
    ],
)
def test_dispatched_result_requires_all_timings(field: str) -> None:
    row = result_row_fixture()
    row[field] = None
    with pytest.raises(MaterializationError, match="dispatched timing must be non-null"):
        _validate_result_row_semantics(row, "test-row")


def test_result_retry_sleep_must_equal_attempt_sum() -> None:
    row = result_row_fixture()
    row["attempts"][0]["retry_sleep_after_attempt_ms"] = 2
    with pytest.raises(MaterializationError, match="retry sleep arithmetic"):
        _validate_result_row_semantics(row, "test-row")


def test_result_attempt_indices_must_be_consecutive() -> None:
    row = result_row_fixture()
    row["attempts"][0]["attempt_index"] = 2
    with pytest.raises(MaterializationError, match="indices must be consecutive"):
        _validate_result_row_semantics(row, "test-row")


def test_result_terminal_timing_must_match_last_attempt() -> None:
    row = result_row_fixture()
    row["attempts"][0]["attempt_elapsed_ms"] = 4
    with pytest.raises(MaterializationError, match="terminal attempt timing mismatch"):
        _validate_result_row_semantics(row, "test-row")


def test_result_terminal_attempt_cannot_have_retry_sleep() -> None:
    row = result_row_fixture()
    row["attempts"][0]["retry_sleep_after_attempt_ms"] = 1
    row["retry_sleep_elapsed_ms"] = 1
    with pytest.raises(MaterializationError, match="terminal attempt cannot have retry sleep"):
        _validate_result_row_semantics(row, "test-row")


def test_result_total_timing_cannot_precede_terminal_attempt() -> None:
    row = result_row_fixture()
    row["total_execution_elapsed_ms"] = 4
    with pytest.raises(MaterializationError, match="total timing precedes"):
        _validate_result_row_semantics(row, "test-row")


def test_result_retry_overhead_must_include_registered_sleep() -> None:
    row = result_row_fixture()
    row["attempts"] = [
        {
            "attempt_index": 1,
            "attempt_status_class": "retryable_transport",
            "attempt_elapsed_ms": 3,
            "retry_sleep_after_attempt_ms": 4,
        },
        {
            "attempt_index": 2,
            "attempt_status_class": "completed",
            "attempt_elapsed_ms": 5,
            "retry_sleep_after_attempt_ms": 0,
        },
    ]
    row["retry_sleep_elapsed_ms"] = 4
    row["total_execution_elapsed_ms"] = 7
    row["retry_overhead_ms"] = 2
    with pytest.raises(MaterializationError, match="excludes registered sleep"):
        _validate_result_row_semantics(row, "test-row")


def test_result_total_timing_must_cover_attempt_components() -> None:
    row = result_row_fixture()
    row["attempts"] = [
        {
            "attempt_index": 1,
            "attempt_status_class": "retryable_transport",
            "attempt_elapsed_ms": 20,
            "retry_sleep_after_attempt_ms": 4,
        },
        {
            "attempt_index": 2,
            "attempt_status_class": "completed",
            "attempt_elapsed_ms": 5,
            "retry_sleep_after_attempt_ms": 0,
        },
    ]
    row["retry_sleep_elapsed_ms"] = 4
    row["total_execution_elapsed_ms"] = 10
    row["retry_overhead_ms"] = 5
    with pytest.raises(MaterializationError, match="omits attempt components"):
        _validate_result_row_semantics(row, "test-row")


def test_result_path_and_hash_missingness_must_match() -> None:
    row = result_row_fixture()
    row["raw_response_sha256"] = None
    with pytest.raises(MaterializationError, match="path/hash pair mismatch"):
        _validate_result_row_semantics(row, "test-row")


def test_completed_body_requires_raw_response() -> None:
    row = result_row_fixture()
    row["raw_response_path"] = None
    row["raw_response_sha256"] = None
    with pytest.raises(MaterializationError, match="requires raw response"):
        _validate_result_row_semantics(row, "test-row")


def test_scored_outcome_requires_canonical_output() -> None:
    row = result_row_fixture()
    row["canonical_output_path"] = None
    row["canonical_output_sha256"] = None
    with pytest.raises(MaterializationError, match="requires canonical output"):
        _validate_result_row_semantics(row, "test-row")


def test_invalid_outcome_rejects_canonical_output() -> None:
    row = result_row_fixture()
    row.update(
        {
            "terminal_outcome": "integrity_or_digest_failure",
            "row_valid": False,
            "condition_success": None,
            "private_score": None,
            "generated_token_ids": None,
            "hard_contract_vector": None,
        }
    )
    with pytest.raises(MaterializationError, match="invalid outcome field must be null"):
        _validate_result_row_semantics(row, "test-row")


def test_result_provider_usage_rejects_partial_null_tuple() -> None:
    row = result_row_fixture()
    row["provider_reported_output_tokens"] = None
    row["provider_usage_missing_reason"] = "provider_usage_not_exposed"
    with pytest.raises(MaterializationError, match="complete or all null"):
        _validate_result_row_semantics(row, "test-row")


def test_result_null_provider_usage_requires_reason() -> None:
    row = result_row_fixture()
    row["provider_reported_input_tokens"] = None
    row["provider_reported_output_tokens"] = None
    row["provider_reported_total_tokens"] = None
    with pytest.raises(MaterializationError, match="requires a missing reason"):
        _validate_result_row_semantics(row, "test-row")


def test_result_null_provider_usage_rejects_unregistered_reason() -> None:
    row = result_row_fixture()
    row["provider_reported_input_tokens"] = None
    row["provider_reported_output_tokens"] = None
    row["provider_reported_total_tokens"] = None
    row["provider_usage_missing_reason"] = " "
    with pytest.raises(MaterializationError, match="requires a missing reason"):
        _validate_result_row_semantics(row, "test-row")


def test_result_usage_missing_reason_must_match_terminal_outcome() -> None:
    row = result_row_fixture()
    row["provider_reported_input_tokens"] = None
    row["provider_reported_output_tokens"] = None
    row["provider_reported_total_tokens"] = None
    row["provider_usage_missing_reason"] = "not_dispatched"
    with pytest.raises(MaterializationError, match="conflicts with terminal outcome"):
        _validate_result_row_semantics(row, "test-row")


def test_result_complete_provider_usage_rejects_missing_reason() -> None:
    row = result_row_fixture()
    row["provider_usage_missing_reason"] = "provider_usage_not_exposed"
    with pytest.raises(MaterializationError, match="cannot have a missing reason"):
        _validate_result_row_semantics(row, "test-row")


def open_anchor_generation_config() -> dict[str, object]:
    return {"max_new_tokens": 1024, "eos_token_id": [151645, 151643]}


def test_open_anchor_generated_tokens_reject_over_cap() -> None:
    with pytest.raises(MaterializationError, match="generated token length"):
        _validate_open_anchor_generated_token_ids(
            [1] * 1024 + [151645], open_anchor_generation_config(), "test-anchor"
        )


def test_open_anchor_generated_tokens_reject_early_eos() -> None:
    with pytest.raises(MaterializationError, match="first EOS must be the final"):
        _validate_open_anchor_generated_token_ids(
            [1, 151645, 2], open_anchor_generation_config(), "test-anchor"
        )


def test_open_anchor_generated_tokens_require_eos_below_cap() -> None:
    with pytest.raises(MaterializationError, match="short generation must terminate with EOS"):
        _validate_open_anchor_generated_token_ids(
            [1, 2, 3], open_anchor_generation_config(), "test-anchor"
        )


def test_closed_model_result_rejects_generated_token_ids() -> None:
    row = result_row_fixture()
    row["generated_token_ids"] = [1, 2, 3]
    with pytest.raises(MaterializationError, match="closed-model token IDs must be null"):
        _validate_result_row_semantics(
            row, "test-row", "deepseek_primary", open_anchor_generation_config()
        )


def test_open_anchor_eos_result_requires_terminal_eos() -> None:
    row = result_row_fixture()
    row["termination_reason"] = "eos"
    row["provider_finish_reason"] = "eos"
    row["generated_token_ids"] = [1] * 1024
    with pytest.raises(MaterializationError, match="must end in registered EOS"):
        _validate_result_row_semantics(
            row, "test-row", "open_seed_anchor", open_anchor_generation_config()
        )


def test_open_anchor_length_result_requires_full_non_eos_cap() -> None:
    row = result_row_fixture()
    row["termination_reason"] = "length"
    row["provider_finish_reason"] = "length"
    row["generated_token_ids"] = [1] * 1023 + [151645]
    with pytest.raises(MaterializationError, match="length termination token semantics"):
        _validate_result_row_semantics(
            row, "test-row", "open_seed_anchor", open_anchor_generation_config()
        )


def build_source_audit_fixture(
    root: Path,
) -> tuple[dict[str, object], dict[str, dict[str, str]]]:
    _, _, _, contract = preregistrations()
    schema = contract["global_artifact_schemas"][
        "implementation_source_audit_manifest"
    ]
    records: dict[str, dict[str, str]] = {}
    audits = []
    for component_id in schema["required_component_ids"]:
        implementation_path = f"support/{component_id}.py"
        implementation_sha256 = digest_text(component_id)
        builder_identity = f"builder-{component_id}"
        records[component_id] = {
            "implementation_path": implementation_path,
            "implementation_sha256": implementation_sha256,
            "builder_identity": builder_identity,
        }
        evidence_path = root / "audits" / f"{component_id}.json"
        write_json(evidence_path, {"component_id": component_id, "verdict": "pass"})
        audits.append(
            {
                "component_id": component_id,
                "implementation_path": implementation_path,
                "implementation_sha256": implementation_sha256,
                "builder_identity": builder_identity,
                "auditor_identity": f"auditor-{component_id}",
                "review_status": "pass",
                "checks": schema["required_checks_by_component"][component_id],
                "evidence_path": evidence_path.relative_to(root).as_posix(),
                "evidence_sha256": _sha256(evidence_path),
                "reviewed_at_utc": "2026-07-22T00:00:00Z",
            }
        )
    write_json(
        root / "implementation_source_audit_manifest.json",
        {"schema_version": schema["schema_version"], "audits": audits},
    )
    return schema, records


def test_implementation_source_audit_requires_independent_auditor(
    tmp_path: Path,
) -> None:
    schema, records = build_source_audit_fixture(tmp_path)
    referenced = _validate_implementation_source_audit(tmp_path, schema, records)
    assert len(referenced) == 3
    manifest_path = tmp_path / "implementation_source_audit_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["audits"][0]["auditor_identity"] = manifest["audits"][0][
        "builder_identity"
    ]
    write_json(manifest_path, manifest)
    with pytest.raises(MaterializationError, match="source-audit independence"):
        _validate_implementation_source_audit(tmp_path, schema, records)


def test_open_anchor_missing_shard_is_rejected(tmp_path: Path) -> None:
    model_root, runtime, schema = build_open_anchor_inventory_fixture(tmp_path)
    missing = "model-00002-of-00002.safetensors"
    (model_root / missing).unlink()
    runtime["weight_files"] = [
        row for row in runtime["weight_files"] if row["path"] != missing
    ]
    with pytest.raises(MaterializationError, match="shard index"):
        _validate_open_anchor_file_inventory(model_root, runtime, schema)


def test_open_anchor_same_family_wrong_size_is_rejected(tmp_path: Path) -> None:
    model_root, runtime, schema = build_open_anchor_inventory_fixture(tmp_path)
    write_json(
        model_root / "config.json",
        {
            "model_type": "qwen2",
            "architectures": ["Qwen2ForCausalLM"],
            "torch_dtype": "bfloat16",
            "hidden_size": 1536,
            "intermediate_size": 18944,
            "num_hidden_layers": 28,
            "num_attention_heads": 28,
            "num_key_value_heads": 4,
            "vocab_size": 152064,
            "max_position_embeddings": 131072,
        },
    )
    refresh_inventory_row(model_root, runtime, "config_files", "config.json")
    with pytest.raises(MaterializationError, match="hidden_size"):
        _validate_open_anchor_file_inventory(model_root, runtime, schema)


def test_ladder_non_strict_chain_is_rejected(tmp_path: Path) -> None:
    task_root = build_task_fixture(tmp_path)

    def mutate(value: dict[str, object]) -> None:
        value["ladder_chain_audit"]["all_chains"][0]["L2_atom_ids"] = value[
            "ladder_chain_audit"
        ]["all_chains"][0]["L1_atom_ids"]

    mutate_json(task_root / "candidate_manifest.json", mutate)
    with pytest.raises(MaterializationError):
        validate_task_artifacts(task_root, TASK_ID, True)


def test_ladder_closure_violation_is_rejected(tmp_path: Path) -> None:
    task_root = build_task_fixture(tmp_path)

    def mutate(value: dict[str, object]) -> None:
        value["atoms"][2]["dependency_ids"] = [value["atoms"][0]["atom_id"]]

    mutate_json(task_root / "atom_dag.json", mutate)
    mutate_json(task_root / "reducer_input_manifest.json", mutate)
    with pytest.raises(MaterializationError):
        validate_task_artifacts(task_root, TASK_ID, True)


def test_reducer_selected_subset_mutation_is_rejected(tmp_path: Path) -> None:
    task_root = build_task_fixture(tmp_path)

    def mutate(value: dict[str, object]) -> None:
        value["primary_reducer_audit"]["selected_candidate_id"] = "F"

    mutate_json(task_root / "candidate_manifest.json", mutate)
    with pytest.raises(MaterializationError):
        validate_task_artifacts(task_root, TASK_ID, True)


def test_missing_required_task_artifact_is_rejected(tmp_path: Path) -> None:
    task_root = build_task_fixture(tmp_path)
    (task_root / "scorer_manifest.json").unlink()
    with pytest.raises(MaterializationError):
        validate_task_artifacts(task_root, TASK_ID, True)


def test_support_implementation_hash_mutation_is_rejected(tmp_path: Path) -> None:
    task_root = build_task_fixture(tmp_path)
    (task_root / "support" / "scorer.py").write_text(
        "IDENTITY = 'mutated'\n", encoding="utf-8"
    )
    with pytest.raises(MaterializationError, match="digest mismatch"):
        validate_task_artifacts(task_root, TASK_ID, True)


def test_tokenizer_fingerprint_mutation_is_rejected(tmp_path: Path) -> None:
    task_root = build_task_fixture(tmp_path)
    tokenizer_path = task_root / "runtime" / "tokenizer_fingerprint.json"

    def mutate_fingerprint(value: dict[str, object]) -> None:
        value["special_token_count"] = int(value["special_token_count"]) + 1

    mutate_json(tokenizer_path, mutate_fingerprint)
    mutated_sha = _sha256(tokenizer_path)

    def mutate_runtime(value: dict[str, object]) -> None:
        value["tokenizer"]["sha256"] = mutated_sha

    mutate_json(task_root / "reducer_runtime_manifest.json", mutate_runtime)

    def mutate_candidates(value: dict[str, object]) -> None:
        for row in value["candidates"]:
            row["tokenizer_asset_sha256"] = mutated_sha

    mutate_json(task_root / "candidate_manifest.json", mutate_candidates)
    with pytest.raises(MaterializationError, match="tokenizer fingerprint mismatch"):
        validate_task_artifacts(task_root, TASK_ID, True)


def test_alternate_reducer_audit_mutation_is_rejected(tmp_path: Path) -> None:
    task_root = build_task_fixture(tmp_path)

    def mutate(value: dict[str, object]) -> None:
        value["alternate_reducer_audit"]["dag_greedy_ratio_60_v1"][
            "enumeration"
        ] = []

    mutate_json(task_root / "candidate_manifest.json", mutate)
    with pytest.raises(MaterializationError, match="alternate reducer audit mismatch"):
        validate_task_artifacts(task_root, TASK_ID, True)


def test_canonical_payload_composition_mutation_is_rejected(tmp_path: Path) -> None:
    task_root = build_task_fixture(tmp_path)
    manifest_path = task_root / "model_visible_payload_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    row = manifest["rows"][0]
    payload_path = task_root / row["canonical_model_visible_payload_path"]
    payload_path.write_bytes(payload_path.read_bytes() + b"mutated")
    row["canonical_model_visible_payload_sha256"] = _sha256(payload_path)
    write_json(manifest_path, manifest)
    with pytest.raises(MaterializationError, match="canonical payload composition mismatch"):
        validate_task_artifacts(task_root, TASK_ID, True)


def test_wire_request_composition_mutation_is_rejected(tmp_path: Path) -> None:
    task_root = build_task_fixture(tmp_path)
    manifest_path = task_root / "model_visible_payload_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    row = manifest["rows"][0]
    wire_path = task_root / row["serialized_wire_request_path"]
    write_json(wire_path, {"stream": False, "mutated": True})
    row["serialized_wire_request_sha256"] = _sha256(wire_path)
    write_json(manifest_path, manifest)
    with pytest.raises(MaterializationError, match="wire request composition mismatch"):
        validate_task_artifacts(
            task_root,
            TASK_ID,
            True,
            {"deepseek_primary": request_template_fixture()},
        )


def test_normalized_output_cap_mutation_is_rejected() -> None:
    with pytest.raises(MaterializationError, match="output-token cap"):
        _render_wire_request(
            request_template_fixture(),
            b"payload",
            {
                "temperature": 0,
                "top_p": 1.0,
                "normalized_max_output_tokens": 2048,
            },
        )


def test_materialized_reducer_semantic_label_is_rejected(tmp_path: Path) -> None:
    task_root = build_task_fixture(tmp_path)

    def mutate(value: dict[str, object]) -> None:
        value["atoms"][0]["hard_contract_label"] = "required"

    mutate_json(task_root / "reducer_input_manifest.json", mutate)
    with pytest.raises(MaterializationError):
        validate_task_artifacts(task_root, TASK_ID, True)


def test_atom_locator_outside_registered_source_is_rejected(tmp_path: Path) -> None:
    task_root = build_task_fixture(tmp_path)

    def mutate(value: dict[str, object]) -> None:
        value["atoms"][0]["source_locator"]["document_sha256"] = digest_text(
            "unregistered-source"
        )

    mutate_json(task_root / "atom_registry.json", mutate)
    with pytest.raises(MaterializationError, match="atom source is not registered"):
        validate_task_artifacts(task_root, TASK_ID, True)


def test_private_registry_overlap_is_rejected(tmp_path: Path) -> None:
    task_root = build_task_fixture(tmp_path)
    registry_a = json.loads(
        (task_root / "private_registry_A_manifest.json").read_text(encoding="utf-8")
    )

    def mutate(value: dict[str, object]) -> None:
        value["case_ids"] = registry_a["case_ids"]

    mutate_json(task_root / "private_registry_B_manifest.json", mutate)
    with pytest.raises(MaterializationError):
        validate_task_artifacts(task_root, TASK_ID, True)


def test_missing_required_global_artifact_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(MaterializationError, match="missing materialization file"):
        audit_materialization(tmp_path)


def build_overlap_fixture(root: Path) -> tuple[list[dict[str, object]], dict[str, object], set[str]]:
    rows = [
        {
            "execution_id": "fg1-exec",
            "pair_id": "fg1-pair",
            "derived_seed": 123,
            "fixture_payload_sha256": digest_text("fg1-fixture"),
            "serialized_wire_request_sha256": digest_text("fg1-wire"),
        }
    ]
    private_ids = {"fg1-case-a", "fg1-case-b"}
    _, _, _, frozen_contract = preregistrations()
    contract = copy.deepcopy(frozen_contract)
    fields: dict[str, object] = {}
    scopes = ["effectslice_fg1", "confirmation_v4", "confirmation_v5r2"]
    source_registry: dict[str, object] = {}
    for field in contract["parent_overlap_audit"]["required_zero_intersections"]:
        fields[field] = {}
        source_registry[field] = {}
        for scope in scopes:
            if scope == "effectslice_fg1":
                values = sorted(private_ids) if field == "private_case_id" else [str(rows[0][field])]
            else:
                values = [f"{scope}-{field}"]
            source_directory = root / "sources" / field / scope
            source_path = source_directory / "values.json"
            source_key = "values"
            write_json(source_path, {source_key: values})
            source_registry[field][scope] = {
                "path_base": "materialization_root",
                "root": source_directory.relative_to(root).as_posix(),
                "glob": "*.json",
                "expected_file_count": 1,
                "extractor": {"kind": "recursive_key", "key": source_key},
            }
            fields[field][scope] = {
                "values": values,
                "sources": [
                    {
                        "path_base": "materialization_root",
                        "path": source_path.relative_to(root).as_posix(),
                        "sha256": _sha256(source_path),
                    }
                ],
            }
    contract["parent_overlap_audit"]["source_registry"] = source_registry
    write_json(
        root / "parent_overlap_value_manifest.json",
        {
            "schema_version": "effectslice-fg1-parent-overlap-values.v1",
            "fields": fields,
        },
    )
    write_json(
        root / "parent_overlap_audit.json",
        {"intersection_counts": {field: 0 for field in fields}},
    )
    return rows, contract, private_ids


def test_overlap_source_hash_mutation_is_rejected(tmp_path: Path) -> None:
    rows, contract, private_ids = build_overlap_fixture(tmp_path)
    source = tmp_path / "sources" / "execution_id" / "confirmation_v4" / "values.json"
    source.write_text("{}\n", encoding="utf-8")
    with pytest.raises(MaterializationError):
        _verify_overlap(tmp_path, rows, contract, private_ids)


def test_overlap_registered_source_set_mutation_is_rejected(tmp_path: Path) -> None:
    rows, contract, private_ids = build_overlap_fixture(tmp_path)
    extra = tmp_path / "sources" / "execution_id" / "confirmation_v4" / "extra.json"
    write_json(extra, {"values": ["confirmation_v4-execution_id-extra"]})
    with pytest.raises(MaterializationError, match="source count mismatch"):
        _verify_overlap(tmp_path, rows, contract, private_ids)


def test_overlap_registered_extractor_mutation_is_rejected(tmp_path: Path) -> None:
    rows, contract, private_ids = build_overlap_fixture(tmp_path)
    contract["parent_overlap_audit"]["source_registry"]["execution_id"][
        "confirmation_v4"
    ]["extractor"] = {"kind": "recursive_key", "key": "missing"}
    with pytest.raises(MaterializationError, match="values not reproduced"):
        _verify_overlap(tmp_path, rows, contract, private_ids)


def test_private_case_registry_value_mismatch_is_rejected(tmp_path: Path) -> None:
    rows, contract, private_ids = build_overlap_fixture(tmp_path)
    manifest = tmp_path / "parent_overlap_value_manifest.json"

    def mutate(value: dict[str, object]) -> None:
        item = value["fields"]["private_case_id"]["effectslice_fg1"]
        item["values"] = ["fg1-case-other"]
        source = tmp_path / item["sources"][0]["path"]
        write_json(source, {"case_ids": item["values"]})
        item["sources"][0]["sha256"] = _sha256(source)

    mutate_json(manifest, mutate)
    with pytest.raises(MaterializationError):
        _verify_overlap(tmp_path, rows, contract, private_ids)
