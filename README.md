# PaperToSkill

PaperToSkill is a research-to-skill system idea: given a paper, extract the
paper's transferable method, workflow, assumptions, evaluation pattern, and
failure cases into a concise Codex/agent skill that ordinary users can inspect,
edit, and reuse.

This repository is the local working memory and artifact hub for developing the
idea with `ai-scientist-v2`.

## Current Phase

Phase 0: research contract, memory discipline, and AI-Scientist-v2 integration
setup.

## Memory

- Long-term memory: `memory/long_term_memory.md`
- Short-term memory: `memory/short_term_memory.md`

After any context compaction or session resume, read both memory files before
continuing work.

## Research Artifacts

- `research/research_contract.md`
- `research/artifact_map.md`
- `research/decision_log.md`
- `research/literature_matrix.md`
- `research/related_work_gap_map.md`
- `research/claim_source_map.md`
- `research/idea_cards.md`
- `research/claim_evidence_matrix.md`
- `research/experiment_design.md`
- `research/experiment_queue.md`
- `research/runbook.md`
- `research/stage_log.md`
- `research/run_logs/`

## AI-Scientist-v2 Inputs

- `ai_scientist_inputs/papertoskill.md`
- `ai_scientist_inputs/papertoskill_seed_ideas.json`

## Skill Prototype

- `skill/SKILL.md`

## Phase 1 Scaffold

- Benchmark manifest: `benchmarks/paper_manifest.json`
- Extractor script: `scripts/papertoskill_extract.py`
- Smoke tests: `tests/test_papertoskill_extract.py`
- Retained generated case: `generated_skills/papertoskill_paper_note/SKILL.md`
