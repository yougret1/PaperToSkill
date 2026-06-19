#!/usr/bin/env python
"""Check the PaperToSkill reproducibility package state."""

from __future__ import annotations

import argparse
import csv
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


PAPERS = [
    {
        "id": "ai_scientist_v2",
        "name": "AI Scientist-v2",
        "skill": "generated_skills/ai_scientist_v2/SKILL.md",
        "source_map": "generated_skills/ai_scientist_v2/references/source_map.json",
        "rubric": "results/evaluations/ai_scientist_v2_rubric_v0.json",
        "context": "results/evaluations/ai_scientist_v2_context_baselines_v0.json",
        "transfer": "results/evaluations/ai_scientist_v2_harness_transfer_v0.json",
        "source_span": "results/evaluations/ai_scientist_v2_source_span_validation_v0.json",
        "live": "results/live_transfer_prompts/ai_scientist_v2_v0/index.json",
    },
    {
        "id": "reflexion",
        "name": "Reflexion",
        "skill": "generated_skills/reflexion/SKILL.md",
        "source_map": "generated_skills/reflexion/references/source_map.json",
        "rubric": "results/evaluations/reflexion_rubric_v0.json",
        "context": "results/evaluations/reflexion_context_baselines_v0.json",
        "transfer": "results/evaluations/reflexion_harness_transfer_v0.json",
        "source_span": "results/evaluations/reflexion_source_span_validation_v0.json",
        "live": "results/live_transfer_prompts/reflexion_v0/index.json",
    },
    {
        "id": "aide",
        "name": "AIDE",
        "skill": "generated_skills/aide/SKILL.md",
        "source_map": "generated_skills/aide/references/source_map.json",
        "rubric": "results/evaluations/aide_rubric_v0.json",
        "context": "results/evaluations/aide_context_baselines_v0.json",
        "transfer": "results/evaluations/aide_harness_transfer_v0.json",
        "source_span": "results/evaluations/aide_source_span_validation_v0.json",
        "live": "results/live_transfer_prompts/aide_v0/index.json",
    },
    {
        "id": "toolformer",
        "name": "Toolformer",
        "skill": "generated_skills/toolformer/SKILL.md",
        "source_map": "generated_skills/toolformer/references/source_map.json",
        "rubric": "results/evaluations/toolformer_rubric_v0.json",
        "context": "results/evaluations/toolformer_context_baselines_v0.json",
        "transfer": "results/evaluations/toolformer_harness_transfer_v0.json",
        "source_span": "results/evaluations/toolformer_source_span_validation_v0.json",
        "live": "results/live_transfer_prompts/toolformer_v0/index.json",
    },
]

CORE_FILES = {
    "memory_long_term": "memory/long_term_memory.md",
    "memory_short_term": "memory/short_term_memory.md",
    "paper_draft": "paper/draft.md",
    "paper_outline": "paper/outline.md",
    "claim_checklist": "paper/claim_checklist.md",
    "limitations": "paper/limitations.md",
    "aaai_package_readme": "paper/aaai/README.md",
    "aaai_papertoskill_tex": "paper/aaai/papertoskill_aaai2027.tex",
    "aaai_papertoskill_tables": "paper/aaai/papertoskill_tables.tex",
    "aaai_papertoskill_refs": "paper/aaai/papertoskill_refs.bib",
    "aaai_build_style": "paper/aaai/aaai2027.sty",
    "aaai_build_bst": "paper/aaai/aaai2027.bst",
    "aaai_author_kit_zip": "paper/aaai/AuthorKit27.zip",
    "aaai_package_checker": "scripts/check_aaai_package.py",
    "aaai_package_report_json": "results/reproducibility/aaai_package_report.json",
    "aaai_package_report_md": "results/reproducibility/aaai_package_report.md",
    "paper_table_checker": "scripts/check_paper_tables.py",
    "paper_table_report_json": "results/reproducibility/paper_table_report.json",
    "paper_table_report_md": "results/reproducibility/paper_table_report.md",
    "paper_claim_checker": "scripts/check_paper_claims.py",
    "paper_claim_report_json": "results/reproducibility/paper_claim_report.json",
    "paper_claim_report_md": "results/reproducibility/paper_claim_report.md",
    "submission_review_checker": "scripts/check_submission_review.py",
    "submission_review_checklist": "research/submission_checklist.md",
    "submission_review_report_json": "results/reproducibility/submission_review_report.json",
    "submission_review_report_md": "results/reproducibility/submission_review_report.md",
    "aaai_submission_decision_checker": "scripts/check_aaai_submission_decision.py",
    "aaai_submission_decision_report_json": "results/aaai_submission_decision/decision.json",
    "aaai_submission_decision_report_md": "results/aaai_submission_decision/decision.md",
    "goal_completion_checker": "scripts/check_goal_completion.py",
    "goal_completion_report_json": "results/reproducibility/goal_completion_report.json",
    "goal_completion_report_md": "results/reproducibility/goal_completion_report.md",
    "external_closure_checker": "scripts/check_external_evidence_closure.py",
    "external_closure_report_json": "results/external_evidence_closure/closure.json",
    "external_closure_report_md": "results/external_evidence_closure/closure.md",
    "external_packets_checker": "scripts/check_external_evidence_packets.py",
    "external_packets_report_json": "results/external_evidence_packets/packets.json",
    "external_packets_report_md": "results/external_evidence_packets/packets.md",
    "ai_scientist_smoke_runner": "scripts/run_ai_scientist_v2_smoke.py",
    "ai_scientist_smoke_report_json": "results/ai_scientist_v2_smoke/run_report.json",
    "ai_scientist_smoke_report_md": "results/ai_scientist_v2_smoke/run_report.md",
    "openai_direct_probe_runner": "scripts/run_openai_compatible_direct_probe.py",
    "openai_direct_probe_claude_report_json": "results/openai_compatible_direct_probe/claude_family/run_report.json",
    "openai_direct_probe_claude_report_md": "results/openai_compatible_direct_probe/claude_family/run_report.md",
    "openai_direct_probe_gpt_report_json": "results/openai_compatible_direct_probe/gpt_family/run_report.json",
    "openai_direct_probe_gpt_report_md": "results/openai_compatible_direct_probe/gpt_family/run_report.md",
    "ai_scientist_live_run_handoff_checker": "scripts/check_ai_scientist_v2_live_run_handoff.py",
    "ai_scientist_live_run_handoff_json": "results/ai_scientist_v2_live_run_handoff/handoff.json",
    "ai_scientist_live_run_handoff_md": "results/ai_scientist_v2_live_run_handoff/handoff.md",
    "usage_examples_readme": "examples/usage/README.md",
    "usage_example_codex_skill": "examples/usage/codex_skill_usage.md",
    "usage_example_auto_note": "examples/usage/auto_note_scaffold_usage.md",
    "usage_example_model_ablation": "examples/usage/model_ablation_usage.md",
    "usage_example_checker": "scripts/check_usage_examples.py",
    "usage_example_report_json": "results/reproducibility/usage_example_report.json",
    "usage_example_report_md": "results/reproducibility/usage_example_report.md",
    "deepseek_followup_configurer": "scripts/configure_deepseek_followup.py",
    "deepseek_followup_checker": "scripts/check_deepseek_followup.py",
    "deepseek_followup_handoff_json": "results/deepseek_followup_handoff/handoff.json",
    "deepseek_followup_handoff_md": "results/deepseek_followup_handoff/handoff.md",
    "artifact_map": "research/artifact_map.md",
    "claim_evidence_matrix": "research/claim_evidence_matrix.md",
    "runbook": "research/runbook.md",
    "goal_completion_audit": "research/goal_completion_audit.md",
    "stage_log": "research/stage_log.md",
    "phase22_model_ablation_run_log": "research/run_logs/2026-06-18_phase22_model_ablation_live_attempt.md",
    "phase23_deepseek_readiness_run_log": "research/run_logs/2026-06-18_phase23_deepseek_followup_readiness.md",
    "phase26_model_ablation_recheck_run_log": "research/run_logs/2026-06-18_phase26_model_ablation_recheck.md",
    "phase27_aaai_package_gate_run_log": "research/run_logs/2026-06-18_phase27_aaai_package_gate.md",
    "phase28_usage_example_gate_run_log": "research/run_logs/2026-06-18_phase28_usage_example_gate.md",
    "phase29_paper_table_gate_run_log": "research/run_logs/2026-06-18_phase29_paper_table_gate.md",
    "phase30_paper_claim_gate_run_log": "research/run_logs/2026-06-18_phase30_paper_claim_gate.md",
    "phase31_goal_completion_run_log": "research/run_logs/2026-06-18_phase31_goal_completion_gate.md",
    "phase32_model_profile_recheck_run_log": "research/run_logs/2026-06-18_phase32_model_profile_recheck.md",
    "phase33_alias_retry_model_recheck_run_log": "research/run_logs/2026-06-19_phase33_alias_retry_model_recheck.md",
    "phase34_pipeline_command_run_log": "research/run_logs/2026-06-19_phase34_pipeline_command.md",
    "phase35_pdf_pipeline_input_run_log": "research/run_logs/2026-06-19_phase35_pdf_pipeline_input.md",
    "phase36_claude_ablation_success_gpt_blocked_run_log": "research/run_logs/2026-06-19_phase36_claude_ablation_success_gpt_blocked.md",
    "phase37_gpt_family_ablation_success_run_log": "research/run_logs/2026-06-19_phase37_gpt_family_ablation_success.md",
    "phase38_model_response_cost_proxy_run_log": "research/run_logs/2026-06-19_phase38_model_response_cost_proxy.md",
    "phase39_toolformer_live_transfer_run_log": "research/run_logs/2026-06-19_phase39_toolformer_live_transfer.md",
    "phase40_all_live_transfer_run_log": "research/run_logs/2026-06-19_phase40_all_live_transfer_responses.md",
    "phase41_ai_scientist_v2_smoke_run_log": "research/run_logs/2026-06-19_phase41_ai_scientist_v2_smoke.md",
    "phase45_ai_scientist_v2_smoke_recheck_run_log": "research/run_logs/2026-06-19_phase45_ai_scientist_v2_smoke_recheck.md",
    "phase46_ai_scientist_v2_smoke_alias_fallback_run_log": "research/run_logs/2026-06-19_phase46_ai_scientist_v2_smoke_alias_fallback.md",
    "phase47_deepseek_followup_handoff_run_log": "research/run_logs/2026-06-19_phase47_deepseek_followup_handoff.md",
    "phase48_ai_scientist_v2_smoke_provider_recheck_run_log": "research/run_logs/2026-06-19_phase48_ai_scientist_v2_smoke_provider_recheck.md",
    "phase49_ai_scientist_v2_live_run_handoff_run_log": "research/run_logs/2026-06-19_phase49_ai_scientist_v2_live_run_handoff.md",
    "phase50_ai_scientist_v2_smoke_timeout_recheck_run_log": "research/run_logs/2026-06-20_phase50_ai_scientist_v2_smoke_timeout_recheck.md",
    "phase51_external_evidence_closure_queue_run_log": "research/run_logs/2026-06-20_phase51_external_evidence_closure_queue.md",
    "phase52_ai_scientist_v2_smoke_retry_run_log": "research/run_logs/2026-06-20_phase52_ai_scientist_v2_smoke_retry.md",
    "phase53_external_evidence_packets_run_log": "research/run_logs/2026-06-20_phase53_external_evidence_packets.md",
    "phase54_ai_scientist_v2_smoke_packet_retry_run_log": "research/run_logs/2026-06-20_phase54_ai_scientist_v2_smoke_packet_retry.md",
    "phase55_aaai_submission_decision_preflight_run_log": "research/run_logs/2026-06-20_phase55_aaai_submission_decision_preflight.md",
    "phase56_ai_scientist_v2_smoke_after_push_recovery_run_log": "research/run_logs/2026-06-20_phase56_ai_scientist_v2_smoke_after_push_recovery.md",
    "phase57_ai_scientist_v2_gpt_smoke_retry_run_log": "research/run_logs/2026-06-20_phase57_ai_scientist_v2_gpt_smoke_retry.md",
    "phase58_ai_scientist_v2_max_token_smoke_run_log": "research/run_logs/2026-06-20_phase58_ai_scientist_v2_max_token_smoke.md",
    "phase59_openai_direct_probe_run_log": "research/run_logs/2026-06-20_phase59_openai_direct_probe.md",
    "provider_billing_protocol": "benchmarks/provider_billing_evidence_v0.json",
    "provider_billing_summarizer": "scripts/summarize_provider_billing_evidence.py",
    "provider_billing_template": "results/provider_billing_evidence/billing_template.csv",
    "provider_billing_summary_json": "results/provider_billing_evidence/billing_summary.json",
    "provider_billing_summary_md": "results/provider_billing_evidence/billing_summary.md",
    "result_cards": "results/result_cards.md",
}

