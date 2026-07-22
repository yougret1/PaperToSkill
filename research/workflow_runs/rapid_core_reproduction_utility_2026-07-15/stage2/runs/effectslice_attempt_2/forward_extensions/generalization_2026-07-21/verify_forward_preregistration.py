from __future__ import annotations

import hashlib
import itertools
import json
from collections import Counter
from pathlib import Path


FORWARD_ROOT = Path(__file__).resolve().parent
PREREG_ROOT = FORWARD_ROOT / "preregistration"
RUN_ROOT = FORWARD_ROOT.parents[1]

EXPECTED_DOMAINS = {
    "nlp",
    "software_engineering",
    "data_analysis",
    "agent_tool_use",
}
EXPECTED_ORDER_PERMUTATIONS = {
    "".join(order) for order in itertools.permutations("BFS")
}
EXPECTED_FIGURES = {
    "F1_protocol_audit",
    "F2_cross_paper_effects",
    "F3_compression_reliability",
    "F4_robustness_and_failures",
}


def _repo_root() -> Path:
    for candidate in (FORWARD_ROOT, *FORWARD_ROOT.parents):
        if (candidate / "paper" / "effectslice_aaai" / "main_v3.tex").is_file():
            return candidate
    raise RuntimeError("repository root not found")


def _load(name: str) -> dict[str, object]:
    path = PREREG_ROOT / name
    return json.loads(path.read_text(encoding="utf-8"))


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


