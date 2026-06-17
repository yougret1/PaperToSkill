# PaperToSkill

PaperToSkill is a research-to-skill system idea: given a paper, extract the
paper's transferable method, workflow, assumptions, evaluation pattern, and
failure cases into a concise Codex/agent skill that ordinary users can inspect,
edit, and reuse.

This repository is the local working memory and artifact hub for developing the
idea with `ai-scientist-v2`.

## Current Phase

Phase 11: paper draft package over a three-paper deterministic/offline
benchmark. Live cross-harness agent execution is still pending because the
remote chat-completion endpoint has returned provider availability errors.

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

## Paper Draft Package

- `paper/outline.md`
- `paper/draft.md`
- `paper/claim_checklist.md`
- `paper/limitations.md`

These files intentionally separate supported deterministic/offline claims from
pending live-agent claims.

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

## Current Benchmark Snapshot

- Real-paper cases: AI Scientist-v2, Reflexion, and AIDE.
- Main result tables: `results/tables/`.
- Generated skills: `generated_skills/ai_scientist_v2/`,
  `generated_skills/reflexion/`, and `generated_skills/aide/`.
- Live transfer prompt packets: `results/live_transfer_prompts/`.
