# PaperToSkill AAAI-27 Overleaf Package

This directory uses the Overleaf project structure from
`paper/Paper2Skill_AAAI2027.zip` while preserving the current PaperToSkill
manuscript, tables, references, and conceptual figures.

## Primary Overleaf Entry

- `main.tex`: canonical Overleaf entry point.
- `src/abstract.tex`: abstract.
- `src/introduction.tex`: introduction.
- `src/related.tex`: related work.
- `src/method.tex`: method and experimental setup.
- `src/result.tex`: results, discussion, and limitations.
- `src/conclusion.tex`: conclusion.
- `src/references.bib`: bibliography used by `main.tex`.
- `images/`: PaperToSkill conceptual figures only.

The unrelated semantic-typography text and image assets from the downloaded
project are intentionally excluded.

## Compatibility Entry

`papertoskill_aaai2027.tex` is the flat compatibility entry used by existing
repository checkers. It contains the same paper revision as the modular
Overleaf entry. The root-level table and bibliography fragments are retained
for this compatibility build.

## Build

From this directory, build the Overleaf entry with:

```powershell
pdflatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

The compatibility entry uses the same sequence with
`papertoskill_aaai2027` as the job name.

The package uses the AAAI-27 submission style. The current internal draft
contains two external-evidence tables with literal `--` values and
`Pending external evidence` statuses; it is not submission-ready until the
external evidence and page-limit gate are closed.
