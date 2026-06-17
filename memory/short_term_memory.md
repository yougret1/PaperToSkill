# PaperToSkill Short-Term Memory

Read this file after any context compaction or session resume, then update it as
the active task state changes.

## Current Date

2026-06-17.

## Active Phase

Phase 7 second-paper benchmark case is implemented locally. Current focus:
finalize records, run verification, commit, and push.

## Latest User Request

The user provided the PaperToSkill idea and asked to:

- create local memory with at least long-term and short-term files;
- use `ai-scientist-v2` to refine and develop the idea;
- use `https://github.com/yougret1/PaperToSkill.git` for phase-level saving;
- use the provided OpenAI-compatible LLM endpoint/model if third-party LLM calls
  are needed;
- report promptly if the request/API has problems.

## Immediate Findings

- `D:\a_work\gitee\PaperToSkill` already exists and has remote
  `origin=https://github.com/yougret1/PaperToSkill.git`.
- PaperToSkill repo was clean before Phase 0 file creation.
- `D:\a_work\gitee\ai-scientist-v2` has pre-existing local modifications in:
  - `ai_scientist/llm.py`
  - `ai_scientist/treesearch/backend/__init__.py`
  - `ai_scientist/treesearch/backend/backend_openai.py`
  - `ai_scientist/treesearch/parallel_agent.py`
  - `bfts_config.yaml`
  - `launch_scientist_bfts.py`
  - `requirements.txt`
- Those `ai-scientist-v2` changes should be treated as existing user/local
  state. Do not revert them.
- The local `ai-scientist-v2` changes already add an OpenAI-compatible backend
  path via `AI_SCIENTIST_OPENAI_BASE_URL` and
  `AI_SCIENTIST_OPENAI_API_KEY`.
- First LLM connectivity test failed before reaching the remote API because the
  current Python environment lacked `tiktoken`.
- Minimal dependencies were installed into the active Anaconda Python:
  `anthropic`, `tiktoken`, `backoff`, then `requirements.txt`.
- `pip install -r requirements.txt` completed, but produced dependency conflict
  warnings:
  - `aiobotocore 2.12.3` expects `botocore <1.34.70`, but `botocore 1.43.31`
    was installed.
  - `streamlit 1.37.1` expects `rich <14`, but `rich 15.0.0` is installed.
- `https://coderxiaoc.com/v1/models` is reachable and returns model IDs.
- The server lists `claude-opus-4-8`; it does not list the dotted user-facing
  spelling `claude-opus-4.8`.
- Direct chat completion tests reached the server but failed because the
  provider has no available accounts:
  - `claude-opus-4-8`: HTTP 502, `All available accounts exhausted`.
  - `claude-opus-4.8`: HTTP 503, `No available accounts: no available accounts`.
- AI-Scientist-v2 dry-run succeeded with PaperToSkill seed idea:
  `D:\a_work\gitee\ai-scientist-v2\experiments\2026-06-17_15-22-40_papertoskill_extractor_attempt_0`.
- The generated run config uses `claude-opus-4-8`, `num_workers=1`, and small
  stage iteration counts, which is suitable for a later smoke run.
- Phase 1 added a seed benchmark manifest at `benchmarks/paper_manifest.json`.
- Phase 1 added a deterministic local extractor at
  `scripts/papertoskill_extract.py`.
- Phase 1 added smoke tests at `tests/test_papertoskill_extract.py`.
- Phase 1 generated retained example skills under `generated_skills/`.
- A parsing failure was found and fixed: multiline list items were initially
  split into fragments and the document title was inferred as `Methods`.
- Phase 2 ingested the real AI Scientist-v2 paper:
  - PDF: `papers/raw/ai_scientist_v2.pdf`
  - Extracted text: `papers/extracted/ai_scientist_v2.txt`
  - Curated note: `papers/notes/ai_scientist_v2_note.md`
  - Generated skill: `generated_skills/ai_scientist_v2/SKILL.md`
  - Rubric output: `results/evaluations/ai_scientist_v2_rubric_v0.json`
