from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path
from typing import Any

import numpy as np

from .swe_scorer_bridge import ScorerEvaluation
from .toolformer_filter_cases import paper_filter_api_calls


class ToolformerFilterScorerError(ValueError):
    """Raised when the Toolformer filter scorer is configured incorrectly."""


def _patch_targets_only_task_file(diff_text: str) -> bool:
    headers = []
    for line in diff_text.splitlines():
        if not line.startswith(("--- ", "+++ ")):
            continue
        path = line[4:].split("\t", 1)[0]
        if path.startswith(("a/", "b/")):
            path = path[2:]
        headers.append(path.replace("\\", "/"))
    return len(headers) >= 2 and all(path == "toolformer_filter.py" for path in headers)


def _run_git_apply(patch_path: Path, cwd: Path) -> dict[str, Any]:
    completed = subprocess.run(
        [
            "git",
            "apply",
            "--recount",
            "--whitespace=nowarn",
            "--ignore-space-change",
            str(patch_path),
        ],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )
    return {
        "returncode": completed.returncode,
        "stdout": completed.stdout[-2000:],
        "stderr": completed.stderr[-2000:],
    }


def _load_candidate(module_path: Path):
    module_name = f"toolformer_filter_candidate_{uuid.uuid4().hex}"
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise ToolformerFilterScorerError("candidate module cannot be loaded")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    try:
        spec.loader.exec_module(module)
    finally:
        sys.modules.pop(module_name, None)
    function = getattr(module, "filter_api_calls", None)
    if not callable(function):
        raise ToolformerFilterScorerError("candidate function is missing")
    return function


def _validate_result(result: Any, n_candidates: int) -> tuple[np.ndarray, np.ndarray]:
    if not isinstance(result, tuple) or len(result) != 2:
        raise ToolformerFilterScorerError("candidate must return a two-item tuple")
    keep, margins = result
    if not isinstance(keep, np.ndarray) or keep.shape != (n_candidates,):
        raise ToolformerFilterScorerError("keep mask has the wrong shape or type")
    if keep.dtype != np.bool_:
        raise ToolformerFilterScorerError("keep mask must have Boolean dtype")
    if not isinstance(margins, np.ndarray) or margins.shape != (n_candidates,):
        raise ToolformerFilterScorerError("margins have the wrong shape or type")
    if not np.issubdtype(margins.dtype, np.floating) or not np.isfinite(margins).all():
        raise ToolformerFilterScorerError("margins must be finite floating values")
    return keep, margins.astype(np.float64, copy=False)


def _contract_check(function) -> tuple[bool, list[str]]:
    valid = np.array([[-1.0, -1.5], [-2.0, -1.0]], dtype=np.float64)
    failures = []
    try:
        _validate_result(function(valid, valid - 0.5, valid - 1.0, 0.1), 2)
    except Exception as error:  # noqa: BLE001 - private contract classification
        failures.append(f"valid:{type(error).__name__}")

    invalid_calls = [
        (np.array([-1.0, -2.0]), valid, valid, 0.1, "rank"),
        (np.empty((0, 2)), valid, valid, 0.1, "empty"),
        (valid, valid[:, :1], valid, 0.1, "shape"),
        (np.array([[-1.0, np.nan], [-2.0, -1.0]]), valid, valid, 0.1, "nonfinite"),
        (np.array([[-1.0, 0.1], [-2.0, -1.0]]), valid, valid, 0.1, "positive"),
        (valid, valid, valid, -0.1, "negative_threshold"),
        (valid, valid, valid, True, "boolean_threshold"),
    ]
    for with_result, call_only, no_call, tau, label in invalid_calls:
        try:
            function(with_result, call_only, no_call, tau)
        except ValueError:
            continue
        except Exception:
            failures.append(f"{label}:wrong_exception")
        else:
            failures.append(f"{label}:accepted")
    return not failures, failures


def _base_metric(block: str) -> dict[str, Any]:
    return {
        "schema_version": "effectslice-toolformer-filter-score.v1",
        "task_id": "TOOLFORMER-FILTER",
        "metric_name": "registered_case_pass_rate",
        "block": block,
        "evidence_boundary": (
            "Objective numerical score for one locked Toolformer filter patch and "
            "case block. Development scores are not general EffectSlice evidence."
        ),
    }


def _public_summary(metric: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": "passed" if metric.get("success") else "failed",
        "task_score": metric.get("task_score", 0.0),
        "passed_cases": sum(metric.get("case_scores", [])),
        "total_cases": len(metric.get("case_scores", [])),
        "contract_passed": metric.get("contract_passed", False),
        "failure_reason": metric.get("failure_reason", "scorer_failure"),
    }


