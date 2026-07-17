from __future__ import annotations

import copy
import json
import math
import re
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class ScorerBridgeError(ValueError):
    """Raised when scorer bridge configuration or input is invalid."""


@dataclass(frozen=True, slots=True)
class ScorerEvaluation:
    model_feedback: str
    metric: dict[str, Any]
    patch_path: Path


class SWEScorerBridge:
    """Materialize a candidate diff and keep scorer-only data model-hidden."""

    _EVALUATION_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}")
    _REQUIRED_METRIC_FIELDS = frozenset(
        {
            "task_score",
            "success",
            "patch_applied",
            "test_passed",
            "failure_reason",
        }
    )
    _MODEL_VISIBLE_FAILURE_REASONS = frozenset(
        {
            "",
            "patch_apply_failed",
            "test_command_failed",
            "test_patch_apply_failed",
        }
    )

    def __init__(
        self,
        *,
        task_id: str,
        workspace: str | Path,
        test_command: str,
        test_patch_path: str | Path | None,
        output_dir: str | Path,
        timeout_seconds: float,
        score_function: Callable[..., dict[str, Any]],
    ) -> None:
        if task_id not in {"SWE-T1", "SWE-T2"}:
            raise ScorerBridgeError("unsupported SWE task_id")
        self._task_id = task_id
        self._workspace = Path(workspace).resolve()
        if not self._workspace.is_dir():
            raise ScorerBridgeError("workspace does not exist or is not a directory")
        if not isinstance(test_command, str) or not test_command.strip():
            raise ScorerBridgeError("test_command must be a non-empty string")
        self._test_command = test_command.strip()
        if test_patch_path is None:
            self._test_patch_path = None
        else:
            self._test_patch_path = Path(test_patch_path).resolve()
            if not self._test_patch_path.is_file():
                raise ScorerBridgeError("test_patch_path does not exist or is not a file")
        self._output_dir = Path(output_dir).resolve()
        if (
            isinstance(timeout_seconds, bool)
            or not isinstance(timeout_seconds, (int, float))
            or not math.isfinite(float(timeout_seconds))
            or timeout_seconds <= 0
        ):
            raise ScorerBridgeError("timeout_seconds must be finite and positive")
        self._timeout_seconds = float(timeout_seconds)
        if not callable(score_function):
            raise ScorerBridgeError("score_function must be callable")
        self._score_function = score_function

    def evaluate(self, diff_text: str, *, evaluation_id: str) -> ScorerEvaluation:
        if not isinstance(diff_text, str) or not diff_text.strip():
            raise ScorerBridgeError("candidate diff must be a non-empty string")
        if not isinstance(evaluation_id, str) or not self._EVALUATION_ID.fullmatch(
            evaluation_id
        ):
            raise ScorerBridgeError("evaluation_id is not a safe bounded identifier")

        patch_path = self._output_dir / evaluation_id / "candidate.patch"
        patch_path.parent.mkdir(parents=True, exist_ok=True)
        normalized_diff = diff_text.rstrip("\r\n") + "\n"
        patch_path.write_text(normalized_diff, encoding="utf-8")
        raw_metric = self._score_function(
            task_id=self._task_id,
            patch_path=patch_path,
            workspace=self._workspace,
            test_command=self._test_command,
            timeout_seconds=self._timeout_seconds,
            test_patch_path=self._test_patch_path,
        )
        if not isinstance(raw_metric, dict):
            raise ScorerBridgeError("score_function must return a metric object")
        missing = self._REQUIRED_METRIC_FIELDS - raw_metric.keys()
        if missing:
            raise ScorerBridgeError(
                f"scorer metric missing fields: {', '.join(sorted(missing))}"
            )
        metric = copy.deepcopy(raw_metric)
        task_score = metric["task_score"]
        if (
            isinstance(task_score, bool)
            or not isinstance(task_score, (int, float))
            or not math.isfinite(float(task_score))
            or not 0.0 <= float(task_score) <= 1.0
        ):
            raise ScorerBridgeError("task_score must be finite and within [0, 1]")
        for field in ("success", "patch_applied", "test_passed"):
            if not isinstance(metric[field], bool):
                raise ScorerBridgeError(f"{field} must be boolean")
        failure_reason = metric["failure_reason"]
        if not isinstance(failure_reason, str):
            raise ScorerBridgeError("failure_reason must be a string")
        visible_failure_reason = (
            failure_reason
            if failure_reason in self._MODEL_VISIBLE_FAILURE_REASONS
            else "scorer_failure"
        )
        feedback = {
            "failure_reason": visible_failure_reason,
            "patch_applied": metric["patch_applied"],
            "status": "passed" if metric["success"] else "failed",
            "task_score": float(task_score),
            "test_passed": metric["test_passed"],
        }
        return ScorerEvaluation(
            model_feedback=json.dumps(
                feedback,
                ensure_ascii=True,
                sort_keys=True,
                separators=(",", ":"),
            ),
            metric=metric,
            patch_path=patch_path,
        )
