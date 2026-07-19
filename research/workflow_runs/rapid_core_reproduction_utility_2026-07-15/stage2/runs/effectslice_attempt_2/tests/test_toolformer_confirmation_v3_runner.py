from __future__ import annotations

import argparse
import dataclasses
import hashlib
import importlib.util
import json
import math
import os
import shutil
import sys
import time
from pathlib import Path
from typing import Any

import pytest


RUN_ROOT = Path(__file__).resolve().parents[1]
RUNNER_PATH = RUN_ROOT / "run_toolformer_filter_confirmation_v3.py"
sys.path.insert(0, str(RUN_ROOT))
sys.path.insert(0, str(RUN_ROOT / "src"))

from effectslice.aci_runner import ModelTurnResult  # noqa: E402
from effectslice.confirmation_v3 import (  # noqa: E402
    balanced_schedule,
    sha256_canonical_text,
    sha256_file,
)
from effectslice.toolformer_filter_cases import generate_case  # noqa: E402
from run_swe_effectslice import workspace_tree_digest  # noqa: E402


REGISTERED = "registered_final_only_confirmation_v3"
REGISTERED_BASE_URL = "https://api.deepseek.com"
SECRET_API_KEY = "do-not-serialize-this-key"


def load_runner_module():
    assert RUNNER_PATH.is_file(), "confirmation-v3 runner has not been implemented"
    spec = importlib.util.spec_from_file_location(
        "run_toolformer_filter_confirmation_v3_under_test", RUNNER_PATH
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_bytes(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def relative(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def stored_path(path: Path, root: Path) -> str:
    try:
        return relative(path, root)
    except ValueError:
        return path.resolve().as_posix()


class FakeTransport:
    instances: list["FakeTransport"] = []
    fail_condition: str | None = None

    def __init__(self, **kwargs: Any) -> None:
        self.kwargs = kwargs
        self.calls: list[dict[str, Any]] = []
        type(self).instances.append(self)

    def public_config(self) -> dict[str, Any]:
        return {
            "base_url": self.kwargs["base_url"],
            "api_key": self.kwargs["api_key"],
            "model_alias": self.kwargs["model_alias"],
            "wire_api": self.kwargs["wire_api"],
            "max_tokens": self.kwargs["max_tokens"],
            "timeout_seconds": self.kwargs["timeout_seconds"],
            "max_attempts": self.kwargs["max_attempts"],
            "retry_delay_seconds": self.kwargs["retry_delay_seconds"],
            "temperature": 0,
            "direct_connection": True,
            "proxy_policy": "disabled",
        }

    def __call__(
        self, *, prompt: str, retry_lineage_id: str, turn_index: int
    ) -> ModelTurnResult:
        condition = retry_lineage_id.split(":")[-2]
        call = {
            "prompt": prompt,
            "retry_lineage_id": retry_lineage_id,
            "turn_index": turn_index,
            "condition": condition,
        }
        self.calls.append(call)
        if condition == type(self).fail_condition:
            raise RuntimeError("injected transport failure")
        responses = {
            1: json.dumps(
                {
                    "action": "open",
                    "path": "toolformer_filter.py",
                    "start_line": 1,
                    "end_line": 20,
                }
            ),
            2: json.dumps(
                {
                    "action": "edit",
                    "path": "toolformer_filter.py",
                    "old_text": '    raise NotImplementedError("todo")',
                    "new_text": "    return None",
                }
            ),
            3: json.dumps({"action": "test"}),
            4: json.dumps({"action": "submit"}),
        }
        return ModelTurnResult(
            status="success",
            response_text=responses[turn_index],
            attempts=1,
            input_tokens=10,
            output_tokens=3,
            provider_model_id="deepseek-v4-flash",
            provider_response_id=f"fake-{len(self.calls)}",
            provider_created=1,
        )


@pytest.fixture(autouse=True)
def reset_fake_transport(monkeypatch):
    FakeTransport.instances = []
    FakeTransport.fail_condition = None
    monkeypatch.setenv("TEST_DEEPSEEK_BASE_URL", REGISTERED_BASE_URL)
    monkeypatch.setenv("TEST_DEEPSEEK_API_KEY", SECRET_API_KEY)


@pytest.fixture
def runner():
    return load_runner_module()


def build_family_tree(
    tmp_path: Path,
    *,
    control: str = "identity",
    registration_status: str = "complete",
    order: list[str] | None = None,
):
    root = tmp_path / f"copied_run_root_{control}"
    artifact_dir = root / "artifacts" / "toolformer_filter" / "confirmation_v3" / control
    full = artifact_dir / "full_artifact.md"
    selected = artifact_dir / "selected_artifact.md"
    full_text = "1. **Base invariant** (`T01`)\n"
    if control == "planted":
        full_text += "2. **Redundant restatement** (`T02`)\n"
    selected_text = "1. **Base invariant** (`T01`)\n"
    write_bytes(full, full_text.encode("utf-8"))
    write_bytes(selected, selected_text.encode("utf-8"))

    source_map = artifact_dir / "source_atom_map.json"
    case_registry = artifact_dir / "case_registry.json"
    reference_registry = root / "artifacts" / "toolformer_filter" / "case_registry_v2_r2.json"
    task_prompt = root / "artifacts" / "toolformer_filter" / "task_prompt.md"
    source_atoms = [{"atom_id": "T01", "title": "Base invariant"}]
    requires = {"T01": []}
    dependency_edges: list[dict[str, str]] = []
    if control == "planted":
        source_atoms.append(
            {"atom_id": "T02", "title": "Redundant restatement"}
        )
        requires["T02"] = ["T01"]
        dependency_edges.append({"from": "T02", "to": "T01"})
    write_json(
        source_map,
        {
            "schema_version": "test-source-map.v1",
            "atoms": source_atoms,
            "requires": requires,
            "dependency_edges": dependency_edges,
        },
    )
    write_json(
        case_registry,
        {
            "schema_version": "test-case-registry.v3",
            "blocks": {
                "confirmation_v3": [
                    generate_case(seed) for seed in range(36_004, 36_068)
                ]
            },
        },
    )
    write_json(reference_registry, {"schema_version": "test-reference.v2"})
    write_bytes(task_prompt, b"LOCKED TASK PROMPT\n\n")

    execution_sources = {
        "scorer": RUN_ROOT / "src" / "effectslice" / "toolformer_filter_scorer.py",
        "aci_runner": RUN_ROOT / "src" / "effectslice" / "aci_runner.py",
        "aci_protocol": RUN_ROOT / "src" / "effectslice" / "aci_protocol.py",
        "case_generator": RUN_ROOT / "src" / "effectslice" / "toolformer_filter_cases.py",
        "transport": RUN_ROOT / "confirmation_transport_v3.py",
        "runner": RUNNER_PATH,
    }
    evidence_binding = root / "src" / "effectslice" / "evidence_binding.py"
    evidence_binding.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(
        RUN_ROOT / "src" / "effectslice" / "evidence_binding.py",
        evidence_binding,
    )
    destinations = {**execution_sources, "evidence_binding": evidence_binding}

    scheduler = root / "run_confirmation_v3.py"
    analyzer = root / "analyze_confirmation_v3.py"
    write_bytes(scheduler, b"# registered scheduler\n")
    write_bytes(analyzer, b"# registered analyzer\n")
    destinations.update({"scheduler": scheduler, "analyzer": analyzer})

    workspace = root / "task_workspaces" / "toolformer_filter_v1"
    write_bytes(
        workspace / "toolformer_filter.py",
        (
            "def filter_api_calls(logp_with_result, logp_call_only, "
            "logp_no_call, tau_filter):\n"
            '    raise NotImplementedError("todo")\n'
        ).encode("utf-8"),
    )
    workspace_state = workspace_tree_digest(workspace)

    bound_paths = {
        "full_artifact": full,
        "selected_artifact": selected,
        "source_map": source_map,
        "case_registry": case_registry,
        "v2_case_registry": reference_registry,
        **destinations,
    }
    bindings = {
        name: {
            "path": stored_path(path, root),
            "sha256": sha256_file(path),
            "status": "bound",
        }
        for name, path in bound_paths.items()
    }
    bindings["task_prompt"] = {
        "path": relative(task_prompt, root),
        "file_sha256": sha256_file(task_prompt),
        "canonical_text_sha256": sha256_canonical_text(task_prompt),
        "status": "bound",
    }

    schedule = balanced_schedule(seed=2026071801, replicate_count=6)
    schedule[0]["condition_order"] = order or ["S", "F", "B"]
    family: dict[str, Any] = {
        "schema_version": "effectslice-confirmation-v3-family.v1",
        "registration_status": registration_status,
        "control": control,
        "task_key": "toolformer_filter",
        "task_id": "TOOLFORMER-FILTER",
        "conditions": ["B", "F", "S"],
        "strict_subset": control == "planted",
        "case_block": "confirmation_v3",
        "case_count": 64,
        "decision_basis": "finite_registered_schedule",
        "primary_event": "joint_substitution_event",
        "independence_verified": False,
        "replicate_count": 6,
        "replicate_schedule": schedule,
        "run_success_threshold": 0.95,
        "maximum_shortfall": 0.05,
        "required_joint_events_for_admission": (
            None if control == "identity" else 6
        ),
        "private_score_policy": "final_only",
        "maximum_transport_attempts": 5,
        "provider_label": "DeepSeek V3.2",
        "base_url": REGISTERED_BASE_URL,
        "model_alias": "deepseek-v4-flash",
        "wire_api": "openai_chat_completions",
        "temperature": 0,
        "max_tokens": 8192,
        "timeout_seconds": 240.0,
        "retry_delay_seconds": 2.0,
        "direct_connection": True,
        "proxy_policy": "disabled",
        "comparison_role": REGISTERED if registration_status == "complete" else "planned_confirmation_v3_draft",
        "evidence_boundary": REGISTERED if registration_status == "complete" else "draft_incomplete_confirmation_v3",
        "bindings": bindings,
        "task_prompt_path": relative(task_prompt, root),
        "task_prompt_status": "bound",
        "task_prompt_file_sha256": sha256_file(task_prompt),
        "task_prompt_canonical_text_sha256": sha256_canonical_text(task_prompt),
        "workspace_path": relative(workspace, root),
        "workspace_tree_sha256": workspace_state["sha256"],
        "workspace_file_count": workspace_state["file_count"],
        "workspace_total_bytes": workspace_state["total_bytes"],
        "workspace_excluded_directory_names": workspace_state[
            "excluded_directory_names"
        ],
    }
    for name, record in bindings.items():
        if name == "task_prompt":
            continue
        family[f"{name}_path"] = record["path"]
        family[f"{name}_sha256"] = record["sha256"]
        family[f"{name}_status"] = record["status"]

    family_path = artifact_dir / "family.json"
    write_json(family_path, family)
    return argparse.Namespace(
        root=root,
        family_path=family_path,
        family=family,
        full=full,
        selected=selected,
        source_map=source_map,
        case_registry=case_registry,
        task_prompt=task_prompt,
        workspace=workspace,
    )


def make_args(tree, output_dir: Path, **overrides: Any) -> argparse.Namespace:
    values = {
        "family": tree.family_path,
        "replicate_id": "r001",
        "output_dir": output_dir,
        "model_alias": "deepseek-v4-flash",
        "base_url_env": "TEST_DEEPSEEK_BASE_URL",
        "api_key_env": "TEST_DEEPSEEK_API_KEY",
        "max_tokens": 8192,
        "timeout_seconds": 240.0,
        "scorer_timeout_seconds": 300.0,
        "max_attempts": 5,
        "retry_delay_seconds": 2.0,
    }
    values.update(overrides)
    return argparse.Namespace(**values)


def mutate_family(tree, mutation) -> None:
    family = json.loads(tree.family_path.read_text(encoding="utf-8"))
    mutation(family)
    write_json(tree.family_path, family)


def rebind_file(tree, name: str, path: Path) -> None:
    family = json.loads(tree.family_path.read_text(encoding="utf-8"))
    digest = sha256_file(path)
    family["bindings"][name]["path"] = stored_path(path, tree.root)
    family["bindings"][name]["sha256"] = digest
    family[f"{name}_path"] = family["bindings"][name]["path"]
    family[f"{name}_sha256"] = digest
    write_json(tree.family_path, family)


def rebind_task_prompt(tree) -> None:
    family = json.loads(tree.family_path.read_text(encoding="utf-8"))
    file_digest = sha256_file(tree.task_prompt)
    try:
        canonical_digest = sha256_canonical_text(tree.task_prompt)
    except UnicodeDecodeError:
        canonical_digest = hashlib.sha256(tree.task_prompt.read_bytes()).hexdigest()
    binding = family["bindings"]["task_prompt"]
    binding["file_sha256"] = file_digest
    binding["canonical_text_sha256"] = canonical_digest
    family["task_prompt_file_sha256"] = file_digest
    family["task_prompt_canonical_text_sha256"] = canonical_digest
    write_json(tree.family_path, family)


def context_section(prompt: str) -> str:
    marker = "# Condition Context\n\n"
    tail = prompt.split(marker, 1)[1]
    return tail.split("\n\n# Locked Task", 1)[0]


def test_draft_family_is_rejected_before_transport_construction(runner, tmp_path):
    tree = build_family_tree(tmp_path, registration_status="draft_incomplete")
    with pytest.raises(ValueError, match="registration_status"):
        runner.run_bundle(
            make_args(tree, tmp_path / "draft-output"),
            transport_factory=FakeTransport,
        )
    assert FakeTransport.instances == []


@pytest.mark.parametrize("control", ["identity", "planted"])
def test_complete_identity_and_planted_families_are_accepted(runner, tmp_path, control):
    tree = build_family_tree(tmp_path, control=control)
    verified = runner.load_and_verify_family(tree.family_path, "r001")
    assert verified["control"] == control
    assert verified["registered_replicate"]["condition_order"] == ["S", "F", "B"]


def test_task_prompt_canonical_digest_normalizes_windows_newlines(runner, tmp_path):
    tree = build_family_tree(tmp_path)
    tree.task_prompt.write_bytes(b"LOCKED TASK PROMPT\r\n\r\n")
    rebind_task_prompt(tree)

    verified = runner.load_and_verify_family(tree.family_path, "r001")

    assert verified["task_prompt_file_sha256"] == sha256_file(tree.task_prompt)
    assert verified["task_prompt_canonical_text_sha256"] == sha256_canonical_text(
        tree.task_prompt
    )


def test_run_preserves_registered_order_context_and_manifest_semantics(runner, tmp_path):
    tree = build_family_tree(tmp_path, control="planted", order=["S", "F", "B"])
    output = tmp_path / "bundle"
    report = runner.run_bundle(make_args(tree, output), transport_factory=FakeTransport)

    assert report["condition_execution_order"] == ["S", "F", "B"]
    transport = FakeTransport.instances[0]
    assert [call["condition"] for call in transport.calls[::4]] == ["S", "F", "B"]
    first_prompts = {call["condition"]: call["prompt"] for call in transport.calls[::4]}
    assert context_section(first_prompts["S"]) == tree.selected.read_text(encoding="utf-8").strip()
    assert context_section(first_prompts["F"]) == tree.full.read_text(encoding="utf-8").strip()
    assert context_section(first_prompts["B"]) == runner.NO_ARTIFACT_CONTEXT
    for condition, prompt in first_prompts.items():
        visible_context = context_section(prompt)
        assert f"Condition {condition}" not in visible_context
        assert "S/F/B" not in visible_context

    pre = json.loads((output / "pair_manifest.pre_run.json").read_text(encoding="utf-8"))
    final = json.loads((output / "pair_manifest.json").read_text(encoding="utf-8"))
    assert pre["schema_version"] == "effectslice-confirmation-v3-pair.v1"
    assert pre["comparison_role"] == REGISTERED
    assert pre["evidence_boundary"] == REGISTERED
    assert pre["decision_basis"] == "finite_registered_schedule"
    assert pre["independence_verified"] is False
    assert pre["primary_event"] == "joint_substitution_event"
    assert pre["private_score_policy"] == "final_only"
    assert pre["family_path"] == tree.family_path.resolve().as_posix()
    assert pre["family_sha256"] == sha256_file(tree.family_path)
    assert pre["replicate_id"] == "r001"
    assert pre["condition_execution_order"] == ["S", "F", "B"]
    assert pre["task_prompt_file_sha256"] == sha256_file(tree.task_prompt)
    assert pre["task_prompt_canonical_text_sha256"] == sha256_canonical_text(tree.task_prompt)
    assert pre["task_prompt_file_sha256"] != pre["task_prompt_canonical_text_sha256"]
    assert pre["full_artifact_sha256"] == sha256_file(tree.full)
    assert pre["selected_artifact_sha256"] == sha256_file(tree.selected)
    assert pre["conditions"]["F"]["context_sha256"] == hashlib.sha256(
        tree.full.read_text(encoding="utf-8").strip().encode("utf-8")
    ).hexdigest()
    assert pre["conditions"]["S"]["context_sha256"] == hashlib.sha256(
        tree.selected.read_text(encoding="utf-8").strip().encode("utf-8")
    ).hexdigest()
    assert pre["workspace_state"]["sha256"] == workspace_tree_digest(tree.workspace)["sha256"]
    assert pre["provider_config"]["model_alias"] == "deepseek-v4-flash"
    assert pre["provider_config"]["temperature"] == 0
    assert pre["provider_config"]["max_attempts"] == 5
    assert pre["conditions"]["S"]["retry_lineage_prefix"].endswith(":S")
    assert final["completion_status"] == "complete"
    assert list(final["results"]) == ["S", "F", "B"]


def test_actual_runner_and_every_required_binding_are_verified(runner, tmp_path):
    tree = build_family_tree(tmp_path)
    verified = runner.load_and_verify_family(tree.family_path, "r001")
    assert verified["verified_bindings"]["runner"]["sha256"] == sha256_file(RUNNER_PATH)
    assert set(runner.REQUIRED_BINDINGS).issubset(verified["verified_bindings"])
    for record in verified["verified_bindings"].values():
        assert Path(record["path"]).is_file()
        assert sha256_file(Path(record["path"])) == record["sha256"]


def test_rerun_rejects_without_extra_provider_calls_or_overwrite(runner, tmp_path):
    tree = build_family_tree(tmp_path)
    output = tmp_path / "write-once"
    args = make_args(tree, output)
    runner.run_bundle(args, transport_factory=FakeTransport)
    before = (output / "pair_manifest.pre_run.json").read_bytes()
    call_count = len(FakeTransport.instances[0].calls)

    with pytest.raises(ValueError, match="already exists"):
        runner.run_bundle(args, transport_factory=FakeTransport)

    assert len(FakeTransport.instances) == 1
    assert len(FakeTransport.instances[0].calls) == call_count
    assert (output / "pair_manifest.pre_run.json").read_bytes() == before


def test_second_condition_failure_preserves_partial_bundle_without_final_manifest(
    runner, tmp_path
):
    tree = build_family_tree(tmp_path, order=["S", "F", "B"])
    output = tmp_path / "partial"
    FakeTransport.fail_condition = "F"

    with pytest.raises(RuntimeError, match="condition F failed"):
        runner.run_bundle(make_args(tree, output), transport_factory=FakeTransport)

    assert (output / "pair_manifest.pre_run.json").is_file()
    assert (output / "S" / "run_result.json").is_file()
    assert (output / "S" / "transcript.json").is_file()
    assert (output / "S" / "candidate.patch").is_file()
    assert not (output / "F").exists()
    assert not (output / "pair_manifest.json").exists()


@pytest.mark.parametrize(
    ("label", "mutation", "message"),
    [
        (
            "binding",
            lambda tree: tree.full.write_text("tampered\n", encoding="utf-8"),
            "digest",
        ),
        (
            "workspace",
            lambda tree: (tree.workspace / "toolformer_filter.py").write_text(
                "tampered\n", encoding="utf-8"
            ),
            "workspace",
        ),
        (
            "order",
            lambda tree: mutate_family(
                tree,
                lambda family: family["replicate_schedule"][0].update(
                    {"condition_order": ["S", "S", "B"]}
                ),
            ),
            "condition_order",
        ),
    ],
)
def test_mismatched_file_workspace_or_order_rejects_before_transport(
    runner, tmp_path, label, mutation, message
):
    tree = build_family_tree(tmp_path)
    mutation(tree)
    with pytest.raises(ValueError, match=message):
        runner.run_bundle(
            make_args(tree, tmp_path / f"bad-{label}"),
            transport_factory=FakeTransport,
        )
    assert FakeTransport.instances == []


def test_missing_or_duplicate_replicate_rejects(runner, tmp_path):
    tree = build_family_tree(tmp_path)
    with pytest.raises(ValueError, match="replicate"):
        runner.load_and_verify_family(tree.family_path, "r999")

    mutate_family(
        tree,
        lambda family: family["replicate_schedule"].append(
            dict(family["replicate_schedule"][0])
        ),
    )
    with pytest.raises(ValueError, match="replicate"):
        runner.load_and_verify_family(tree.family_path, "r001")


def test_final_only_test_is_unavailable_and_submit_is_terminal(runner, tmp_path):
    tree = build_family_tree(tmp_path)
    output = tmp_path / "terminal"
    runner.run_bundle(make_args(tree, output), transport_factory=FakeTransport)

    for condition in ["S", "F", "B"]:
        result = json.loads((output / condition / "run_result.json").read_text(encoding="utf-8"))
        assert result["private_score_policy"] == "final_only"
        assert result["private_score_count"] == 1
        assert result["private_feedback_exposed"] is False
        assert len(result["scorer_metrics"]) == 1
        assert result["turns"][-2]["observation_status"] == "unavailable"
        assert result["turns"][-1]["action"]["action"] == "submit"
        assert result["turns"][-1]["observation_status"] == "scored"
        assert len(result["turns"]) == 4


def test_serialized_json_contains_no_secret_values(runner, tmp_path):
    tree = build_family_tree(tmp_path)
    output = tmp_path / "no-secrets"
    runner.run_bundle(make_args(tree, output), transport_factory=FakeTransport)
    serialized = "\n".join(
        path.read_text(encoding="utf-8") for path in output.rglob("*.json")
    )
    assert SECRET_API_KEY not in serialized
    assert REGISTERED_BASE_URL in serialized


@pytest.mark.parametrize("identity_failure", ["model", "duplicate_response"])
def test_provider_identity_mismatch_cannot_complete_bundle(
    runner, tmp_path, identity_failure
):
    tree = build_family_tree(tmp_path)
    output = tmp_path / f"bad-identity-{identity_failure}"

    class InconsistentTransport(FakeTransport):
        def __call__(self, **kwargs):
            result = super().__call__(**kwargs)
            if identity_failure == "model":
                return dataclasses.replace(result, provider_model_id="other-model")
            return dataclasses.replace(result, provider_response_id="duplicate")

    with pytest.raises(ValueError, match="provider .*identity"):
        runner.run_bundle(
            make_args(tree, output), transport_factory=InconsistentTransport
        )
    assert not (output / "pair_manifest.json").exists()


def test_identical_byte_execution_source_decoy_is_rejected(runner, tmp_path):
    tree = build_family_tree(tmp_path)
    decoy = tree.root / "decoy_runner.py"
    shutil.copyfile(RUNNER_PATH, decoy)
    rebind_file(tree, "runner", decoy)

    with pytest.raises(ValueError, match="actual runner execution source"):
        runner.load_and_verify_family(tree.family_path, "r001")


def test_provider_mutation_cannot_change_verified_context_or_workspace(
    runner, tmp_path
):
    tree = build_family_tree(tmp_path, control="planted")
    original_full = tree.full.read_text(encoding="utf-8").strip()
    original_selected = tree.selected.read_text(encoding="utf-8").strip()
    original_workspace = (tree.workspace / "toolformer_filter.py").read_bytes()
    output = tmp_path / "immutable-snapshot"

    def mutating_factory(**kwargs):
        tree.full.write_text("MUTATED FULL\n", encoding="utf-8")
        tree.selected.write_text("MUTATED SELECTED\n", encoding="utf-8")
        tree.task_prompt.write_text("MUTATED PROMPT\n", encoding="utf-8")
        (tree.workspace / "toolformer_filter.py").write_text(
            "MUTATED WORKSPACE\n", encoding="utf-8"
        )
        return FakeTransport(**kwargs)

    runner.run_bundle(
        make_args(tree, output), transport_factory=mutating_factory
    )
    transport = FakeTransport.instances[0]
    first_prompts = {call["condition"]: call["prompt"] for call in transport.calls[::4]}
    assert context_section(first_prompts["F"]) == original_full
    assert context_section(first_prompts["S"]) == original_selected
    assert "LOCKED TASK PROMPT" in first_prompts["F"]
    assert "MUTATED" not in "\n".join(first_prompts.values())
    assert (
        output / "workspace_snapshot" / "toolformer_filter.py"
    ).read_bytes() == original_workspace


@pytest.mark.parametrize("failure_stage", ["constructor", "public_config"])
def test_provider_preflight_failure_is_sanitized_and_leaves_no_output(
    runner, tmp_path, failure_stage
):
    tree = build_family_tree(tmp_path)
    output = tmp_path / f"preflight-{failure_stage}"

    class SecretFailureTransport(FakeTransport):
        def __init__(self, **kwargs):
            if failure_stage == "constructor":
                raise RuntimeError(f"{REGISTERED_BASE_URL} {SECRET_API_KEY}")
            super().__init__(**kwargs)

        def public_config(self):
            if failure_stage == "public_config":
                raise RuntimeError(f"{REGISTERED_BASE_URL} {SECRET_API_KEY}")
            return super().public_config()

    with pytest.raises(ValueError, match="provider preflight failed") as caught:
        runner.run_bundle(
            make_args(tree, output), transport_factory=SecretFailureTransport
        )
    assert SECRET_API_KEY not in str(caught.value)
    assert not output.exists()


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("max_tokens", True, "max_tokens"),
        ("case_count", True, "case_count"),
        ("case_count", 63, "case_count"),
        ("maximum_shortfall", math.inf, "maximum_shortfall"),
        ("maximum_shortfall", -0.01, "maximum_shortfall"),
        ("run_success_threshold", -0.1, "run_success_threshold"),
    ],
)
def test_malformed_registered_numeric_metadata_rejects(
    runner, tmp_path, field, value, message
):
    tree = build_family_tree(tmp_path)
    mutate_family(tree, lambda family: family.update({field: value}))
    with pytest.raises(ValueError, match=message):
        runner.load_and_verify_family(tree.family_path, "r001")


@pytest.mark.parametrize("mutation", ["not_subset", "not_dependency_closed"])
def test_planted_artifact_truth_is_verified(runner, tmp_path, mutation):
    tree = build_family_tree(tmp_path, control="planted")
    if mutation == "not_subset":
        tree.selected.write_text(
            "1. **Base invariant** (`T01`)\n"
            "2. **Unknown atom** (`T03`)\n",
            encoding="utf-8",
        )
        rebind_file(tree, "selected_artifact", tree.selected)
    else:
        source = json.loads(tree.source_map.read_text(encoding="utf-8"))
        source["requires"]["T01"] = ["T02"]
        source["dependency_edges"].append({"from": "T01", "to": "T02"})
        write_json(tree.source_map, source)
        rebind_file(tree, "source_map", tree.source_map)
    with pytest.raises(ValueError, match="subset|dependency"):
        runner.load_and_verify_family(tree.family_path, "r001")


def test_invalid_utf8_is_normalized_and_leaves_no_output(runner, tmp_path):
    tree = build_family_tree(tmp_path)
    tree.full.write_bytes(b"\xff")
    tree.selected.write_bytes(b"\xff")
    rebind_file(tree, "full_artifact", tree.full)
    rebind_file(tree, "selected_artifact", tree.selected)
    output = tmp_path / "bad-utf8"
    with pytest.raises(ValueError, match="UTF-8"):
        runner.run_bundle(
            make_args(tree, output), transport_factory=FakeTransport
        )
    assert FakeTransport.instances == []
    assert not output.exists()


def test_invalid_bound_json_and_short_family_path_are_normalized(runner, tmp_path):
    tree = build_family_tree(tmp_path)
    tree.source_map.write_text("{", encoding="utf-8")
    rebind_file(tree, "source_map", tree.source_map)
    with pytest.raises(ValueError, match="source_map.*JSON"):
        runner.load_and_verify_family(tree.family_path, "r001")

    with pytest.raises(ValueError, match="family path"):
        runner._resolve_run_root(Path("D:/family.json"), tree.family)


def test_scorer_timeout_is_passed_and_enforced(runner, tmp_path, monkeypatch):
    tree = build_family_tree(tmp_path)

    def hanging_score(**kwargs):
        del kwargs
        time.sleep(0.15)
        return {"public_summary": {}, "task_score": 0.0, "success": False}

    monkeypatch.setattr(runner, "score_toolformer_filter_patch", hanging_score)
    bridge = runner._ExclusiveToolformerScorerBridge(
        workspace=tree.workspace,
        case_registry_path=tree.case_registry,
        condition_dir=tmp_path / "timeout-condition",
        timeout_seconds=0.01,
    )
    with pytest.raises(ValueError, match="timed out"):
        bridge.evaluate(
            "--- a/toolformer_filter.py\n+++ b/toolformer_filter.py\n",
            evaluation_id="submit-01",
        )
    time.sleep(0.2)


@pytest.mark.parametrize("value", [math.inf, 0.0, True])
def test_invalid_runtime_timeout_rejects_before_provider_and_output(
    runner, tmp_path, value
):
    tree = build_family_tree(tmp_path)
    output = tmp_path / "bad-timeout"
    with pytest.raises(ValueError, match="timeout_seconds"):
        runner.run_bundle(
            make_args(tree, output, scorer_timeout_seconds=value),
            transport_factory=FakeTransport,
        )
    assert FakeTransport.instances == []
    assert not output.exists()


def test_cli_has_no_arbitrary_condition_argument(runner):
    parser = runner.build_parser()
    option_strings = {
        option
        for action in parser._actions
        for option in action.option_strings
    }
    assert "--family" in option_strings
    assert "--replicate-id" in option_strings
    assert "--output-dir" in option_strings
    assert "--model-alias" in option_strings
    assert "--base-url-env" in option_strings
    assert "--api-key-env" in option_strings
    assert "--timeout-seconds" in option_strings
    assert "--scorer-timeout-seconds" in option_strings
    assert "--max-tokens" in option_strings
    assert "--max-attempts" in option_strings
    assert "--condition" not in option_strings


def test_confirmation_runner_imports_only_the_bound_transport_module():
    source = RUNNER_PATH.read_text(encoding="utf-8")
    assert "from confirmation_transport_v3 import" in source
    assert "run_swe_effectslice" not in source
