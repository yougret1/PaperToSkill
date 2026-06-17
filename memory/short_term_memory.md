# PaperToSkill Short-Term Memory

Read this file after any context compaction or session resume, then update it as
the active task state changes.

## Current Date

2026-06-17.

## Active Phase

Phase 0 is implemented locally. Current focus: validate and commit Phase 0
artifacts, then move to Phase 1 benchmark and extractor implementation.

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

## Current Blockers / Pending Checks

- Remote LLM chat completion is currently blocked by the provider account pool,
  not by the local code path.
- For AI-Scientist-v2, use base URL `https://coderxiaoc.com/v1`.
- Prefer model string `claude-opus-4-8` in local configs because that is what the
  server advertises.
- For stable long-running work, create an isolated Python environment because
  the current global Anaconda environment now has package-version conflicts.

## Next Actions

1. Validate `skill/SKILL.md`.
2. Commit Phase 0 artifacts in PaperToSkill.
3. Push to `origin/main` if credentials allow.
4. Start Phase 1: build the first paper benchmark manifest and a deterministic
   PaperToSkill extraction scaffold.
5. Re-test the remote LLM endpoint when provider accounts are available.