TABLE_FILES = {
    "main_results_md": "results/tables/main_results.md",
    "main_results_csv": "results/tables/main_results.csv",
    "transfer_ablation_md": "results/tables/transfer_ablation.md",
    "context_cost_proxy_md": "results/tables/context_cost_proxy.md",
    "context_cost_proxy_json": "results/tables/context_cost_proxy.json",
    "context_cost_proxy_tokenizer_md": "results/tables/context_cost_proxy_tokenizer.md",
    "context_cost_proxy_tokenizer_json": "results/tables/context_cost_proxy_tokenizer.json",
    "model_response_cost_proxy_md": "results/tables/model_response_cost_proxy.md",
    "model_response_cost_proxy_json": "results/tables/model_response_cost_proxy.json",
    "model_response_cost_proxy_csv": "results/tables/model_response_cost_proxy.csv",
    "auto_note_comparison_md": "results/tables/auto_note_comparison.md",
    "auto_note_comparison_csv": "results/tables/auto_note_comparison.csv",
    "paper_ready_summary": "results/tables/paper_ready_summary.md",
}

AUTO_NOTE_CASES = [
    {
        "id": "toolformer_auto",
        "files": {
            "toolformer_auto_note_script": "scripts/papertoskill_note_from_text.py",
            "toolformer_auto_pipeline_script": "scripts/papertoskill_pipeline.py",
            "toolformer_auto_note": "papers/auto_notes/toolformer_auto_note.md",
            "toolformer_auto_skill": "generated_skills/toolformer_auto/SKILL.md",
            "toolformer_auto_source_map": "generated_skills/toolformer_auto/references/source_map.json",
            "toolformer_auto_note_report": "results/evaluations/toolformer_auto_note_scaffold_v0.json",
            "toolformer_auto_rubric": "results/evaluations/toolformer_auto_rubric_v0.json",
            "toolformer_auto_context": "results/evaluations/toolformer_auto_context_baselines_v0.json",
            "toolformer_auto_transfer": "results/evaluations/toolformer_auto_harness_transfer_v0.json",
            "toolformer_auto_source_span": "results/evaluations/toolformer_auto_source_span_validation_v0.json",
        },
        "rubric": "results/evaluations/toolformer_auto_rubric_v0.json",
        "context": "results/evaluations/toolformer_auto_context_baselines_v0.json",
        "transfer": "results/evaluations/toolformer_auto_harness_transfer_v0.json",
        "source_span": "results/evaluations/toolformer_auto_source_span_validation_v0.json",
    },
    {
        "id": "aide_auto",
        "files": {
            "aide_auto_note": "papers/auto_notes/aide_auto_note.md",
            "aide_auto_skill": "generated_skills/aide_auto/SKILL.md",
            "aide_auto_source_map": "generated_skills/aide_auto/references/source_map.json",
            "aide_auto_note_report": "results/evaluations/aide_auto_note_scaffold_v0.json",
            "aide_auto_rubric": "results/evaluations/aide_auto_rubric_v0.json",
            "aide_auto_context": "results/evaluations/aide_auto_context_baselines_v0.json",
            "aide_auto_transfer": "results/evaluations/aide_auto_harness_transfer_v0.json",
            "aide_auto_source_span": "results/evaluations/aide_auto_source_span_validation_v0.json",
            "aide_auto_context_task": "benchmarks/tasks/aide_auto_research_run.json",
            "aide_auto_transfer_task": "benchmarks/tasks/aide_auto_harness_transfer.json",
            "aide_auto_source_span_task": "benchmarks/tasks/aide_auto_source_span_validation.json",
        },
        "rubric": "results/evaluations/aide_auto_rubric_v0.json",
        "context": "results/evaluations/aide_auto_context_baselines_v0.json",
        "transfer": "results/evaluations/aide_auto_harness_transfer_v0.json",
        "source_span": "results/evaluations/aide_auto_source_span_validation_v0.json",
    },
]