def audit() -> dict[str, object]:
    repo = _repo_root()
    registry = _load("paper_registry.json")
    candidates = _load("candidate_matrix.json")
    experiment = _load("experiment_plan.json")
    models = _load("model_ablation_registry.json")
    figures = _load("figure_statistical_plan.json")

    assert registry["registration_status"] == "frozen_before_provider_calls"
    papers = registry["papers"]
    assert isinstance(papers, list) and len(papers) == 12
    domains = Counter(paper["domain"] for paper in papers)
    assert set(domains) == EXPECTED_DOMAINS
    assert set(domains.values()) == {3}

    paper_ids = [paper["paper_id"] for paper in papers]
    persistent_ids = [paper["persistent_id"] for paper in papers]
    assert len(paper_ids) == len(set(paper_ids))
    assert len(persistent_ids) == len(set(persistent_ids))

    task_ids: list[str] = []
    for paper in papers:
        assert "arxiv" not in paper["venue"].lower(), (
            f"selected paper lacks formal venue: {paper['paper_id']}"
        )
        tasks = paper["tasks"]
        assert len(tasks) == 2
        assert tasks[0]["name"] != tasks[1]["name"]
        evidence_texts: list[str] = []
        for relative in paper["metadata_evidence"]:
            path = _evidence_path(repo, relative)
            assert path.is_file(), f"missing metadata evidence: {relative}"
            evidence_texts.append(path.read_text(encoding="utf-8").lower())
        identifier = paper["persistent_id"].split(":", 1)[1].lower()
        assert any(identifier in text for text in evidence_texts), (
            f"persistent identifier is not present in evidence: {paper['paper_id']}"
        )
        for task in tasks:
            task_ids.append(task["task_id"])
            assert task["bounded_objective"]
            assert task["mechanism_boundary"]
            assert task["private_scorer"]
            assert task["primary_metric"]
            assert len(task["hard_contracts"]) >= 4
    assert len(task_ids) == 24 == len(set(task_ids))

    matrix_entries = candidates["entries"]
    selected_matrix = [row for row in matrix_entries if row["status"] == "selected"]
    assert len(selected_matrix) == 12
    assert {row["paper_id"] for row in selected_matrix} == set(paper_ids)
    assert all(len(row["task_ids"]) == 2 for row in selected_matrix)
    assert all(row["source_status"] for row in selected_matrix)
    assert all(row["scorer_feasibility"] for row in selected_matrix)
    assert all(row["dependency_risk"] for row in selected_matrix)
    assert all(row["license_risk"] for row in selected_matrix)
    assert {row["status"] for row in matrix_entries} == {
        "selected",
        "reserve",
        "rejected",
    }

    design = experiment["primary_design"]
    assert design["papers"] == 12
    assert design["tasks_per_paper"] == 2
    assert design["paper_task_clusters"] == 24
    assert design["blocks_per_cluster"] == 6
    assert design["conditions"] == ["B", "F", "S"]
    assert design["provider_conversations"] == 24 * 6 * 3 == 432
    assert design["independent_inference_unit"].startswith("paper-task")

    schedule = experiment["schedule"]
    assert set(schedule["within_cluster_orders"]) == EXPECTED_ORDER_PERMUTATIONS
    assert len(schedule["within_cluster_orders"]) == 6
    assert schedule["block_seed_base"] == 2026072100
    assert schedule["global_interleave_seed"] == 20260721

    sla = experiment["scoring"]["admission_sla"]
    assert sla == {
        "maximum_B_successes": 1,
        "minimum_F_successes": 5,
        "minimum_S_successes": 5,
        "minimum_paired_margin_blocks": 5,
        "paired_margin_rule": (
            "S private_score >= F private_score - 0.05 within the matched block"
        ),
        "all_outputs_complete": True,
        "all_integrity_checks_pass": True,
    }
    assert set(experiment["scoring"]["decision_states"]) == {
        "Admit",
        "Reject",
        "Invalid",
    }

    secondary_ids = set(experiment["control_subset"]["paper_task_ids"])
    assert secondary_ids == set(experiment["atom_ladder_subset"]["paper_task_ids"])
    assert secondary_ids == set(experiment["model_ablation"]["paper_task_ids"])
    assert len(secondary_ids) == 4
    task_to_domain = {
        task["task_id"]: paper["domain"]
        for paper in papers
        for task in paper["tasks"]
    }
    assert {task_to_domain[task_id] for task_id in secondary_ids} == EXPECTED_DOMAINS

    model_slots = models["model_slots"]
    slot_ids = [slot["slot_id"] for slot in model_slots]
    assert len(slot_ids) == len(set(slot_ids))
    required_closed = [
        slot for slot in model_slots if slot["role"] == "required_closed_ablation"
    ]
    assert len(required_closed) == 4
    assert all(slot["additional_conversations"] == 72 for slot in required_closed)
    assert sum(slot["additional_conversations"] for slot in required_closed) == 288
    assert {slot["model_alias"] for slot in required_closed} == {
        "gpt-5.5",
        "gpt-5.6-sol",
        "gpt-5.6-terra",
        "claude-opus-4-7",
    }
    optional_aliases = {
        slot["model_alias"] for slot in model_slots if not slot["required"]
    }
    assert optional_aliases == {"gpt-5.6-luna", "claude-opus-4-6"}
    open_anchor = next(slot for slot in model_slots if slot["slot_id"] == "open_seed_anchor")
    assert open_anchor["seed_support"] == "required"
    assert len(open_anchor["generation_seeds"]) == 6
    assert len(set(open_anchor["generation_seeds"])) == 6
    assert open_anchor["decoding"]["do_sample"] is False

    budget = experiment["resource_budget"]
    recomputed_required = (
        budget["primary_provider_conversations"]
        + budget["required_model_ablation_provider_conversations"]
        + budget["atom_ladder_provider_conversations"]
        + budget["control_provider_conversations"]
    )
    assert recomputed_required == budget["required_provider_conversation_cap"] == 840
    assert budget["optional_model_provider_conversation_cap"] == 144
    assert budget["open_seed_anchor_local_conversations"] == 72

    assert experiment["transport_and_failure_policy"]["maximum_transport_attempts"] == 5
    assert experiment["transport_and_failure_policy"]["retry_delays_seconds"] == [
        2,
        4,
        8,
        16,
    ]
    assert experiment["transport_and_failure_policy"]["semantic_rerun"].startswith(
        "forbidden"
    )

    figure_ids = {figure["figure_id"] for figure in figures["figures"]}
    assert figure_ids == EXPECTED_FIGURES
    assert figures["conditional_outputs"][0]["default"] == "do_not_render"
    assert figures["conditional_outputs"][0]["current_independent_controls_per_class"] == 4
    bootstrap = figures["statistics"]["cluster_bootstrap"]
    assert bootstrap["seed"] == 20260721
    assert bootstrap["replicates"] == 10000
    assert "paper" in figures["statistics"]["primary_unit"]

    for item in experiment["forward_only_scope"]["immutable_inputs"][:2]:
        path = RUN_ROOT / item["path"]
        assert path.is_file(), f"missing frozen parent input: {path}"
        assert _sha256(path) == item["sha256"], f"frozen parent changed: {path}"

    expected_retrievals = {
        "candidate-perses.json",
        "candidate-umap.json",
        "candidate-leiden.json",
        "candidate-hdbscan.json",
        "candidate-longllmlingua.json",
        "candidate-react.json",
        "candidate-reflexion.json",
        "candidate-llmlingua2.json",
        "candidate-context-sentence-compression.json",
        "generalization-nlp-procedures.json",
        "generalization-software-reduction.json",
        "generalization-data-analysis.json",
        "generalization-agent-tool-use.json",
    }
    retrieval_root = FORWARD_ROOT / "stage1" / "retrieval"
    assert expected_retrievals <= {path.name for path in retrieval_root.glob("*.json")}

    return {
        "status": "passed",
        "selected_papers": len(papers),
        "paper_task_clusters": len(task_ids),
        "domains": dict(sorted(domains.items())),
        "primary_provider_conversations": design["provider_conversations"],
        "required_provider_conversation_cap": budget[
            "required_provider_conversation_cap"
        ],
        "required_closed_model_slots": len(required_closed),
        "optional_closed_model_slots": len(optional_aliases),
        "open_seed_anchor": open_anchor["model_alias"],
        "figure_contracts": sorted(figure_ids),
        "frozen_parent_hashes_verified": 2,
    }


if __name__ == "__main__":
    print(json.dumps(audit(), indent=2, sort_keys=True))
