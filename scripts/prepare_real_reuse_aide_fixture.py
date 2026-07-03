#!/usr/bin/env python
"""Prepare locked AIDE real-reuse fixtures from a Kaggle-style train CSV."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_VERSION = "0.1"
PREPARED_ON = "2026-07-03"
STATUS = "prepared_assets_ready_for_dry_scoring"
TARGET_COLUMN = "Transported"
ID_COLUMN = "PassengerId"


AIDE_SUMMARY_FALLBACK = """# Generic Summary: AIDE

AIDE frames machine-learning engineering as search over executable Python
solutions. It keeps a tree of candidate scripts, evaluates each candidate with
an objective metric, records feedback, and uses that feedback to draft, debug,
or improve the next candidate.

The method emphasizes concise task context, static data previews, measured
validation scores, and choosing the best solution based on the objective
function rather than narrative confidence.

Known limitations include local optima, repeated local patches, benchmark/data
contamination concerns, and dependence on the available runtime and objective
metric.
"""


def resolve(root: Path, path: Path) -> Path:
    return path if path.is_absolute() else root / path


def relative(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        fieldnames = list(reader.fieldnames or [])
        rows = [dict(row) for row in reader]
    if not fieldnames:
        raise ValueError(f"{path} has no CSV header")
    return fieldnames, rows


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def normalize_bool(value: Any) -> str:
    text = str(value).strip().lower()
    if text in {"true", "1", "yes", "y"}:
        return "True"
    if text in {"false", "0", "no", "n"}:
        return "False"
    raise ValueError(f"unsupported boolean label: {value!r}")


def validate_rows(fieldnames: list[str], rows: list[dict[str, str]], source: Path) -> None:
    missing = {ID_COLUMN, TARGET_COLUMN} - set(fieldnames)
    if missing:
        raise ValueError(f"{source} missing required columns: {', '.join(sorted(missing))}")
    if len(rows) < 4:
        raise ValueError("AIDE fixture preparation requires at least four labeled rows")
    ids = [row[ID_COLUMN] for row in rows]
    duplicates = [item for item, count in Counter(ids).items() if count > 1]
    if duplicates:
        raise ValueError(f"duplicate {ID_COLUMN} values: {duplicates[:3]}")
    for row in rows:
        row[TARGET_COLUMN] = normalize_bool(row[TARGET_COLUMN])


def split_rows(
    rows: list[dict[str, str]],
    validation_fraction: float,
    seed: int,
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    if not 0 < validation_fraction < 1:
        raise ValueError("--validation-fraction must be between 0 and 1")
    shuffled = [dict(row) for row in rows]
    random.Random(seed).shuffle(shuffled)
    validation_count = max(1, round(len(shuffled) * validation_fraction))
    validation_count = min(validation_count, len(shuffled) - 1)
    validation_rows = sorted(shuffled[:validation_count], key=lambda row: row[ID_COLUMN])
    train_rows = sorted(shuffled[validation_count:], key=lambda row: row[ID_COLUMN])
    return train_rows, validation_rows


def majority_label(rows: list[dict[str, str]]) -> str:
    counts = Counter(row[TARGET_COLUMN] for row in rows)
    return sorted(counts.items(), key=lambda item: (-item[1], item[0]))[0][0]


def accuracy(submission_rows: list[dict[str, str]], label_rows: list[dict[str, str]]) -> float:
    labels = {row[ID_COLUMN]: normalize_bool(row[TARGET_COLUMN]) for row in label_rows}
    predictions = {row[ID_COLUMN]: normalize_bool(row[TARGET_COLUMN]) for row in submission_rows}
    if set(predictions) != set(labels):
        raise ValueError("submission ids do not match validation labels")
    correct = sum(1 for passenger_id, answer in labels.items() if predictions[passenger_id] == answer)
    return correct / len(labels)


def write_summary_context(task_id: str, root: Path, condition_dir: Path) -> Path:
    path = condition_dir / f"{task_id}_summary.md"
    text = f"""# Real-Reuse Summary Baseline: {task_id}

This context is the Summary baseline for the locked AIDE real-reuse task. It
summarizes the source-paper method only. It does not include hidden validation
labels or scorer-only thresholds.

{AIDE_SUMMARY_FALLBACK.strip()}
"""
    write_text(path, text)
    return path


def feature_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [{key: value for key, value in row.items() if key != TARGET_COLUMN} for row in rows]


def make_task_prompt(task_id: str, baseline_score: float) -> str:
    if task_id == "AIDE-T1":
        return f"""# AIDE-T1 Locked Task Prompt

You are solving a Kaggle-style tabular ML task under a local validation split.
The workspace contains:

- `train.csv`: labeled training rows.
- `validation_features.csv`: validation rows without labels.
- `baseline_submission.csv`: a majority-class starter submission.
- `baseline_score.json`: the starter validation score ({baseline_score:.6f}).

Write a complete Python script that reads `train.csv` and
`validation_features.csv`, trains or applies a measurable model, and writes
`submission.csv` with columns `{ID_COLUMN}` and `{TARGET_COLUMN}`.

