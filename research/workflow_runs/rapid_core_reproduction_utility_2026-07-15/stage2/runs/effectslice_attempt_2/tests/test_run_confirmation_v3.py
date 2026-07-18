import hashlib
import json
import sys
import threading
from pathlib import Path

import pytest


RUN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RUN_ROOT))
sys.path.insert(0, str(RUN_ROOT / "src"))

import run_confirmation_v3 as scheduler  # noqa: E402
from effectslice.confirmation_v3 import balanced_schedule  # noqa: E402


CONTROL_SPECS = {
    "identity": (2026071801, 6),
    "planted": (2026071802, 18),
}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_family(root: Path, control: str) -> tuple[Path, dict]:
    schedule_seed, replicate_count = CONTROL_SPECS[control]
    runner_path = RUN_ROOT / "run_toolformer_filter_confirmation_v3.py"
    scheduler_path = Path(scheduler.__file__).resolve()
    bindings = {
        "runner": {
            "path": runner_path.as_posix(),
            "sha256": sha256_file(runner_path),
            "status": "bound",
        },
        "scheduler": {
            "path": scheduler_path.as_posix(),
            "sha256": sha256_file(scheduler_path),
            "status": "bound",
        },
    }
    family = {
        "schema_version": "effectslice-confirmation-v3-family.v1",
        "registration_status": "complete",
        "control": control,
        "task_key": "toolformer_filter",
        "task_id": "TOOLFORMER-FILTER",
        "conditions": ["B", "F", "S"],
        "strict_subset": control == "planted",
        "calibration_role": (
            "identity_instrumentation_only"
            if control == "identity"
            else "planted_redundancy_positive_control"
        ),
        "case_block": "confirmation_v3",
        "case_count": 64,
        "decision_basis": "finite_registered_schedule",
        "primary_event": "joint_substitution_event",
        "independence_verified": False,
        "replicate_count": replicate_count,
        "replicate_schedule": balanced_schedule(
            seed=schedule_seed, replicate_count=replicate_count
        ),
        "schedule_seed": schedule_seed,
        "run_success_threshold": 0.95,
        "maximum_shortfall": 0.05,
        "admission_rule": (
            "descriptive_only"
            if control == "identity"
            else "all_registered_joint_events"
        ),
        "required_joint_events_for_admission": (
            None if control == "identity" else 18
        ),
        "private_score_policy": "final_only",
        "maximum_transport_attempts": 5,
        "provider_label": "DeepSeek V3.2",
        "model_alias": "deepseek-v4-flash",
        "wire_api": "openai_chat_completions",
        "temperature": 0,
        "max_tokens": 8192,
        "fresh_provider_conversation_per_condition": True,
        "comparison_role": "registered_final_only_confirmation_v3",
        "evidence_boundary": "registered_final_only_confirmation_v3",
        "bindings": bindings,
        "runner_path": bindings["runner"]["path"],
        "runner_sha256": bindings["runner"]["sha256"],
        "runner_status": "bound",
        "scheduler_path": bindings["scheduler"]["path"],
        "scheduler_sha256": bindings["scheduler"]["sha256"],
        "scheduler_status": "bound",
    }
    family_path = root / f"{control}_family.json"
    family_path.write_text(json.dumps(family), encoding="utf-8")
    return family_path, family


def load_synthetic_family(family_path: Path, replicate_id: str) -> dict:
    family = json.loads(Path(family_path).read_text(encoding="utf-8"))
    assert replicate_id in {
        row["replicate_id"] for row in family["replicate_schedule"]
    }
    return family


def write_completed_bundle(args) -> dict:
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=False)
    manifest = {
        "schema_version": "effectslice-confirmation-v3-pair.v1",
        "completion_status": "complete",
        "pair_id": args.pair_id,
        "control": args.control,
        "family_path": Path(args.family).resolve().as_posix(),
        "family_sha256": sha256_file(args.family),
        "replicate_id": args.replicate_id,
        "condition_execution_order": list(args.condition),
    }
    (output_dir / "pair_manifest.json").write_text(
        json.dumps(manifest), encoding="utf-8"
    )
    return {
        "schema_version": "effectslice-confirmation-v3-run-report.v1",
        "pair_id": args.pair_id,
        "replicate_id": args.replicate_id,
        "condition_execution_order": list(args.condition),
    }