- Rubric v0 scored the AI Scientist-v2 generated skill at 20/20, but this only
  covers structure, anchors, keyword coverage, failure coverage, and compactness.
- Phase 3 added a deterministic context baseline task:
  `benchmarks/tasks/ai_scientist_v2_research_run.json`.
- Phase 3 compared generated skill vs generic summary vs abstract-only context:
  - skill: 7.867/9
  - generic summary: 1.733/9
  - abstract-only: 1.2/9
- The Phase 3 result supports only coverage/fidelity, not actual LLM downstream
  task success.
- Phase 4 added a source-map-aware unsupported-instruction audit task:
  `benchmarks/tasks/skill_source_audit.json`.
- Phase 4 audit ranked unsupported rates:
  - AI Scientist-v2 real skill: 0.2
  - Paper-like retained case: 0.222
  - Abstract-only seed: 1.0
- The first audit pass had a section-mapping bug that was fixed before the final
  result.
- Phase 4 was committed and pushed as `7cfd582` on `origin/main`.
- Phase 5 added offline harness-transfer readiness evaluation:
  `benchmarks/tasks/ai_scientist_v2_harness_transfer.json`.
- Phase 5 compared full generated skill, skill without `Transfer Notes`, and
  generic summary across Codex-style and Claude-style harness targets:
  - full skill: 10.0/10 average readiness
  - no-transfer-notes variant: 7.6/10 average readiness
  - generic summary: 1.2/10 average readiness
- Phase 5 result supports only offline artifact readiness, not live
  cross-harness agent success.
- Phase 5 was committed and pushed as `9a393a7` on `origin/main`.
- Phase 6 added live transfer prompt packets and source-span validation:
  - `benchmarks/tasks/ai_scientist_v2_live_transfer.json`
  - `benchmarks/tasks/ai_scientist_v2_source_span_validation.json`
- Phase 6 live prompt packets were generated under
  `results/live_transfer_prompts/ai_scientist_v2_v0/`.
- Phase 6 source-span validation after fixing line-count semantics produced:
  - 15 supported claims
  - 1 weak claim
  - 0 invalid ranges
  - support rate `0.938`
- The remote chat endpoint still returns `502 All available accounts exhausted`.
- Phase 6 was committed and pushed as `b72381c` on `origin/main`.
- Phase 7 added Reflexion as the second real paper case:
  - `papers/raw/reflexion.pdf`
  - `papers/extracted/reflexion.txt`
  - `papers/notes/reflexion_note.md`
  - `generated_skills/reflexion/SKILL.md`
  - `benchmarks/rubric_reflexion_v0.json`
  - `benchmarks/tasks/reflexion_source_span_validation.json`
- Reflexion generated skill scored `20/20` on the paper-specific rubric.
- Reflexion source-span validation produced 11 supported claims, 0 invalid
  ranges, support rate `1.0`.

## Current Blockers / Pending Checks

- Remote LLM chat completion is currently blocked by the provider account pool,
  not by the local code path.
- For AI-Scientist-v2, use base URL `https://coderxiaoc.com/v1`.
- Prefer model string `claude-opus-4-8` in local configs because that is what the
  server advertises.
- For stable long-running work, create an isolated Python environment because
  the current global Anaconda environment now has package-version conflicts.
- Need improve evaluator further toward human or source-span validation.
- Need run actual LLM task execution once the remote endpoint works or another
  model backend is available.

## Next Actions

1. Commit and push Phase 7 artifacts.
2. Add Reflexion context-vs-summary and transfer-readiness tasks.
3. Re-test the remote LLM endpoint when provider accounts are available.
4. Execute live cross-harness runs using the prompt packets when the endpoint
   recovers.
5. Expand the benchmark to more agent/LLM-method papers.
