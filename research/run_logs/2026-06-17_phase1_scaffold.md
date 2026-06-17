# Run Log: 2026-06-17 Phase 1 Scaffold

## Objective

Create a non-LLM PaperToSkill extraction scaffold, seed benchmark manifest, and
retained generated example so the project can progress while the remote LLM
provider account pool is exhausted.

## Files Added

- `benchmarks/paper_manifest.json`
- `research/literature_matrix.md`
- `research/related_work_gap_map.md`
- `research/claim_source_map.md`
- `research/experiment_queue.md`
- `scripts/papertoskill_extract.py`
- `tests/test_papertoskill_extract.py`
- `examples/papertoskill_paper_note.md`
- `generated_skills/papertoskill_paper_note/SKILL.md`
- `generated_skills/papertoskill_paper_note/references/source_map.json`
- `generated_skills/papertoskill_seed/SKILL.md`
- `generated_skills/papertoskill_seed/references/source_map.json`

## Commands

```powershell
python -m json.tool benchmarks\paper_manifest.json
python -m unittest discover -s tests -v
python scripts\papertoskill_extract.py --source examples\papertoskill_paper_note.md --output generated_skills\papertoskill_paper_note --name papertoskill-paper-note
python scripts\papertoskill_extract.py --source ai_scientist_inputs\papertoskill.md --output generated_skills\papertoskill_seed --name papertoskill-seed --title "PaperToSkill Seed"
```

## Results

- `paper_manifest.json` is valid JSON.
- Unit tests passed: `Ran 1 test ... OK`.
- The paper-like note generated a skill with:
  - method-derived workflow steps;
  - experiment-derived validation checks;
  - limitation-derived failure cases;
  - `references/source_map.json`.
- The abstract-only seed generated a fallback skill, demonstrating the scaffold's
  behavior when method sections are absent.

## Failure Found And Fixed

Initial scaffold output split multiline numbered lists into broken fragments and
inferred the title as `Methods`. Fixes:

- merged continuation lines into the previous bullet or numbered item;
- inferred the document title from the first Markdown H1 or LaTeX `\title{...}`;
- added a unittest assertion that generated skills preserve the paper H1 title.

Retain this as an early failure-case example for the eventual paper.

