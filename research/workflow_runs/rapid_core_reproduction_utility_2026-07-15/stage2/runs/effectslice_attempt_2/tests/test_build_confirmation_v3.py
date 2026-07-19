import hashlib
import itertools
import json
import shutil
import sys
import tempfile
from collections import Counter
from pathlib import Path

import pytest


RUN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RUN_ROOT))
sys.path.insert(0, str(RUN_ROOT / "src"))

import build_confirmation_v3 as builder  # noqa: E402
from build_confirmation_v3 import build_family  # noqa: E402
from effectslice.confirmation_v3 import (  # noqa: E402
    sha256_canonical_text,
    sha256_file,
)
from effectslice.toolformer_filter_cases import generate_case  # noqa: E402


EXPECTED_ORDERS = set(itertools.permutations(("B", "F", "S")))
T06_MARKDOWN = (
    "6. **Restate the shared selection invariant** (`T06`)\n"
    "   Apply the same inclusive `margin >= tau_filter` rule independently to every\n"
    "   proposed call and preserve the proposals' original order in the returned\n"
    "   decisions. This restates the registered T04/T05 invariant and introduces no\n"
    "   new computation.\n"
)


REQUIRED_INPUT_FILES = (
    "artifacts/toolformer_filter/full_artifact.md",
    "artifacts/toolformer_filter/source_atom_map.json",
    "artifacts/toolformer_filter/task_prompt.md",
    "artifacts/toolformer_filter/case_registry_v2_r2.json",
    "src/effectslice/toolformer_filter_scorer.py",
    "src/effectslice/aci_runner.py",
    "src/effectslice/aci_protocol.py",
    "src/effectslice/evidence_binding.py",
    "src/effectslice/toolformer_filter_cases.py",
    "run_swe_effectslice.py",
    "confirmation_transport_v3.py",
)
PLANNED_EXECUTABLES = (
    "run_toolformer_filter_confirmation_v3.py",
    "run_confirmation_v3.py",
    "analyze_confirmation_v3.py",
)


