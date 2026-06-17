# Phase 10 Run Log: AIDE Third Real-Paper Case

- Run ID: phase10_aide_third_paper
- Date: 2026-06-17
- Objective: add AIDE as a third real-paper benchmark case for PaperToSkill and
  refresh the paper-ready result tables.
- Endpoint check:
  - `/v1/models` succeeded and listed `claude-opus-4-8`.
  - `/v1/chat/completions` returned HTTP 503 Service Unavailable with an empty
    response body.
  - Decision: continue with deterministic/offline benchmark expansion rather
    than blocking on remote provider recovery.
- Source processing:
  - `Invoke-WebRequest -Uri https://arxiv.org/pdf/2502.13138 -OutFile papers\raw\aide.pdf`
  - `pdfinfo papers\raw\aide.pdf`
  - `pdftotext -layout papers\raw\aide.pdf papers\extracted\aide.txt`
  - `pdftoppm -f 1 -l 1 -png -r 120 papers\raw\aide.pdf output\pdf\aide\page`
- Main commands:
  - `python scripts\papertoskill_extract.py --source papers\notes\aide_note.md --output generated_skills\aide --name aide-paper-skill`
  - `python scripts\evaluate_skill.py --skill generated_skills\aide\SKILL.md --rubric benchmarks\rubric_aide_v0.json --output results\evaluations\aide_rubric_v0.json`
  - `python scripts\evaluate_context_baselines.py --task benchmarks\tasks\aide_research_run.json --output results\evaluations\aide_context_baselines_v0.json`
  - `python scripts\evaluate_harness_transfer.py --task benchmarks\tasks\aide_harness_transfer.json --output results\evaluations\aide_harness_transfer_v0.json`
  - `python scripts\validate_source_spans.py --task benchmarks\tasks\aide_source_span_validation.json --output results\evaluations\aide_source_span_validation_v0.json`
  - `python scripts\build_live_transfer_prompts.py --task benchmarks\tasks\aide_live_transfer.json --output-dir results\live_transfer_prompts\aide_v0`
  - `python scripts\aggregate_results_tables.py --output-dir results\tables`
- Failure found and fixed:
  - Initial AIDE skill scored 18.05/20 because the extractor capped workflow at
    six method bullets and failure cases at five bullets, dropping source-backed
    `data preview` and LLM cost content.
  - Fixed by increasing extractor limits to 8 workflow, 7 validation, and 6
    failure bullets, with a regression test that keeps richer method bullets.
  - A second weak source-span claim was rewritten to match the paper's wording
    about tabular ML, neural architecture search, Triton Kernel optimization,
    and AI R&D tasks.
- Results:
  - AIDE skill rubric: 20/20.
  - AIDE context coverage: skill 9.1/10, generic summary 1.916/10,
    abstract-only 1.333/10.
  - AIDE transfer readiness: full skill 10/10, no-transfer-notes 7.6/10,
    generic summary 1.5/10.
  - AIDE source-span validation: 21 supported claims, 0 weak, 0 unsupported,
    0 invalid ranges, support rate 1.0.
  - Updated `results/tables/` now covers AI Scientist-v2, Reflexion, and AIDE.
- Evidence boundary: all AIDE results are deterministic/offline; no live
  cross-harness agent responses were collected.
- Retain as case: yes.