def output_roots(root: Path) -> dict[str, Path]:
    return {
        "identity": root / "raw" / "identity",
        "planted": root / "raw" / "planted",
    }


def test_namespace_uses_registered_order_and_control_specific_output_root(tmp_path):
    family_path, family = write_family(tmp_path, "planted")
    replicate = family["replicate_schedule"][4]

    args = scheduler.build_run_namespace(
        family_path=family_path,
        family=family,
        replicate=replicate,
        output_root=tmp_path / "raw" / "planted",
    )

    assert args.family == family_path.resolve()
    assert args.replicate_id == replicate["replicate_id"]
    assert args.condition == replicate["condition_order"]
    assert args.pair_id == f"confirmation-v3:planted:{replicate['replicate_id']}"
    assert args.output_dir == (
        tmp_path / "raw" / "planted" / replicate["replicate_id"]
    ).resolve()
    assert args.model_alias == "deepseek-v4-flash"
    assert args.max_attempts == 5
    assert args.max_tokens == 8192


def test_family_path_symlink_is_rejected_before_resolution(tmp_path, monkeypatch):
    family_path, _ = write_family(tmp_path, "identity")
    alias_parent = tmp_path / "alias_parent"
    alias_parent.mkdir()
    family_alias = alias_parent / ".." / family_path.name
    original_is_symlink = Path.is_symlink

    def simulated_is_symlink(path):
        if str(path) == str(family_alias):
            return True
        return original_is_symlink(path)

    monkeypatch.setattr(Path, "is_symlink", simulated_is_symlink)

    with pytest.raises(ValueError, match="missing or unsafe"):
        scheduler.run_schedule(
            family_paths=[family_alias],
            output_roots=output_roots(tmp_path),
            runner_by_task={"toolformer_filter": write_completed_bundle},
            family_loader=load_synthetic_family,
            allow_test_injection=True,
        )


def test_explicit_progress_path_symlink_is_rejected_before_resolution(
    tmp_path, monkeypatch
):
    family_path, _ = write_family(tmp_path, "identity")
    alias_parent = tmp_path / "alias_parent"
    alias_parent.mkdir()
    progress_alias = alias_parent / ".." / "confirmation_v3_progress.json"
    original_is_symlink = Path.is_symlink

    def simulated_is_symlink(path):
        if str(path) == str(progress_alias):
            return True
        return original_is_symlink(path)

    monkeypatch.setattr(Path, "is_symlink", simulated_is_symlink)

    with pytest.raises(ValueError, match="progress path must be a regular file"):
        scheduler.run_schedule(
            family_paths=[family_path],
            output_roots=output_roots(tmp_path),
            progress_path=progress_alias,
            runner_by_task={"toolformer_filter": write_completed_bundle},
            family_loader=load_synthetic_family,
            allow_test_injection=True,
        )


def test_fake_runner_and_family_loader_require_explicit_test_injection(tmp_path):
    family_path, _ = write_family(tmp_path, "identity")

    with pytest.raises(ValueError, match="test injection"):
        scheduler.run_schedule(
            family_paths=[family_path],
            output_roots=output_roots(tmp_path),
            runner_by_task={"toolformer_filter": write_completed_bundle},
            family_loader=load_synthetic_family,
        )


def test_production_default_runner_must_still_match_its_registered_binding(
    tmp_path, monkeypatch
):
    monkeypatch.setitem(
        scheduler.DEFAULT_RUNNERS, "toolformer_filter", write_completed_bundle
    )

    with pytest.raises(ValueError, match="default runner.*binding"):
        scheduler.run_schedule(
            family_paths=[tmp_path / "missing-family.json"],
            output_roots=output_roots(tmp_path),
        )


def test_registered_schedule_must_contain_at_least_one_family(tmp_path):
    with pytest.raises(ValueError, match="family_paths.*nonempty"):
        scheduler.run_schedule(
            family_paths=[],
            output_roots=output_roots(tmp_path),
        )