def copy_input(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def make_run_root(base: Path, *, complete: bool = False) -> Path:
    run_root = base / "run_root"
    for relative in REQUIRED_INPUT_FILES:
        copy_input(RUN_ROOT / relative, run_root / relative)
    workspace_source = RUN_ROOT / "task_workspaces" / "toolformer_filter_v1"
    workspace_destination = run_root / "task_workspaces" / "toolformer_filter_v1"
    workspace_destination.mkdir(parents=True)
    for name in ("toolformer_filter.py", "test_toolformer_filter_public.py"):
        copy_input(workspace_source / name, workspace_destination / name)
    if complete:
        add_complete_executables(run_root)
    return run_root


def add_complete_executables(run_root: Path) -> None:
    for name in PLANNED_EXECUTABLES:
        (run_root / name).write_text(f"# bound {name}\n", encoding="utf-8")


def registered_output(run_root: Path, control: str) -> Path:
    return (
        run_root
        / "artifacts"
        / "toolformer_filter"
        / "confirmation_v3"
        / control
    )


def bound_path(family: dict, prefix: str, run_root: Path) -> Path:
    path = Path(family[f"{prefix}_path"])
    return path if path.is_absolute() else run_root / path


def build_in_temp(
    control: str,
    *,
    complete: bool = False,
    require_complete_bindings: bool = False,
) -> tuple[tempfile.TemporaryDirectory, Path, Path, dict]:
    temporary = tempfile.TemporaryDirectory()
    run_root = make_run_root(Path(temporary.name), complete=complete)
    output_dir = registered_output(run_root, control)
    kwargs = {"run_root": run_root}
    if require_complete_bindings:
        kwargs["require_complete_bindings"] = True
    family = build_family(control, output_dir, **kwargs)
    return temporary, run_root, output_dir, family


def canonical_case_payload_hash(case: dict) -> str:
    payload = {
        key: value for key, value in case.items() if key not in {"case_id", "seed"}
    }
    canonical = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def all_registry_cases(registry: dict) -> list[dict]:
    return [case for block in registry["blocks"].values() for case in block]


def assert_balanced_schedule(family: dict, expected_repetitions: int) -> None:
    schedule = family["replicate_schedule"]
    counts = Counter(tuple(row["condition_order"]) for row in schedule)
    assert set(counts) == EXPECTED_ORDERS
    assert set(counts.values()) == {expected_repetitions}
    assert [row["replicate_id"] for row in schedule] == [
        f"r{index:03d}" for index in range(1, len(schedule) + 1)
    ]


def test_identity_builds_six_byte_identical_full_and_slice_conditions():
    temporary, run_root, output_dir, family = build_in_temp("identity", complete=True)
    with temporary:
        full_path = bound_path(family, "full_artifact", run_root)
        slice_path = bound_path(family, "selected_artifact", run_root)

        assert family["schema_version"] == "effectslice-confirmation-v3-family.v1"
        assert family["control"] == "identity"
        assert family["conditions"] == ["B", "F", "S"]
        assert family["strict_subset"] is False
        assert family["calibration_role"] == "identity_instrumentation_only"
        assert family["admission_rule"] == "descriptive_only"
        assert family["required_joint_events_for_admission"] is None
        assert family["replicate_count"] == 6
        assert family["schedule_seed"] == 2026071801
        assert_balanced_schedule(family, expected_repetitions=1)

        original_bytes = (
            run_root / "artifacts" / "toolformer_filter" / "full_artifact.md"
        ).read_bytes()
        assert full_path.read_bytes() == original_bytes
        assert slice_path.read_bytes() == original_bytes
        assert family["full_artifact_sha256"] == family["selected_artifact_sha256"]
        assert output_dir == full_path.parent == slice_path.parent


def test_planted_builds_exact_redundant_unit_and_dependency_closed_subset():
    temporary, run_root, _, family = build_in_temp("planted", complete=True)
    with temporary:
        full_path = bound_path(family, "full_artifact", run_root)
        slice_path = bound_path(family, "selected_artifact", run_root)
        source_map = json.loads(
            bound_path(family, "source_map", run_root).read_text(encoding="utf-8")
        )

        assert family["strict_subset"] is True
        assert (
            family["calibration_role"]
            == "planted_redundancy_positive_control"
        )
        assert family["admission_rule"] == "all_registered_joint_events"
        assert family["required_joint_events_for_admission"] == 18
        assert family["replicate_count"] == 18
        assert family["schedule_seed"] == 2026071802
        assert_balanced_schedule(family, expected_repetitions=3)

        original_bytes = (
            run_root / "artifacts" / "toolformer_filter" / "full_artifact.md"
        ).read_bytes()
        assert slice_path.read_bytes() == original_bytes
        assert full_path.read_bytes() == original_bytes + b"\n" + T06_MARKDOWN.encode()
        assert family["full_artifact_sha256"] != family["selected_artifact_sha256"]

        t06 = [atom for atom in source_map["atoms"] if atom["atom_id"] == "T06"]
        assert len(t06) == 1
        assert t06[0]["novel"] is False
        assert t06[0]["redundancy_status"] == "registered_redundant"
        assert source_map["requires"]["T06"] == ["T04", "T05"]
        retained = set(family["retained_atom_ids"])
        assert retained == {"T01", "T02", "T03", "T04", "T05"}
        assert "T06" not in retained
        assert all(
            set(source_map["requires"][atom_id]).issubset(retained)
            for atom_id in retained
        )


@pytest.mark.parametrize("control", ["identity", "planted"])
def test_family_freezes_new_structured_cases_prompt_hashes_and_protocol(control):
    temporary, run_root, _, family = build_in_temp(control, complete=True)
    with temporary:
        case_path = bound_path(family, "case_registry", run_root)
        registry = json.loads(case_path.read_text(encoding="utf-8"))
        cases = registry["blocks"]["confirmation_v3"]
        seeds = registry["generator_inputs"]["seeds"]
        v2_registry = json.loads(
            (
                run_root
                / "artifacts"
                / "toolformer_filter"
                / "case_registry_v2_r2.json"
            ).read_text(encoding="utf-8")
        )
        v2_cases = all_registry_cases(v2_registry)

        assert family["case_block"] == "confirmation_v3"
        assert family["case_count"] == 64
        assert family["case_role"] == "clustered"
        assert len(cases) == len(seeds) == 64
        assert len(set(seeds)) == 64
        assert registry["generator_api"] == (
            "effectslice.toolformer_filter_cases.generate_case"
        )
        assert registry["generator_config_id"].startswith(
            "toolformer_filter_confirmation_v3_"
        )
        assert "generate_case(seed)" in registry["generation_mechanism"]
        assert cases == [generate_case(seed) for seed in seeds]
        assert {case["seed"] for case in cases} == set(seeds)
        assert set(seeds).isdisjoint({case["seed"] for case in v2_cases})
        assert {
            canonical_case_payload_hash(case) for case in cases
        }.isdisjoint(
            {canonical_case_payload_hash(case) for case in v2_cases}
        )

        task_prompt = (
            run_root / "artifacts" / "toolformer_filter" / "task_prompt.md"
        )
        assert family["task_prompt_file_sha256"] == sha256_file(task_prompt)
        assert (
            family["task_prompt_canonical_text_sha256"]
            == sha256_canonical_text(task_prompt)
        )
        assert family["task_prompt_file_sha256"] == hashlib.sha256(
            task_prompt.read_bytes()
        ).hexdigest()
        assert family["task_prompt_canonical_text_sha256"] == hashlib.sha256(
            task_prompt.read_text(encoding="utf-8").strip().encode("utf-8")
        ).hexdigest()

        assert family["decision_basis"] == "finite_registered_schedule"
        assert family["independence_verified"] is False
        assert family["iid_conditional_reference"] == {
            "label": "iid_conditional_only"
        }
        assert family["primary_event"] == "joint_substitution_event"
        assert family["maximum_shortfall"] == 0.05
        assert family["run_success_threshold"] == 0.95
        assert family["private_score_policy"] == "final_only"
        assert family["maximum_transport_attempts"] == 5
        assert family["provider_label"] == "DeepSeek V3.2"
        assert family["base_url"] == "https://api.deepseek.com"
        assert family["model_alias"] == "deepseek-v4-flash"
        assert family["wire_api"] == "openai_chat_completions"
        assert family["temperature"] == 0
        assert family["max_tokens"] == 8192
        assert family["timeout_seconds"] == 240.0
        assert family["retry_delay_seconds"] == 2.0
        assert family["direct_connection"] is True
        assert family["proxy_policy"] == "disabled"
        assert family["registration_status"] == "complete"
        assert family["comparison_role"] == "registered_final_only_confirmation_v3"
        assert family["evidence_boundary"] == "registered_final_only_confirmation_v3"
        assert registry["registration_status"] == "complete"
        assert registry["evidence_boundary"] == "registered_final_only_confirmation_v3"


def test_bindings_hash_existing_inputs_and_mark_missing_v3_executables_planned():
    temporary, run_root, output_dir, family = build_in_temp("identity")
    with temporary:
        required_bindings = {
            "full_artifact",
            "selected_artifact",
            "source_map",
            "case_registry",
            "v2_case_registry",
            "task_prompt",
            "scorer",
            "runner",
            "scheduler",
            "analyzer",
            "aci_runner",
            "aci_protocol",
            "evidence_binding",
            "transport",
            "case_generator",
        }
        assert set(family["bindings"]) == required_bindings

        for prefix in required_bindings - {"task_prompt"}:
            record = family["bindings"][prefix]
            path = bound_path(family, prefix, run_root)
            assert record["path"] == family[f"{prefix}_path"]
            if path.is_file():
                expected = hashlib.sha256(path.read_bytes()).hexdigest()
                assert record["sha256"] == family[f"{prefix}_sha256"] == expected
                assert record["status"] == "bound"
            else:
                assert record == {
                    "path": family[f"{prefix}_path"],
                    "status": "planned_before_preregistration",
                }
                assert f"{prefix}_sha256" not in family

        prompt_record = family["bindings"]["task_prompt"]
        assert prompt_record == {
            "path": family["task_prompt_path"],
            "file_sha256": family["task_prompt_file_sha256"],
            "canonical_text_sha256": family[
                "task_prompt_canonical_text_sha256"
            ],
            "status": "bound",
        }
        assert family["runner_path"] == "run_toolformer_filter_confirmation_v3.py"
        assert family["scheduler_path"] == "run_confirmation_v3.py"
        assert family["analyzer_path"] == "analyze_confirmation_v3.py"
        for prefix in ("runner", "scheduler", "analyzer"):
            assert not (run_root / family[f"{prefix}_path"]).is_file()
            assert family[f"{prefix}_status"] == (
                "planned_before_preregistration"
            )
            assert f"{prefix}_sha256" not in family

        assert family["registration_status"] == "draft_incomplete"
        assert family["comparison_role"] == "planned_confirmation_v3_draft"
        assert family["evidence_boundary"] == "draft_incomplete_confirmation_v3"

        assert family["workspace_path"] == "task_workspaces/toolformer_filter_v1"
        assert len(family["workspace_tree_sha256"]) == 64
        assert family["workspace_file_count"] == 2
        assert json.loads(
            (output_dir / "family.json").read_text(encoding="utf-8")
        ) == family


def test_builder_is_write_once_and_rejects_unknown_controls_without_output():
    with tempfile.TemporaryDirectory() as tmp:
        run_root = make_run_root(Path(tmp), complete=True)
        output_dir = registered_output(run_root, "identity")
        build_family("identity", output_dir, run_root=run_root)
        before = {
            path.relative_to(output_dir): path.read_bytes()
            for path in output_dir.rglob("*")
            if path.is_file()
        }

        with pytest.raises(FileExistsError):
            build_family("identity", output_dir, run_root=run_root)

        after = {
            path.relative_to(output_dir): path.read_bytes()
            for path in output_dir.rglob("*")
            if path.is_file()
        }
        assert after == before

        invalid_output = registered_output(run_root, "unknown")
        with pytest.raises(ValueError, match="unsupported confirmation-v3 control"):
            build_family("unknown", invalid_output, run_root=run_root)
        assert not invalid_output.exists()


def test_mid_build_failure_is_atomic_and_preserves_unrelated_staging(monkeypatch):
    with tempfile.TemporaryDirectory() as tmp:
        run_root = make_run_root(Path(tmp), complete=True)
        output_dir = registered_output(run_root, "identity")
        output_dir.parent.mkdir(parents=True)
        unrelated = output_dir.parent / ".identity.staging-user-owned"
        unrelated.mkdir()
        (unrelated / "marker.txt").write_text("keep", encoding="utf-8")
        real_write = builder._write_json_exclusive

        def fail_on_case_registry(path: Path, payload: dict) -> None:
            if path.name == "case_registry.json":
                raise RuntimeError("injected case-registry write failure")
            real_write(path, payload)

        with monkeypatch.context() as patcher:
            patcher.setattr(builder, "_write_json_exclusive", fail_on_case_registry)
            with pytest.raises(RuntimeError, match="injected case-registry"):
                build_family("identity", output_dir, run_root=run_root)

        assert not output_dir.exists()
        assert (unrelated / "marker.txt").read_text(encoding="utf-8") == "keep"
        assert [
            path
            for path in output_dir.parent.glob(".identity.staging-*")
            if path != unrelated
        ] == []

        build_family("identity", output_dir, run_root=run_root)
        assert (output_dir / "family.json").is_file()
        assert unrelated.is_dir()


def test_later_file_conflict_is_atomic_and_rerunnable(monkeypatch):
    with tempfile.TemporaryDirectory() as tmp:
        run_root = make_run_root(Path(tmp), complete=True)
        output_dir = registered_output(run_root, "planted")
        real_write = builder._write_json_exclusive

        def conflict_on_family(path: Path, payload: dict) -> None:
            if path.name == "family.json":
                path.write_text("preexisting staging conflict", encoding="utf-8")
            real_write(path, payload)

        with monkeypatch.context() as patcher:
            patcher.setattr(builder, "_write_json_exclusive", conflict_on_family)
            with pytest.raises(FileExistsError):
                build_family("planted", output_dir, run_root=run_root)

        assert not output_dir.exists()
        assert list(output_dir.parent.glob(".planted.staging-*")) == []
        family = build_family("planted", output_dir, run_root=run_root)
        assert family["control"] == "planted"


def test_incomplete_bindings_are_draft_and_strict_mode_requires_completion():
    with tempfile.TemporaryDirectory() as tmp:
        run_root = make_run_root(Path(tmp))
        strict_output = registered_output(run_root, "identity")

        with pytest.raises(FileNotFoundError, match="complete.*binding"):
            build_family(
                "identity",
                strict_output,
                run_root=run_root,
                require_complete_bindings=True,
            )
        assert not strict_output.exists()

        add_complete_executables(run_root)
        family = build_family(
            "identity",
            strict_output,
            run_root=run_root,
            require_complete_bindings=True,
        )
        assert family["registration_status"] == "complete"
        assert family["comparison_role"] == "registered_final_only_confirmation_v3"
        assert family["evidence_boundary"] == "registered_final_only_confirmation_v3"
        for prefix in ("runner", "scheduler", "analyzer"):
            assert family["bindings"][prefix]["status"] == "bound"
            assert family[f"{prefix}_sha256"] == sha256_file(run_root / family[f"{prefix}_path"])
        case_registry = json.loads(
            bound_path(family, "case_registry", run_root).read_text(encoding="utf-8")
        )
        source_map = json.loads(
            bound_path(family, "source_map", run_root).read_text(encoding="utf-8")
        )
        assert case_registry["registration_status"] == "complete"
        assert source_map["registration_status"] == "complete"
        assert (
            case_registry["evidence_boundary"]
            == source_map["evidence_boundary"]
            == "registered_final_only_confirmation_v3"
        )


def test_output_path_must_be_exact_registered_control_directory():
    with tempfile.TemporaryDirectory() as tmp:
        run_root = make_run_root(Path(tmp), complete=True)
        confirmation_root = (
            run_root / "artifacts" / "toolformer_filter" / "confirmation_v3"
        )
        wrong_outputs = (
            confirmation_root / "planted",
            confirmation_root / "identity" / "nested",
            run_root / "arbitrary" / "identity",
        )
        for output_dir in wrong_outputs:
            with pytest.raises(ValueError, match="exact confirmation-v3 control"):
                build_family("identity", output_dir, run_root=run_root)
            assert not output_dir.exists()


def test_missing_artifact_atom_is_rejected_before_publication():
    with tempfile.TemporaryDirectory() as tmp:
        run_root = make_run_root(Path(tmp), complete=True)
        artifact = run_root / "artifacts" / "toolformer_filter" / "full_artifact.md"
        artifact.write_text(
            artifact.read_text(encoding="utf-8").replace(" (`T05`)", ""),
            encoding="utf-8",
        )
        output_dir = registered_output(run_root, "identity")

        with pytest.raises(ValueError, match="artifact atom membership"):
            build_family("identity", output_dir, run_root=run_root)
        assert not output_dir.exists()


def test_source_map_dependency_to_missing_atom_is_rejected_before_publication():
    with tempfile.TemporaryDirectory() as tmp:
        run_root = make_run_root(Path(tmp), complete=True)
        source_path = run_root / "artifacts" / "toolformer_filter" / "source_atom_map.json"
        source_map = json.loads(source_path.read_text(encoding="utf-8"))
        source_map["requires"]["T05"] = ["T99"]
        source_path.write_text(json.dumps(source_map), encoding="utf-8")
        output_dir = registered_output(run_root, "identity")

        with pytest.raises(ValueError, match="missing atom T99"):
            build_family("identity", output_dir, run_root=run_root)
        assert not output_dir.exists()


def test_non_dependency_closed_slice_is_rejected_before_publication():
    with tempfile.TemporaryDirectory() as tmp:
        run_root = make_run_root(Path(tmp), complete=True)
        source_path = run_root / "artifacts" / "toolformer_filter" / "source_atom_map.json"
        source_map = json.loads(source_path.read_text(encoding="utf-8"))
        source_map["requires"]["T05"] = ["T04", "T06"]
        source_map["dependency_edges"].append({"from": "T05", "to": "T06"})
        source_path.write_text(json.dumps(source_map), encoding="utf-8")
        output_dir = registered_output(run_root, "planted")

        with pytest.raises(ValueError, match="dependency-closed"):
            build_family("planted", output_dir, run_root=run_root)
        assert not output_dir.exists()


def test_planted_full_and_slice_with_same_atom_membership_are_rejected(
    monkeypatch,
):
    with tempfile.TemporaryDirectory() as tmp:
        run_root = make_run_root(Path(tmp), complete=True)
        output_dir = registered_output(run_root, "planted")
        monkeypatch.setattr(builder, "T06_MARKDOWN", "")

        with pytest.raises(ValueError, match="strict subset"):
            build_family("planted", output_dir, run_root=run_root)
        assert not output_dir.exists()


def test_requires_and_dependency_edges_must_encode_the_same_graph():
    with tempfile.TemporaryDirectory() as tmp:
        run_root = make_run_root(Path(tmp), complete=True)
        source_path = run_root / "artifacts" / "toolformer_filter" / "source_atom_map.json"
        source_map = json.loads(source_path.read_text(encoding="utf-8"))
        source_map["requires"]["T04"] = ["T03", "T05"]
        source_path.write_text(json.dumps(source_map), encoding="utf-8")

        output_dir = registered_output(run_root, "identity")
        with pytest.raises(ValueError, match="same directed graph"):
            build_family("identity", output_dir, run_root=run_root)
        assert not output_dir.exists()


@pytest.mark.parametrize(
    "defect",
    ["duplicate_requires", "duplicate_edge", "self_requires", "self_edge"],
)
def test_dependency_graph_rejects_duplicates_and_self_edges(defect):
    with tempfile.TemporaryDirectory() as tmp:
        run_root = make_run_root(Path(tmp), complete=True)
        source_path = run_root / "artifacts" / "toolformer_filter" / "source_atom_map.json"
        source_map = json.loads(source_path.read_text(encoding="utf-8"))
        if defect == "duplicate_requires":
            source_map["requires"]["T04"].append("T03")
        elif defect == "duplicate_edge":
            source_map["dependency_edges"].append(
                dict(source_map["dependency_edges"][0])
            )
        elif defect == "self_requires":
            source_map["requires"]["T04"].append("T04")
        else:
            source_map["dependency_edges"].append({"from": "T04", "to": "T04"})
        source_path.write_text(json.dumps(source_map), encoding="utf-8")
        output_dir = registered_output(run_root, "identity")

        with pytest.raises(ValueError, match="duplicate|self-edge"):
            build_family("identity", output_dir, run_root=run_root)
        assert not output_dir.exists()


def test_missing_v2_reference_registry_is_rejected_before_publication():
    with tempfile.TemporaryDirectory() as tmp:
        run_root = make_run_root(Path(tmp), complete=True)
        v2_path = (
            run_root
            / "artifacts"
            / "toolformer_filter"
            / "case_registry_v2_r2.json"
        )
        v2_path.unlink()
        output_dir = registered_output(run_root, "identity")

        with pytest.raises(FileNotFoundError, match="case_registry_v2_r2"):
            build_family("identity", output_dir, run_root=run_root)
        assert not output_dir.exists()


@pytest.mark.parametrize(
    ("relative_path", "binding_name"),
    [
        ("src/effectslice/toolformer_filter_cases.py", "case_generator"),
        ("confirmation_transport_v3.py", "transport"),
    ],
)
def test_alternate_run_root_execution_sources_must_match_imported_code(
    relative_path,
    binding_name,
):
    with tempfile.TemporaryDirectory() as tmp:
        run_root = make_run_root(Path(tmp), complete=True)
        claimed_source = run_root / relative_path
        changed = bytearray(claimed_source.read_bytes())
        changed[-1] ^= 1
        claimed_source.write_bytes(changed)
        output_dir = registered_output(run_root, "identity")

        with pytest.raises(ValueError, match=rf"{binding_name}.*execution source"):
            build_family("identity", output_dir, run_root=run_root)
        assert not output_dir.exists()


def test_cli_success_json_exposes_registration_status_and_comparison_role(
    monkeypatch,
    capsys,
):
    family = {
        "control": "identity",
        "case_count": 64,
        "replicate_count": 6,
        "registration_status": "draft_incomplete",
        "comparison_role": "planned_confirmation_v3_draft",
    }
    monkeypatch.setattr(builder, "build_family", lambda *args, **kwargs: family)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "build_confirmation_v3.py",
            "--control",
            "identity",
            "--output-dir",
            "unused",
        ],
    )

    assert builder.main() == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["registration_status"] == "draft_incomplete"
    assert payload["comparison_role"] == "planned_confirmation_v3_draft"


def test_builder_rejects_v3_case_payload_overlap_with_v2():
    with tempfile.TemporaryDirectory() as tmp:
        run_root = make_run_root(Path(tmp), complete=True)
        v2_path = (
            run_root
            / "artifacts"
            / "toolformer_filter"
            / "case_registry_v2_r2.json"
        )
        v2_registry = json.loads(v2_path.read_text(encoding="utf-8"))
        overlap = generate_case(36_000)
        overlap["case_id"] = "v2-metadata-does-not-hide-payload-overlap"
        overlap["seed"] = 99_999
        v2_registry["blocks"]["confirmation_v2"].append(overlap)
        v2_path.write_text(json.dumps(v2_registry), encoding="utf-8")
        output_dir = registered_output(run_root, "identity")

        with pytest.raises(ValueError, match="case payload overlap"):
            build_family("identity", output_dir, run_root=run_root)
        assert not output_dir.exists()