MODEL_ABLATION_FILES = {
    "model_ablation_task": "benchmarks/model_ablation_v0.json",
    "model_ablation_builder": "scripts/build_model_ablation_prompts.py",
    "model_ablation_runner": "scripts/run_model_ablation_prompts.py",
    "model_ablation_response_evaluator": "scripts/evaluate_model_ablation_responses.py",
    "model_response_cost_evaluator": "scripts/evaluate_model_response_costs.py",
    "model_ablation_prompt_index": "results/model_ablation_prompts/v0/index.json",
    "model_ablation_run_report_json": "results/model_ablation_prompts/v0/run_report.json",
    "model_ablation_run_report_md": "results/model_ablation_prompts/v0/run_report.md",
    "model_ablation_gpt_retry_run_report_json": "results/model_ablation_prompts/v0/gpt_retry_run_report.json",
    "model_ablation_gpt_retry_run_report_md": "results/model_ablation_prompts/v0/gpt_retry_run_report.md",
    "model_ablation_evaluation_json": "results/model_ablation_prompts/v0/evaluation.json",
    "model_ablation_evaluation_md": "results/model_ablation_prompts/v0/evaluation.md",
}

LIVE_TRANSFER_FILES = {
    "live_transfer_runner": "scripts/run_live_transfer_prompts.py",
    "live_transfer_response_evaluator": "scripts/evaluate_live_transfer_responses.py",
    "live_transfer_evaluation_json": "results/live_transfer_prompts/evaluation.json",
    "live_transfer_evaluation_md": "results/live_transfer_prompts/evaluation.md",
    "ai_scientist_v2_live_run_report_json": "results/live_transfer_prompts/ai_scientist_v2_v0/run_report.json",
    "ai_scientist_v2_live_run_report_md": "results/live_transfer_prompts/ai_scientist_v2_v0/run_report.md",
    "reflexion_live_run_report_json": "results/live_transfer_prompts/reflexion_v0/run_report.json",
    "reflexion_live_run_report_md": "results/live_transfer_prompts/reflexion_v0/run_report.md",
    "aide_live_run_report_json": "results/live_transfer_prompts/aide_v0/run_report.json",
    "aide_live_run_report_md": "results/live_transfer_prompts/aide_v0/run_report.md",
    "toolformer_live_run_report_json": "results/live_transfer_prompts/toolformer_v0/run_report.json",
    "toolformer_live_run_report_md": "results/live_transfer_prompts/toolformer_v0/run_report.md",
}

LIVE_TRANSFER_CASES = [
    {
        "id": "ai_scientist_v2",
        "task": "ai_scientist_v2_live_transfer",
        "run_report": "results/live_transfer_prompts/ai_scientist_v2_v0/run_report.json",
    },
    {
        "id": "reflexion",
        "task": "reflexion_live_transfer",
        "run_report": "results/live_transfer_prompts/reflexion_v0/run_report.json",
    },
    {
        "id": "aide",
        "task": "aide_live_transfer",
        "run_report": "results/live_transfer_prompts/aide_v0/run_report.json",
    },
    {
        "id": "toolformer",
        "task": "toolformer_live_transfer",
        "run_report": "results/live_transfer_prompts/toolformer_v0/run_report.json",
    },
]

TEXT_SUFFIXES = {
    ".csv",
    ".json",
    ".md",
    ".py",
    ".txt",
    ".yaml",
    ".yml",
}

SECRET_PATTERN = re.compile(r"sk-[A-Za-z0-9]{20,}")


@dataclass
class Check:
    id: str
    status: str
    detail: str
    evidence: str

    def as_dict(self) -> dict[str, str]:
        return {
            "id": self.id,
            "status": self.status,
            "detail": self.detail,
            "evidence": self.evidence,
        }


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_path(root: Path, raw_path: str | Path) -> Path:
    path = Path(raw_path)
    return path if path.is_absolute() else root / path


def required_file_checks(root: Path, files: dict[str, str]) -> list[Check]:
    checks = []
    for check_id, raw_path in files.items():
        path = resolve_path(root, raw_path)
        status = "ready" if path.exists() else "fail"
        detail = "present" if path.exists() else "missing"
        checks.append(Check(check_id, status, detail, str(raw_path)))
    return checks


def score_by_id(results: list[dict[str, Any]], result_id: str) -> dict[str, Any]:
    for item in results:
        if item.get("id") == result_id:
            return item
    raise KeyError(result_id)


def paper_checks(root: Path) -> list[Check]:
    checks: list[Check] = []
    for paper in PAPERS:
        prefix = paper["id"]
        checks.extend(
            required_file_checks(
                root,
                {
                    f"{prefix}_skill": paper["skill"],
                    f"{prefix}_source_map": paper["source_map"],
                    f"{prefix}_rubric": paper["rubric"],
                    f"{prefix}_context": paper["context"],
                    f"{prefix}_transfer": paper["transfer"],
                    f"{prefix}_source_span": paper["source_span"],
                    f"{prefix}_live_prompt_index": paper["live"],
                },
            )
        )

        rubric_path = root / paper["rubric"]
        if rubric_path.exists():
            rubric = load_json(rubric_path)
            score = float(rubric.get("score", 0))
            max_score = float(rubric.get("max_score", 20))
            status = "ready" if score == max_score else "fail"
            checks.append(
                Check(
                    f"{prefix}_rubric_score",
                    status,
                    f"{score:g}/{max_score:g}",
                    paper["rubric"],
                )
            )

        context_path = root / paper["context"]
        if context_path.exists():
            context = load_json(context_path)
            try:
                skill = score_by_id(context["results"], "skill")
                generic = score_by_id(context["results"], "generic_summary")
                abstract = score_by_id(context["results"], "abstract_only")
                status = "ready" if skill["score"] > generic["score"] and skill["score"] > abstract["score"] else "fail"
                detail = f"skill={skill['score']}; generic={generic['score']}; abstract={abstract['score']}"
            except (KeyError, TypeError):
                status = "fail"
                detail = "missing expected skill/generic_summary/abstract_only rows"
            checks.append(Check(f"{prefix}_context_baseline_order", status, detail, paper["context"]))

        transfer_path = root / paper["transfer"]
        if transfer_path.exists():
            transfer = load_json(transfer_path)
            try:
                full = score_by_id(transfer["results"], "full_skill")
                without = score_by_id(transfer["results"], "skill_without_transfer_notes")
                status = "ready" if full["average_normalized_score"] > without["average_normalized_score"] else "fail"
                detail = f"full={full['average_normalized_score']}; no_transfer={without['average_normalized_score']}"
            except (KeyError, TypeError):
                status = "fail"
                detail = "missing expected full_skill/skill_without_transfer_notes rows"
            checks.append(Check(f"{prefix}_transfer_ablation_order", status, detail, paper["transfer"]))

        source_span_path = root / paper["source_span"]
        if source_span_path.exists():
            source_span = load_json(source_span_path)
            result = source_span.get("results", [{}])[0]
            support_rate = float(result.get("support_rate", 0))
            invalid_ranges = int(result.get("invalid_ranges", 0))
            status = "ready" if support_rate >= 0.9 and invalid_ranges == 0 else "fail"
            detail = f"support_rate={support_rate:g}; invalid_ranges={invalid_ranges}"
            checks.append(Check(f"{prefix}_source_span_support", status, detail, paper["source_span"]))

        live_path = root / paper["live"]
        if live_path.exists():
            live = load_json(live_path)
            prompts = live.get("prompts", [])
            prompt_missing = [
                item["prompt_path"]
                for item in prompts
                if not resolve_path(root, item.get("prompt_path", "")).exists()
            ]
            status = "ready" if len(prompts) == 6 and not prompt_missing else "fail"
            detail = f"prompt_packets={len(prompts)}; missing_prompts={len(prompt_missing)}"
            checks.append(Check(f"{prefix}_live_prompt_packets", status, detail, paper["live"]))

            missing_responses = [
                item.get("expected_response_path", "")
                for item in prompts
                if not resolve_path(root, item.get("expected_response_path", "")).exists()
            ]
            response_status = "ready" if not missing_responses else "pending"
            checks.append(
                Check(
                    f"{prefix}_live_responses",
                    response_status,
                    f"missing_response_files={len(missing_responses)}",
                    paper["live"],
                )
            )
    return checks