Use an AIDE-style loop mentally: inspect the data columns, propose a candidate,
respect the objective metric, and prefer measured validation improvement over
unsupported claims. Do not request hidden labels.
"""
    return f"""# AIDE-T2 Locked Task Prompt

You are given a weak AIDE-style baseline for a Kaggle-style tabular ML task.
The workspace contains:

- `train.csv`: labeled training rows.
- `validation_features.csv`: validation rows without labels.
- `weak_script.py`: the weak starting script.
- `error_or_score_feedback.md`: objective feedback for the weak script.
- `baseline_score.json`: the weak-script validation score ({baseline_score:.6f}).

Write an improved Python script that reads `train.csv` and
`validation_features.csv`, uses the feedback, and writes `submission.csv` with
columns `{ID_COLUMN}` and `{TARGET_COLUMN}`.

Keep the change focused, log assumptions in comments only when needed, and do
not request hidden labels.
"""


def weak_script_text() -> str:
    return f'''import csv
from collections import Counter

TARGET = "{TARGET_COLUMN}"
ID = "{ID_COLUMN}"

with open("train.csv", newline="", encoding="utf-8") as handle:
    rows = list(csv.DictReader(handle))

label = Counter(row[TARGET] for row in rows).most_common(1)[0][0]

with open("validation_features.csv", newline="", encoding="utf-8") as handle:
    features = list(csv.DictReader(handle))

with open("submission.csv", "w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=[ID, TARGET])
    writer.writeheader()
    for row in features:
        writer.writerow({{ID: row[ID], TARGET: label}})
'''


def file_entry(root: Path, path: Path, slot: str, visibility: str) -> dict[str, str]:
    return {
        "slot": slot,
        "path": relative(root, path),
        "sha256": sha256_file(path),
        "visibility": visibility,
    }


def prepare(args: argparse.Namespace) -> Path:
    root = args.root.resolve()
    task_id = args.task.upper()
    output_dir = resolve(root, args.output_dir)
    condition_dir = resolve(root, args.condition_dir)
    papertoskill_context = resolve(root, args.papertoskill_context)
    train_csv = resolve(root, args.train_csv)

    fieldnames, rows = read_csv(train_csv)
    validate_rows(fieldnames, rows, train_csv)
    train_rows, validation_rows = split_rows(rows, args.validation_fraction, args.split_seed)
    feature_fieldnames = [field for field in fieldnames if field != TARGET_COLUMN]
    label_fieldnames = [ID_COLUMN, TARGET_COLUMN]
    majority = majority_label(train_rows)
    baseline_rows = [{ID_COLUMN: row[ID_COLUMN], TARGET_COLUMN: majority} for row in validation_rows]
    baseline_score = accuracy(baseline_rows, validation_rows)

    output_dir.mkdir(parents=True, exist_ok=True)
    workspace_dir = output_dir / "starter_workspace"
    workspace_dir.mkdir(parents=True, exist_ok=True)

    dataset_manifest_path = output_dir / "dataset_manifest.json"
    train_split_path = output_dir / "train_split.csv"
    validation_features_path = output_dir / "validation_features.csv"
    validation_labels_path = output_dir / "validation_labels.csv"
    baseline_submission_path = output_dir / "baseline_submission.csv"
    baseline_score_path = output_dir / "baseline_score.json"
    task_prompt_path = output_dir / "task_prompt.md"
    readme_path = workspace_dir / "README.md"
    workspace_train_path = workspace_dir / "train.csv"
    workspace_validation_path = workspace_dir / "validation_features.csv"
    workspace_baseline_path = workspace_dir / "baseline_submission.csv"
    workspace_baseline_score_path = workspace_dir / "baseline_score.json"
    weak_script_path = workspace_dir / "weak_script.py"
    feedback_path = output_dir / "error_or_score_feedback.md"

    write_csv(train_split_path, fieldnames, train_rows)
    write_csv(validation_features_path, feature_fieldnames, feature_rows(validation_rows))
    write_csv(validation_labels_path, label_fieldnames, validation_rows)
    write_csv(baseline_submission_path, label_fieldnames, baseline_rows)
    write_csv(workspace_train_path, fieldnames, train_rows)
    write_csv(workspace_validation_path, feature_fieldnames, feature_rows(validation_rows))
    write_csv(workspace_baseline_path, label_fieldnames, baseline_rows)
    baseline_payload = {
        "task_id": task_id,
        "metric_name": "validation_score" if task_id == "AIDE-T1" else "best_node_score",
        "baseline_kind": "majority_class_weak_script",
        "baseline_label": majority,
        "baseline_score": baseline_score,
        "validation_rows": len(validation_rows),
        "visibility": "model_visible_feedback",
    }
    write_json(baseline_score_path, baseline_payload)
    write_json(workspace_baseline_score_path, baseline_payload)
    write_text(task_prompt_path, make_task_prompt(task_id, baseline_score))
    write_text(
        readme_path,
        f"""# {task_id} Starter Workspace

Run candidate scripts from this directory. A valid candidate must write
`submission.csv` with `{ID_COLUMN}` and `{TARGET_COLUMN}` columns.

