# Run Log: 2026-06-17 Phase 2 Real Paper

## Objective

Ingest one real benchmark paper, convert it to a source-anchored paper note,
generate a paper-derived skill, and score the generated skill with the first
deterministic rubric.

## Paper

- ID: `ai_scientist_v2`
- PDF URL: `https://arxiv.org/pdf/2504.08066`
- Raw PDF: `papers/raw/ai_scientist_v2.pdf`
- Extracted text: `papers/extracted/ai_scientist_v2.txt`
- Curated note: `papers/notes/ai_scientist_v2_note.md`

## Commands

```powershell
Invoke-WebRequest -Uri 'https://arxiv.org/pdf/2504.08066' -OutFile 'papers\raw\ai_scientist_v2.pdf'
pdfinfo papers\raw\ai_scientist_v2.pdf
pdftotext -layout papers\raw\ai_scientist_v2.pdf papers\extracted\ai_scientist_v2.txt
pdftoppm -f 1 -l 1 -png -r 120 papers\raw\ai_scientist_v2.pdf output\pdf\ai_scientist_v2\page
python scripts\papertoskill_extract.py --source papers\notes\ai_scientist_v2_note.md --output generated_skills\ai_scientist_v2 --name ai-scientist-v2-paper-skill
python scripts\evaluate_skill.py --skill generated_skills\ai_scientist_v2\SKILL.md --rubric benchmarks\rubric_v0.json --output results\evaluations\ai_scientist_v2_rubric_v0.json
python -m unittest discover -s tests -v
```

## Results

- PDF downloaded successfully: 8,923,691 bytes.
- `pdfinfo`: 69 pages, A4, not encrypted.
- `pdftotext -layout`: extracted 253,537-byte text file.
- `pdftoppm`: rendered page 1 successfully; Poppler reported `No display font
  for 'ArialUnicode'`, but the page image was readable on visual inspection.
- Generated `generated_skills/ai_scientist_v2/SKILL.md`.
- Generated `generated_skills/ai_scientist_v2/references/source_map.json`.
- Rubric v0 score: 20/20.
- Unit tests passed: `Ran 2 tests ... OK`.

## Evidence Boundary

The v0 rubric proves only deterministic structural coverage, source anchors,
keyword coverage, failure keyword coverage, and compactness. It does not prove
that the skill improves an agent's downstream task performance compared with
summaries or full paper excerpts.

