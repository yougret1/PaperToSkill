#!/usr/bin/env python
"""Check AAAI paper table values against generated result tables."""

from __future__ import annotations

import argparse
import csv
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


TABLE_SOURCES = {
    "main_results": "results/tables/main_results.csv",
    "transfer_ablation": "results/tables/transfer_ablation.csv",
    "cost_proxy": "results/tables/context_cost_proxy_tokenizer.csv",
    "auto_note": "results/tables/auto_note_comparison.csv",
}


@dataclass
class Check:
    id: str
    status: str
    detail: str
    evidence: str

    def as_dict(self) -> dict[str, str]:
        return {
            "id": self.id,
            "status": self.status,
            "detail": self.detail,
            "evidence": self.evidence,
        }


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def display_path(root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def clean_latex_cell(value: str) -> str:
    text = value.strip()
    text = text.replace(r"\%", "%")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def parse_tabular_rows(tex_text: str, label: str) -> list[list[str]]:
    label_marker = rf"\label{{{label}}}"
    label_index = tex_text.find(label_marker)
    if label_index < 0:
        raise ValueError(f"Missing table label: {label}")

    begin_index = tex_text.find(r"\begin{tabular}", label_index)
    end_index = tex_text.find(r"\end{tabular}", begin_index)
    if begin_index < 0 or end_index < 0:
        raise ValueError(f"Missing tabular block for label: {label}")

    block = tex_text[begin_index:end_index]
    in_body = False
    rows: list[list[str]] = []
    for raw_line in block.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line == r"\midrule":
            in_body = True
            continue
        if line == r"\bottomrule":
            break
        if not in_body or line.startswith("\\"):
            continue
        if line.endswith(r"\\"):
            line = line[:-2].strip()
        rows.append([clean_latex_cell(cell) for cell in line.split("&")])
    return rows


def by_key(rows: list[dict[str, str]], key: str) -> dict[str, dict[str, str]]:
    return {row[key]: row for row in rows}


def normalize_for_detail(value: str) -> str:
    return value.replace("%", r"\%")


def numeric_value(value: str) -> float | None:
    text = clean_latex_cell(value)
    percent = text.endswith("%")
    if percent:
        text = text[:-1]
    try:
        number = float(text)
    except ValueError:
        return None
    return number / 100 if percent else number


def values_match(actual: str, expected: str, tolerance: float = 0.001) -> bool:
    actual_clean = clean_latex_cell(actual)
    expected_clean = clean_latex_cell(expected)
    if actual_clean == expected_clean:
        return True

    actual_number = numeric_value(actual_clean)
    expected_number = numeric_value(expected_clean)
    if actual_number is not None and expected_number is not None:
        return abs(actual_number - expected_number) <= tolerance

    score_match = re.fullmatch(r"([0-9.]+)/([0-9.]+)", actual_clean)
    expected_score_match = re.fullmatch(r"([0-9.]+)/([0-9.]+)", expected_clean)
    if score_match and expected_score_match:
        return all(
            abs(float(left) - float(right)) <= tolerance
            for left, right in zip(score_match.groups(), expected_score_match.groups())
        )

    return False


def check_value(check_id: str, actual: str, expected: str, evidence: str) -> Check:
    if values_match(actual, expected):
        return Check(
            check_id,
            "ready",
            f"value={normalize_for_detail(actual)}",
            evidence,
        )
    return Check(
        check_id,
        "fail",
        f"actual={normalize_for_detail(actual)}; expected={normalize_for_detail(expected)}",
        evidence,
    )


def table_rows_by_paper(tex_rows: list[list[str]], label: str, expected_width: int) -> dict[str, list[str]]:
    rows: dict[str, list[str]] = {}
    for row in tex_rows:
        if len(row) != expected_width:
            raise ValueError(f"Unexpected width in {label}: expected {expected_width}, got {len(row)} for {row}")
        rows[row[0]] = row
    return rows


def main_results_checks(root: Path, tex_rows: list[list[str]]) -> list[Check]:
    source_path = root / TABLE_SOURCES["main_results"]
    source = by_key(read_csv_rows(source_path), "Paper")
    actual = table_rows_by_paper(tex_rows, "tab:main-results", 9)
    evidence = f"paper/aaai/papertoskill_tables.tex vs {TABLE_SOURCES['main_results']}"
    checks: list[Check] = []
    column_map = [
        ("rubric", 1, "Skill rubric"),
        ("skill_coverage", 2, "Skill coverage"),
        ("generic_summary", 3, "Generic summary coverage"),
        ("abstract_only", 4, "Abstract-only coverage"),
        ("delta_summary", 5, "Skill vs generic delta"),
        ("transfer", 6, "Transfer readiness"),
        ("support", 7, "Source support rate"),
        ("words", 8, "Skill words"),
    ]
    for paper, expected_row in source.items():
        actual_row = actual.get(paper)
        if not actual_row:
            checks.append(Check(f"paper_table_main_{paper}_row", "fail", "missing row", evidence))
            continue
        for suffix, index, column in column_map:
            checks.append(
                check_value(
                    f"paper_table_main_{slug(paper)}_{suffix}",
                    actual_row[index],
                    expected_row[column],
                    evidence,
                )
            )
    return checks


def transfer_checks(root: Path, tex_rows: list[list[str]]) -> list[Check]:
    source_path = root / TABLE_SOURCES["transfer_ablation"]
    source_rows = read_csv_rows(source_path)
    actual = table_rows_by_paper(tex_rows, "tab:transfer-ablation", 3)
    evidence = f"paper/aaai/papertoskill_tables.tex vs {TABLE_SOURCES['transfer_ablation']}"
    by_paper_variant = {(row["Paper"], row["Variant"]): row for row in source_rows}
    checks: list[Check] = []
    for paper in sorted({row["Paper"] for row in source_rows}):
        actual_row = actual.get(paper)
        if not actual_row:
            checks.append(Check(f"paper_table_transfer_{slug(paper)}_row", "fail", "missing row", evidence))
            continue
        checks.append(
            check_value(
                f"paper_table_transfer_{slug(paper)}_full",
                actual_row[1],
                by_paper_variant[(paper, "Full skill")]["Average readiness"],
                evidence,
            )
        )
        checks.append(
            check_value(
                f"paper_table_transfer_{slug(paper)}_no_transfer",
                actual_row[2],
                by_paper_variant[(paper, "No transfer notes")]["Average readiness"],
                evidence,
            )
        )
    return checks


def cost_proxy_checks(root: Path, tex_rows: list[list[str]]) -> list[Check]:
    source_path = root / TABLE_SOURCES["cost_proxy"]
    source_rows = read_csv_rows(source_path)
    actual = table_rows_by_paper(tex_rows, "tab:cost-proxy", 5)
    evidence = f"paper/aaai/papertoskill_tables.tex vs {TABLE_SOURCES['cost_proxy']}"
    by_paper_variant = {(row["Paper"], row["Variant"]): row for row in source_rows}
    checks: list[Check] = []
    for paper in sorted({row["Paper"] for row in source_rows}):
        full_row = by_paper_variant[(paper, "Full extracted paper")]
        skill_row = by_paper_variant[(paper, "Generated skill")]
        actual_row = actual.get(paper)
        if not actual_row:
            checks.append(Check(f"paper_table_cost_{slug(paper)}_row", "fail", "missing row", evidence))
            continue
        checks.append(
            check_value(
                f"paper_table_cost_{slug(paper)}_full_tokens",
                actual_row[1],
                full_row["Estimated input tokens"],
                evidence,
            )
        )
        checks.append(
            check_value(
                f"paper_table_cost_{slug(paper)}_skill_tokens",
                actual_row[2],
                skill_row["Estimated input tokens"],
                evidence,
            )
        )
        checks.append(
            check_value(
                f"paper_table_cost_{slug(paper)}_skill_over_full",
                actual_row[3],
                skill_row["Tokens vs full paper"],
                evidence,
            )
        )
        checks.append(
            check_value(
                f"paper_table_cost_{slug(paper)}_reduction",
                actual_row[4],
                skill_row["Token reduction vs full paper"],
                evidence,
            )
        )
    return checks


def auto_note_checks(root: Path, tex_rows: list[list[str]]) -> list[Check]:
    source_path = root / TABLE_SOURCES["auto_note"]
    source_rows = read_csv_rows(source_path)
    evidence = f"paper/aaai/papertoskill_tables.tex vs {TABLE_SOURCES['auto_note']}"
    input_aliases = {
        "Curated note": "Curated source-anchored note",
        "Auto note scaffold": "Automatic extracted-text note scaffold",
    }
    actual = {(row[0], input_aliases.get(row[1], row[1])): row for row in tex_rows if len(row) == 7}
    checks: list[Check] = []
    column_map = [
        ("rubric", 2, "Skill rubric"),
        ("coverage", 3, "Skill coverage"),
        ("transfer", 4, "Transfer readiness"),
        ("support", 5, "Source support rate"),
        ("words", 6, "Skill words"),
    ]
    for expected_row in source_rows:
        key = (expected_row["Paper"], expected_row["Input"])
        actual_row = actual.get(key)
        row_slug = f"{slug(key[0])}_{slug(key[1])}"
        if not actual_row:
            checks.append(Check(f"paper_table_auto_{row_slug}_row", "fail", "missing row", evidence))
            continue
        for suffix, index, column in column_map:
            checks.append(
                check_value(
                    f"paper_table_auto_{row_slug}_{suffix}",
                    actual_row[index],
                    expected_row[column],
                    evidence,
                )
            )
    return checks


def slug(value: str) -> str:
    text = value.lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")


def build_report(root: Path, tables_tex: Path) -> dict[str, Any]:
    root = root.resolve()
    tables_tex = tables_tex.resolve()
    tex_text = tables_tex.read_text(encoding="utf-8")

    checks: list[Check] = []
    try:
        checks.extend(main_results_checks(root, parse_tabular_rows(tex_text, "tab:main-results")))
        checks.extend(transfer_checks(root, parse_tabular_rows(tex_text, "tab:transfer-ablation")))
        checks.extend(cost_proxy_checks(root, parse_tabular_rows(tex_text, "tab:cost-proxy")))
        checks.extend(auto_note_checks(root, parse_tabular_rows(tex_text, "tab:auto-note")))
    except ValueError as exc:
        checks.append(Check("paper_table_parse", "fail", str(exc), display_path(root, tables_tex)))

    status_counts = {"ready": 0, "fail": 0}
    for check in checks:
        status_counts[check.status] = status_counts.get(check.status, 0) + 1

    return {
        "schema_version": "0.1",
        "evidence_boundary": (
            "Checks that the AAAI LaTeX table values match the generated CSV result tables. "
            "A ready report prevents manuscript-table drift; it does not add new empirical evidence."
        ),
        "tables_tex": str(tables_tex),
        "table_sources": TABLE_SOURCES,
        "overall_status": "fail" if status_counts.get("fail", 0) else "ready",
        "status_counts": status_counts,
        "checks": [check.as_dict() for check in checks],
    }


def markdown_table(rows: list[list[str]], columns: list[str]) -> str:
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for row in rows:
        values = [value.replace("|", "\\|").replace("\n", " ") for value in row]
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    rows = [[check["id"], check["status"], check["detail"], check["evidence"]] for check in report["checks"]]
    counts = report["status_counts"]
    lines = [
        "# Paper Table Consistency Report",
        "",
        "Evidence boundary: this report checks that AAAI LaTeX table values match "
        "generated CSV result tables. It does not add new empirical evidence.",
        "",
        f"- Overall status: {report['overall_status']}",
        f"- Ready checks: {counts.get('ready', 0)}",
        f"- Failed checks: {counts.get('fail', 0)}",
        "",
        "## Checks",
        "",
        markdown_table(rows, ["Check", "Status", "Detail", "Evidence"]),
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def write_json(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="Check PaperToSkill AAAI table consistency.")
    parser.add_argument("--root", type=Path, default=root)
    parser.add_argument("--tables-tex", type=Path, default=root / "paper" / "aaai" / "papertoskill_tables.tex")
    parser.add_argument(
        "--output-json",
        type=Path,
        default=root / "results" / "reproducibility" / "paper_table_report.json",
    )
    parser.add_argument(
        "--output-md",
        type=Path,
        default=root / "results" / "reproducibility" / "paper_table_report.md",
    )
    parser.add_argument("--strict", action="store_true", help="Exit non-zero if any table consistency check fails.")
    args = parser.parse_args()

    report = build_report(args.root, args.tables_tex)
    write_json(args.output_json, report)
    write_markdown(args.output_md, report)
    print(args.output_json)
    print(args.output_md)
    if args.strict and report["overall_status"] == "fail":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