def human_fidelity_checks(root: Path) -> list[Check]:
    checks = required_file_checks(
        root,
        {
            "human_fidelity_protocol": "benchmarks/human_fidelity_review_v0.json",
            "human_fidelity_guide": "results/human_fidelity_packets/annotation_guide.md",
            "human_fidelity_template": "results/human_fidelity_packets/annotation_template.csv",
            "human_fidelity_summary_json": "results/human_fidelity_packets/annotation_summary.json",
            "human_fidelity_summary_md": "results/human_fidelity_packets/annotation_summary.md",
        },
    )
    index_path = root / "results/human_fidelity_packets/index.json"
    template_path = root / "results/human_fidelity_packets/annotation_template.csv"
    summary_path = root / "results/human_fidelity_packets/annotation_summary.json"
    if summary_path.exists():
        summary = load_json(summary_path)
        errors = summary.get("errors", [])
        status = "ready" if not errors else "fail"
        checks.append(Check("human_fidelity_summary_valid", status, f"errors={len(errors)}", str(summary_path.relative_to(root))))
        expected_rows = 0
        if index_path.exists():
            index = load_json(index_path)
            expected_rows = int(index.get("required_annotation_rows", 0))
        template_rows = 0
        if template_path.exists():
            with template_path.open(newline="", encoding="utf-8") as handle:
                template_rows = sum(1 for _ in csv.DictReader(handle))
        guide_text = (root / "results/human_fidelity_packets/annotation_guide.md").read_text(
            encoding="utf-8", errors="ignore"
        ) if (root / "results/human_fidelity_packets/annotation_guide.md").exists() else ""
        handoff_ready = (
            expected_rows == 24
            and template_rows == expected_rows
            and int(summary.get("total_rows", 0)) == expected_rows
            and "confidence_0_to_1" in guide_text
            and "evidence_locator" in guide_text
        )
        checks.append(
            Check(
                "human_fidelity_annotation_handoff_ready",
                "ready" if handoff_ready else "fail",
                f"expected_rows={expected_rows}; template_rows={template_rows}; summary_rows={summary.get('total_rows', 0)}",
                "results/human_fidelity_packets/index.json; results/human_fidelity_packets/annotation_guide.md",
            )
        )
        annotation_status = summary.get("annotation_status")
        complete_status = "ready" if annotation_status == "complete" else "pending"
        checks.append(
            Check(
                "human_fidelity_annotation_complete",
                complete_status,
                f"status={annotation_status}; scored_rows={summary.get('scored_rows', 0)}; pending_rows={summary.get('pending_rows', 0)}",
                str(summary_path.relative_to(root)),
            )
        )
    return checks


def failure_archive_checks(root: Path) -> list[Check]:
    checks = required_file_checks(
        root,
        {
            "failure_archive_config": "benchmarks/failure_case_archive_v0.json",
            "failure_archive_json": "results/failure_cases/failure_case_archive.json",
            "failure_archive_md": "results/failure_cases/failure_case_archive.md",
            "failure_archive_csv": "results/failure_cases/failure_case_archive.csv",
        },
    )
    archive_path = root / "results/failure_cases/failure_case_archive.json"
    if archive_path.exists():
        archive = load_json(archive_path)
        scope_counts = archive.get("scope_counts", {})
        status = (
            "ready"
            if archive.get("total_cases") == 27 and scope_counts.get("paper") == 21 and scope_counts.get("project") == 6
            else "fail"
        )
        detail = (
            f"total={archive.get('total_cases')}; "
            f"paper={scope_counts.get('paper')}; project={scope_counts.get('project')}"
        )
        checks.append(Check("failure_archive_counts", status, detail, str(archive_path.relative_to(root))))
    return checks


def aaai_package_checks(root: Path) -> list[Check]:
    checks: list[Check] = []
    report_path = root / "results/reproducibility/aaai_package_report.json"
    if not report_path.exists():
        return checks
    report = load_json(report_path)
    status = "ready" if report.get("overall_status") == "ready" else "fail"
    counts = report.get("status_counts", {})
    detail = f"overall={report.get('overall_status')}; counts={counts}"
    checks.append(Check("aaai_package_report_ready", status, detail, str(report_path.relative_to(root))))
    ready_ids = {check.get("id") for check in report.get("checks", []) if check.get("status") == "ready"}
    required_ready = {
        "aaai_author_kit_sha256",
        "aaai_tex_declares_style",
        "aaai_log_loads_style",
        "aaai_log_no_unresolved_items",
        "aaai_log_reports_pdf_output",
        "aaai_pdf_is_fresh",
        "aaai_bbl_is_fresh",
    }
    missing = sorted(required_ready - ready_ids)
    checks.append(
        Check(
            "aaai_package_core_checks_ready",
            "ready" if not missing else "fail",
            "core checks ready" if not missing else "missing=" + ",".join(missing),
            str(report_path.relative_to(root)),
        )
    )
    return checks


def paper_table_checks(root: Path) -> list[Check]:
    checks: list[Check] = []
    report_path = root / "results/reproducibility/paper_table_report.json"
    if not report_path.exists():
        return checks
    report = load_json(report_path)
    status = "ready" if report.get("overall_status") == "ready" else "fail"
    counts = report.get("status_counts", {})
    detail = f"overall={report.get('overall_status')}; counts={counts}"
    checks.append(Check("paper_table_report_ready", status, detail, str(report_path.relative_to(root))))
    ready_ids = {check.get("id") for check in report.get("checks", []) if check.get("status") == "ready"}
    required_ready = {
        "paper_table_main_aide_skill_coverage",
        "paper_table_transfer_toolformer_no_transfer",
        "paper_table_cost_ai_scientist_v2_skill_tokens",
        "paper_table_auto_aide_automatic_extracted_text_note_scaffold_transfer",
    }
    missing = sorted(required_ready - ready_ids)
    checks.append(
        Check(
            "paper_table_core_checks_ready",
            "ready" if not missing else "fail",
            "core checks ready" if not missing else "missing=" + ",".join(missing),
            str(report_path.relative_to(root)),
        )
    )
    return checks


def paper_claim_checks(root: Path) -> list[Check]:
    checks: list[Check] = []
    report_path = root / "results/reproducibility/paper_claim_report.json"
    if not report_path.exists():
        return checks
    report = load_json(report_path)
    status = "ready" if report.get("overall_status") == "ready" else "fail"
    counts = report.get("status_counts", {})
    detail = f"overall={report.get('overall_status')}; counts={counts}"
    checks.append(Check("paper_claim_report_ready", status, detail, str(report_path.relative_to(root))))
    ready_ids = {check.get("id") for check in report.get("checks", []) if check.get("status") == "ready"}
    required_ready = {
        "paper_claim_boundary_curated_scope",
        "paper_claim_boundary_not_pdf_automation",
        "paper_claim_boundary_live_transfer_saved_response_boundary",
        "paper_claim_boundary_model_ablation_partial_boundary",
    }
    missing = sorted(required_ready - ready_ids)
    checks.append(
        Check(
            "paper_claim_core_checks_ready",
            "ready" if not missing else "fail",
            "core checks ready" if not missing else "missing=" + ",".join(missing),
            str(report_path.relative_to(root)),
        )
    )
    return checks


def submission_review_checks(root: Path) -> list[Check]:
    checks: list[Check] = []
    report_path = root / "results/reproducibility/submission_review_report.json"
    if not report_path.exists():
        return checks
    report = load_json(report_path)
    status = "ready" if report.get("overall_status") == "ready" else "fail"
    counts = report.get("status_counts", {})
    detail = f"overall={report.get('overall_status')}; counts={counts}"
    checks.append(Check("submission_review_report_ready", status, detail, str(report_path.relative_to(root))))
    ready_ids = {check.get("id") for check in report.get("checks", []) if check.get("status") == "ready"}
    required_ready = {
        "submission_review_live_transfer_current",
        "submission_review_model_ablation_current",
        "submission_review_human_fidelity_current",
        "submission_review_provider_billing_current",
        "submission_review_ai_scientist_smoke_current",
        "submission_review_goal_package_counts_current",
    }
    missing = sorted(required_ready - ready_ids)
    checks.append(
        Check(
            "submission_review_core_checks_ready",
            "ready" if not missing else "fail",
            "core checks ready" if not missing else "missing=" + ",".join(missing),
            str(report_path.relative_to(root)),
        )
    )
    return checks


