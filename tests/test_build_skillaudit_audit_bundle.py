from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import zipfile
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_skillaudit_audit_bundle.py"
SPEC = importlib.util.spec_from_file_location("build_skillaudit_audit_bundle", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True), encoding="utf-8")


def make_task(task_root: Path) -> None:
    task = task_root / "TASK-01"
    for relative in MODULE.TASK_ROOT_FILES:
        path = task / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.suffix == ".json":
            write_json(path, {"task_id": "TASK-01", "path": "sources/paper_evidence.txt"})
        else:
            path.write_text("registered task\n", encoding="utf-8")
    for relative in MODULE.TASK_SUBFILES:
        path = task / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.suffix == ".json":
            write_json(path, {"task_id": "TASK-01", "relative": relative})
        else:
            path.write_text(f"fixture for {relative}\n", encoding="utf-8")

    evidence = task / "sources" / "paper_evidence.txt"
    evidence_sha = hashlib.sha256(evidence.read_bytes()).hexdigest()
    write_json(
        task / "source_manifest.json",
        {
            "task_id": "TASK-01",
            "sources": [
                {
                    "path": "sources/paper_evidence.txt",
                    "sha256": evidence_sha,
                    "upstream_sha256": "a" * 64,
                    "upstream_url": "https://example.org/paper.pdf",
                    "transformation": "Bounded method summary.",
                }
            ],
        },
    )
    write_json(
        task / "atom_registry.json",
        {
            "task_id": "TASK-01",
            "atoms": [
                {
                    "atom_id": "a1",
                    "source_locator": {
                        "document_sha256": evidence_sha,
                        "byte_start": 0,
                        "byte_end": evidence.stat().st_size,
                    },
                }
            ],
        },
    )
    write_json(
        task / "task_to_span_matrix.json",
        {
            "task_id": "TASK-01",
            "central_spans": [
                {
                    "document_sha256": evidence_sha,
                    "byte_start": 0,
                    "byte_end": evidence.stat().st_size,
                }
            ],
        },
    )


def make_primary(primary_root: Path) -> None:
    logical = "cell-01"
    request = b'{"input":"registered request","model":"gpt-5.6-sol"}'
    request_sha = hashlib.sha256(request).hexdigest()
    request_path = primary_root / "registration" / "full_grid" / "requests" / f"{logical}.json"
    request_path.parent.mkdir(parents=True, exist_ok=True)
    request_path.write_bytes(request)
    for repeat in ("SOL1", "SOL2", "SOL3"):
        execution = f"{repeat.lower()}-exec-01"
        schedule_row = {
            "execution_family": "primary",
            "execution_id": execution,
            "logical_cell_id": logical,
            "global_sequence_index": 1,
            "task_id": "TASK-01",
            "paper_id": "paper-01",
            "domain": "test",
            "registry_id": "A",
            "block_id": 1,
            "pair_id": "pair-01",
            "condition": "F",
            "candidate_id": "F",
            "variant_id": "primary",
            "order_code": "BFS",
            "order_position": 2,
            "repeat_id": repeat,
            "repeat_sequence_index": 1,
            "model_slot_id": "gpt_5_6_sol",
            "serialized_wire_request_sha256": request_sha,
        }
        write_json(
            primary_root / "registration" / "full_grid" / repeat / "schedule.json",
            {"rows": [schedule_row]},
        )
        response = b'{"implementation":"pass"}\n'
        response_sha = hashlib.sha256(response).hexdigest()
        run = primary_root / "runs" / "full_grid" / repeat
        response_path = run / "canonical" / f"{execution}.txt"
        response_path.parent.mkdir(parents=True, exist_ok=True)
        response_path.write_bytes(response)
        write_json(
            run / "rows" / f"{execution}.json",
            {
                "execution_id": execution,
                "canonical_output_path": f"canonical/{execution}.txt",
                "canonical_output_sha256": response_sha,
                "registered_request_sha256": request_sha,
                "actual_model_identifier": "gpt-5.6-sol",
                "condition_success": True,
                "hard_contract_vector": [True],
                "private_score": 1.0,
                "row_valid": True,
                "terminal_outcome": "operational_success",
            },
        )


