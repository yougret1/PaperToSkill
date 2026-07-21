from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import shutil
import sys
import uuid
from collections import Counter
from pathlib import Path

import pytest


RUN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RUN_ROOT))
sys.path.insert(0, str(RUN_ROOT / "src"))

import analyze_confirmation_v4 as analyzer  # noqa: E402
import build_confirmation_v4 as builder  # noqa: E402
import run_confirmation_v4 as scheduler  # noqa: E402


@pytest.fixture
def short_tmp():
    path = RUN_ROOT / "tmp" / f"v4t-{uuid.uuid4().hex[:8]}"
    path.mkdir(parents=True)
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _resolve(raw: str) -> Path:
    path = Path(raw)
    return path.resolve() if path.is_absolute() else (RUN_ROOT / path).resolve()


def test_finite_schedule_and_identity_contract_boundaries():
    admitted = builder.finite_schedule_decision({"B": 2, "F": 16, "S": 16})
    assert admitted["passed"] and admitted["status"] == "Admit"
    rejected = builder.finite_schedule_decision({"B": 3, "F": 18, "S": 18})
    assert not rejected["passed"] and rejected["status"] == "Reject"
    assert not builder.finite_schedule_decision({"B": 0, "F": 15, "S": 16})[
        "passed"
    ]
    assert not builder.finite_schedule_decision({"B": 0, "F": 18, "S": 15})[
        "passed"
    ]
    invalid = builder.finite_schedule_decision(
        {"B": 0, "F": 18, "S": 16}, integrity_passed=False
    )
    assert not invalid["passed"] and invalid["status"] == "Invalid"
    with pytest.raises(ValueError):
        builder.finite_schedule_decision({"B": False, "F": 18, "S": 18})
    with pytest.raises(ValueError):
        builder.finite_schedule_decision({"B": 0, "F": 19, "S": 18})

    passed = builder.identity_instrumentation_decision(
        full_successes=[True] * 6,
        slice_successes=[True] * 5 + [False],
    )
    failed = builder.identity_instrumentation_decision(
        full_successes=[True] * 6,
        slice_successes=[True] * 4 + [False] * 2,
    )
    assert passed["passed"]
    assert not failed["passed"]


def test_builder_freezes_balanced_global_schedule_and_artifact_truth(short_tmp):
    output = short_tmp / "registration"
    registration = builder.build_registration(output)
    preregistration = output / "preregistration.json"
    assert registration == json.loads(preregistration.read_text(encoding="utf-8"))
    assert registration["registered_block_count"] == 60
    assert registration["registered_condition_run_count"] == 180
    schedule = registration["global_interleaved_schedule"]
    assert [row["global_order_index"] for row in schedule] == list(range(1, 61))
    assert Counter(row["family_key"] for row in schedule) == {
        "snap_mfse": 18,
        "toolformer_negative": 18,
        "toolformer_positive": 18,
        "toolformer_identity": 6,
    }
    expected_orders = set(itertools.permutations(("B", "F", "S")))
    for family_key, expected_repetitions in {
        "snap_mfse": 3,
        "toolformer_negative": 3,
        "toolformer_positive": 3,
        "toolformer_identity": 1,
    }.items():
        counts = Counter(
            tuple(row["condition_order"])
            for row in schedule
            if row["family_key"] == family_key
        )
        assert set(counts) == expected_orders
        assert set(counts.values()) == {expected_repetitions}

    families = {}
    for family_key, record in registration["families"].items():
        path = _resolve(record["path"])
        assert path.is_file()
        assert _sha256(path) == record["sha256"]
        family = json.loads(path.read_text(encoding="utf-8"))
        families[family_key] = family
        for key, value in family.items():
            if not key.endswith("_path"):
                continue
            prefix = key.removesuffix("_path")
            digest_key = f"{prefix}_sha256"
            if digest_key not in family:
                continue
            bound = _resolve(value)
            assert bound.is_file(), (family_key, prefix, bound)
            assert _sha256(bound) == family[digest_key]

    positive = families["toolformer_positive"]
    positive_full = _resolve(positive["full_artifact_path"])
    positive_selected = _resolve(positive["selected_artifact_path"])
    assert positive_full.read_bytes().endswith(builder.T06_MARKDOWN.encode("utf-8"))
    assert b"(`T06`)" not in positive_selected.read_bytes()
    positive_map = json.loads(
        _resolve(positive["source_map_path"]).read_text(encoding="utf-8")
    )
    t06 = [row for row in positive_map["atoms"] if row["atom_id"] == "T06"]
    assert len(t06) == 1
    assert t06[0]["novel"] is False
    assert t06[0]["redundancy_status"] == "registered_redundant"

    identity = families["toolformer_identity"]
    assert _resolve(identity["full_artifact_path"]).read_bytes() == _resolve(
        identity["selected_artifact_path"]
    ).read_bytes()
    assert identity["admission_decision_applicable"] is False
    assert identity["expected_admission"] is None
    assert families["snap_mfse"]["expected_admission"] is True
    assert families["toolformer_negative"]["expected_admission"] is False
    assert families["toolformer_positive"]["expected_admission"] is True

    with pytest.raises(FileExistsError):
        builder.build_registration(output)


