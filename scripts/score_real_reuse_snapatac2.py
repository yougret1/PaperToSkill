#!/usr/bin/env python
"""Score locked SnapATAC2 real-reuse analysis artifacts."""

from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "0.1"
TASK_IDS = ("SNAP-T1", "SNAP-T2")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def artifact_path(artifact_dir: Path) -> Path:
    for name in ("candidate_output.json", "analysis_artifacts.json", "metric.json"):
        path = artifact_dir / name
        if path.exists():
            return path
    raise ValueError(f"missing candidate_output.json in {artifact_dir}")


def slot_path(manifest: dict[str, Any], slot: str, root: Path) -> Path | None:
    for item in manifest.get("files", []):
        if item.get("slot") == slot:
            path = Path(str(item["path"]))
            return path if path.is_absolute() else root / path
    return None


def load_budget(manifest: dict[str, Any] | None, root: Path) -> dict[str, Any]:
    if manifest:
        path = slot_path(manifest, "resource_budget", root)
        if path and path.exists():
            return load_json(path)
    return {"max_runtime_seconds": 1800, "max_peak_memory_mb": 8192}


def comb2(value: int) -> float:
    return value * (value - 1) / 2


def adjusted_rand_index(labels_true: list[Any], labels_pred: list[Any]) -> float:
    if len(labels_true) != len(labels_pred) or not labels_true:
        return 0.0
    contingency = Counter(zip(labels_true, labels_pred))
    true_counts = Counter(labels_true)
    pred_counts = Counter(labels_pred)
    sum_comb = sum(comb2(count) for count in contingency.values())
    sum_true = sum(comb2(count) for count in true_counts.values())
    sum_pred = sum(comb2(count) for count in pred_counts.values())
    total = comb2(len(labels_true))
    if total == 0:
        return 1.0
    expected = sum_true * sum_pred / total
    maximum = (sum_true + sum_pred) / 2
    denom = maximum - expected
    return 1.0 if denom == 0 else max(-1.0, min(1.0, (sum_comb - expected) / denom))


def normalized_mutual_info(labels_true: list[Any], labels_pred: list[Any]) -> float:
    if len(labels_true) != len(labels_pred) or not labels_true:
        return 0.0
    total = len(labels_true)
    true_counts = Counter(labels_true)
    pred_counts = Counter(labels_pred)
    joint_counts = Counter(zip(labels_true, labels_pred))

    def entropy(counts: Counter[Any]) -> float:
        value = 0.0
        for count in counts.values():
            p = count / total
            value -= p * math.log(p)
        return value

    mutual_info = 0.0
    for (true_label, pred_label), count in joint_counts.items():
        pxy = count / total
        px = true_counts[true_label] / total
        py = pred_counts[pred_label] / total
        mutual_info += pxy * math.log(pxy / (px * py))
    denom = (entropy(true_counts) + entropy(pred_counts)) / 2
    return 1.0 if denom == 0 else max(0.0, min(1.0, mutual_info / denom))


def as_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if value is None:
        return []
    return [value]


def has_artifacts(candidate: dict[str, Any], task_id: str) -> bool:
    key = "embedding_artifacts" if task_id == "SNAP-T1" else "clustering_artifacts"
    artifacts = candidate.get(key)
    if isinstance(artifacts, list):
        return len(artifacts) > 0
    if isinstance(artifacts, dict):
        return bool(artifacts)
    return bool(artifacts)


def has_method_alignment(candidate: dict[str, Any]) -> bool:
    text = json.dumps(candidate.get("method_steps", candidate), ensure_ascii=False).lower()
    required = ["snapatac2", "spectral", "embedding"]
    return sum(1 for item in required if item in text) >= 2


def resource_score(candidate: dict[str, Any], budget: dict[str, Any]) -> tuple[float, dict[str, Any]]:
    runtime = candidate.get("runtime_seconds")
    memory = candidate.get("peak_memory_mb")
    runtime_ok = isinstance(runtime, (int, float)) and runtime >= 0 and runtime <= float(budget.get("max_runtime_seconds", 1800))
    memory_ok = isinstance(memory, (int, float)) and memory >= 0 and memory <= float(budget.get("max_peak_memory_mb", 8192))
    return (int(runtime_ok) + int(memory_ok)) / 2, {
        "runtime_seconds": runtime,
        "peak_memory_mb": memory,
        "runtime_ok": runtime_ok,
        "memory_ok": memory_ok,
    }