def _failed_metric(
    *,
    base: dict[str, Any],
    cases: list[dict[str, Any]],
    reason: str,
    patch_applied: bool,
    contract_failures: list[str] | None = None,
    private_apply_result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    metric = {
        **base,
        "task_score": 0.0,
        "success": False,
        "patch_applied": patch_applied,
        "contract_passed": False,
        "contract_failures": contract_failures or [],
        "case_scores": [0 for _ in cases],
        "case_details": [],
        "failure_reason": reason,
        "private_apply_result": private_apply_result or {},
    }
    metric["public_summary"] = _public_summary(metric)
    return metric


def score_toolformer_filter_patch(
    *,
    diff_text: str,
    workspace: Path,
    case_registry_path: Path,
    block: str,
) -> dict[str, Any]:
    workspace = Path(workspace).resolve()
    registry_path = Path(case_registry_path).resolve()
    if not workspace.is_dir() or not (workspace / "toolformer_filter.py").is_file():
        raise ToolformerFilterScorerError("locked workspace is missing")
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    cases = registry.get("blocks", {}).get(block)
    if not isinstance(cases, list) or not cases:
        raise ToolformerFilterScorerError("case block is missing or empty")
    base = _base_metric(block)
    if not _patch_targets_only_task_file(diff_text):
        return _failed_metric(
            base=base,
            cases=cases,
            reason="patch_apply_failed",
            patch_applied=False,
        )

    with tempfile.TemporaryDirectory() as temporary:
        temporary_root = Path(temporary)
        candidate_root = temporary_root / "workspace"
        shutil.copytree(
            workspace,
            candidate_root,
            ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache", ".git"),
        )
        patch_path = temporary_root / "candidate.patch"
        patch_path.write_text(diff_text, encoding="utf-8", newline="\n")
        apply_result = _run_git_apply(patch_path, candidate_root)
        if apply_result["returncode"] != 0:
            return _failed_metric(
                base=base,
                cases=cases,
                reason="patch_apply_failed",
                patch_applied=False,
                private_apply_result=apply_result,
            )

        try:
            function = _load_candidate(candidate_root / "toolformer_filter.py")
            contract_passed, contract_failures = _contract_check(function)
        except Exception as error:  # noqa: BLE001 - private failure classification
            return _failed_metric(
                base=base,
                cases=cases,
                reason="candidate_load_or_contract_failed",
                patch_applied=True,
                contract_failures=[type(error).__name__],
                private_apply_result=apply_result,
            )
        if not contract_passed:
            return _failed_metric(
                base=base,
                cases=cases,
                reason="candidate_load_or_contract_failed",
                patch_applied=True,
                contract_failures=contract_failures,
                private_apply_result=apply_result,
            )

        case_scores = []
        case_details = []
        for case in cases:
            try:
                arrays = [
                    np.asarray(case[key], dtype=np.float64)
                    for key in (
                        "logp_with_result",
                        "logp_call_only",
                        "logp_no_call",
                    )
                ]
                expected_keep, expected_margins = paper_filter_api_calls(
                    *arrays, case["tau_filter"]
                )
                candidate_keep, candidate_margins = _validate_result(
                    function(*(array.copy() for array in arrays), case["tau_filter"]),
                    arrays[0].shape[0],
                )
                keep_match = bool(np.array_equal(candidate_keep, expected_keep))
                margin_match = bool(
                    np.allclose(
                        candidate_margins,
                        expected_margins,
                        rtol=1e-10,
                        atol=1e-12,
                    )
                )
                passed = keep_match and margin_match
                detail = {
                    "case_id": case["case_id"],
                    "passed": passed,
                    "keep_match": keep_match,
                    "margin_match": margin_match,
                    "max_abs_margin_error": float(
                        np.max(np.abs(candidate_margins - expected_margins))
                    ),
                    "error_type": None,
                }
            except Exception as error:  # noqa: BLE001 - private case classification
                passed = False
                detail = {
                    "case_id": case["case_id"],
                    "passed": False,
                    "error_type": type(error).__name__,
                }
            case_scores.append(1 if passed else 0)
            case_details.append(detail)

        task_score = sum(case_scores) / len(case_scores)
        success = bool(all(case_scores))
        metric = {
            **base,
            "task_score": task_score,
            "success": success,
            "patch_applied": True,
            "contract_passed": True,
            "contract_failures": [],
            "case_scores": case_scores,
            "case_details": case_details,
            "failure_reason": "" if success else "numerical_case_failed",
            "private_apply_result": apply_result,
        }
        metric["public_summary"] = _public_summary(metric)
        return metric


class ToolformerFilterScorerBridge:
    def __init__(
        self,
        *,
        workspace: Path,
        case_registry_path: Path,
        block: str,
        output_dir: Path,
    ) -> None:
        self._workspace = Path(workspace).resolve()
        self._case_registry_path = Path(case_registry_path).resolve()
        self._block = block
        self._output_dir = Path(output_dir).resolve()
        if not self._workspace.is_dir() or not self._case_registry_path.is_file():
            raise ToolformerFilterScorerError("scorer inputs are missing")

    def evaluate(self, diff_text: str, *, evaluation_id: str) -> ScorerEvaluation:
        if not isinstance(diff_text, str) or not diff_text.strip():
            raise ToolformerFilterScorerError("candidate diff must be nonempty")
        if not isinstance(evaluation_id, str) or not evaluation_id:
            raise ToolformerFilterScorerError("evaluation_id must be nonempty")
        evaluation_dir = self._output_dir / evaluation_id
        evaluation_dir.mkdir(parents=True, exist_ok=True)
        patch_path = evaluation_dir / "candidate.patch"
        patch_path.write_text(diff_text, encoding="utf-8", newline="\n")
        metric = score_toolformer_filter_patch(
            diff_text=diff_text,
            workspace=self._workspace,
            case_registry_path=self._case_registry_path,
            block=self._block,
        )
        feedback = json.dumps(
            metric["public_summary"], sort_keys=True, separators=(",", ":")
        )
        return ScorerEvaluation(feedback, metric, patch_path)
