from __future__ import annotations

import hashlib
import importlib.util
import itertools
import json
from collections import Counter
from pathlib import Path
from typing import Any


FORWARD_ROOT = Path(__file__).resolve().parent
PREREG_ROOT = FORWARD_ROOT / "preregistration"
RUN_ROOT = FORWARD_ROOT.parents[1]
STATUS = "stage_2_2_design_registered_materialization_pending"
EXPECTED_DOMAINS = {
    "nlp",
    "software_engineering",
    "data_analysis",
    "agent_tool_use",
}
EXPECTED_SECONDARY_TASKS = {
    "NLP-LLM-01",
    "SE-PE-01",
    "DATA-HDB-01",
    "AGENT-TF-01",
}
EXPECTED_ORDERS = {"".join(order) for order in itertools.permutations("BFS")}
EXPECTED_FIGURES = {
    "F1_protocol_audit",
    "F2_cross_paper_effects",
    "F3_compression_reliability",
    "F4_robustness_and_failures",
}
EXPECTED_BUNDLE_PATHS = {
    "analyze_sla_operating_characteristics.py",
    "build_preregistration_hash_manifest.py",
    "build_stage_2_2_registration.py",
    "preregistration/candidate_matrix.json",
    "preregistration/experiment_plan.json",
    "preregistration/experiment_plan.md",
    "preregistration/figure_statistical_plan.json",
    "preregistration/materialization_contract.json",
    "preregistration/model_ablation_registry.json",
    "preregistration/paper_registry.json",
    "preregistration/sla_operating_characteristics.json",
    "tests/test_forward_preregistration.py",
    "verify_forward_preregistration.py",
    "verify_forward_preregistration_v2.py",
}


class VerificationError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


def _repo_root() -> Path:
    for candidate in (FORWARD_ROOT, *FORWARD_ROOT.parents):
        if (candidate / "paper" / "effectslice_aaai" / "main_v3.tex").is_file():
            return candidate
    raise VerificationError("repository root not found")


