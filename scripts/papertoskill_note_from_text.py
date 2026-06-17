#!/usr/bin/env python
"""Create a source-anchored PaperToSkill note from extracted paper text.

This is a deterministic scaffold, not a semantic paper reader. It selects
high-signal line windows from `pdftotext` output and emits a Markdown note that
can be audited, edited, and passed to `papertoskill_extract.py`.
"""

from __future__ import annotations

import argparse
import json
import re
import textwrap
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class LineEntry:
    number: int
    raw: str
    text: str


@dataclass(frozen=True)
class SectionRange:
    start: int
    end: int


@dataclass(frozen=True)
class CandidateSpec:
    prefix: str
    keywords: tuple[str, ...]
    group: str
    prefer_later: bool = False


@dataclass(frozen=True)
class Candidate:
    prefix: str
    snippet: str
    start: int
    end: int
    score: int


METHOD_SPECS = [
    CandidateSpec(
        "Represent the text-to-text API-call contract with tool name, input, result, and delimiter",
        ("api call", "input", "output", "text sequence", "special token"),
        "method",
    ),
    CandidateSpec(
        "Use few demonstrations or prompts to propose candidate actions",
        ("demonstrations", "prompt", "sample", "candidate", "api call"),
        "method",
    ),
    CandidateSpec(
        "Execute proposed calls or actions with the required backend",
        ("execute", "api calls", "response", "python", "retrieval"),
        "method",
    ),
    CandidateSpec(
        "Filter candidates by future-token loss or another source-defined utility threshold",
        ("filter", "loss", "future tokens", "threshold", "reduces"),
        "method",
    ),
    CandidateSpec(
        "Interleave retained calls to build the augmented dataset while preserving the original text",
        ("augmented", "interleave", "original", "dataset", "finetune"),
        "method",
    ),
    CandidateSpec(
        "Fine-tune or train on retained source-backed examples",
        ("finetune", "training", "language modeling", "objective", "dataset"),
        "method",
    ),
    CandidateSpec(
        "At inference time, interrupt generation, insert the response, and continue",
        ("inference", "interrupt", "response", "continue", "decoding"),
        "method",
    ),
    CandidateSpec(
        "Record the tool set, constraints, and required demonstrations",
        ("tools", "question answering", "calculator", "wikipedia", "calendar", "machine translation"),
        "method",
    ),
]

EXPERIMENT_SPECS = [
    CandidateSpec(
        "Evaluate whether the system works without further supervision in zero-shot settings",
        ("zero-shot", "without", "supervision", "downstream", "tasks"),
        "experiment",
    ),
    CandidateSpec(
        "Compare against same-size and larger baselines",
        ("baseline", "gpt-j", "gpt-3", "opt", "larger"),
        "experiment",
    ),
    CandidateSpec(
        "Track benchmark domains such as LAMA, mathematical reasoning, question answering, and temporal datasets",
        ("lama", "math", "question answering", "temporal", "datasets"),
        "experiment",
    ),
    CandidateSpec(
        "Check whether the added mechanism preserves core language-modeling quality",
        ("perplexity", "language modeling", "without any", "api calls"),
        "experiment",
    ),
    CandidateSpec(
        "Run scale or sensitivity analysis when the paper reports model-size effects",
        ("model size", "scaling", "parameters", "smaller", "larger"),
        "experiment",
    ),
]

LIMITATION_SPECS = [
    CandidateSpec(
        "Avoid claiming that the method removes the need for large human annotations or task-specific setup",
        ("large amounts of human", "human annotations", "task-specific", "settings"),
        "limitation",
    ),
    CandidateSpec(
        "Check whether external backend execution is required before transfer",
        ("depends entirely", "api itself", "python", "retrieval", "external"),
        "limitation",
    ),
    CandidateSpec(
        "Treat heuristics and sample efficiency as explicit costs",
        ("heuristics", "computational cost", "sample-inefficient", "few thousand"),
        "limitation",
    ),
    CandidateSpec(
        "Do not overstate question-answering performance when Atlas or search limitations remain",
        ("atlas", "lags behind", "search", "query", "top results"),
        "limitation",
    ),
    CandidateSpec(
        "Audit calendar API or temporal gains before attributing all improvement to the tool",
        ("calendar api", "cannot be attributed", "0.2", "calendar tool"),
        "limitation",
    ),
    CandidateSpec(
        "Do not claim perplexity with live tool calls when the paper says it is not evaluated",
        ("do not evaluate", "perplexity", "marginalizing", "api calls"),
        "limitation",
        True,
    ),
    CandidateSpec(
        "Treat model scale or model size as a condition for the method to emerge",
        ("model size", "model scale", "smaller models", "parameters", "larger models"),
        "limitation",
        True,
    ),
]