@pytest.mark.parametrize("max_workers", [True, False, 0, 3, -1, 1.5, "2"])
def test_max_workers_must_be_a_non_bool_integer_from_one_to_two(
    tmp_path, max_workers
):
    with pytest.raises(ValueError, match=r"max_workers.*\[1, 2\]"):
        scheduler.run_schedule(
            family_paths=[],
            output_roots=output_roots(tmp_path),
            max_workers=max_workers,
            family_loader=load_synthetic_family,
        )


def test_registered_schedule_keeps_exact_orders_failures_and_denominator(tmp_path):
    identity_path, identity = write_family(tmp_path, "identity")
    planted_path, planted = write_family(tmp_path, "planted")
    roots = output_roots(tmp_path)
    calls = []
    lock = threading.Lock()
    active = 0
    maximum_active = 0

    def fake_runner(args):
        nonlocal active, maximum_active
        with lock:
            active += 1
            maximum_active = max(maximum_active, active)
            calls.append(
                (args.control, args.replicate_id, list(args.condition), args.output_dir)
            )
        try:
            if args.control == "planted" and args.replicate_id == "r002":
                raise RuntimeError("secret-test-value-must-not-leak")
            return write_completed_bundle(args)
        finally:
            with lock:
                active -= 1

    result = scheduler.run_schedule(
        family_paths=[identity_path, planted_path],
        output_roots=roots,
        max_workers=2,
        runner_by_task={"toolformer_filter": fake_runner},
        family_loader=load_synthetic_family,
        allow_test_injection=True,
    )

    expected_rows = [
        (family["control"], row["replicate_id"], row["condition_order"])
        for family in (identity, planted)
        for row in family["replicate_schedule"]
    ]
    observed = {(control, replicate_id): order for control, replicate_id, order, _ in calls}
    assert [
        (control, replicate_id, observed[(control, replicate_id)])
        for control, replicate_id, _ in expected_rows
    ] == expected_rows
    assert maximum_active <= 2
    assert result["schema_version"] == "effectslice-confirmation-v3-progress.v1"
    assert result["registered_schedule_length"] == 24
    assert result["counts"] == {"completed": 23, "failed": 1, "preserved": 0}
    assert sum(result["counts"].values()) == result["registered_schedule_length"]
    assert [(row["control"], row["replicate_id"]) for row in result["records"]] == [
        (control, replicate_id) for control, replicate_id, _ in expected_rows
    ]

    failed = [row for row in result["records"] if row["status"] == "failed"]
    assert len(failed) == 1
    assert (failed[0]["control"], failed[0]["replicate_id"]) == (
        "planted",
        "r002",
    )
    assert "secret-test-value" not in json.dumps(failed)
    registered_ids = {
        (control, row["replicate_id"])
        for control, family in (("identity", identity), ("planted", planted))
        for row in family["replicate_schedule"]
    }
    assert {
        (row["control"], row["replicate_id"]) for row in result["records"]
    } == registered_ids
    for control, replicate_id, _, output_dir in calls:
        assert Path(output_dir).parent == roots[control].resolve()
        assert Path(output_dir).name == replicate_id

    stored = json.loads(
        (tmp_path / "raw" / "confirmation_v3_progress.json").read_text(
            encoding="utf-8"
        )
    )
    assert stored == result


def test_same_raw_roots_cannot_run_concurrently_with_different_progress_paths(
    tmp_path,
):
    family_path, _ = write_family(tmp_path, "identity")
    roots = output_roots(tmp_path)
    entered = threading.Event()
    release = threading.Event()
    background_errors = []

    def blocking_runner(args):
        if args.replicate_id == "r001":
            entered.set()
            if not release.wait(timeout=5):
                raise TimeoutError("test did not release the scheduler")
        return write_completed_bundle(args)

    def run_in_background():
        try:
            scheduler.run_schedule(
                family_paths=[family_path],
                output_roots=roots,
                max_workers=1,
                runner_by_task={"toolformer_filter": blocking_runner},
                family_loader=load_synthetic_family,
                allow_test_injection=True,
            )
        except Exception as exc:  # Captured for an assertion on the test thread.
            background_errors.append(exc)

    thread = threading.Thread(target=run_in_background)
    thread.start()
    assert entered.wait(timeout=5)
    try:
        with pytest.raises(ValueError, match="scheduler.*already active"):
            scheduler.run_schedule(
                family_paths=[family_path],
                output_roots=roots,
                max_workers=1,
                progress_path=tmp_path / "alternate-progress.json",
                runner_by_task={"toolformer_filter": write_completed_bundle},
                family_loader=load_synthetic_family,
                allow_test_injection=True,
            )
    finally:
        release.set()
        thread.join(timeout=10)

    assert not thread.is_alive()
    assert background_errors == []