def quality_score(candidate: dict[str, Any], reference_labels: list[Any] | None) -> tuple[float, dict[str, Any]]:
    metrics = candidate.get("quality_metrics", {})
    if not isinstance(metrics, dict):
        metrics = {}
    predicted = as_list(candidate.get("predicted_labels"))
    if reference_labels and predicted:
        ari = adjusted_rand_index(reference_labels, predicted)
        nmi = normalized_mutual_info(reference_labels, predicted)
        return (max(0.0, ari) + nmi) / 2, {"ari": ari, "nmi": nmi, "source": "computed_from_reference_labels"}
    for key in ("ari", "nmi", "proxy_quality_score", "silhouette", "embedding_quality"):
        value = metrics.get(key)
        if isinstance(value, (int, float)):
            return max(0.0, min(1.0, float(value))), {"source": f"reported_{key}", key: value}
    return 0.0, {"source": "missing_quality_metric"}


def reference_labels_from_manifest(manifest: dict[str, Any] | None, root: Path) -> list[Any] | None:
    if not manifest:
        return None
    path = slot_path(manifest, "reference_labels_or_proxy", root)
    if not path or not path.exists():
        return None
    payload = load_json(path)
    labels = payload.get("labels", payload.get("reference_labels"))
    return as_list(labels) if labels is not None else None


def score_candidate(task_id: str, candidate: dict[str, Any], budget: dict[str, Any], reference_labels: list[Any] | None) -> dict[str, Any]:
    completed = candidate.get("completed") is True
    artifacts = has_artifacts(candidate, task_id)
    method = has_method_alignment(candidate)
    resource, resource_detail = resource_score(candidate, budget)
    components: dict[str, float] = {
        "completed": 1.0 if completed else 0.0,
        "artifacts": 1.0 if artifacts else 0.0,
        "resource": resource,
        "method_alignment": 1.0 if method else 0.0,
    }
    quality_detail: dict[str, Any] | None = None
    if task_id == "SNAP-T2":
        quality, quality_detail = quality_score(candidate, reference_labels)
        components["quality"] = quality
    score = round(sum(components.values()) / len(components), 3)
    return {
        "schema_version": SCHEMA_VERSION,
        "task_id": task_id,
        "metric_name": "runtime_memory_quality" if task_id == "SNAP-T1" else "ari_nmi_runtime_memory",
        "task_score": score,
        "success": score >= 0.8,
        "components": components,
        "resource_detail": resource_detail,
        "quality_detail": quality_detail,
        "failure_reason": "" if score >= 0.8 else "missing_required_artifacts_or_metrics",
        "evidence_boundary": (
            "Objective local scoring for one locked SnapATAC2 output. This "
            "does not compare Summary and PaperToSkill or claim aggregate "
            "downstream effectiveness."
        ),
    }


def score_artifact(task_id: str, artifact_dir: Path, asset_manifest: Path | None = None, root: Path | None = None) -> dict[str, Any]:
    root = (root or Path.cwd()).resolve()
    manifest = load_json(asset_manifest) if asset_manifest and asset_manifest.exists() else None
    try:
        candidate = load_json(artifact_path(artifact_dir))
    except (ValueError, json.JSONDecodeError) as exc:
        return {
            "schema_version": SCHEMA_VERSION,
            "task_id": task_id,
            "metric_name": "runtime_memory_quality" if task_id == "SNAP-T1" else "ari_nmi_runtime_memory",
            "task_score": 0.0,
            "success": False,
            "failure_reason": str(exc),
            "components": {},
        }
    budget = load_budget(manifest, root)
    labels = reference_labels_from_manifest(manifest, root)
    result = score_candidate(task_id, candidate, budget, labels)
    result["artifact_dir"] = artifact_dir.as_posix()
    result["asset_manifest"] = asset_manifest.as_posix() if asset_manifest else ""
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Score locked SnapATAC2 real-reuse outputs.")
    parser.add_argument("--task", choices=TASK_IDS, required=True)
    parser.add_argument("--artifact-dir", type=Path, required=True)
    parser.add_argument("--asset-manifest", type=Path)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output-json", type=Path)
    args = parser.parse_args()

    result = score_artifact(args.task, args.artifact_dir, args.asset_manifest, args.root)
    if args.output_json:
        write_json(args.output_json, result)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