HEADING_PATTERNS = {
    "abstract": (r"\bAbstract\b",),
    "introduction": (r"\b1\s+Introduction\b", r"\bIntroduction\b"),
    "method": (r"\b2\s+Approach\b", r"\bMethods?\b", r"\bApproach\b"),
    "tools": (r"\b3\s+Tools\b", r"\bTools\b"),
    "experiment": (r"\b4\s+Experiments\b", r"\bExperiments\b", r"\bEvaluation\b"),
    "analysis": (r"\b5\s+Analysis\b", r"\bAnalysis\b"),
    "related": (r"\b6\s+Related Work\b", r"\bRelated Work\b"),
    "limitation": (r"\b7\s+Limitations\b", r"\bLimitations\b"),
    "conclusion": (r"\b8\s+Conclusion\b", r"\bConclusion\b"),
    "references": (r"\bReferences\b",),
}


def clean_text(value: str) -> str:
    value = value.replace("\f", " ")
    value = value.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"\s+", " ", value).strip()


def normalize_keyword(value: str) -> str:
    return clean_text(value).lower()


def line_entries(text: str) -> list[LineEntry]:
    return [
        LineEntry(number=idx, raw=line.rstrip("\r"), text=clean_text(line))
        for idx, line in enumerate(text.split("\n"), start=1)
    ]


def nonempty_lines(entries: list[LineEntry]) -> list[LineEntry]:
    return [entry for entry in entries if entry.text]


def find_line(entries: list[LineEntry], patterns: tuple[str, ...], start: int = 1) -> int | None:
    for entry in entries:
        if entry.number < start:
            continue
        for pattern in patterns:
            if re.search(pattern, entry.text):
                return entry.number
    return None


def infer_title(entries: list[LineEntry], source: Path, explicit_title: str | None) -> str:
    if explicit_title:
        return explicit_title
    for entry in nonempty_lines(entries)[:8]:
        lowered = entry.text.lower()
        if lowered.startswith("arxiv:") or lowered == "abstract":
            continue
        if 8 <= len(entry.text) <= 140 and re.search(r"[A-Za-z]", entry.text):
            return entry.text
    return source.stem.replace("_", " ").replace("-", " ").title()


def section_ranges(entries: list[LineEntry]) -> dict[str, SectionRange]:
    max_line = entries[-1].number if entries else 1
    found = {name: find_line(entries, patterns) for name, patterns in HEADING_PATTERNS.items()}

    intro = found.get("introduction") or found.get("abstract") or 1
    method = found.get("method") or intro
    tools = found.get("tools")
    experiment = found.get("experiment") or max_line
    analysis = found.get("analysis")
    related = found.get("related")
    limitation = found.get("limitation")
    conclusion = found.get("conclusion")

    method_end = max((experiment or max_line) - 1, method)
    if tools and experiment:
        method_end = max(method_end, experiment - 1)

    experiment_end_candidates = [line for line in (related, limitation, conclusion) if line and line > experiment]
    experiment_end = min(experiment_end_candidates) - 1 if experiment_end_candidates else max_line

    limitation_start = limitation or related or analysis or experiment
    limitation_end = (conclusion - 1) if conclusion and conclusion > limitation_start else max_line

    abstract_start = found.get("abstract") or 1
    abstract_end = (intro - 1) if intro and intro > abstract_start else min(max_line, abstract_start + 25)

    return {
        "abstract": SectionRange(abstract_start, max(abstract_start, abstract_end)),
        "method": SectionRange(method, min(max_line, method_end)),
        "experiment": SectionRange(experiment, min(max_line, experiment_end)),
        "limitation": SectionRange(limitation_start, min(max_line, limitation_end)),
        "all": SectionRange(1, max_line),
    }


def entries_in_range(entries: list[LineEntry], section: SectionRange) -> list[LineEntry]:
    return [entry for entry in entries if section.start <= entry.number <= section.end]


def split_columns(raw_line: str) -> list[str]:
    pieces = [clean_text(piece) for piece in re.split(r"\s{4,}", raw_line.strip())]
    return [piece for piece in pieces if piece]


def window_entries(entries: list[LineEntry], start: int, end: int) -> list[LineEntry]:
    return [entry for entry in entries if start <= entry.number <= end]


def window_text(entries: list[LineEntry], start: int, end: int) -> str:
    return clean_text(" ".join(entry.text for entry in window_entries(entries, start, end)))


def relevant_window_text(entries: list[LineEntry], start: int, end: int, keywords: tuple[str, ...]) -> str:
    rows = [split_columns(entry.raw) for entry in window_entries(entries, start, end)]
    max_columns = max((len(row) for row in rows), default=0)
    if max_columns <= 1:
        return window_text(entries, start, end)

    column_scores = []
    for column_idx in range(max_columns):
        text = clean_text(" ".join(row[column_idx] for row in rows if column_idx < len(row)))
        column_scores.append((score_window(text, keywords), len(text), column_idx))
    best_score, _length, best_column = max(column_scores)
    if best_score <= 0:
        return window_text(entries, start, end)
    return clean_text(" ".join(row[best_column] for row in rows if best_column < len(row)))