def _registered_success(family_key: str, condition: str) -> bool:
    if family_key in {"snap_mfse", "toolformer_positive"}:
        return condition in {"F", "S"}
    if family_key == "toolformer_negative":
        return condition == "F"
    if family_key == "toolformer_identity":
        return condition in {"F", "S"}
    raise AssertionError(family_key)


def _fake_runner(args: argparse.Namespace) -> dict:
    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=False)
    family_path = Path(args.confirmation_family).resolve()
    family = json.loads(family_path.read_text(encoding="utf-8"))
    registry = json.loads(Path(args.case_registry).read_text(encoding="utf-8"))
    case_ids = [
        case["case_id"] for case in registry["blocks"]["confirmation_v4"]
    ]
    verified = scheduler.validate_file_bindings(family, root=RUN_ROOT)
    task_prompt = Path(verified["task_prompt"]["path"]).read_text(
        encoding="utf-8"
    ).strip()
    task_prompt_sha256 = hashlib.sha256(task_prompt.encode()).hexdigest()
    context_builder = (
        analyzer.build_snap_context
        if family["task_key"] == "snap_mfse"
        else analyzer.build_toolformer_context
    )
    conditions = {
        condition: {
            "context_sha256": hashlib.sha256(
                context_builder(
                    condition,
                    full_artifact_path=Path(verified["full_artifact"]["path"]),
                    slice_path=Path(verified["selected_artifact"]["path"]),
                ).encode()
            ).hexdigest()
        }
        for condition in args.condition
    }
    public_results = {}
    for condition in args.condition:
        operational_success = _registered_success(args.family_key, condition)
        case_scores = [1 if operational_success else 0 for _ in case_ids]
        task_score = sum(case_scores) / len(case_scores)
        patch = f"--- a/module.py\n+++ b/module.py\n+{args.family_key}:{condition}\n"
        patch_sha256 = hashlib.sha256(patch.encode()).hexdigest()
        turns = [
            {
                "step": 1,
                "retry_lineage_id": f"{args.pair_id}:{condition}:turn-001",
                "prompt_sha256": "2" * 64,
                "response_sha256": "3" * 64,
                "response_text": '{"action":"test"}',
                "action": {
                    "action": "test",
                    "query": None,
                    "path": None,
                    "max_results": None,
                    "start_line": None,
                    "end_line": None,
                    "old_text": None,
                    "new_text": None,
                },
                "observation_status": "public_tested",
                "observation_message": "1 passed in 0.01s",
                "transport_attempts": 1,
                "input_tokens": 10,
                "output_tokens": 2,
                "provider_model_id": args.model_alias,
                "provider_response_id": f"{args.pair_id}:{condition}:test",
                "provider_created": 1,
            },
            {
                "step": 2,
                "retry_lineage_id": f"{args.pair_id}:{condition}:turn-002",
                "prompt_sha256": "4" * 64,
                "response_sha256": "5" * 64,
                "response_text": '{"action":"submit"}',
                "action": {
                    "action": "submit",
                    "query": None,
                    "path": None,
                    "max_results": None,
                    "start_line": None,
                    "end_line": None,
                    "old_text": None,
                    "new_text": None,
                },
                "observation_status": "scored",
                "observation_message": "terminal private score",
                "transport_attempts": 1,
                "input_tokens": 12,
                "output_tokens": 2,
                "provider_model_id": args.model_alias,
                "provider_response_id": f"{args.pair_id}:{condition}:submit",
                "provider_created": 2,
            },
        ]
        metric = {
            "schema_version": f"effectslice-{family['task_key']}-score.test",
            "task_id": family["task_id"],
            "metric_name": "registered_case_pass_rate",
            "block": "confirmation_v4",
            "evidence_boundary": "test fixture",
            "task_score": task_score,
            "success": operational_success,
            "patch_applied": True,
            "contract_passed": True,
            "contract_failures": [],
            "case_scores": case_scores,
            "case_details": [
                {"case_id": case_id, "passed": operational_success}
                for case_id in case_ids
            ],
            "failure_reason": "" if operational_success else "case_failed",
        }
        run_result = {
            "status": "scored",
            "terminal_reason": "submitted",
            "submitted": True,
            "task_score": task_score,
            "success": operational_success,
            "diff_text": patch,
            "state": {
                "max_actions": 16,
                "observations": [
                    {"step": 1, "action": turns[0]["action"], "status": "public_tested", "message": "1 passed in 0.01s"},
                    {"step": 2, "action": turns[1]["action"], "status": "scored", "message": "terminal private score"},
                ],
            },
            "turns": turns,
            "scorer_metrics": [metric],
            "input_tokens": 22,
            "output_tokens": 4,
            "transport_attempts": 2,
            "elapsed_seconds": 0.1,
            "common_scaffold_sha256": "6" * 64,
            "condition_context_sha256": conditions[condition]["context_sha256"],
            "task_prompt_sha256": task_prompt_sha256,
            "private_score_policy": "final_only",
            "private_score_count": 1,
            "private_feedback_exposed": False,
            "public_error": "",
        }
        condition_dir = output / condition
        condition_dir.mkdir()
        _write_json(condition_dir / "run_result.json", run_result)
        _write_json(
            condition_dir / "transcript.json",
            {
                "schema_version": "effectslice-test-transcript.v1",
                "evidence_boundary": builder.EVIDENCE_BOUNDARY,
                "condition": condition,
                "turns": turns,
            },
        )
        (condition_dir / "candidate.patch").write_text(
            patch, encoding="utf-8", newline="\n"
        )
        public_results[condition] = {
            "status": "scored",
            "terminal_reason": "submitted",
            "submitted": True,
            "task_score": task_score,
            "success": operational_success,
            "actions_used": 2,
            "input_tokens": 22,
            "output_tokens": 4,
            "transport_attempts": 2,
            "elapsed_seconds": 0.1,
            "candidate_patch_sha256": patch_sha256,
            "run_result_path": (condition_dir / "run_result.json").as_posix(),
            "transcript_path": (condition_dir / "transcript.json").as_posix(),
            "candidate_patch_path": (condition_dir / "candidate.patch").as_posix(),
            "private_score_policy": "final_only",
            "private_score_count": 1,
            "private_feedback_exposed": False,
        }
    manifest = {
        "schema_version": "effectslice-test-pair.v1",
        "evidence_boundary": builder.EVIDENCE_BOUNDARY,
        "pair_id": args.pair_id,
        "case_block": "confirmation_v4",
        "comparison_role": builder.EVIDENCE_BOUNDARY,
        "condition_execution_order": list(args.condition),
        "conditions": conditions,
        "task_prompt_sha256": task_prompt_sha256,
        "full_artifact_sha256": verified["full_artifact"]["sha256"],
        "atom_map_sha256": verified["source_map"]["sha256"],
        "case_registry_sha256": verified["case_registry"]["sha256"],
        "scorer_sha256": verified["scorer"]["sha256"],
        "slice_artifact_sha256": verified["selected_artifact"]["sha256"],
        "slice_registry_sha256": verified["slice_registry"]["sha256"],
        "retained_atom_ids": family["retained_atom_ids"],
        "verified_family_inputs": verified,
        "workspace_state": {
            **analyzer.workspace_tree_digest(Path(family["workspace_path"])),
            "workspace": Path(family["workspace_path"]).as_posix(),
        },
        "private_score_policy": "final_only",
        "confirmation_family_path": family_path.as_posix(),
        "confirmation_family_sha256": _sha256(family_path),
        "confirmation_case_count": 64,
        "results": public_results,
    }
    report = {
        "schema_version": "effectslice-test-run-report.v1",
        "evidence_boundary": builder.EVIDENCE_BOUNDARY,
        "pair_id": args.pair_id,
        "case_block": "confirmation_v4",
        "comparison_role": builder.EVIDENCE_BOUNDARY,
        "condition_execution_order": list(args.condition),
        "results": public_results,
    }
    _write_json(output / "pair_manifest.json", manifest)
    _write_json(output / "run_report.json", report)
    return report


