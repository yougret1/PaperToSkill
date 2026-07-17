from __future__ import annotations

import ast
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

from .snap_mfse_cases import compare_embedding, generate_case, paper_reference_embedding
from .swe_scorer_bridge import ScorerEvaluation


class SnapMFSEScorerError(ValueError):
    """Raised when the SNAP-MFSE scorer is configured incorrectly."""


class _DenseSimilarityVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.violations: set[str] = set()

    @staticmethod
    def _name(node: ast.AST) -> str | None:
        return node.id if isinstance(node, ast.Name) else None

    @classmethod
    def _transpose_name(cls, node: ast.AST) -> str | None:
        if isinstance(node, ast.Attribute) and node.attr == "T":
            return cls._name(node.value)
        return None

    @staticmethod
    def _call_name(node: ast.Call) -> str | None:
        if isinstance(node.func, ast.Attribute):
            return node.func.attr
        if isinstance(node.func, ast.Name):
            return node.func.id
        return None

    def visit_BinOp(self, node: ast.BinOp) -> None:  # noqa: N802 - ast visitor API
        if isinstance(node.op, ast.MatMult):
            left_name = self._name(node.left)
            right_transpose = self._transpose_name(node.right)
            left_transpose = self._transpose_name(node.left)
            right_name = self._name(node.right)
            if (left_name and left_name == right_transpose) or (
                right_name and right_name == left_transpose
            ):
                self.violations.add("dense_similarity_matmul")
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:  # noqa: N802 - ast visitor API
        name = self._call_name(node)
        if name in {"dot", "matmul"} and len(node.args) >= 2:
            first_name = self._name(node.args[0])
            second_transpose = self._transpose_name(node.args[1])
            if first_name and first_name == second_transpose:
                self.violations.add("dense_similarity_call")
        if name in {"zeros", "ones", "empty", "full"} and node.args:
            shape = node.args[0]
            if isinstance(shape, (ast.Tuple, ast.List)) and len(shape.elts) == 2:
                if ast.dump(shape.elts[0]) == ast.dump(shape.elts[1]):
                    self.violations.add("dense_square_allocation")
        if name in {"eye", "identity"}:
            self.violations.add("dense_identity_allocation")
        self.generic_visit(node)


def matrix_free_guard_violations(source_text: str) -> list[str]:
    try:
        tree = ast.parse(source_text)
    except SyntaxError:
        return ["candidate_syntax_error"]
    visitor = _DenseSimilarityVisitor()
    visitor.visit(tree)
    return sorted(visitor.violations)


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
    module_name = f"snap_mfse_candidate_{uuid.uuid4().hex}"
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise SnapMFSEScorerError("candidate module cannot be loaded")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    try:
        spec.loader.exec_module(module)
    finally:
        sys.modules.pop(module_name, None)
    function = getattr(module, "matrix_free_spectral_embedding", None)
    if not callable(function):
        raise SnapMFSEScorerError("candidate function is missing")
    return function


def _contract_check(function) -> tuple[bool, list[str]]:
    valid = generate_case(
        {
            "case_id": "contract",
            "seed": 99_001,
            "n_cells": 8,
            "n_features": 12,
            "n_components": 2,
            "cluster_count": 2,
        }
    )
    invalid_calls = [
        (np.array([1.0, 2.0]), 1, "rank"),
        (np.array([[1.0, -1.0], [0.0, 1.0], [1.0, 0.0]]), 1, "negative"),
        (np.array([[1.0, np.nan], [0.0, 1.0], [1.0, 0.0]]), 1, "nonfinite"),
        (np.vstack([np.zeros(valid.shape[1]), valid[1:]]), 2, "zero_row"),
        (valid, 0, "zero_components"),
        (valid, valid.shape[0], "too_many_components"),
    ]
    failures = []
    for counts, components, label in invalid_calls:
        try:
            function(counts, components, random_state=0)
        except ValueError:
            continue
        except Exception:
            failures.append(f"{label}:wrong_exception")
        else:
            failures.append(f"{label}:accepted")
    return not failures, failures


def _base_metric(block: str) -> dict[str, Any]:
    return {
        "schema_version": "effectslice-snap-mfse-score.v1",
        "task_id": "SNAP-MFSE",
        "metric_name": "registered_case_pass_rate",
        "block": block,
        "evidence_boundary": (
            "Objective numerical score for one locked SNAP-MFSE patch and case block. "
            "Development scores do not establish EffectSlice effectiveness."
        ),
    }


def _public_summary(metric: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": "passed" if metric.get("success") else "failed",
        "task_score": metric.get("task_score", 0.0),
        "passed_cases": sum(metric.get("case_scores", [])),
        "total_cases": len(metric.get("case_scores", [])),
        "contract_passed": metric.get("contract_passed", False),
        "matrix_free_guard_passed": metric.get("matrix_free_guard_passed", False),
        "failure_reason": metric.get("failure_reason", "scorer_failure"),
    }