def aaai_submission_decision_checks(root: Path) -> list[Check]:
    checks: list[Check] = []
    report_path = root / "results/aaai_submission_decision/decision.json"
    if not report_path.exists():
        return checks
    report = load_json(report_path)
    failed = [check for check in report.get("checks", []) if check.get("status") == "fail"]
    status = (
        "ready"
        if report.get("overall_status") in {"pending_human_decision", "ready"}
        and not failed
        else "fail"
    )
    counts = report.get("status_counts", {})
    checks.append(
        Check(
            "aaai_submission_decision_preflight_ready",
            status,
            f"overall={report.get('overall_status')}; decision_status={report.get('decision_status')}; counts={counts}",
            str(report_path.relative_to(root)),
        )
    )

    check_statuses = {check.get("id"): check.get("status") for check in report.get("checks", [])}
    required_ready = {
        "aaai_submission_decision_local_gates_ready",
        "aaai_submission_decision_pending_evidence_state_current",
        "aaai_submission_decision_external_packet_ready",
        "aaai_submission_decision_boundaries_declared",
        "aaai_submission_decision_options_declared",
        "aaai_submission_decision_no_default_selection",
        "aaai_submission_decision_no_secret_material",
    }
    missing = sorted(check_id for check_id in required_ready if check_statuses.get(check_id) != "ready")
    checks.append(
        Check(
            "aaai_submission_decision_core_checks_ready",
            "ready" if not missing else "fail",
            "core decision preflight checks ready" if not missing else "missing=" + ",".join(missing),
            str(report_path.relative_to(root)),
        )
    )

    option_ids = {option.get("id") for option in report.get("options", [])}
    expected_option_ids = {"submit_now_deterministic_offline", "wait_for_external_evidence"}
    unavailable = sorted(
        option.get("id", "")
        for option in report.get("options", [])
        if option.get("status") != "available_for_human_decision"
    )
    checks.append(
        Check(
            "aaai_submission_decision_options_available",
            "ready" if option_ids == expected_option_ids and not unavailable else "fail",
            (
                "both decision options available for human decision"
                if option_ids == expected_option_ids and not unavailable
                else f"options={','.join(sorted(str(item) for item in option_ids))}; unavailable={','.join(unavailable)}"
            ),
            str(report_path.relative_to(root)),
        )
    )
    return checks


def goal_completion_checks(root: Path) -> list[Check]:
    checks: list[Check] = []
    report_path = root / "results/reproducibility/goal_completion_report.json"
    if not report_path.exists():
        return checks
    report = load_json(report_path)
    status = "ready" if report.get("overall_status") == "not_complete_pending_external_evidence" else "fail"
    counts = report.get("status_counts", {})
    detail = f"overall={report.get('overall_status')}; counts={counts}"
    checks.append(Check("goal_completion_report_ready", status, detail, str(report_path.relative_to(root))))
    check_statuses = {check.get("id"): check.get("status") for check in report.get("checks", [])}
    required_statuses = {
        "active_goal_complete": "pending",
        "aaai_package_gate_ready": "ready",
        "usage_example_gate_ready": "ready",
        "claude_opus_4_8_ablation_attempted": "ready",
        "claude_opus_4_8_ablation_complete": "ready",
        "gpt_family_ablation_complete": "ready",
        "submission_review_handoff_ready": "ready",
        "deepseek_followup_process_ready": "ready",
        "deepseek_followup_response_complete": "pending",
        "human_fidelity_annotation_complete": "pending",
        "provider_billing_evidence_complete": "pending",
        "external_evidence_closure_queue_ready": "ready",
        "external_evidence_execution_packets_ready": "ready",
    }
    mismatches = [
        f"{check_id}={check_statuses.get(check_id)}"
        for check_id, expected_status in required_statuses.items()
        if check_statuses.get(check_id) != expected_status
    ]
    checks.append(
        Check(
            "goal_completion_core_checks_ready",
            "ready" if not mismatches else "fail",
            "core completion boundaries ready" if not mismatches else "mismatches=" + ",".join(mismatches),
            str(report_path.relative_to(root)),
        )
    )
    return checks


def external_evidence_closure_checks(root: Path) -> list[Check]:
    checks: list[Check] = []
    report_path = root / "results/external_evidence_closure/closure.json"
    if not report_path.exists():
        return checks
    report = load_json(report_path)
    failed = [check for check in report.get("checks", []) if check.get("status") == "fail"]
    status = (
        "ready"
        if report.get("overall_status") in {"pending_external_evidence", "complete"}
        and not failed
        else "fail"
    )
    counts = report.get("status_counts", {})
    detail = f"overall={report.get('overall_status')}; counts={counts}; item_counts={report.get('item_status_counts')}"
    checks.append(Check("external_evidence_closure_report_ready", status, detail, str(report_path.relative_to(root))))

    check_statuses = {check.get("id"): check.get("status") for check in report.get("checks", [])}
    required_ready = {
        "external_closure_required_reports_present",
        "external_closure_goal_pending_items_covered",
        "external_closure_queue_items_declared",
    }
    missing = sorted(check_id for check_id in required_ready if check_statuses.get(check_id) != "ready")
    checks.append(
        Check(
            "external_evidence_closure_core_checks_ready",
            "ready" if not missing else "fail",
            "core closure checks ready" if not missing else "missing=" + ",".join(missing),
            str(report_path.relative_to(root)),
        )
    )

    item_ids = {item.get("id") for item in report.get("items", [])}
    required_items = {
        "ai_scientist_v2_smoke_completion",
        "ai_scientist_v2_full_live_run",
        "deepseek_followup_responses",
        "human_fidelity_annotation",
        "provider_billing_success_per_dollar",
        "aaai_submission_decision",
    }
    missing_items = sorted(required_items - item_ids)
    checks.append(
        Check(
            "external_evidence_closure_queue_items_ready",
            "ready" if not missing_items else "fail",
            "closure queue items declared" if not missing_items else "missing=" + ",".join(missing_items),
            str(report_path.relative_to(root)),
        )
    )
    return checks


def external_evidence_packet_checks(root: Path) -> list[Check]:
    checks: list[Check] = []
    report_path = root / "results/external_evidence_packets/packets.json"
    if not report_path.exists():
        return checks
    report = load_json(report_path)
    failed = [check for check in report.get("checks", []) if check.get("status") == "fail"]
    status = "ready" if report.get("overall_status") == "ready" and not failed else "fail"
    counts = report.get("status_counts", {})
    checks.append(
        Check(
            "external_evidence_packets_report_ready",
            status,
            f"overall={report.get('overall_status')}; counts={counts}; packets={len(report.get('packets', []))}",
            str(report_path.relative_to(root)),
        )
    )

    check_statuses = {check.get("id"): check.get("status") for check in report.get("checks", [])}
    required_ready = {
        "external_evidence_packets_closure_present",
        "external_evidence_packets_match_closure",
        "external_evidence_packets_have_details",
        "external_evidence_packets_commands_declared",
        "external_evidence_packets_completion_criteria_declared",
        "external_evidence_packets_boundaries_declared",
        "external_evidence_packets_no_secret_material",
    }
    missing = sorted(check_id for check_id in required_ready if check_statuses.get(check_id) != "ready")
    checks.append(
        Check(
            "external_evidence_packets_core_checks_ready",
            "ready" if not missing else "fail",
            "core packet checks ready" if not missing else "missing=" + ",".join(missing),
            str(report_path.relative_to(root)),
        )
    )

    packet_ids = {packet.get("id") for packet in report.get("packets", [])}
    required_packets = {
        "ai_scientist_v2_smoke_completion",
        "ai_scientist_v2_full_live_run",
        "deepseek_followup_responses",
        "human_fidelity_annotation",
        "provider_billing_success_per_dollar",
        "aaai_submission_decision",
    }
    missing_packets = sorted(required_packets - packet_ids)
    checks.append(
        Check(
            "external_evidence_packets_items_ready",
            "ready" if not missing_packets else "fail",
            "execution packets declared" if not missing_packets else "missing=" + ",".join(missing_packets),
            str(report_path.relative_to(root)),
        )
    )
    return checks