def write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )


def make_prospective(root: Path) -> None:
    bundle = "b" * 64
    request_path = (
        root / "registration" / "requests" / f"req-{'0' * 24}.json"
    )
    candidate_path = (
        root / "registration" / "candidates" / f"cand-{'1' * 24}.txt"
    )
    request_path.parent.mkdir(parents=True, exist_ok=True)
    candidate_path.parent.mkdir(parents=True, exist_ok=True)
    request_path.write_text(
        json.dumps(
            {
                "input": "registered prospective request",
                "model": "gpt-5.6-sol",
                "temperature": 1.0,
                "top_p": 0.98,
            },
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    candidate_path.write_text("registered candidate\n", encoding="utf-8")
    request_sha = hashlib.sha256(request_path.read_bytes()).hexdigest()
    candidate_sha = hashlib.sha256(candidate_path.read_bytes()).hexdigest()

    jobs: list[dict[str, object]] = []
    results: list[dict[str, object]] = []
    for index, phase in enumerate(("pilot", "confirmatory"), start=1):
        execution_id = f"ex3-exec-{index:024x}"
        condition_id = f"cond-{index:024x}"
        jobs.append(
            {
                "phase": phase,
                "execution_id": execution_id,
                "condition_id": condition_id,
                "task_id": "TASK-01",
                "registry_id": "A",
                "repetition_id": 1,
                "block_id": 1,
                "request_file": request_path.relative_to(root).as_posix(),
                "request_sha256": request_sha,
                "candidate_file": candidate_path.relative_to(root).as_posix(),
                "candidate_sha256": candidate_sha,
            }
        )
        run_root = root / "runs" / phase
        response_path = run_root / "canonical" / f"{execution_id}.txt"
        response_path.parent.mkdir(parents=True, exist_ok=True)
        response_path.write_text('{"implementation":"pass"}\n', encoding="utf-8")
        response_sha = hashlib.sha256(response_path.read_bytes()).hexdigest()
        result = {
            "phase": phase,
            "execution_id": execution_id,
            "condition_id": condition_id,
            "canonical_output_path": f"canonical/{execution_id}.txt",
            "canonical_output_sha256": response_sha,
            "registered_request_sha256": request_sha,
            "registered_candidate_sha256": candidate_sha,
            "registration_bundle_sha256": bundle,
            "actual_model_identifier": "gpt-5.6-sol",
            "condition_success": True,
            "credential_value_recorded": False,
            "digest_ok": True,
            "hard_contract_vector": [True],
            "lineage_ok": True,
            "private_score": 1.0,
            "row_valid": True,
            "scorer_interpretation_present": True,
            "terminal_outcome": "operational_success",
            "terminal_result_present": True,
        }
        results.append(result)
        write_json(
            run_root / "transport" / f"{execution_id}.json",
            {
                "execution_id": execution_id,
                "condition_id": condition_id,
                "response_reported_temperature": 1.0,
                "response_reported_top_p": 0.98,
                "decoding_config_match": True,
            },
        )

    write_jsonl(root / "registration" / "runtime_jobs.jsonl", jobs)
    write_jsonl(root / "runs" / "results.jsonl", results)

    required = set(MODULE.PROSPECTIVE_REQUIRED_FROZEN_PATHS)
    required.update(
        {
            request_path.relative_to(root).as_posix(),
            candidate_path.relative_to(root).as_posix(),
        }
    )
    for relative in sorted(required):
        path = root / relative
        if path.exists():
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.suffix == ".json":
            write_json(path, {"schema_version": "fixture.v1"})
        elif path.suffix == ".jsonl":
            write_jsonl(path, [])
        else:
            path.write_text(f"frozen fixture for {relative}\n", encoding="utf-8")

    records = []
    for relative in sorted(required):
        path = root / relative
        records.append(
            {
                "path": relative,
                "bytes": path.stat().st_size,
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
        )
    write_json(
        root / "registration" / "freeze.json",
        {"bundle_sha256": bundle, "files": records},
    )
    write_json(root / "registration" / "LAUNCHED", {"registration_bundle_sha256": bundle})

    completed = root / "registration" / "truth" / "completed"
    reviewer_a = completed / "reviewer_a.json"
    reviewer_b = completed / "reviewer_b.json"
    write_json(reviewer_a, {"reviewer_role": "A", "overall_decision": "pass"})
    write_json(reviewer_b, {"reviewer_role": "B", "overall_decision": "pass"})
    (completed / "reviewer_a_findings.md").write_text("Reviewer A passed.\n", encoding="utf-8")
    (completed / "reviewer_b_findings.md").write_text("Reviewer B passed.\n", encoding="utf-8")
    write_json(
        completed / "evidence" / "reviewer_b" / "hard_contract.json",
        {"status": "pass"},
    )
    reviewer_a_sha = hashlib.sha256(reviewer_a.read_bytes()).hexdigest()
    reviewer_b_sha = hashlib.sha256(reviewer_b.read_bytes()).hexdigest()

    for relative in MODULE.PROSPECTIVE_SUPPLEMENTAL_FILES:
        path = root / relative
        if path.exists():
            continue
        write_json(path, {"schema_version": "fixture.v1"})
    write_json(
        root / "analysis" / "truth_comparison.json",
        {
            "review_gate": {
                "launch_authorized": True,
                "truth_join_authorized": True,
                "registration_bundle_sha256": bundle,
                "reviewer_a_sha256": reviewer_a_sha,
                "reviewer_b_sha256": reviewer_b_sha,
            }
        },
    )
def test_bundle_is_anonymous_complete_and_deterministic(tmp_path: Path) -> None:
    task_root = tmp_path / "materialization" / "tasks"
    primary_root = tmp_path / "primary"
    prospective_root = tmp_path / "prospective"
    make_task(task_root)
    make_primary(primary_root)
    make_prospective(prospective_root)
    first = tmp_path / "first.zip"
    second = tmp_path / "second.zip"

    one = MODULE.build_bundle(
        task_root,
        primary_root,
        first,
        1,
        3,
        prospective_root,
        2,
    )
    two = MODULE.build_bundle(
        task_root,
        primary_root,
        second,
        1,
        3,
        prospective_root,
        2,
    )

    assert one["output_sha256"] == two["output_sha256"]
    assert one["task_count"] == 1
    assert one["evidence_rows"] == 3
    assert one["prospective_evidence_rows"] == 2
    verified = MODULE.verify_bundle(first)
    assert verified["status"] == "passed"
    assert verified["evidence_rows"] == 3
    assert verified["prospective_evidence_rows"] == 2
    with zipfile.ZipFile(first) as archive:
        names = archive.namelist()
        readme = archive.read("README.md").decode("utf-8")
        normalized_readme = " ".join(readme.split())
        assert "builder-authored operationalizations" in readme
        assert "does not independently establish fidelity" in normalized_readme
        assert "tasks/TASK-01/atom_registry.json" in names
        assert "SOURCE_SCOPE.json" in names
        source_scope = json.loads(archive.read("SOURCE_SCOPE.json"))
        assert source_scope["tasks"][0]["locator_target"] == (
            "builder-authored bounded source summary"
        )
        assert source_scope["tasks"][0]["independent_original_paper_fidelity_review"] == (
            "not included"
        )
        assert "tasks/TASK-01/artifacts/F.txt" in names
        assert "schedules/SOL1.json" in names
        assert "evidence/SOL1/sol1-exec-01.json" in names
        assert "responses/SOL1/sol1-exec-01.txt" in names
        assert "prospective/registration/freeze.json" in names
        assert "prospective/frozen/runner.py" in names
        assert "prospective/analysis/blinded_decisions.json" in names
        assert "prospective/registration/truth/completed/reviewer_a.json" in names
        assert "prospective/registration/truth/completed/reviewer_b.json" in names
        assert "PROSPECTIVE_EVIDENCE_INDEX.json" in names
        assert "prospective/evidence/pilot/ex3-exec-000000000000000000000001.json" in names
        assert "prospective/responses/confirmatory/ex3-exec-000000000000000000000002.txt" in names
        assert "MANIFEST.json" in names
        for name in names:
            if Path(name).suffix in {".json", ".md", ".txt", ".py"}:
                text = archive.read(name).decode("utf-8")
                if not (
                    name.startswith("responses/")
                    or name.startswith("prospective/responses/")
                    or name.startswith("prospective/frozen/tests/")
                ):
                    assert not MODULE.WINDOWS_ABSOLUTE_PATH.search(text)
                assert not MODULE.FORBIDDEN_OPERATIONAL_TEXT.search(text)


def test_unknown_absolute_path_is_rejected(tmp_path: Path) -> None:
    source = tmp_path / "value.json"
    write_json(source, {"path": r"E:\\private\\unknown.json"})
    with pytest.raises(MODULE.BundleError, match="absolute local path"):
        MODULE.normalized_bytes(source, {}, "value.json")


def test_filesystem_path_preserves_existing_file(tmp_path: Path) -> None:
    source = tmp_path / "value.txt"
    source.write_text("ok", encoding="utf-8")
    usable = MODULE.filesystem_path(source)
    assert usable.is_file()
    assert usable.read_text(encoding="utf-8") == "ok"


def test_public_url_is_not_treated_as_a_windows_drive() -> None:
    MODULE.validate_anonymous_text("https://arxiv.org/pdf/1234.5678", "source.json")


def test_json_escaping_is_validated_after_decoding() -> None:
    value = {"implementation": "def solve(case):\n    return True\n"}
    data = MODULE.normalized_json_value(value, {}, "response.json")
    assert json.loads(data) == value


def test_json_escaped_newline_after_identifier_is_not_a_drive() -> None:
    MODULE.validate_anonymous_text(r'{"code":"if root_v:\\n pass"}', "response.txt")


def test_escaped_regular_expression_is_not_a_unc_path() -> None:
    MODULE.validate_anonymous_text(
        r'{"code":"^(Thought|Action):[ \\\\t]*(.*)$\\n"}', "response.txt"
    )


def test_escaped_newline_character_literal_is_not_a_unc_path() -> None:
    MODULE.validate_anonymous_text(r'{"code":"if \\\\n\\ in line"}', "response.txt")


def test_generated_code_may_contain_drive_like_variable_syntax() -> None:
    MODULE.validate_anonymous_text(
        r'{"code":"if u == v:\\n pass"}',
        "responses/example.txt",
        check_generic_paths=False,
    )


def test_known_identity_path_is_rejected_even_for_response() -> None:
    with pytest.raises(MODULE.BundleError, match="known local identity"):
        MODULE.validate_anonymous_text(
            r"C:\\Users\\Z\\Desktop\\result.txt",
            "responses/example.txt",
            check_generic_paths=False,
        )


def test_credential_shape_requires_a_token_boundary() -> None:
    MODULE.validate_anonymous_text("task-0123456789abcdef01234567", "request.json")
    with pytest.raises(MODULE.BundleError, match="credential-shaped token"):
        MODULE.validate_anonymous_text(
            "credential sk-0123456789abcdef01234567", "request.json"
        )


def test_provider_identity_is_rejected() -> None:
    with pytest.raises(MODULE.BundleError, match="provider identity"):
        MODULE.validate_anonymous_text(
            "https://coderxiaoc.com/v1/responses", "provider.json"
        )


def test_source_scope_rejects_upstream_pdf_locator_claim(tmp_path: Path) -> None:
    task_root = tmp_path / "materialization" / "tasks"
    make_task(task_root)
    task = task_root / "TASK-01"
    registry = json.loads((task / "atom_registry.json").read_text(encoding="utf-8"))
    registry["atoms"][0]["source_locator"]["document_sha256"] = "a" * 64
    write_json(task / "atom_registry.json", registry)

    with pytest.raises(MODULE.BundleError, match="bounded source summary"):
        MODULE.add_source_scope(tmp_path / "staging", task_root, ["TASK-01"])