def score_snap_mfse_patch(
    *,
    diff_text: str,
    workspace: Path,
    case_registry_path: Path,
    block: str,
) -> dict[str, Any]:
    workspace = Path(workspace).resolve()
    registry_path = Path(case_registry_path).resolve()
    if not workspace.is_dir() or not (workspace / "snap_core.py").is_file():
        raise SnapMFSEScorerError("locked workspace is missing")
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    cases = registry.get("blocks", {}).get(block)
    if not isinstance(cases, list) or not cases:
        raise SnapMFSEScorerError("case block is missing or empty")
    base = _base_metric(block)

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
            metric = {
                **base,
                "task_score": 0.0,
                "success": False,
                "patch_applied": False,
                "matrix_free_guard_passed": False,
                "guard_violations": [],
                "contract_passed": False,
                "contract_failures": [],
                "case_scores": [0 for _ in cases],
                "case_details": [],
                "failure_reason": "patch_apply_failed",
                "private_apply_result": apply_result,
            }
            metric["public_summary"] = _public_summary(metric)
            return metric

        source_text = (candidate_root / "snap_core.py").read_text(encoding="utf-8")
        guard_violations = matrix_free_guard_violations(source_text)
        guard_passed = not guard_violations
        if not guard_passed:
            metric = {
                **base,
                "task_score": 0.0,
                "success": False,
                "patch_applied": True,
                "matrix_free_guard_passed": False,
                "guard_violations": guard_violations,
                "contract_passed": False,
                "contract_failures": [],
                "case_scores": [0 for _ in cases],
                "case_details": [],
                "failure_reason": "matrix_free_guard_failed",
                "private_apply_result": apply_result,
            }
            metric["public_summary"] = _public_summary(metric)
            return metric

        try:
            function = _load_candidate(candidate_root / "snap_core.py")
            contract_passed, contract_failures = _contract_check(function)
        except Exception as error:  # noqa: BLE001 - preserved only in private metric
            metric = {
                **base,
                "task_score": 0.0,
                "success": False,
                "patch_applied": True,
                "matrix_free_guard_passed": True,
                "guard_violations": [],
                "contract_passed": False,
                "contract_failures": [type(error).__name__],
                "case_scores": [0 for _ in cases],
                "case_details": [],
                "failure_reason": "candidate_load_or_contract_failed",
                "private_apply_result": apply_result,
            }
            metric["public_summary"] = _public_summary(metric)
            return metric

        case_scores = []
        case_details = []
        for case in cases:
            try:
                counts = generate_case(case)
                expected_values, expected_vectors = paper_reference_embedding(
                    counts, case["n_components"]
                )
                candidate_values, candidate_vectors = function(
                    counts.copy(),
                    case["n_components"],
                    random_state=case["seed"],
                )
                comparison = compare_embedding(
                    counts,
                    candidate_values,
                    candidate_vectors,
                    expected_values=expected_values,
                    expected_vectors=expected_vectors,
                )
                passed = bool(comparison["passed"])
                detail = {
                    "case_id": case["case_id"],
                    **comparison,
                    "error_type": None,
                }
            except Exception as error:  # noqa: BLE001 - private per-case classification
                passed = False
                detail = {
                    "case_id": case["case_id"],
                    "passed": False,
                    "error_type": type(error).__name__,
                }
            case_scores.append(1 if passed else 0)
            case_details.append(detail)

        task_score = sum(case_scores) / len(case_scores) if contract_passed else 0.0
        success = bool(contract_passed and all(case_scores))
        metric = {
            **base,
            "task_score": task_score,
            "success": success,
            "patch_applied": True,
            "matrix_free_guard_passed": True,
            "guard_violations": [],
            "contract_passed": contract_passed,
            "contract_failures": contract_failures,
            "case_scores": case_scores,
            "case_details": case_details,
            "failure_reason": "" if success else (
                "contract_failed" if not contract_passed else "numerical_case_failed"
            ),
            "private_apply_result": apply_result,
        }
        metric["public_summary"] = _public_summary(metric)
        return metric


class SnapMFSEScorerBridge:
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
            raise SnapMFSEScorerError("scorer inputs are missing")

    def evaluate(self, diff_text: str, *, evaluation_id: str) -> ScorerEvaluation:
        if not isinstance(diff_text, str) or not diff_text.strip():
            raise SnapMFSEScorerError("candidate diff must be nonempty")
        if not isinstance(evaluation_id, str) or not evaluation_id:
            raise SnapMFSEScorerError("evaluation_id must be nonempty")
        evaluation_dir = self._output_dir / evaluation_id
        evaluation_dir.mkdir(parents=True, exist_ok=True)
        patch_path = evaluation_dir / "candidate.patch"
        patch_path.write_text(diff_text, encoding="utf-8", newline="\n")
        metric = score_snap_mfse_patch(
            diff_text=diff_text,
            workspace=self._workspace,
            case_registry_path=self._case_registry_path,
            block=self._block,
        )
        feedback = json.dumps(
            metric["public_summary"],
            sort_keys=True,
            separators=(",", ":"),
        )
        return ScorerEvaluation(feedback, metric, patch_path)