def ai_scientist_smoke_checks(root: Path) -> list[Check]:
    checks: list[Check] = []
    runner_path = root / "scripts/run_ai_scientist_v2_smoke.py"
    if runner_path.exists():
        runner_text = runner_path.read_text(encoding="utf-8")
        has_status_summary = "def status_summary(" in runner_text and "overall_status=" in runner_text
        has_require_complete = "--require-complete" in runner_text and "def exit_code(" in runner_text
        has_timeout = "--timeout-seconds" in runner_text and "thread.join(args.timeout_seconds)" in runner_text
        has_alias_fallback = "--model-alias" in runner_text and "attempted_models" in runner_text
        has_max_tokens = "--max-tokens" in runner_text and "MAX_NUM_TOKENS" in runner_text
        checks.append(
            Check(
                "ai_scientist_v2_smoke_cli_status_summary",
                "ready"
                if has_status_summary and has_require_complete and has_timeout and has_alias_fallback and has_max_tokens
                else "fail",
                (
                    f"status_summary={has_status_summary}; "
                    f"require_complete={has_require_complete}; "
                    f"timeout={has_timeout}; "
                    f"alias_fallback={has_alias_fallback}; "
                    f"max_tokens={has_max_tokens}"
                ),
                str(runner_path.relative_to(root)),
            )
        )
    report_path = root / "results/ai_scientist_v2_smoke/run_report.json"
    if not report_path.exists():
        return checks
    report = load_json(report_path)
    status = "ready" if report.get("overall_status") == "complete" else "pending"
    counts = report.get("status_counts", {})
    detail = f"overall={report.get('overall_status')}; counts={counts}"
    checks.append(Check("ai_scientist_v2_llm_smoke_complete", status, detail, str(report_path.relative_to(root))))
    response_path = root / "results/ai_scientist_v2_smoke/response.md"
    checks.append(
        Check(
            "ai_scientist_v2_llm_smoke_response",
            "ready" if response_path.exists() else "pending",
            "present" if response_path.exists() else "missing until provider returns response",
            str(response_path.relative_to(root)),
        )
    )
    ready_ids = {check.get("id") for check in report.get("checks", []) if check.get("status") == "ready"}
    required_ready = {
        "ai_scientist_v2_llm_response_saved",
        "ai_scientist_v2_smoke_marker_papertoskill_smoke_ok",
        "ai_scientist_v2_smoke_marker_ai_scientist_v2",
        "ai_scientist_v2_smoke_marker_paper_to_skill",
    }
    missing = sorted(required_ready - ready_ids)
    checks.append(
        Check(
            "ai_scientist_v2_llm_smoke_contract_ready",
            "ready" if not missing else "pending",
            "contract markers ready" if not missing else "missing=" + ",".join(missing),
            str(report_path.relative_to(root)),
        )
    )
    return checks


def openai_compatible_direct_probe_checks(root: Path) -> list[Check]:
    checks: list[Check] = []
    runner_path = root / "scripts/run_openai_compatible_direct_probe.py"
    if runner_path.exists():
        runner_text = runner_path.read_text(encoding="utf-8")
        has_status_summary = "def status_summary(" in runner_text and "overall_status=" in runner_text
        has_require_complete = "--require-complete" in runner_text and "def exit_code(" in runner_text
        has_alias_fallback = "--model-alias" in runner_text and "attempted_models" in runner_text
        has_max_tokens = "--max-tokens" in runner_text and "max_tokens" in runner_text
        checks.append(
            Check(
                "openai_direct_probe_cli_ready",
                "ready"
                if has_status_summary and has_require_complete and has_alias_fallback and has_max_tokens
                else "fail",
                (
                    f"status_summary={has_status_summary}; "
                    f"require_complete={has_require_complete}; "
                    f"alias_fallback={has_alias_fallback}; "
                    f"max_tokens={has_max_tokens}"
                ),
                str(runner_path.relative_to(root)),
            )
        )

    profile_reports = {
        "claude_family": root / "results/openai_compatible_direct_probe/claude_family/run_report.json",
        "gpt_family": root / "results/openai_compatible_direct_probe/gpt_family/run_report.json",
    }
    allowed_statuses = {
        "complete",
        "blocked_by_provider_or_model_availability",
        "pending_configuration",
        "pending",
    }
    required_markers = {
        "direct_probe_response_saved",
        "direct_probe_marker_papertoskill_smoke_ok",
        "direct_probe_marker_ai_scientist_v2",
        "direct_probe_marker_paper_to_skill",
    }
    for profile, report_path in profile_reports.items():
        if not report_path.exists():
            continue
        report = load_json(report_path)
        overall = report.get("overall_status")
        counts = report.get("status_counts", {})
        checks.append(
            Check(
                f"openai_direct_probe_{profile}_report_ready",
                "ready" if overall in allowed_statuses else "fail",
                f"overall={overall}; counts={counts}; attempted={len(report.get('attempted_models', []))}",
                str(report_path.relative_to(root)),
            )
        )
        ready_ids = {check.get("id") for check in report.get("checks", []) if check.get("status") == "ready"}
        marker_failures = [check.get("id") for check in report.get("checks", []) if check.get("status") == "fail"]
        missing_markers = sorted(required_markers - ready_ids)
        complete = overall == "complete"
        consistent = (complete and not missing_markers and not marker_failures) or (
            not complete and not marker_failures
        )
        detail = "contract consistent"
        if missing_markers and complete:
            detail = "missing=" + ",".join(missing_markers)
        elif marker_failures:
            detail = "failed=" + ",".join(str(item) for item in marker_failures)
        checks.append(
            Check(
                f"openai_direct_probe_{profile}_contract_consistent",
                "ready" if consistent else "fail",
                detail,
                str(report_path.relative_to(root)),
            )
        )
    return checks


def ai_scientist_live_run_handoff_checks(root: Path) -> list[Check]:
    checks: list[Check] = []
    report_path = root / "results/ai_scientist_v2_live_run_handoff/handoff.json"
    if not report_path.exists():
        return checks
    report = load_json(report_path)
    failed = [check for check in report.get("checks", []) if check.get("status") == "fail"]
    check_statuses = {check.get("id"): check.get("status") for check in report.get("checks", [])}
    ready_or_pending = report.get("overall_status") in {
        "blocked_by_provider_smoke",
        "ready_to_run",
        "complete",
    }
    checks.append(
        Check(
            "ai_scientist_v2_live_run_handoff_report_ready",
            "ready" if ready_or_pending and not failed else "fail",
            f"overall={report.get('overall_status')}; failed={len(failed)}",
            str(report_path.relative_to(root)),
        )
    )
    required_ready = {
        "ai_scientist_v2_live_root_present",
        "ai_scientist_v2_live_launcher_present",
        "ai_scientist_v2_live_launcher_flags_ready",
        "ai_scientist_v2_live_config_present",
        "ai_scientist_v2_live_config_laptop_profile",
        "ai_scientist_v2_live_seed_ideas_present",
        "ai_scientist_v2_live_seed_idea_selected",
        "ai_scientist_v2_live_dry_run_artifacts_present",
        "ai_scientist_v2_live_env_names_declared",
        "ai_scientist_v2_live_next_commands_declared",
    }
    missing = sorted(check_id for check_id in required_ready if check_statuses.get(check_id) != "ready")
    checks.append(
        Check(
            "ai_scientist_v2_live_run_handoff_core_checks_ready",
            "ready" if not missing else "fail",
            "core live-run handoff checks ready" if not missing else "missing=" + ",".join(missing),
            str(report_path.relative_to(root)),
        )
    )
    checks.append(
        Check(
            "ai_scientist_v2_live_run_completion",
            "ready" if report.get("overall_status") == "complete" else "pending",
            f"overall={report.get('overall_status')}; completion_dirs={len(report.get('completion_dirs', []))}",
            str(report_path.relative_to(root)),
        )
    )
    return checks