Hidden scorer asset: `../validation_labels.csv`.
""",
    )
    if task_id == "AIDE-T2":
        write_text(weak_script_path, weak_script_text())
        write_text(
            feedback_path,
            f"""# AIDE-T2 Weak-Script Feedback

The weak starting script predicts the majority class `{majority}` for every
validation row. Its objective validation score is {baseline_score:.6f}.

Use the provided training columns and validation features to produce a better
candidate under the same output contract.
""",
        )
    else:
        if weak_script_path.exists():
            weak_script_path.unlink()
        if feedback_path.exists():
            feedback_path.unlink()

    dataset_payload = {
        "schema_version": SCHEMA_VERSION,
        "task_id": task_id,
        "source_kind": "kaggle_style_train_csv",
        "competition_slug": args.competition_slug,
        "source_train_csv": str(train_csv),
        "source_train_sha256": sha256_file(train_csv),
        "split_seed": args.split_seed,
        "validation_fraction": args.validation_fraction,
        "row_count": len(rows),
        "train_rows": len(train_rows),
        "validation_rows": len(validation_rows),
        "columns": fieldnames,
        "target_column": TARGET_COLUMN,
        "id_column": ID_COLUMN,
        "evidence_boundary": (
            "Dataset manifest for a local AIDE real-reuse fixture. Validation "
            "labels are scorer-only and must not enter model-visible context."
        ),
    }
    write_json(dataset_manifest_path, dataset_payload)
    summary_path = write_summary_context(task_id, root, condition_dir)

    files = [
        file_entry(root, dataset_manifest_path, "dataset_manifest", "model_visible"),
        file_entry(root, train_split_path, "train_split", "model_visible"),
        file_entry(root, validation_features_path, "validation_features", "model_visible"),
        file_entry(root, baseline_submission_path, "baseline_submission", "model_visible"),
        file_entry(root, baseline_score_path, "baseline_score", "model_visible"),
        file_entry(root, task_prompt_path, "task_prompt", "model_visible"),
        file_entry(root, workspace_train_path, "workspace_train_csv", "model_visible"),
        file_entry(root, workspace_validation_path, "workspace_validation_features", "model_visible"),
        file_entry(root, workspace_baseline_path, "workspace_baseline_submission", "model_visible"),
        file_entry(root, workspace_baseline_score_path, "workspace_baseline_score", "model_visible"),
        file_entry(root, readme_path, "workspace_readme", "model_visible"),
        file_entry(root, validation_labels_path, "validation_labels", "scorer_only"),
        file_entry(root, summary_path, "summary_context", "condition_context"),
    ]
    if task_id == "AIDE-T2":
        files.extend(
            [
                file_entry(root, weak_script_path, "weak_script", "model_visible"),
                file_entry(root, feedback_path, "error_or_score_feedback", "model_visible"),
            ]
        )

    manifest = {
        "schema_version": SCHEMA_VERSION,
        "benchmark_id": "papertoskill_real_reuse_v0",
        "task_id": task_id,
        "source_paper_id": "aide",
        "status": STATUS,
        "prepared_on": PREPARED_ON,
        "evidence_boundary": (
            "Prepared AIDE fixture assets and condition contexts for dry "
            "scoring. This manifest does not run a model, compare Summary "
            "against PaperToSkill, score downstream outputs, or claim task "
            "success."
        ),
        "source_snapshot": f"{args.competition_slug} local validation split seed {args.split_seed}",
        "license_and_provenance": {
            "source_urls": [
                "https://github.com/WecoAI/aideml",
                "https://github.com/openai/mle-bench",
                "https://www.kaggle.com/competitions/spaceship-titanic",
            ],
            "local_use_scope": "locked local validation fixture for reproducible experiment setup",
            "redistribution_note": "Do not redistribute Kaggle competition data without checking the competition terms.",
        },
        "condition_contexts": [
            {"condition": "summary", "path": relative(root, summary_path), "visibility": "model_visible"},
            {"condition": "papertoskill", "path": relative(root, papertoskill_context), "visibility": "model_visible"},
        ],
        "workspace_dir": relative(root, workspace_dir),
        "hidden_from_model": [relative(root, validation_labels_path)],
        "asset_dir": relative(root, output_dir),
        "files": files,
    }
    manifest_path = output_dir / "asset_manifest.json"
    write_json(manifest_path, manifest)
    return manifest_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare locked AIDE real-reuse fixture assets.")
    parser.add_argument("--task", choices=["AIDE-T1", "AIDE-T2"], required=True)
    parser.add_argument("--train-csv", type=Path, required=True)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--condition-dir", type=Path, default=Path("baselines/real_reuse"))
    parser.add_argument("--papertoskill-context", type=Path, default=Path("generated_skills/aide/SKILL.md"))
    parser.add_argument("--split-seed", type=int, default=20260703)
    parser.add_argument("--validation-fraction", type=float, default=0.2)
    parser.add_argument("--competition-slug", default="spaceship-titanic")
    args = parser.parse_args()

    try:
        manifest_path = prepare(args)
    except ValueError as exc:
        parser.error(str(exc))
    print(manifest_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