def _load(name: str) -> dict[str, Any]:
    path = PREREG_ROOT / name
    _require(path.is_file(), f"missing preregistration artifact: {name}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise VerificationError(f"cannot parse {name}: {exc}") from exc
    _require(isinstance(value, dict), f"{name} must contain a JSON object")
    return value


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _evidence_path(repo: Path, relative: str) -> Path:
    if relative.startswith(("paper/", "papers/", "research/")):
        return repo / relative
    return FORWARD_ROOT / relative


def _load_operating_analyzer():
    path = FORWARD_ROOT / "analyze_sla_operating_characteristics.py"
    spec = importlib.util.spec_from_file_location("fg1_sla_analysis", path)
    _require(spec is not None and spec.loader is not None, "cannot load SLA analyzer")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _verify_hash_manifest() -> str:
    manifest_path = PREREG_ROOT / "bundle_hash_manifest.json"
    _require(manifest_path.is_file(), "missing preregistration bundle hash manifest")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    _require(
        manifest.get("schema_version") == "effectslice-fg1-bundle-hashes.v1",
        "unexpected hash-manifest schema",
    )
    entries = manifest.get("files")
    _require(isinstance(entries, list), "hash manifest files must be a list")
    paths = {entry.get("path") for entry in entries}
    _require(paths == EXPECTED_BUNDLE_PATHS, "hash manifest path set is incomplete")
    canonical_pairs: list[str] = []
    for entry in entries:
        relative = entry["path"]
        path = FORWARD_ROOT / relative
        _require(path.is_file(), f"hash-bound file missing: {relative}")
        actual = _sha256(path)
        _require(actual == entry.get("sha256"), f"hash mismatch: {relative}")
        _require(path.stat().st_size == entry.get("bytes"), f"size mismatch: {relative}")
        canonical_pairs.append(f"{relative}\0{actual}")
    bundle = hashlib.sha256("\n".join(sorted(canonical_pairs)).encode()).hexdigest()
    _require(bundle == manifest.get("bundle_sha256"), "bundle digest mismatch")
    return bundle


def audit() -> dict[str, object]:
    repo = _repo_root()
    registry = _load("paper_registry.json")
    candidates = _load("candidate_matrix.json")
    experiment = _load("experiment_plan.json")
    models = _load("model_ablation_registry.json")
    figures = _load("figure_statistical_plan.json")
    materialization = _load("materialization_contract.json")
    operating = _load("sla_operating_characteristics.json")

    for name, artifact in {
        "paper_registry": registry,
        "candidate_matrix": candidates,
        "experiment_plan": experiment,
        "model_registry": models,
        "figure_plan": figures,
        "materialization_contract": materialization,
    }.items():
        _require(
            artifact.get("registration_status") == STATUS,
            f"{name} has inconsistent registration status",
        )

    papers = registry.get("papers")
    _require(isinstance(papers, list) and len(papers) == 12, "expected 12 papers")
    domains = Counter(paper.get("domain") for paper in papers)
    _require(set(domains) == EXPECTED_DOMAINS, "paper domains are incomplete")
    _require(set(domains.values()) == {3}, "expected three papers per domain")

    paper_ids = [paper.get("paper_id") for paper in papers]
    persistent_ids = [paper.get("persistent_id") for paper in papers]
    _require(len(paper_ids) == len(set(paper_ids)), "duplicate paper ID")
    _require(len(persistent_ids) == len(set(persistent_ids)), "duplicate persistent ID")

    task_ids: list[str] = []
    registry_mapping: dict[str, tuple[str, str]] = {}
    task_to_domain: dict[str, str] = {}
    for paper in papers:
        venue = str(paper.get("venue", ""))
        _require("arxiv" not in venue.lower(), f"non-formal selected venue: {paper_ids}")
        tasks = paper.get("tasks")
        _require(isinstance(tasks, list) and len(tasks) == 2, "paper must have two tasks")
        _require(tasks[0].get("name") != tasks[1].get("name"), "duplicate task names")
        evidence_texts: list[str] = []
        for relative in paper.get("metadata_evidence", []):
            path = _evidence_path(repo, relative)
            _require(path.is_file(), f"missing metadata evidence: {relative}")
            evidence_texts.append(path.read_text(encoding="utf-8").lower())
        identifier = str(paper["persistent_id"]).split(":", 1)[1].lower()
        _require(
            any(identifier in text for text in evidence_texts),
            f"persistent identifier absent from evidence: {paper['paper_id']}",
        )
        pair: list[str] = []
        for task in tasks:
            task_id = task.get("task_id")
            _require(isinstance(task_id, str) and task_id, "task ID missing")
            task_ids.append(task_id)
            pair.append(task_id)
            task_to_domain[task_id] = paper["domain"]
            for field in (
                "bounded_objective",
                "mechanism_boundary",
                "private_scorer",
                "primary_metric",
            ):
                _require(bool(task.get(field)), f"{task_id} missing {field}")
            _require(len(task.get("hard_contracts", [])) >= 4, f"{task_id} contracts")
        registry_mapping[paper["paper_id"]] = tuple(pair)
    _require(len(task_ids) == 24 == len(set(task_ids)), "expected 24 unique tasks")

    implementation = registry.get("implementation_policy", {})
    for field in (
        "independent_semantic_audit",
        "task_specificity_gate",
        "private_registry_gate",
    ):
        _require(bool(implementation.get(field)), f"paper registry missing {field}")

    selected = [row for row in candidates.get("entries", []) if row.get("status") == "selected"]
    _require(len(selected) == 12, "candidate matrix must select 12 papers")
    selected_mapping = {
        row["paper_id"]: tuple(row.get("task_ids", [])) for row in selected
    }
    _require(selected_mapping == registry_mapping, "candidate/task mapping mismatch")
    _require(
        {row.get("status") for row in candidates.get("entries", [])}
        == {"selected", "reserve", "rejected"},
        "candidate statuses changed",
    )
    audit_contract = candidates.get("audit_contract", {})
    _require(
        audit_contract.get("source_auditor_must_differ_from_candidate_builder") is True,
        "candidate audit independence missing",
    )
    _require(
        audit_contract.get("outcome_access_during_selection_or_replacement") == "forbidden",
        "candidate selection outcome blindness missing",
    )

    design = experiment.get("primary_design", {})
    _require(design.get("papers") == 12, "primary paper count")
    _require(design.get("independent_aggregate_unit") == "paper", "unit must be paper")
    _require(design.get("independent_papers") == 12, "independent n must be 12")
    _require(design.get("tasks_per_paper") == 2, "tasks per paper")
    _require(design.get("nested_task_decisions") == 24, "nested task count")
    _require(design.get("blocks_per_task") == 6, "blocks per task")
    _require(design.get("conditions") == ["B", "F", "S"], "primary conditions")
    _require(design.get("remote_conversations") == 12 * 2 * 6 * 3, "primary arithmetic")

    schedule = experiment.get("schedule", {})
    _require(set(schedule.get("all_orders", [])) == EXPECTED_ORDERS, "BFS orders")
    _require(
        set(schedule["registry_A"]["orders"]) == {"BFS", "FSB", "SBF"},
        "registry A orders",
    )
    _require(
        set(schedule["registry_B"]["orders"]) == {"BSF", "FBS", "SFB"},
        "registry B orders",
    )
    _require(schedule["registry_A"]["blocks"] == 3, "registry A block count")
    _require(schedule["registry_B"]["blocks"] == 3, "registry B block count")

    reducer = experiment.get("candidate_construction", {}).get("primary_reducer", {})
    _require(reducer.get("id") == "dag_ratio_60_v1", "primary reducer ID")
    _require(
        reducer.get("visible_fields")
        == ["atom_id", "dependency_ids", "rendered_token_count"],
        "reducer visible fields",
    )
    forbidden = set(reducer.get("forbidden_fields", []))
    _require(
        {"hard_contract_label", "guardrail_label", "scorer_interface_label"}
        <= forbidden,
        "reducer can see protected semantic labels",
    )
    _require(reducer.get("target_token_retention") == 0.60, "target retention")
    _require(
        reducer.get("eligible_token_retention_interval") == [0.45, 0.75],
        "retention interval",
    )
    _require(
        reducer.get("tie_break_order")
        == [
            "minimum_absolute_distance_to_0.60",
            "fewer_rendered_tokens",
            "lexicographic_canonical_atom_id_list",
        ],
        "reducer tie breaks",
    )

    sla = experiment.get("scoring", {}).get("admission_sla", {})
    _require(
        sla.get("total_six_blocks")
        == {
            "maximum_B_successes": 1,
            "minimum_F_successes": 5,
            "minimum_S_successes": 5,
            "minimum_valid_paired_margin_blocks": 5,
        },
        "six-block SLA",
    )
    _require(
        sla.get("each_three_block_registry")
        == {
            "maximum_B_successes": 1,
            "minimum_F_successes": 2,
            "minimum_S_successes": 2,
            "minimum_valid_paired_margin_blocks": 2,
        },
        "per-registry SLA",
    )
    _require(
        experiment["scoring"].get("reject_reason_precedence")
        == [
            "full-insufficient",
            "baseline-sensitive",
            "slice-insufficient",
            "margin-shortfall",
        ],
        "reject taxonomy",
    )
    _require(
        set(experiment["scoring"].get("decision_states", {}))
        == {"Admit", "Reject", "Invalid"},
        "decision states",
    )

    secondary = experiment.get("secondary_experiments", {})
    _require(
        set(secondary.get("paper_task_ids", [])) == EXPECTED_SECONDARY_TASKS,
        "secondary task set",
    )
    _require(
        {task_to_domain[task_id] for task_id in EXPECTED_SECONDARY_TASKS}
        == EXPECTED_DOMAINS,
        "secondary domains",
    )
    controls = secondary.get("controls", {})
    ladder = secondary.get("structural_restoration_ladder", {})
    alternates = secondary.get("alternate_candidate_reducers", {})
    robustness = secondary.get("model_robustness", {})
    _require(controls.get("remote_conversations") == 4 * 3 * 6 * 2, "controls")
    _require(ladder.get("remote_conversations") == 4 * 3 * 6 * 2, "ladder")
    _require(alternates.get("remote_conversations") == 4 * 2 * 6 * 2, "alternates")
    _require(robustness.get("conditions") == ["B", "F", "S", "I"], "BFSI")
    _require(robustness.get("required_remote_conversations") == 4 * 4 * 6 * 4, "models")
    for item in (controls, ladder, alternates, robustness):
        _require(item.get("reuse_primary_rows") is False, "secondary row reuse")
    _require(
        "fresh_F" in controls.get("pair", [])
        and "fresh_F" in ladder.get("pair", [])
        and "fresh_F" in alternates.get("pair", []),
        "fresh contemporaneous F pairs",
    )

    budget = experiment.get("resource_budget", {})
    recomputed_remote = sum(
        budget[key]
        for key in (
            "primary_remote_conversations",
            "control_remote_conversations",
            "structural_ladder_remote_conversations",
            "alternate_reducer_remote_conversations",
            "required_model_robustness_remote_conversations",
        )
    )
    _require(recomputed_remote == budget.get("required_remote_conversation_cap") == 1200, "remote total")
    _require(budget.get("open_anchor_local_execution_cap") == 96, "local total")
    _require(budget.get("required_execution_cap") == 1296, "required total")
    _require(
        budget.get("optional_closed_model_remote_conversation_cap") == 192,
        "optional total",
    )
    _require(budget.get("required_realistic_remote_hours") == [51, 70], "time plan")

    model_slots = models.get("model_slots", [])
    slot_ids = [slot.get("slot_id") for slot in model_slots]
    _require(len(slot_ids) == len(set(slot_ids)), "duplicate model slot")
    required_closed = [
        slot for slot in model_slots if slot.get("role") == "required_closed_robustness"
    ]
    _require(len(required_closed) == 4, "required closed slot count")
    _require(
        {slot.get("model_alias") for slot in required_closed}
        == {"gpt-5.5", "gpt-5.6-sol", "gpt-5.6-terra", "claude-opus-4-7"},
        "required model aliases",
    )
    _require(
        all(slot.get("remote_conversations") == 96 for slot in required_closed),
        "closed slot execution count",
    )
    optional = [slot for slot in model_slots if slot.get("required") is False]
    _require(
        {slot.get("model_alias") for slot in optional}
        == {"gpt-5.6-luna", "claude-opus-4-6"},
        "optional model aliases",
    )
    open_anchor = next(
        (slot for slot in model_slots if slot.get("slot_id") == "open_seed_anchor"),
        None,
    )
    _require(open_anchor is not None, "open anchor missing")
    _require(open_anchor.get("local_executions") == 96, "open anchor count")
    _require(open_anchor.get("decoding", {}).get("do_sample") is False, "sampling")
    seed = open_anchor.get("seed_derivation", {})
    _require(seed.get("F_I_same_seed") is True, "F/I seed pairing")
    _require(
        seed.get("condition_seed_groups", {}).get("F")
        == seed.get("condition_seed_groups", {}).get("I"),
        "F/I condition seed group mismatch",
    )
    _require("turn_id" in seed.get("formula", ""), "turn seed derivation missing")

    terminal = experiment.get("transport_and_failure_policy", {}).get(
        "mutually_exclusive_terminal_outcomes_in_precedence_order", []
    )
    _require(len(terminal) == len(set(terminal)) == 8, "terminal taxonomy overlap")
    _require(
        experiment["transport_and_failure_policy"].get(
            "transport_retry_recovered_is_annotation"
        )
        is True,
        "recovered retry classification",
    )

    figure_ids = {figure.get("figure_id") for figure in figures.get("figures", [])}
    _require(figure_ids == EXPECTED_FIGURES, "figure set")
    stats = figures.get("statistics", {})
    _require(stats.get("primary_unit") == "paper", "figure primary unit")
    _require(stats.get("independent_n") == 12, "figure independent n")
    _require(stats.get("valid_pair_reporting") == "valid_pairs/registered_pairs", "pair denominators")
    _require(stats.get("invalid_partial_identification_bounds") is True, "invalid bounds")
    forbidden_intervals = set(stats.get("per_task_display", {}).get("forbidden", []))
    _require("per-task Clopper-Pearson interval" in forbidden_intervals, "CP ban")
    _require("six-block bootstrap interval" in forbidden_intervals, "block bootstrap ban")
    conditional = figures.get("conditional_outputs", [])[0]
    _require(conditional.get("default") == "do_not_render", "confusion matrix ban")

    required_task_artifacts = set(materialization.get("required_task_artifacts", []))
    _require(
        {
            "task_to_span_matrix.json",
            "atom_registry.json",
            "atom_dag.json",
            "semantic_audit.json",
            "differential_test_report.json",
        }
        <= required_task_artifacts,
        "materialization task contracts",
    )
    specificity = materialization.get("source_and_task_specificity", {})
    _require(specificity.get("minimum_central_spans_per_task") == 2, "source spans")
    _require(
        specificity.get("two_tasks_same_paper_must_have_distinct_central_boundaries")
        is True,
        "task specificity",
    )
    semantic_audit = materialization.get("semantic_audit", {})
    _require(
        semantic_audit.get("source_auditor_must_differ_from_candidate_builder") is True,
        "builder/auditor independence",
    )
    _require(len(semantic_audit.get("required_identities", [])) == 6, "audit identities")
    schedule_counts = materialization.get("schedule_counts", {})
    _require(schedule_counts.get("required_remote_rows") == 1200, "materialized remote rows")
    _require(schedule_counts.get("required_local_rows") == 96, "materialized local rows")
    _require(schedule_counts.get("required_total_rows") == 1296, "materialized total rows")

    analyzer = _load_operating_analyzer()
    recomputed_operating = analyzer.analyze()
    _require(operating == recomputed_operating, "stale SLA operating analysis")
    _require(operating.get("total_count_states") == 4**8, "SLA state enumeration")
    _require(operating.get("passing_count_states") == 81, "SLA passing state count")

    for item in experiment.get("forward_only_scope", {}).get("immutable_inputs", [])[:2]:
        path = RUN_ROOT / item["path"]
        _require(path.is_file(), f"missing frozen parent input: {path}")
        _require(_sha256(path) == item["sha256"], f"frozen parent changed: {path}")

    bundle_sha256 = _verify_hash_manifest()

    return {
        "status": "passed",
        "registration_status": STATUS,
        "selected_papers": len(papers),
        "independent_papers": 12,
        "nested_task_decisions": len(task_ids),
        "domains": dict(sorted(domains.items())),
        "primary_remote_conversations": design["remote_conversations"],
        "required_remote_conversation_cap": 1200,
        "open_anchor_local_execution_cap": 96,
        "required_execution_cap": 1296,
        "optional_remote_conversation_cap": 192,
        "required_closed_model_slots": len(required_closed),
        "optional_closed_model_slots": len(optional),
        "open_seed_anchor": open_anchor["model_alias"],
        "figure_contracts": sorted(figure_ids),
        "frozen_parent_hashes_verified": 2,
        "bundle_sha256": bundle_sha256,
    }


from preregistration_verifier_v3 import (  # noqa: E402
    VerificationError,
    audit,
)


if __name__ == "__main__":
    print(json.dumps(audit(), indent=2, sort_keys=True))