def provider_billing_checks(root: Path) -> list[Check]:
    checks: list[Check] = []
    summary_path = root / "results/provider_billing_evidence/billing_summary.json"
    template_path = root / "results/provider_billing_evidence/billing_template.csv"
    if not summary_path.exists():
        return checks
    summary = load_json(summary_path)
    errors = summary.get("errors", [])
    checks.append(
        Check(
            "provider_billing_summary_valid",
            "ready" if not errors else "fail",
            f"errors={len(errors)}",
            str(summary_path.relative_to(root)),
        )
    )
    template_rows = 0
    if template_path.exists():
        with template_path.open(newline="", encoding="utf-8") as handle:
            template_rows = sum(1 for _ in csv.DictReader(handle))
    handoff_ready = template_rows == int(summary.get("total_rows", 0)) == 6
    checks.append(
        Check(
            "provider_billing_evidence_handoff_ready",
            "ready" if handoff_ready else "fail",
            f"template_rows={template_rows}; summary_rows={summary.get('total_rows', 0)}",
            "results/provider_billing_evidence/billing_template.csv; results/provider_billing_evidence/billing_summary.json",
        )
    )
    checks.append(
        Check(
            "provider_billing_evidence_complete",
            "ready" if summary.get("billing_status") == "complete" else "pending",
            f"status={summary.get('billing_status')}; measured_rows={summary.get('measured_rows')}; pending_rows={summary.get('pending_rows')}",
            str(summary_path.relative_to(root)),
        )
    )
    return checks


def usage_example_checks(root: Path) -> list[Check]:
    checks: list[Check] = []
    report_path = root / "results/reproducibility/usage_example_report.json"
    if not report_path.exists():
        return checks
    report = load_json(report_path)
    status = "ready" if report.get("overall_status") == "ready" else "fail"
    counts = report.get("status_counts", {})
    detail = f"overall={report.get('overall_status')}; counts={counts}"
    checks.append(Check("usage_example_report_ready", status, detail, str(report_path.relative_to(root))))
    ready_ids = {check.get("id") for check in report.get("checks", []) if check.get("status") == "ready"}
    required_ready = {
        "codex_toolformer_prompt",
        "usage_model_ablation_prompt_grid",
        "usage_model_ablation_response_slots",
        "usage_model_ablation_gpt_profile",
        "usage_model_ablation_claude_alias_candidates",
        "usage_deepseek_followup_handoff",
        "usage_deepseek_followup_prompt_rows",
        "usage_deepseek_followup_next_commands",
        "usage_auto_note_example_rubric_score",
        "usage_auto_note_example_selected_windows",
        "usage_pdf_pipeline_example_manifest_created",
        "usage_pdf_pipeline_example_text_extracted",
    }
    missing = sorted(required_ready - ready_ids)
    checks.append(
        Check(
            "usage_example_core_checks_ready",
            "ready" if not missing else "fail",
            "core checks ready" if not missing else "missing=" + ",".join(missing),
            str(report_path.relative_to(root)),
        )
    )
    return checks


def deepseek_followup_handoff_checks(root: Path) -> list[Check]:
    checks: list[Check] = []
    report_path = root / "results/deepseek_followup_handoff/handoff.json"
    if not report_path.exists():
        return checks
    report = load_json(report_path)
    failed = [check for check in report.get("checks", []) if check.get("status") == "fail"]
    check_statuses = {check.get("id"): check.get("status") for check in report.get("checks", [])}
    ready_or_pending = report.get("overall_status") in {
        "pending_user_configuration",
        "ready_to_run",
        "responses_present",
    }
    checks.append(
        Check(
            "deepseek_followup_handoff_report_ready",
            "ready" if ready_or_pending and not failed else "fail",
            f"overall={report.get('overall_status')}; failed={len(failed)}",
            str(report_path.relative_to(root)),
        )
    )
    required_ready = {
        "deepseek_followup_slot_present",
        "deepseek_followup_index_rows",
        "deepseek_followup_prompt_files",
        "deepseek_followup_response_paths_declared",
        "deepseek_followup_env_names_declared",
    }
    missing = sorted(check_id for check_id in required_ready if check_statuses.get(check_id) != "ready")
    checks.append(
        Check(
            "deepseek_followup_handoff_core_checks_ready",
            "ready" if not missing else "fail",
            "core handoff checks ready" if not missing else "missing=" + ",".join(missing),
            str(report_path.relative_to(root)),
        )
    )
    return checks


def auto_note_checks(root: Path) -> list[Check]:
    checks: list[Check] = []
    for case in AUTO_NOTE_CASES:
        prefix = case["id"]
        checks.extend(required_file_checks(root, case["files"]))

        rubric_path = root / case["rubric"]
        if rubric_path.exists():
            rubric = load_json(rubric_path)
            score = float(rubric.get("score", 0))
            max_score = float(rubric.get("max_score", 20))
            status = "ready" if score == max_score else "fail"
            checks.append(Check(f"{prefix}_rubric_score", status, f"{score:g}/{max_score:g}", str(rubric_path.relative_to(root))))

        context_path = root / case["context"]
        if context_path.exists():
            context = load_json(context_path)
            try:
                skill = score_by_id(context["results"], "skill")
                generic = score_by_id(context["results"], "generic_summary")
                abstract = score_by_id(context["results"], "abstract_only")
                status = "ready" if skill["score"] > generic["score"] and skill["score"] > abstract["score"] else "fail"
                detail = f"skill={skill['score']}; generic={generic['score']}; abstract={abstract['score']}"
            except (KeyError, TypeError):
                status = "fail"
                detail = "missing expected skill/generic_summary/abstract_only rows"
            checks.append(Check(f"{prefix}_context_baseline_order", status, detail, str(context_path.relative_to(root))))

        transfer_path = root / case["transfer"]
        if transfer_path.exists():
            transfer = load_json(transfer_path)
            try:
                full = score_by_id(transfer["results"], "full_skill")
                without = score_by_id(transfer["results"], "skill_without_transfer_notes")
                status = "ready" if full["average_normalized_score"] > without["average_normalized_score"] else "fail"
                detail = f"full={full['average_normalized_score']}; no_transfer={without['average_normalized_score']}"
            except (KeyError, TypeError):
                status = "fail"
                detail = "missing expected full_skill/skill_without_transfer_notes rows"
            checks.append(Check(f"{prefix}_transfer_ablation_order", status, detail, str(transfer_path.relative_to(root))))

        source_span_path = root / case["source_span"]
        if source_span_path.exists():
            source_span = load_json(source_span_path)
            result = source_span.get("results", [{}])[0]
            support_rate = float(result.get("support_rate", 0))
            invalid_ranges = int(result.get("invalid_ranges", 0))
            status = "ready" if support_rate >= 0.9 and invalid_ranges == 0 else "fail"
            detail = f"support_rate={support_rate:g}; invalid_ranges={invalid_ranges}"
            checks.append(Check(f"{prefix}_source_span_support", status, detail, str(source_span_path.relative_to(root))))
    return checks


