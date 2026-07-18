import hashlib
import itertools
import json
import sys
import tempfile
from collections import Counter
from pathlib import Path

import pytest


RUN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RUN_ROOT))
sys.path.insert(0, str(RUN_ROOT / "src"))

from build_confirmation_v3 import build_family  # noqa: E402
from effectslice.confirmation_v3 import (  # noqa: E402
    sha256_canonical_text,
    sha256_file,
)
from effectslice.toolformer_filter_cases import generate_case  # noqa: E402


ORIGINAL_ARTIFACT = (
    RUN_ROOT / "artifacts" / "toolformer_filter" / "full_artifact.md"
)
V2_CASE_REGISTRY = (
    RUN_ROOT / "artifacts" / "toolformer_filter" / "case_registry_v2_r2.json"
)
TASK_PROMPT = RUN_ROOT / "artifacts" / "toolformer_filter" / "task_prompt.md"
EXPECTED_ORDERS = set(itertools.permutations(("B", "F", "S")))
T06_MARKDOWN = (
    "6. **Restate the shared selection invariant** (`T06`)\n"
    "   Apply the same inclusive `margin >= tau_filter` rule independently to every\n"
    "   proposed call and preserve the proposals' original order in the returned\n"
    "   decisions. This restates the registered T04/T05 invariant and introduces no\n"
    "   new computation.\n"
)


def bound_path(family: dict, prefix: str) -> Path:
    path = Path(family[f"{prefix}_path"])
    return path if path.is_absolute() else RUN_ROOT / path


def build_in_temp(control: str) -> tuple[tempfile.TemporaryDirectory, Path, dict]:
    temporary = tempfile.TemporaryDirectory()
    output_dir = Path(temporary.name) / control
    family = build_family(control, output_dir)
    return temporary, output_dir, family


def assert_balanced_schedule(family: dict, expected_repetitions: int) -> None:
    schedule = family["replicate_schedule"]
    counts = Counter(tuple(row["condition_order"]) for row in schedule)
    assert set(counts) == EXPECTED_ORDERS
    assert set(counts.values()) == {expected_repetitions}
    assert [row["replicate_id"] for row in schedule] == [
        f"r{index:03d}" for index in range(1, len(schedule) + 1)
    ]


def test_identity_builds_six_byte_identical_full_and_slice_conditions():
    temporary, output_dir, family = build_in_temp("identity")
    with temporary:
        full_path = bound_path(family, "full_artifact")
        slice_path = bound_path(family, "selected_artifact")

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

        original_bytes = ORIGINAL_ARTIFACT.read_bytes()
        assert full_path.read_bytes() == original_bytes
        assert slice_path.read_bytes() == original_bytes
        assert family["full_artifact_sha256"] == family["selected_artifact_sha256"]
        assert output_dir == full_path.parent == slice_path.parent


def test_planted_builds_exact_redundant_unit_and_dependency_closed_subset():
    temporary, _, family = build_in_temp("planted")
    with temporary:
        full_path = bound_path(family, "full_artifact")
        slice_path = bound_path(family, "selected_artifact")
        source_map = json.loads(
            bound_path(family, "source_map").read_text(encoding="utf-8")
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

        original_bytes = ORIGINAL_ARTIFACT.read_bytes()
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
    temporary, _, family = build_in_temp(control)
    with temporary:
        case_path = bound_path(family, "case_registry")
        registry = json.loads(case_path.read_text(encoding="utf-8"))
        cases = registry["blocks"]["confirmation_v3"]
        seeds = registry["generator_inputs"]["seeds"]

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
        assert case_path.read_bytes() != V2_CASE_REGISTRY.read_bytes()

        assert family["task_prompt_file_sha256"] == sha256_file(TASK_PROMPT)
        assert (
            family["task_prompt_canonical_text_sha256"]
            == sha256_canonical_text(TASK_PROMPT)
        )
        assert family["task_prompt_file_sha256"] == hashlib.sha256(
            TASK_PROMPT.read_bytes()
        ).hexdigest()
        assert family["task_prompt_canonical_text_sha256"] == hashlib.sha256(
            TASK_PROMPT.read_text(encoding="utf-8").strip().encode("utf-8")
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
        assert family["model_alias"] == "deepseek-v4-flash"
        assert family["wire_api"] == "openai_chat_completions"
        assert family["temperature"] == 0
        assert (
            family["comparison_role"]
            == family["evidence_boundary"]
            == "registered_final_only_confirmation_v3"
        )


def test_bindings_hash_existing_inputs_and_mark_missing_v3_executables_planned():
    temporary, output_dir, family = build_in_temp("identity")
    with temporary:
        required_bindings = {
            "full_artifact",
            "selected_artifact",
            "source_map",
            "case_registry",
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
            path = bound_path(family, prefix)
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
            if not (RUN_ROOT / family[f"{prefix}_path"]).is_file():
                assert family[f"{prefix}_status"] == (
                    "planned_before_preregistration"
                )
                assert f"{prefix}_sha256" not in family

        assert family["workspace_path"] == "task_workspaces/toolformer_filter_v1"
        assert len(family["workspace_tree_sha256"]) == 64
        assert family["workspace_file_count"] == 2
        assert json.loads(
            (output_dir / "family.json").read_text(encoding="utf-8")
        ) == family


def test_builder_is_write_once_and_rejects_unknown_controls_without_output():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        output_dir = root / "identity"
        build_family("identity", output_dir)
        before = {
            path.relative_to(output_dir): path.read_bytes()
            for path in output_dir.rglob("*")
            if path.is_file()
        }

        with pytest.raises(FileExistsError):
            build_family("identity", output_dir)

        after = {
            path.relative_to(output_dir): path.read_bytes()
            for path in output_dir.rglob("*")
            if path.is_file()
        }
        assert after == before

        invalid_output = root / "invalid"
        with pytest.raises(ValueError, match="unsupported confirmation-v3 control"):
            build_family("unknown", invalid_output)
        assert not invalid_output.exists()