def test_synthetic_registered_schedule_runs_and_analyzes_end_to_end(short_tmp):
    registration_root = short_tmp / "registration"
    builder.build_registration(registration_root)
    preregistration_path = registration_root / "preregistration.json"
    preregistration_sha256 = _sha256(preregistration_path)
    output_root = short_tmp / "results"
    progress_path = output_root / "confirmation_v4_progress.json"
    progress = scheduler.run_schedule(
        preregistration_path=preregistration_path,
        expected_preregistration_sha256=preregistration_sha256,
        output_root=output_root,
        progress_path=progress_path,
        max_workers=2,
        runner_by_task={
            "snap_mfse": _fake_runner,
            "toolformer_filter": _fake_runner,
        },
        allow_test_injection=True,
    )
    assert progress["counts"] == {
        "completed": 60,
        "failed": 0,
        "preserved": 0,
        "pending": 0,
    }
    analysis_path = short_tmp / "derived" / "analysis.json"
    analysis = analyzer.analyze_schedule(
        preregistration_path=preregistration_path,
        expected_preregistration_sha256=preregistration_sha256,
        output_root=output_root,
        progress_path=progress_path,
        output_path=analysis_path,
        allow_test_input=True,
    )
    assert analysis_path.is_file()
    assert analysis["analysis_status"] == "passed"
    assert analysis["calibration"]["passed"]
    assert analysis["real_candidate_decisions"]["snap_mfse"]["passed"]
    assert not analysis["real_candidate_decisions"]["toolformer_filter"]["passed"]
    assert analysis["resource_summary"]["provider_conversations"] == 180
    assert analysis["resource_summary"]["public_test_requests"] == 180

    first = progress["records"][0]
    run_result_path = Path(first["output_dir"]) / "B" / "run_result.json"
    run_result = json.loads(run_result_path.read_text(encoding="utf-8"))
    test_turn = next(
        turn for turn in run_result["turns"] if turn["action"]["action"] == "test"
    )
    test_turn["observation_status"] = "unavailable"
    _write_json(run_result_path, run_result)
    transcript_path = run_result_path.parent / "transcript.json"
    transcript = json.loads(transcript_path.read_text(encoding="utf-8"))
    transcript_turn = next(
        turn
        for turn in transcript["turns"]
        if turn["action"]["action"] == "test"
    )
    transcript_turn["observation_status"] = "unavailable"
    _write_json(transcript_path, transcript)
    with pytest.raises(analyzer.AnalysisInputError, match="public-test channel"):
        analyzer.analyze_schedule(
            preregistration_path=preregistration_path,
            expected_preregistration_sha256=preregistration_sha256,
            output_root=output_root,
            progress_path=progress_path,
            output_path=analysis_path,
            allow_test_input=True,
        )


def test_scheduler_rejects_wrong_anchor_and_more_than_two_workers(short_tmp):
    registration_root = short_tmp / "registration"
    builder.build_registration(registration_root)
    preregistration_path = registration_root / "preregistration.json"
    with pytest.raises(ValueError, match="external anchor"):
        scheduler.load_and_verify_registration(
            preregistration_path,
            "0" * 64,
            allow_test_registration=True,
        )
    with pytest.raises(ValueError, match=r"\[1, 2\]"):
        scheduler.run_schedule(
            preregistration_path=preregistration_path,
            expected_preregistration_sha256=_sha256(preregistration_path),
            output_root=short_tmp / "results",
            progress_path=short_tmp / "results" / "progress.json",
            max_workers=3,
            runner_by_task={
                "snap_mfse": _fake_runner,
                "toolformer_filter": _fake_runner,
            },
            allow_test_injection=True,
        )