def model_ablation_checks(root: Path) -> list[Check]:
    checks = required_file_checks(root, MODEL_ABLATION_FILES)
    index_path = root / "results/model_ablation_prompts/v0/index.json"
    if index_path.exists():
        index = load_json(index_path)
        prompts = index.get("prompts", [])
        prompt_missing = [
            item.get("prompt_path", "")
            for item in prompts
            if not resolve_path(root, item.get("prompt_path", "")).exists()
        ]
        status = "ready" if len(prompts) == 6 and not prompt_missing else "fail"
        detail = f"prompt_packets={len(prompts)}; missing_prompts={len(prompt_missing)}"
        checks.append(Check("model_ablation_prompt_packets", status, detail, str(index_path.relative_to(root))))

        model_ids = {item.get("model_id", "") for item in prompts}
        expected_model_ids = {"claude_opus_4_8", "gpt_5_5_or_gpt_family", "deepseek_followup_slot"}
        status = "ready" if expected_model_ids <= model_ids else "fail"
        detail = "models=" + ",".join(sorted(model_ids))
        checks.append(Check("model_ablation_model_slots", status, detail, str(index_path.relative_to(root))))

        missing_responses = [
            item.get("expected_response_path", "")
            for item in prompts
            if not resolve_path(root, item.get("expected_response_path", "")).exists()
        ]
        response_status = "ready" if not missing_responses else "pending"
        checks.append(
            Check(
                "model_ablation_responses",
                response_status,
                f"missing_response_files={len(missing_responses)}",
                str(index_path.relative_to(root)),
            )
        )

    run_report_path = root / "results/model_ablation_prompts/v0/run_report.json"
    if run_report_path.exists():
        run_report = load_json(run_report_path)
        status = "ready" if run_report.get("results") else "fail"
        detail = f"overall={run_report.get('overall_status')}; counts={run_report.get('status_counts')}"
        checks.append(Check("model_ablation_run_report_valid", status, detail, str(run_report_path.relative_to(root))))

    evaluation_path = root / "results/model_ablation_prompts/v0/evaluation.json"
    if evaluation_path.exists():
        evaluation = load_json(evaluation_path)
        summary = evaluation.get("summary", {})
        pending = int(summary.get("pending_rows", 0))
        scored = int(summary.get("scored_rows", 0))
        status = "ready" if pending == 0 and scored > 0 else "pending"
        detail = f"scored_rows={scored}; pending_rows={pending}"
        checks.append(Check("model_ablation_evaluation_complete", status, detail, str(evaluation_path.relative_to(root))))
    response_cost_path = root / "results/tables/model_response_cost_proxy.json"
    if response_cost_path.exists():
        response_cost = load_json(response_cost_path)
        summary = response_cost.get("summary", {})
        measured = int(summary.get("measured_rows", 0))
        pending = int(summary.get("pending_rows", 0))
        tokenizer_tokens = summary.get("total_tokenizer_output_tokens")
        status = "ready" if measured >= 4 and pending == 2 and tokenizer_tokens else "fail"
        detail = f"measured_rows={measured}; pending_rows={pending}; tokenizer_output_tokens={tokenizer_tokens}"
        checks.append(Check("model_response_output_token_proxy", status, detail, str(response_cost_path.relative_to(root))))
    return checks


def live_transfer_checks(root: Path) -> list[Check]:
    checks = required_file_checks(root, LIVE_TRANSFER_FILES)
    evaluation_path = root / "results/live_transfer_prompts/evaluation.json"
    if evaluation_path.exists():
        evaluation = load_json(evaluation_path)
        summary = evaluation.get("summary", {})
        results = evaluation.get("results", [])
        total = int(summary.get("total_rows", 0))
        scored = int(summary.get("scored_rows", 0))
        pending = int(summary.get("pending_rows", 0))
        counted_scored = sum(1 for row in results if row.get("status") == "scored")
        counted_pending = sum(1 for row in results if row.get("status") == "pending")
        valid = total == len(results) == 24 and scored == counted_scored and pending == counted_pending
        checks.append(
            Check(
                "live_transfer_evaluation_valid",
                "ready" if valid else "fail",
                f"total_rows={total}; scored_rows={scored}; pending_rows={pending}",
                str(evaluation_path.relative_to(root)),
            )
        )

        for case in LIVE_TRANSFER_CASES:
            rows = [row for row in results if row.get("task") == case["task"]]
            scored_rows = [row for row in rows if row.get("status") == "scored"]
            ready = len(rows) == 6 and len(scored_rows) == 6 and all(
                float(row.get("normalized_score", 0)) >= 1.0 for row in scored_rows
            )
            checks.append(
                Check(
                    f"{case['id']}_live_transfer_responses_scored",
                    "ready" if ready else "pending",
                    f"scored_rows={len(scored_rows)}/6",
                    str(evaluation_path.relative_to(root)),
                )
            )
        checks.append(
            Check(
                "live_transfer_all_responses_scored",
                "ready" if pending == 0 and scored == total and total > 0 else "pending",
                f"scored_rows={scored}; pending_rows={pending}",
                str(evaluation_path.relative_to(root)),
            )
        )

    for case in LIVE_TRANSFER_CASES:
        run_report_path = root / case["run_report"]
        if not run_report_path.exists():
            continue
        run_report = load_json(run_report_path)
        counts = run_report.get("status_counts", {})
        status = "ready" if run_report.get("overall_status") == "complete" and counts.get("success") == 6 else "fail"
        detail = f"overall={run_report.get('overall_status')}; counts={counts}; alias_count={len(run_report.get('model_aliases', []))}"
        checks.append(Check(f"{case['id']}_live_run_report_complete", status, detail, str(run_report_path.relative_to(root))))
    return checks


def secret_scan_check(root: Path) -> Check:
    matches = []
    for path in root.rglob("*"):
        if not path.is_file() or ".git" in path.parts or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for line_number, line in enumerate(text.splitlines(), start=1):
            if SECRET_PATTERN.search(line):
                matches.append(f"{path.relative_to(root)}:{line_number}")
    status = "ready" if not matches else "fail"
    detail = "no raw API-key-like strings found" if not matches else "; ".join(matches[:10])
    return Check("secret_scan", status, detail, "repository text files")


def build_report(root: Path) -> dict[str, Any]:
    checks: list[Check] = []
    checks.extend(required_file_checks(root, CORE_FILES))
    checks.extend(required_file_checks(root, TABLE_FILES))
    checks.extend(paper_checks(root))
    checks.extend(human_fidelity_checks(root))
    checks.extend(failure_archive_checks(root))
    checks.extend(aaai_package_checks(root))
    checks.extend(paper_table_checks(root))
    checks.extend(paper_claim_checks(root))
    checks.extend(submission_review_checks(root))
    checks.extend(aaai_submission_decision_checks(root))
    checks.extend(goal_completion_checks(root))
    checks.extend(external_evidence_closure_checks(root))
    checks.extend(external_evidence_packet_checks(root))
    checks.extend(ai_scientist_smoke_checks(root))
    checks.extend(openai_compatible_direct_probe_checks(root))
    checks.extend(ai_scientist_live_run_handoff_checks(root))
    checks.extend(provider_billing_checks(root))
    checks.extend(usage_example_checks(root))
    checks.extend(deepseek_followup_handoff_checks(root))
    checks.extend(auto_note_checks(root))
    checks.extend(model_ablation_checks(root))
    checks.extend(live_transfer_checks(root))
    checks.append(secret_scan_check(root))

    status_counts = {"ready": 0, "pending": 0, "fail": 0}
    for check in checks:
        status_counts[check.status] = status_counts.get(check.status, 0) + 1

    if status_counts.get("fail", 0):
        overall = "fail"
    elif status_counts.get("pending", 0):
        overall = "ready_with_pending_external_evidence"
    else:
        overall = "ready"

    return {
        "schema_version": "0.1",
        "evidence_boundary": (
            "Checks local reproducibility artifacts and evidence gates. Pending live responses or human "
            "annotations are reported as pending external evidence, not local package failures."
        ),
        "overall_status": overall,
        "status_counts": status_counts,
        "checks": [check.as_dict() for check in checks],
    }


def markdown_table(rows: list[list[str]], columns: list[str]) -> str:
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for row in rows:
        values = [value.replace("|", "\\|").replace("\n", " ") for value in row]
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    rows = [
        [check["id"], check["status"], check["detail"], check["evidence"]]
        for check in report["checks"]
    ]
    counts = report["status_counts"]
    lines = [
        "# Reproducibility Package Report",
        "",
        "Evidence boundary: this report checks local package completeness and separates "
        "pending external evidence from local failures.",
        "",
        f"- Overall status: {report['overall_status']}",
        f"- Ready checks: {counts.get('ready', 0)}",
        f"- Pending checks: {counts.get('pending', 0)}",
        f"- Failed checks: {counts.get('fail', 0)}",
        "",
        "## Checks",
        "",
        markdown_table(rows, ["Check", "Status", "Detail", "Evidence"]),
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def write_json(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="Check the PaperToSkill reproducibility package.")
    parser.add_argument("--output-json", type=Path, default=root / "results" / "reproducibility" / "package_report.json")
    parser.add_argument("--output-md", type=Path, default=root / "results" / "reproducibility" / "package_report.md")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero if any local package check fails.")
    args = parser.parse_args()

    report = build_report(root)
    write_json(args.output_json, report)
    write_markdown(args.output_md, report)
    print(args.output_json)
    print(args.output_md)
    if args.strict and report["overall_status"] == "fail":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