def test_resume_preserves_completed_bundles_and_prior_failed_records(tmp_path):
    family_path, family = write_family(tmp_path, "identity")
    roots = output_roots(tmp_path)
    calls = []

    def first_runner(args):
        calls.append(args.replicate_id)
        if args.replicate_id == "r003":
            raise OSError("offline")
        return write_completed_bundle(args)

    first = scheduler.run_schedule(
        family_paths=[family_path],
        output_roots=roots,
        runner_by_task={"toolformer_filter": first_runner},
        family_loader=load_synthetic_family,
        allow_test_injection=True,
    )
    preserved_manifest = roots["identity"] / "r001" / "pair_manifest.json"
    original_bytes = preserved_manifest.read_bytes()

    def forbidden_runner(args):
        raise AssertionError(f"resume reran {args.replicate_id}")

    second = scheduler.run_schedule(
        family_paths=[family_path],
        output_roots=roots,
        runner_by_task={"toolformer_filter": forbidden_runner},
        family_loader=load_synthetic_family,
        allow_test_injection=True,
    )

    assert first["counts"] == {"completed": 5, "failed": 1, "preserved": 0}
    assert second["counts"] == {"completed": 0, "failed": 1, "preserved": 5}
    assert len(calls) == family["replicate_count"]
    assert preserved_manifest.read_bytes() == original_bytes
    failed = next(row for row in second["records"] if row["status"] == "failed")
    assert failed["replicate_id"] == "r003"
    assert sum(second["counts"].values()) == family["replicate_count"]


def test_resume_preserves_failures_when_final_progress_write_was_interrupted(
    tmp_path, monkeypatch
):
    family_path, family = write_family(tmp_path, "identity")
    roots = output_roots(tmp_path)
    original_write_progress = scheduler._write_progress

    def first_runner(args):
        if args.replicate_id == "r003":
            raise OSError("offline")
        return write_completed_bundle(args)

    monkeypatch.setattr(
        scheduler,
        "_write_progress",
        lambda progress_path, records: (_ for _ in ()).throw(
            OSError("progress write interrupted")
        ),
    )
    with pytest.raises(OSError, match="progress write interrupted"):
        scheduler.run_schedule(
            family_paths=[family_path],
            output_roots=roots,
            runner_by_task={"toolformer_filter": first_runner},
            family_loader=load_synthetic_family,
            allow_test_injection=True,
        )
    monkeypatch.setattr(scheduler, "_write_progress", original_write_progress)

    reruns = []

    def forbidden_runner(args):
        reruns.append(args.replicate_id)
        raise AssertionError(f"resume reran {args.replicate_id}")

    resumed = scheduler.run_schedule(
        family_paths=[family_path],
        output_roots=roots,
        runner_by_task={"toolformer_filter": forbidden_runner},
        family_loader=load_synthetic_family,
        allow_test_injection=True,
    )

    assert reruns == []
    assert resumed["counts"] == {"completed": 0, "failed": 1, "preserved": 5}
    assert len(resumed["records"]) == family["replicate_count"]


def test_resume_cleans_an_atomic_journal_temp_left_by_a_crash(tmp_path):
    family_path, family = write_family(tmp_path, "identity")
    roots = output_roots(tmp_path)
    progress_path = tmp_path / "raw" / "confirmation_v3_progress.json"

    scheduler.run_schedule(
        family_paths=[family_path],
        output_roots=roots,
        runner_by_task={"toolformer_filter": write_completed_bundle},
        family_loader=load_synthetic_family,
        allow_test_injection=True,
    )
    progress_path.unlink()
    journal = scheduler._journal_directory(progress_path)
    stale = journal / ".i-r001.json.999.abcdef123456.tmp"
    stale.write_text("partial", encoding="utf-8")
    reruns = []

    resumed = scheduler.run_schedule(
        family_paths=[family_path],
        output_roots=roots,
        runner_by_task={
            "toolformer_filter": lambda args: reruns.append(args.replicate_id)
        },
        family_loader=load_synthetic_family,
        allow_test_injection=True,
    )

    assert reruns == []
    assert not stale.exists()
    assert resumed["counts"] == {
        "completed": 0,
        "failed": 0,
        "preserved": family["replicate_count"],
    }


