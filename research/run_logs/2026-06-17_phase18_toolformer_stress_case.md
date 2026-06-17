# Phase 18 Toolformer Stress Case Run Log

Date: 2026-06-17

## Purpose

Add Toolformer as a fourth curated real-paper benchmark case to reduce the
agent/ML-engineering-only benchmark risk and test PaperToSkill on an explicit
tool-use/API-contract paper.

## Commands

```powershell
python scripts/evaluate_skill.py --skill generated_skills/toolformer/SKILL.md --rubric benchmarks/rubric_toolformer_v0.json --output results/evaluations/toolformer_rubric_v0.json
python scripts/evaluate_context_baselines.py --task benchmarks/tasks/toolformer_research_run.json --output results/evaluations/toolformer_context_baselines_v0.json
python scripts/evaluate_harness_transfer.py --task benchmarks/tasks/toolformer_harness_transfer.json --output results/evaluations/toolformer_harness_transfer_v0.json
python scripts/validate_source_spans.py --task benchmarks/tasks/toolformer_source_span_validation.json --output results/evaluations/toolformer_source_span_validation_v0.json
python scripts/build_live_transfer_prompts.py --task benchmarks/tasks/toolformer_live_transfer.json --output-dir results/live_transfer_prompts/toolformer_v0
python scripts/aggregate_results_tables.py --output-dir results/tables
python scripts/evaluate_context_costs.py --output-dir results/tables
python scripts/build_human_fidelity_packets.py --output-dir results/human_fidelity_packets
python scripts/summarize_human_fidelity_annotations.py --output-json results/human_fidelity_packets/annotation_summary.json --output-md results/human_fidelity_packets/annotation_summary.md
python scripts/build_failure_case_archive.py --output-dir results/failure_cases
python scripts/check_reproducibility_package.py --output-json results/reproducibility/package_report.json --output-md results/reproducibility/package_report.md --strict
```

## Outputs

- `papers/raw/toolformer.pdf`
- `papers/extracted/toolformer.txt`
- `papers/notes/toolformer_note.md`
- `generated_skills/toolformer/SKILL.md`
- `generated_skills/toolformer/references/source_map.json`
- `benchmarks/rubric_toolformer_v0.json`
- `benchmarks/tasks/toolformer_research_run.json`
- `benchmarks/tasks/toolformer_harness_transfer.json`
- `benchmarks/tasks/toolformer_live_transfer.json`
- `benchmarks/tasks/toolformer_source_span_validation.json`
- `baselines/toolformer_generic_summary.md`
- `baselines/toolformer_abstract_only.md`
- `results/evaluations/toolformer_rubric_v0.json`
- `results/evaluations/toolformer_context_baselines_v0.json`
- `results/evaluations/toolformer_harness_transfer_v0.json`
- `results/evaluations/toolformer_source_span_validation_v0.json`
- `results/live_transfer_prompts/toolformer_v0/`
- Updated result tables, context-cost proxy, human-fidelity packets, failure
  archive, reproducibility package report, paper draft package, and memory.

## Results

- Toolformer skill rubric: `20/20`.
- Toolformer context coverage:
  - generated skill: `8.9/10`
  - generic summary: `2.5/10`
  - abstract-only context: `1.534/10`
- Toolformer harness-transfer readiness:
  - full skill: `10.0/10`
  - no-transfer-notes: `7.6/10`
  - generic summary: `1.45/10`
- Toolformer source-span validation:
  - supported claims: `22/22`
  - support rate: `1.0`
  - invalid ranges: `0`
- Context cost proxy for Toolformer:
  - generated skill: `1,526` estimated input tokens
  - full extracted paper: `24,097` estimated input tokens
  - token-proxy reduction: `93.67%`
- Human-fidelity packet set now covers four papers with `24` blank annotation
  rows.
- Failure archive now records `27` cases: `21` paper-reported and `6`
  project-level.
- Reproducibility package report now shows `75` ready checks, `5` pending
  checks, and `0` failed checks.

## Evidence Boundary

Phase 18 adds deterministic/offline evidence for a fourth curated paper note. It
does not complete live cross-harness execution, human-fidelity annotation,
tokenizer-exact pricing, provider billing, or success-per-dollar evidence.

## Verification

- `python -m unittest discover -s tests -v`
  - passed, 17 tests OK
- `git diff --check`
  - no whitespace errors; Windows LF/CRLF warnings only
- `rg -n "sk-[A-Za-z0-9]{20,}" .`
  - no matches
