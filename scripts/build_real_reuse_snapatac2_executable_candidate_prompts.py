#!/usr/bin/env python
"""Build SNAP executable-candidate prompt packets without calling a model."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "0.1"
TASK_IDS = ("SNAP-T1", "SNAP-T2")
CONDITIONS = ("summary", "papertoskill")
REQUIRED_ARTIFACTS = {
    "SNAP-T1": ("embedding.csv", "cell_features.csv", "fragment_summary.json"),
    "SNAP-T2": ("clusters.csv", "marker_summary.json", "embedding.csv"),
}
DEFAULT_OUTPUT_DIR = Path("results/real_reuse/snapatac2_executable_candidate_prompts")
DEFAULT_OUTPUT_JSON = Path("results/real_reuse/snapatac2_executable_candidate_prompt_plan.json")
DEFAULT_OUTPUT_MD = Path("results/real_reuse/snapatac2_executable_candidate_prompt_plan.md")
DEFAULT_COMPACT_OUTPUT_DIR = Path("results/real_reuse/snapatac2_executable_candidate_compact_prompts")
DEFAULT_COMPACT_OUTPUT_JSON = Path("results/real_reuse/snapatac2_executable_candidate_compact_prompt_plan.json")
DEFAULT_COMPACT_OUTPUT_MD = Path("results/real_reuse/snapatac2_executable_candidate_compact_prompt_plan.md")
COMPACT_CONTEXT_KEYWORDS = (
    "snapatac2",
    "spectral",
    "embedding",
    "cluster",
    "marker",
    "artifact",
    "runtime",
    "memory",
    "ari",
    "nmi",
    "preprocess",
    "normalization",
    "idf",
    "fallback",
    "failure",
    "validation",
)


def root_path() -> Path:
    return Path(__file__).resolve().parents[1]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def resolve(root: Path, raw_path: str | Path) -> Path:
    path = Path(raw_path)
    return path if path.is_absolute() else root / path


def relative(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def asset_manifest_path(root: Path, task_id: str) -> Path:
    return root / "benchmarks" / "real_reuse" / "assets" / task_id / "asset_manifest.json"


def visible_file_entries(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    result = []
    for item in manifest.get("files", []):
        if item.get("visibility") == "model_visible":
            result.append(item)
    return result


def find_slot(manifest: dict[str, Any], slot: str) -> dict[str, Any]:
    for item in manifest.get("files", []):
        if item.get("slot") == slot:
            return item
    raise KeyError(f"missing slot {slot}")


def condition_context_path(root: Path, manifest: dict[str, Any], condition: str) -> Path:
    for item in manifest.get("condition_contexts", []):
        if item.get("condition") == condition:
            return resolve(root, item["path"])
    raise KeyError(f"missing condition context {condition}")


def text_or_json(path: Path) -> str:
    if path.suffix.lower() == ".json":
        return json.dumps(load_json(path), indent=2, ensure_ascii=False)
    return path.read_text(encoding="utf-8")


def json_value(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False)


def compact_json_summary(path: Path) -> str:
    payload = load_json(path)
    lines: list[str] = []
    for key in (
        "dataset_function",
        "materialization_mode",
        "dataset_status",
        "max_runtime_seconds",
        "max_peak_memory_mb",
        "same_budget_across_conditions",
        "required_fields",
        "optional_fields",
    ):
        if key in payload:
            lines.append(f"- {key}: {json_value(payload[key])}")
    miniature = payload.get("miniature_fixture")
    if isinstance(miniature, dict):
        for key in ("copied_path", "sha256", "size_bytes"):
            if key in miniature:
                lines.append(f"- miniature_fixture.{key}: {json_value(miniature[key])}")
    source_repository = payload.get("source_repository")
    if isinstance(source_repository, dict):
        for key in ("revision", "license"):
            if key in source_repository:
                lines.append(f"- source_repository.{key}: {json_value(source_repository[key])}")
    if not lines:
        lines.append(f"- Top-level keys: {', '.join(payload.keys())}")
    return "\n".join(lines)


def truncate_line(line: str, limit: int = 180) -> str:
    stripped = " ".join(line.strip().split())
    if len(stripped) <= limit:
        return stripped
    return stripped[: limit - 3].rstrip() + "..."


def compact_text_summary(path: Path, max_lines: int = 14) -> str:
    text = path.read_text(encoding="utf-8")
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if len(text) <= 900 and len(lines) <= max_lines:
        return "\n".join(f"- {truncate_line(line)}" for line in lines)
    selected: list[str] = []
    for line in lines:
        lowered = line.lower()
        if line.startswith("#") or any(keyword in lowered for keyword in COMPACT_CONTEXT_KEYWORDS):
            selected.append(truncate_line(line))
        if len(selected) >= max_lines:
            break
    if not selected:
        selected = [truncate_line(line) for line in lines[:max_lines]]
    return "\n".join(f"- {line}" for line in selected)


def compact_asset_summary(path: Path) -> str:
    if path.suffix.lower() == ".json":
        return compact_json_summary(path)
    return compact_text_summary(path, max_lines=6)


def visible_asset_block(root: Path, manifest: dict[str, Any]) -> str:
    blocks: list[str] = []
    for item in visible_file_entries(manifest):
        slot = str(item["slot"])
        path = resolve(root, item["path"])
        rel = relative(root, path)
        if slot == "miniature_fragment":
            blocks.append(
                "\n".join(
                    [
                        f"## {slot}",
                        f"- Path: `{rel}`",
                        f"- SHA256: `{item.get('sha256', '')}`",
                        "- Do not inline this gzip file; pass its path to the candidate script through `--fragment`.",
                    ]
                )
            )
        else:
            blocks.append("\n".join([f"## {slot}", f"Path: `{rel}`", "", "```", text_or_json(path), "```"]))
    return "\n\n".join(blocks)


def compact_visible_asset_block(root: Path, manifest: dict[str, Any]) -> str:
    blocks: list[str] = []
    for item in visible_file_entries(manifest):
        slot = str(item["slot"])
        path = resolve(root, item["path"])
        rel = relative(root, path)
        lines = [f"## {slot}", f"- Path: `{rel}`", f"- SHA256: `{item.get('sha256', '')}`"]
        if slot == "miniature_fragment":
            lines.append("- Use this gzip file only through the candidate script `--fragment` argument.")
        else:
            lines.extend(["- Compact summary:", compact_asset_summary(path)])
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks)


def build_prompt(root: Path, task_id: str, condition: str, *, mode: str = "full") -> tuple[str, dict[str, Any]]:
    manifest_path = asset_manifest_path(root, task_id)
    manifest = load_json(manifest_path)
    context_path = condition_context_path(root, manifest, condition)
    context_text = context_path.read_text(encoding="utf-8")
    fragment_entry = find_slot(manifest, "miniature_fragment")
    fragment_path = resolve(root, fragment_entry["path"])
    required_artifacts = REQUIRED_ARTIFACTS[task_id]
    script_name = f"{task_id}_{condition}.py"
    if mode == "compact":
        prompt = "\n\n".join(
            [
                f"# SNAP Executable-Candidate Compact Prompt: {task_id} / {condition}",
                "Return exactly one Python script, no Markdown fences. It must run under `scripts/run_real_reuse_snapatac2_executable_candidate.py`.",
                "This compact local-path/SHA packet prepares a future paired diagnostic rerun; it is not scored evidence.",
                "## Interface",
                "\n".join(
                    [
                        "Accept: `--task-id`, `--condition`, `--fragment`, `--artifact-dir`, `--result-json`.",
                        f"Expected file name for this packet: `{script_name}`.",
                        f"Fixture path passed through `--fragment`: `{relative(root, fragment_path)}`.",
                        f"Create under `--artifact-dir`: {', '.join(required_artifacts)}.",
                        "Write candidate notes/quality metrics to `--result-json` as JSON.",
                        "Runner owns final `completed=true` after execution/artifact checks.",
                    ]
                ),
                "## Hard Boundaries",
                "\n".join(
                    [
                        "No raw-row append; no main-row replacement unless `results/real_reuse/main_run_selection.json` is explicitly promoted later.",
                        "No scorer-only labels, scorer thresholds, hidden metrics, or post-run scorer files.",
                        "No network, package installation, package-manager subprocesses, or writes outside `--artifact-dir` and `--result-json`.",
                        "Use cross-platform Python for Windows/Linux; do not import `resource` or other POSIX-only modules.",
                    ]
                ),
                "## Compact Condition Context",
                "\n".join(
                    [
                        f"- Full context path: `{relative(root, context_path)}`",
                        "- Deterministic compact summary:",
                        compact_text_summary(context_path, max_lines=14),
                    ]
                ),
                "## Compact Model-Visible Locked Assets",
                compact_visible_asset_block(root, manifest),
                "## Output Requirements",
                "\n".join(
                    [
                        "Return valid Python code only.",
                        "The code should be deterministic on the provided miniature fixture.",
                        "If SnapATAC2 is unavailable, write a transparent fallback that still materializes the required artifacts and records what happened in `--result-json`.",
                    ]
                ),
            ]
        )
    else:
        prompt = "\n\n".join(
        [
            f"# SNAP Executable-Candidate Prompt: {task_id} / {condition}",
            "You are preparing a Python candidate script for a locked SnapATAC2 real-reuse diagnostic rerun.",
            "Return one Python script only. Do not wrap it in Markdown fences.",
            "The script must be executable by `scripts/run_real_reuse_snapatac2_executable_candidate.py`.",
            "## Candidate Script Interface",
            "\n".join(
                [
                    "Your script must accept these command-line arguments:",
                    "- `--task-id`",
                    "- `--condition`",
                    "- `--fragment`",
                    "- `--artifact-dir`",
                    "- `--result-json`",
                    "",
                    f"Expected file name for this packet: `{script_name}`.",
                    f"Use the `--fragment` path for the locked miniature fixture. The current fixture path is `{relative(root, fragment_path)}`.",
                    f"Create these required artifacts under `--artifact-dir`: {', '.join(required_artifacts)}.",
                    "Write optional candidate-side notes and quality metrics to `--result-json` as JSON.",
                    "Do not set final task completion by yourself; the runner owns `completed=true` only after execution and artifact checks.",
                    "Use cross-platform Python that runs on the current Windows runner and Linux; do not import POSIX-only modules such as `resource`.",
                    "The runner records final runtime and peak-memory metadata, so your script should not depend on platform-specific resource APIs.",
                    "Do not use network access, package installation, subprocess package managers, or writes outside `--artifact-dir` and `--result-json`.",
                ]
            ),
            "## Evidence Boundary",
            "\n".join(
                [
                    "This prompt packet prepares a future paired diagnostic rerun.",
                    "It must not append to `results/real_reuse/raw_rows.jsonl`.",
                    "It must not replace paper-facing main rows unless a later explicit promotion updates `results/real_reuse/main_run_selection.json`.",
                    "Do not request scorer-only labels, scorer thresholds, or hidden metrics.",
                ]
            ),
            "## Condition Context",
            context_text,
            "## Model-Visible Locked Assets",
            visible_asset_block(root, manifest),
            "## Output Requirements",
            "\n".join(
                [
                    "Return valid Python code only.",
                    "The code should be deterministic on the provided miniature fixture.",
                    "Prefer lightweight standard-library or widely available scientific Python logic.",
                    "If SnapATAC2 is unavailable, write a transparent fallback that still materializes the required artifacts and records what happened in `--result-json`.",
                    "Do not import `resource`; use only cross-platform modules or guard optional scientific dependencies behind fallbacks.",
                ]
            ),
        ]
    )
    if mode not in {"full", "compact"}:
        raise ValueError(f"unsupported prompt mode: {mode}")
    row = {
        "task_id": task_id,
        "condition": condition,
        "prompt_mode": mode,
        "expected_script_name": script_name,
        "asset_manifest": relative(root, manifest_path),
        "condition_context": relative(root, context_path),
        "fragment": relative(root, fragment_path),
        "required_artifacts": list(required_artifacts),
    }
    return prompt + "\n", row


def write_markdown(path: Path, plan: dict[str, Any]) -> None:
    title_suffix = " Compact" if plan.get("prompt_mode") == "compact" else ""
    lines = [
        f"# SNAP Executable-Candidate{title_suffix} Prompt Plan",
        "",
        f"Evidence boundary: {plan['evidence_boundary']}",
        "",
        f"- Prompt mode: `{plan['prompt_mode']}`",
        "",
        "| Task | Condition | Prompt | Expected Script | Required Artifacts |",
        "| --- | --- | --- | --- | --- |",
    ]
    for packet in plan["packets"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    packet["task_id"],
                    packet["condition"],
                    packet["prompt_path"],
                    packet["expected_script_name"],
                    ", ".join(packet["required_artifacts"]),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "Use these prompt packets only to generate paired Summary/PaperToSkill candidate scripts for the executable-candidate runner.",
            "Provider latency, timeout, and retry counts remain availability metadata, not method-effectiveness metrics.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def build_plan(root: Path, output_dir: Path, *, mode: str = "full") -> dict[str, Any]:
    packets: list[dict[str, Any]] = []
    output_dir.mkdir(parents=True, exist_ok=True)
    for task_id in TASK_IDS:
        for condition in CONDITIONS:
            prompt, row = build_prompt(root, task_id, condition, mode=mode)
            prompt_path = output_dir / f"{task_id}_{condition}.md"
            prompt_path.write_text(prompt, encoding="utf-8")
            row["prompt_path"] = relative(root, prompt_path)
            packets.append(row)
    return {
        "schema_version": SCHEMA_VERSION,
        "purpose": (
            "Prepare future SNAP executable-candidate rerun prompt packets without calling a model."
            if mode == "full"
            else "Prepare compact SNAP executable-candidate prompt packets without calling a model."
        ),
        "prompt_mode": mode,
        "evidence_boundary": (
            "This is a local prompt-packet plan only. It does not execute model calls, "
            "does not score task outputs, does not append raw rows, and does not replace main rows."
        ),
        "compact_prompt_policy": (
            "Compact packets summarize context/assets deterministically and keep local paths/hashes visible; "
            "they are intended to reduce large-context provider 524 risk before any future paired rerun."
            if mode == "compact"
            else ""
        ),
        "runner": "scripts/run_real_reuse_snapatac2_executable_candidate.py",
        "model_default": "gpt-5.5 for non-ablation future model calls",
        "provider_policy": "Use generous timeout/retry budgets; provider timing is availability metadata.",
        "packets": packets,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=root_path())
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument("--mode", choices=("full", "compact"), default="full")
    parser.add_argument("--compact", action="store_true", help="Write compact prompt packets to compact default paths.")
    args = parser.parse_args()

    root = args.root.resolve()
    mode = "compact" if args.compact else args.mode
    if mode == "compact":
        if args.output_dir == DEFAULT_OUTPUT_DIR:
            args.output_dir = DEFAULT_COMPACT_OUTPUT_DIR
        if args.output_json == DEFAULT_OUTPUT_JSON:
            args.output_json = DEFAULT_COMPACT_OUTPUT_JSON
        if args.output_md == DEFAULT_OUTPUT_MD:
            args.output_md = DEFAULT_COMPACT_OUTPUT_MD
    output_dir = args.output_dir if args.output_dir.is_absolute() else root / args.output_dir
    plan = build_plan(root, output_dir, mode=mode)
    output_json = args.output_json if args.output_json.is_absolute() else root / args.output_json
    output_md = args.output_md if args.output_md.is_absolute() else root / args.output_md
    write_json(output_json, plan)
    write_markdown(output_md, plan)
    print(output_json)
    print(output_md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
