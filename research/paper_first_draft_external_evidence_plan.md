# Paper First Draft and External-Evidence Layout Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and verify an AAAI first-draft PDF that includes two final-size external-evidence tables with blank cells and two non-empirical companion figures.

**Architecture:** A deterministic Matplotlib script owns both conceptual figure assets. A dedicated LaTeX include owns the two placeholder tables so later evidence can replace `--` cells without editing the manuscript prose. Focused tests enforce row counts, status wording, and the absence of fabricated numeric results, while the existing AAAI package checker remains the unchanged authority on page-limit readiness.

**Tech Stack:** Python 3.12, `unittest`, Matplotlib 3.9, AAAI 2027 LaTeX, TeX Live 2024, pypdf, Poppler.

---

### Task 1: Lock the Figure and Table Contracts with Tests

**Files:**
- Create: `tests/test_make_paper_figures.py`
- Create: `tests/test_external_evidence_tables.py`

- [ ] **Step 1: Write the failing figure-generator tests**

Create `tests/test_make_paper_figures.py` with tests that run the script into a
temporary directory and assert the two PDF assets exist, begin with `%PDF`, and
contain no result-series API or numeric result payload:

```python
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "make_paper_figures.py"


class MakePaperFiguresTest(unittest.TestCase):
    def test_generates_two_pdf_figures(self):
        with tempfile.TemporaryDirectory() as tmp:
            env = os.environ.copy()
            env["MPLCONFIGDIR"] = str(Path(tmp) / "mplconfig")
            subprocess.run(
                [sys.executable, str(SCRIPT), "--output-dir", tmp],
                check=True,
                capture_output=True,
                text=True,
                env=env,
            )
            for name in ("papertoskill_pipeline.pdf", "external_evidence_design.pdf"):
                data = (Path(tmp) / name).read_bytes()
                self.assertTrue(data.startswith(b"%PDF"))
                self.assertGreater(len(data), 1_000)

    def test_script_contains_no_empirical_plot_series(self):
        text = SCRIPT.read_text(encoding="utf-8")
        for forbidden in ("ax.bar(", "ax.plot(", "ax.scatter(", "errorbar("):
            self.assertNotIn(forbidden, text)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Write the failing table-contract tests**

Create `tests/test_external_evidence_tables.py` to assert exact labels, row
counts, placeholder values, and status cells:

```python
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "paper" / "aaai" / "papertoskill_external_evidence_tables.tex"


def body_rows(text: str, label: str) -> list[str]:
    start = text.index(rf"\label{{{label}}}")
    tabular = text.index(r"\begin{tabular}", start)
    midrule = text.index(r"\midrule", tabular)
    bottomrule = text.index(r"\bottomrule", midrule)
    return [line.strip() for line in text[midrule:bottomrule].splitlines()[1:] if line.strip().endswith(r"\\")]


class ExternalEvidenceTablesTest(unittest.TestCase):
    def test_live_table_has_nine_final_rows(self):
        text = TABLES.read_text(encoding="utf-8")
        rows = body_rows(text, "tab:external-live-real-reuse")
        self.assertEqual(9, len(rows))
        self.assertTrue(all(row.count("--") == 4 for row in rows))
        self.assertTrue(all("Pending external evidence" in row for row in rows))

    def test_human_table_has_six_final_rows(self):
        text = TABLES.read_text(encoding="utf-8")
        rows = body_rows(text, "tab:external-independent-human")
        self.assertEqual(6, len(rows))
        self.assertTrue(all(row.count("--") == 5 for row in rows))
        self.assertTrue(all("Pending external evidence" in row for row in rows))

    def test_captions_do_not_claim_completion_or_planning(self):
        text = TABLES.read_text(encoding="utf-8")
        captions = " ".join(re.findall(r"\\caption\{([^}]*)\}", text))
        for forbidden in ("planned", "preregistered", "completed", "future"):
            self.assertNotIn(forbidden, captions.lower())


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 3: Run the focused tests and verify they fail**

Run:

```powershell
python -m unittest tests.test_make_paper_figures tests.test_external_evidence_tables -v
```

Expected: both modules fail because `scripts/make_paper_figures.py` and
`paper/aaai/papertoskill_external_evidence_tables.tex` do not exist.

### Task 2: Generate the Two Conceptual PDF Figures

**Files:**
- Create: `scripts/make_paper_figures.py`
- Create: `paper/aaai/figures/papertoskill_pipeline.pdf`
- Create: `paper/aaai/figures/external_evidence_design.pdf`

- [ ] **Step 1: Implement a deterministic figure generator**

Create `scripts/make_paper_figures.py` with these interfaces and fixed labels:

```python
#!/usr/bin/env python
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = ROOT / "paper" / "aaai" / "figures"
LOCAL_COLOR = "#2F6F62"
EXTERNAL_COLOR = "#B35C44"
INK = "#20262B"
PAPER = "#FFFFFF"
MUTED = "#E8ECEB"


def add_box(ax, x, y, width, height, text, color):
    patch = FancyBboxPatch(
        (x, y), width, height,
        boxstyle="round,pad=0.015,rounding_size=0.025",
        linewidth=1.2, edgecolor=color, facecolor=PAPER,
    )
    ax.add_patch(patch)
    ax.text(x + width / 2, y + height / 2, text, ha="center", va="center", fontsize=8, color=INK)


def add_arrow(ax, start, end):
    ax.add_patch(FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=11, linewidth=1.1, color=INK))


def save_pipeline(path: Path):
    fig, ax = plt.subplots(figsize=(7.0, 1.65))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    labels = [
        "Extracted paper\n+ source anchors",
        "Operational note\n+ failure boundaries",
        "Portable skill\n+ deterministic gates",
        "Live reuse\n+ independent review",
    ]
    xs = [0.02, 0.265, 0.51, 0.755]
    colors = [LOCAL_COLOR, LOCAL_COLOR, LOCAL_COLOR, EXTERNAL_COLOR]
    for x, label, color in zip(xs, labels, colors):
        add_box(ax, x, 0.34, 0.205, 0.34, label, color)
    for x in (0.225, 0.47, 0.715):
        add_arrow(ax, (x, 0.51), (x + 0.035, 0.51))
    ax.text(0.365, 0.12, "Validated local pipeline", ha="center", fontsize=7.5, color=LOCAL_COLOR)
    ax.text(0.86, 0.12, "External-evidence layer", ha="center", fontsize=7.5, color=EXTERNAL_COLOR)
    fig.savefig(path, bbox_inches="tight", pad_inches=0.03)
    plt.close(fig)


def save_external_design(path: Path):
    fig, ax = plt.subplots(figsize=(7.0, 2.15))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.text(0.02, 0.80, "Live real-reuse", fontsize=9, weight="bold", color=INK)
    for x, text in zip((0.18, 0.39, 0.60, 0.81), ("Model families", "Task slices", "Repeated seeds", "Paired outcomes")):
        add_box(ax, x, 0.67, 0.16, 0.22, text, EXTERNAL_COLOR)
    ax.text(0.02, 0.31, "Independent review", fontsize=9, weight="bold", color=INK)
    for x, text in zip((0.18, 0.39, 0.60, 0.81), ("Paper artifacts", "Independent raters", "Six criteria", "Scores + agreement")):
        add_box(ax, x, 0.18, 0.16, 0.22, text, EXTERNAL_COLOR)
    for y in (0.78, 0.29):
        for x in (0.34, 0.55, 0.76):
            add_arrow(ax, (x, y), (x + 0.045, y))
    fig.savefig(path, bbox_inches="tight", pad_inches=0.03)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    save_pipeline(args.output_dir / "papertoskill_pipeline.pdf")
    save_external_design(args.output_dir / "external_evidence_design.pdf")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run the figure tests**

Run:

```powershell
$env:MPLCONFIGDIR='output\mplconfig'
python -m unittest tests.test_make_paper_figures -v
```

Expected: 2 tests pass.

- [ ] **Step 3: Generate repository figure assets**

Run:

```powershell
$env:MPLCONFIGDIR='output\mplconfig'
python scripts\make_paper_figures.py
```

Expected: both PDF figure files exist under `paper/aaai/figures/`.

### Task 3: Add Final-Size External-Evidence Tables

**Files:**
- Create: `paper/aaai/papertoskill_external_evidence_tables.tex`

- [ ] **Step 1: Add the nine-row live table**

Use a two-column `table*` with label `tab:external-live-real-reuse`, the seven
approved columns, and exactly these model/task pairs: GPT-family, Claude-family,
and DeepSeek-family crossed with AIDE-T2, SWE-T2, and REF-T2. Use `--` in the
four measurement cells and `Pending external evidence` in every status cell.
Use the neutral caption `Cross-model live real-reuse evaluation.`

- [ ] **Step 2: Add the six-row human-study table**

Use a two-column `table*` with label `tab:external-independent-human`, the
seven approved columns, and the six criterion names from
`results/human_fidelity_packets/annotation_summary.md`. Use `--` in the five
measurement cells and `Pending external evidence` in every status cell. Use
the neutral caption `Expanded independent human evaluation.`

- [ ] **Step 3: Run the table-contract tests**

Run:

```powershell
python -m unittest tests.test_external_evidence_tables -v
```

Expected: 3 tests pass.

### Task 4: Integrate Figures and Tables into the AAAI Manuscript

**Files:**
- Modify: `paper/aaai/papertoskill_aaai2027.tex:4-12`
- Modify: `paper/aaai/papertoskill_aaai2027.tex:115-191`
- Modify: `paper/outline.md:263-289`
- Modify: `paper/aaai/README.md`

- [ ] **Step 1: Add stable figure lookup**

After `\usepackage{graphicx}`, add:

```tex
\graphicspath{{figures/}}
```

- [ ] **Step 2: Add Figure 1 after the Method section**

Insert a `figure*` containing `papertoskill_pipeline.pdf`, width
`0.96\textwidth`, label `fig:papertoskill-pipeline`, and a factual caption that
names the four stages without claiming external results.

- [ ] **Step 3: Add Figure 2 and the table include before Results**

Insert `external_evidence_design.pdf` as a `figure*` at `0.96\textwidth` with
label `fig:external-evidence-design`, followed by:

```tex
\input{papertoskill_external_evidence_tables}
```

Do not add manuscript prose that discusses, cites, or explains the empty
tables.

- [ ] **Step 4: Synchronize internal paper documentation**

Add Figure 1, Figure 2, and the two tables to `paper/outline.md`'s figure/table
plan. Add the new include, figure assets, and generator script to
`paper/aaai/README.md`. Do not add planning prose to `paper/draft.md`.

- [ ] **Step 5: Run focused manuscript checks**

Run:

```powershell
python -m unittest tests.test_make_paper_figures tests.test_external_evidence_tables -v
python scripts\check_paper_claims.py --strict
python scripts\check_paper_tables.py --strict
```

Expected: focused tests pass; existing claim and generated-result table checks
remain ready because unavailable values are isolated in the dedicated include.

### Task 5: Compile, Render, and Audit the First Draft

**Files:**
- Update build artifacts: `paper/aaai/papertoskill_aaai2027.pdf`
- Update build artifacts: `paper/aaai/papertoskill_aaai2027.log`
- Update build artifacts: `paper/aaai/papertoskill_aaai2027.bbl`
- Create temporary renders under: `output/pdf/papertoskill-first-draft/`

- [ ] **Step 1: Compile with the existing TeX Live installation**

Run from `paper/aaai` using
`D:\texlive\texlive\2024\bin\windows\pdflatex.exe` and the matching
`bibtex.exe`:

```powershell
& 'D:\texlive\texlive\2024\bin\windows\pdflatex.exe' -interaction=nonstopmode -halt-on-error papertoskill_aaai2027.tex
& 'D:\texlive\texlive\2024\bin\windows\bibtex.exe' papertoskill_aaai2027
& 'D:\texlive\texlive\2024\bin\windows\pdflatex.exe' -interaction=nonstopmode -halt-on-error papertoskill_aaai2027.tex
& 'D:\texlive\texlive\2024\bin\windows\pdflatex.exe' -interaction=nonstopmode -halt-on-error papertoskill_aaai2027.tex
```

Expected: all commands exit 0 with no unresolved citation or reference warning.

- [ ] **Step 2: Record the new page count**

Run:

```powershell
& 'C:\Users\Z\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -c "from pypdf import PdfReader; print(len(PdfReader(r'paper\aaai\papertoskill_aaai2027.pdf').pages))"
```

Compare against the baseline of 8 pages and report the increase.

- [ ] **Step 3: Render every page to PNG**

Run:

```powershell
New-Item -ItemType Directory -Path 'output\pdf\papertoskill-first-draft' -Force
& 'C:\Users\Z\.cache\codex-runtimes\codex-primary-runtime\dependencies\bin\override\pdftoppm.cmd' -png -r 150 'paper\aaai\papertoskill_aaai2027.pdf' 'output\pdf\papertoskill-first-draft\page'
```

Expected: one PNG per PDF page.

- [ ] **Step 4: Inspect figure/table pages visually**

Inspect all rendered pages, with particular attention to the pages containing
`Pipeline and Evidence Boundary`, `Cross-model live real-reuse evaluation`,
and `Expanded independent human evaluation`. Reject clipped labels, overlap,
unreadable status cells, black boxes, and float-order inversions.

- [ ] **Step 5: Run strict checks**

Run:

```powershell
python -m unittest tests.test_make_paper_figures tests.test_external_evidence_tables -v
python scripts\check_paper_tables.py --strict
python scripts\check_paper_claims.py --strict
python scripts\check_submission_review.py --strict
python scripts\check_aaai_package.py --strict
git diff --check
rg -n "(sk-[A-Za-z0-9]{20,}|Bearer\s+[A-Za-z0-9._-]{20,}|AKIA[0-9A-Z]{16}|AIza[0-9A-Za-z_-]{20,})" .
```

Expected: focused tests, table checks, claim checks, submission review, diff
check, and key scan pass. The current PDF baseline is eight pages. If the new
final-size floats push non-reference content beyond the AAAI limit,
`check_aaai_package.py --strict` and the existing package-readiness unit test
must fail explicitly; the final report must state the measured overflow rather
than weakening the checker or its test.

- [ ] **Step 6: Review the final diff**

Confirm that only the approved paper, figure, checker, test, and internal
documentation files changed. Do not modify `research/run_logs/**` or
`research/stage_log.md`.