def score_window(text: str, keywords: tuple[str, ...]) -> int:
    lowered = normalize_keyword(text)
    score = sum(1 for keyword in keywords if normalize_keyword(keyword) in lowered)
    if "do not evaluate" in lowered:
        score += 2
    return score


def overlaps_used(start: int, end: int, used: list[tuple[int, int]]) -> bool:
    return any(start <= used_end and end >= used_start for used_start, used_end in used)


def trim_snippet(text: str, keywords: tuple[str, ...], max_chars: int = 210) -> str:
    text = clean_text(text)
    if len(text) <= max_chars:
        return text
    lowered = text.lower()
    positions = [lowered.find(normalize_keyword(keyword)) for keyword in keywords]
    positions = [position for position in positions if position >= 0]
    center = min(positions) if positions else 0
    start = max(0, center - max_chars // 4)
    end = min(len(text), start + max_chars)
    start = text.find(" ", start)
    if start < 0 or start > center:
        start = max(0, center - max_chars // 4)
    end_space = text.rfind(" ", start, end)
    if end_space > start + 80:
        end = end_space
    snippet = text[start:end].strip(" ,;:-")
    if start > 0:
        snippet = "... " + snippet
    if end < len(text):
        snippet += " ..."
    return snippet


def select_candidates(
    entries: list[LineEntry],
    ranges: dict[str, SectionRange],
    specs: list[CandidateSpec],
    *,
    limit: int,
    radius: int = 2,
) -> list[Candidate]:
    selected: list[Candidate] = []
    used: list[tuple[int, int]] = []
    max_line = entries[-1].number if entries else 1

    for spec in specs:
        search_ranges = [ranges.get(spec.group), ranges.get("all")]
        best: Candidate | None = None
        for section in [item for item in search_ranges if item is not None]:
            for entry in entries_in_range(entries, section):
                if not entry.text:
                    continue
                start = max(1, entry.number - radius)
                end = min(max_line, entry.number + radius)
                if overlaps_used(start, end, used):
                    continue
                text = relevant_window_text(entries, start, end, spec.keywords)
                score = score_window(text, spec.keywords)
                if score <= 0:
                    continue
                candidate = Candidate(
                    prefix=spec.prefix,
                    snippet=trim_snippet(text, spec.keywords),
                    start=start,
                    end=end,
                    score=score,
                )
                if best is None:
                    best = candidate
                elif spec.prefer_later:
                    if (candidate.score, candidate.start) > (best.score, best.start):
                        best = candidate
                elif (candidate.score, -candidate.start) > (best.score, -best.start):
                    best = candidate
        if best is not None:
            selected.append(best)
            used.append((best.start, best.end))
        if len(selected) >= limit:
            break
    return selected


def fallback_candidates(entries: list[LineEntry], section: SectionRange, *, limit: int) -> list[Candidate]:
    candidates = []
    chunk: list[LineEntry] = []

    def flush() -> None:
        nonlocal chunk
        if not chunk:
            return
        text = clean_text(" ".join(entry.text for entry in chunk))
        if len(text) >= 60:
            candidates.append(
                Candidate(
                    prefix="Inspect this source window before converting it into a skill step",
                    snippet=trim_snippet(text, ()),
                    start=chunk[0].number,
                    end=chunk[-1].number,
                    score=1,
                )
            )
        chunk = []

    for entry in entries_in_range(entries, section):
        if not entry.text:
            flush()
            continue
        chunk.append(entry)
        if len(chunk) >= 4:
            flush()
        if len(candidates) >= limit:
            break
    flush()
    return candidates[:limit]


def candidates_for_group(entries: list[LineEntry], ranges: dict[str, SectionRange], group: str) -> list[Candidate]:
    if group == "method":
        candidates = select_candidates(entries, ranges, METHOD_SPECS, limit=8)
        return candidates or fallback_candidates(entries, ranges["method"], limit=4)
    if group == "experiment":
        candidates = select_candidates(entries, ranges, EXPERIMENT_SPECS, limit=7)
        return candidates or fallback_candidates(entries, ranges["experiment"], limit=3)
    if group == "limitation":
        candidates = select_candidates(entries, ranges, LIMITATION_SPECS, limit=7)
        return candidates or fallback_candidates(entries, ranges["limitation"], limit=3)
    raise ValueError(f"Unknown candidate group: {group}")


def abstract_snippet(entries: list[LineEntry], ranges: dict[str, SectionRange]) -> tuple[str, int, int]:
    section = ranges["abstract"]
    text = relevant_window_text(entries, section.start, section.end, ("we introduce", "we propose", "this paper", "we show"))
    if not text:
        nonempty = nonempty_lines(entries)[:8]
        if not nonempty:
            return "", 1, 1
        text = clean_text(" ".join(entry.text for entry in nonempty))
        return trim_snippet(text, ("we introduce", "we propose", "this paper"), max_chars=360), nonempty[0].number, nonempty[-1].number
    return trim_snippet(text, ("we introduce", "we propose", "this paper", "we show"), max_chars=300), section.start, section.end


def wrap_markdown_bullet(prefix: str, text: str, start: int, end: int, *, ordered: bool, index: int | None = None) -> str:
    marker = f"{index}. " if ordered else "- "
    body = f"{prefix}: {text}. Source anchors: lines {start}-{end}."
    wrapped = textwrap.fill(
        body,
        width=88,
        initial_indent=marker,
        subsequent_indent=" " * len(marker),
        break_on_hyphens=False,
    )
    return wrapped


def candidate_list(candidates: list[Candidate], *, ordered: bool) -> str:
    lines = []
    for idx, candidate in enumerate(candidates, start=1):
        lines.append(
            wrap_markdown_bullet(
                candidate.prefix,
                candidate.snippet,
                candidate.start,
                candidate.end,
                ordered=ordered,
                index=idx if ordered else None,
            )
        )
    return "\n".join(lines)


def build_note(source: Path, paper_id: str, title: str, entries: list[LineEntry]) -> tuple[str, dict]:
    ranges = section_ranges(entries)
    abstract, abstract_start, abstract_end = abstract_snippet(entries, ranges)
    methods = candidates_for_group(entries, ranges, "method")
    experiments = candidates_for_group(entries, ranges, "experiment")
    limitations = candidates_for_group(entries, ranges, "limitation")

    note = f"""# {title}

## Source

- Paper ID: `{paper_id}`
- Extracted text: `{source.as_posix()}`
- Extraction notes: Automatic deterministic scaffold from extracted text. It
  should be audited against the paper before being treated as validated paper
  knowledge.

## Abstract

{abstract}

Source anchors: lines {abstract_start}-{abstract_end}.

## Methods

{candidate_list(methods, ordered=True)}

## Experiments

{candidate_list(experiments, ordered=False)}

## Limitations

{candidate_list(limitations, ordered=False)}

## Transfer Notes

- Treat this file as an audit scaffold, not a final skill.
- Keep each generated skill instruction tied to source anchors or mark it as an
  inference.
- Save the JSON selection report or generated skill source map with the skill so
  later audits can trace each line range.
- Re-run source-span validation after converting this note into `SKILL.md`.
- Compare the resulting skill against any curated note before using it in a
  live agent workflow.
"""
    report = {
        "source": str(source),
        "paper_id": paper_id,
        "title": title,
        "line_count": entries[-1].number if entries else 0,
        "ranges": {name: {"start": value.start, "end": value.end} for name, value in ranges.items()},
        "selected": {
            "abstract": {"start": abstract_start, "end": abstract_end},
            "methods": [candidate.__dict__ for candidate in methods],
            "experiments": [candidate.__dict__ for candidate in experiments],
            "limitations": [candidate.__dict__ for candidate in limitations],
        },
        "evidence_boundary": (
            "Deterministic line-window scaffold. It identifies auditable source spans but does not prove "
            "semantic completeness or human fidelity."
        ),
    }
    return note, report


def write_outputs(source: Path, output: Path, paper_id: str | None, title: str | None, report_path: Path | None) -> dict:
    text = source.read_text(encoding="utf-8", errors="replace")
    entries = line_entries(text)
    inferred_paper_id = paper_id or source.stem
    inferred_title = infer_title(entries, source, title)
    note, report = build_note(source, inferred_paper_id, inferred_title, entries)

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(note, encoding="utf-8")
    if report_path:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return report | {"output": str(output)}


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a source-anchored PaperToSkill note from extracted text.")
    parser.add_argument("--source", required=True, type=Path, help="Extracted paper text, e.g. pdftotext output.")
    parser.add_argument("--output", required=True, type=Path, help="Output Markdown note path.")
    parser.add_argument("--paper-id", help="Optional paper identifier. Defaults to source stem.")
    parser.add_argument("--title", help="Optional paper title. Defaults to the first plausible title line.")
    parser.add_argument("--report", type=Path, help="Optional JSON report of selected line windows.")
    args = parser.parse_args()

    if not args.source.exists():
        parser.error(f"Source file not found: {args.source}")

    report = write_outputs(args.source, args.output, args.paper_id, args.title, args.report)
    print(json.dumps({"note": str(args.output), "paper_id": report["paper_id"], "title": report["title"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