def test_resume_rejects_an_unsanitized_prior_error_type(tmp_path):
    family_path, _ = write_family(tmp_path, "identity")
    roots = output_roots(tmp_path)
    progress_path = tmp_path / "raw" / "confirmation_v3_progress.json"

    scheduler.run_schedule(
        family_paths=[family_path],
        output_roots=roots,
        runner_by_task={
            "toolformer_filter": lambda args: (_ for _ in ()).throw(
                RuntimeError("private-provider-detail")
            )
        },
        family_loader=load_synthetic_family,
        allow_test_injection=True,
    )
    progress = json.loads(progress_path.read_text(encoding="utf-8"))
    progress["records"][0]["error_type"] = "private provider detail"
    progress_path.write_text(json.dumps(progress), encoding="utf-8")

    with pytest.raises(ValueError, match="error_type"):
        scheduler.run_schedule(
            family_paths=[family_path],
            output_roots=roots,
            runner_by_task={
                "toolformer_filter": lambda args: pytest.fail(
                    f"resume reran {args.replicate_id}"
                )
            },
            family_loader=load_synthetic_family,
            allow_test_injection=True,
        )


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (lambda family: family.update(conditions=["B", "S", "F"]), "conditions"),
        (
            lambda family: family["replicate_schedule"][1].update(
                replicate_id="r001"
            ),
            "replicate",
        ),
        (
            lambda family: family["bindings"]["runner"].update(sha256="0" * 64),
            "runner.*binding",
        ),
        (
            lambda family: family["bindings"]["scheduler"].update(
                path=(RUN_ROOT / "run_confirmation_v2.py").as_posix()
            ),
            "scheduler.*binding",
        ),
    ],
)
def test_family_schedule_metadata_and_execution_bindings_fail_closed(
    tmp_path, mutation, message
):
    family_path, family = write_family(tmp_path, "identity")
    mutation(family)
    family_path.write_text(json.dumps(family), encoding="utf-8")
    calls = []

    with pytest.raises(ValueError, match=message):
        scheduler.run_schedule(
            family_paths=[family_path],
            output_roots=output_roots(tmp_path),
            runner_by_task={"toolformer_filter": calls.append},
            family_loader=load_synthetic_family,
            allow_test_injection=True,
        )

    assert calls == []


def test_family_bytes_cannot_change_between_validation_and_scheduling(tmp_path):
    family_path, _ = write_family(tmp_path, "identity")
    calls = []

    def mutating_loader(path, replicate_id):
        verified = load_synthetic_family(path, replicate_id)
        mutated = dict(verified)
        mutated["provider_label"] = "different provider"
        path.write_text(json.dumps(mutated), encoding="utf-8")
        return verified

    with pytest.raises(ValueError, match="changed during validation"):
        scheduler.run_schedule(
            family_paths=[family_path],
            output_roots=output_roots(tmp_path),
            runner_by_task={"toolformer_filter": calls.append},
            family_loader=mutating_loader,
            allow_test_injection=True,
        )

    assert calls == []


def test_existing_incomplete_bundle_becomes_an_explicit_failure(tmp_path):
    family_path, family = write_family(tmp_path, "identity")
    roots = output_roots(tmp_path)
    incomplete = roots["identity"] / "r004"
    incomplete.mkdir(parents=True)
    (incomplete / "pair_manifest.pre_run.json").write_text("{}", encoding="utf-8")
    calls = []

    result = scheduler.run_schedule(
        family_paths=[family_path],
        output_roots=roots,
        runner_by_task={
            "toolformer_filter": lambda args: (
                calls.append(args.replicate_id),
                write_completed_bundle(args),
            )[1]
        },
        family_loader=load_synthetic_family,
        allow_test_injection=True,
    )

    record = next(row for row in result["records"] if row["replicate_id"] == "r004")
    assert record["status"] == "failed"
    assert record["error_type"] == "IncompleteBundle"
    assert "r004" not in calls
    assert len(result["records"]) == family["replicate_count"]
