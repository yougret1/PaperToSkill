# Stage Log

## 2026-06-17 Phase 0

Actions:

- Created long-term and short-term memory files.
- Created research contract, artifact map, decision log, idea cards,
  claim-evidence matrix, and experiment design.
- Created AI-Scientist-v2 workshop input and seed idea JSON.
- Inspected AI-Scientist-v2 README, launch script, BFTS config, LLM client, and
  OpenAI-compatible backend changes.
- Installed missing local Python dependencies needed for smoke tests.
- Tested the provided endpoint at `/v1/models` and direct chat completion.
- Ran AI-Scientist-v2 dry-run using
  `ai_scientist_inputs/papertoskill_seed_ideas.json`.
- Created first PaperToSkill skill prototype at `skill/SKILL.md`.

Findings:

- PaperToSkill repo is connected to `https://github.com/yougret1/PaperToSkill.git`.
- AI-Scientist-v2 already has local modifications that add
  OpenAI-compatible backend support and smaller local-laptop BFTS settings.
- `/v1/models` works and advertises `claude-opus-4-8`.
- Chat completion currently fails because the provider reports exhausted/no
  available accounts.
- Dry-run succeeded and created:
  `D:\a_work\gitee\ai-scientist-v2\experiments\2026-06-17_15-22-40_papertoskill_extractor_attempt_0`.
- The generated `idea.md` and `bfts_config.yaml` look structurally valid.
- Phase 0 artifacts are ready for validation and commit.

Risks:

- Global Python environment has dependency conflicts after installing the
  AI-Scientist-v2 requirements.
- Long AI-Scientist-v2 experiments should wait until the remote endpoint works
  and an isolated environment exists.

## 2026-06-17 Phase 1

Actions:

- Created a seed benchmark manifest with agent/LLM-method papers.
- Created a seed literature matrix, related-work gap map, and claim source map.
- Implemented `scripts/papertoskill_extract.py`, a deterministic local extractor
  that produces `SKILL.md` plus `references/source_map.json`.
- Added `tests/test_papertoskill_extract.py`.
- Added `examples/papertoskill_paper_note.md` as a paper-like retained case.
- Generated retained skills under `generated_skills/`.

Findings:

- The scaffold can progress without remote LLM availability.
- Method, experiment, and limitation sections can be mapped into workflow,
  validation, and failure-case sections.
- An abstract-only input falls back to a generic scaffold, which is useful but
  should not be treated as high-fidelity extraction.

Failure found and fixed:

- Initial extraction split multiline Markdown list items and inferred the title
  incorrectly as `Methods`.
- Fixed by merging continuation lines and inferring title from the first H1 or
  LaTeX title.

Verification:

- `python -m json.tool benchmarks\paper_manifest.json`
- `python -m unittest discover -s tests -v`
- `python scripts\papertoskill_extract.py --source examples\papertoskill_paper_note.md --output generated_skills\papertoskill_paper_note --name papertoskill-paper-note`
- `python scripts\papertoskill_extract.py --source ai_scientist_inputs\papertoskill.md --output generated_skills\papertoskill_seed --name papertoskill-seed --title "PaperToSkill Seed"`
