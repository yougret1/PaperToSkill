from __future__ import annotations

import hashlib
import json
import math
import time
from dataclasses import dataclass
from typing import Any

from .aci_protocol import (
    ACIAction,
    ACILoopState,
    ActionLimits,
    ActionProtocolError,
    parse_action,
)
from .aci_workspace import OverlayWorkspace, WorkspaceError


DEFAULT_COMMON_SCAFFOLD = """You are operating a bounded software-engineering interface.
Return exactly one JSON object per turn and no narrative or code fence.
Allowed actions:
- {"action":"search","query":"literal","path":".","max_results":10}
- {"action":"open","path":"relative/file.py","start_line":1,"end_line":80}
- {"action":"edit","path":"relative/file.py","old_text":"exact text","new_text":"replacement"}
- {"action":"test"}
- {"action":"submit"}
Paths must be relative. Search and open before editing. Use test feedback when
available. Submit only after producing the smallest justified source patch.
"""


class RunnerConfigurationError(ValueError):
    """Raised when a runner or transport result violates its contract."""


@dataclass(frozen=True, slots=True)
class ModelTurnResult:
    status: str
    response_text: str | None
    attempts: int
    input_tokens: int
    output_tokens: int
    error_message: str = ""
    provider_model_id: str = ""
    provider_response_id: str = ""
    provider_created: int | None = None

    def __post_init__(self) -> None:
        if self.status not in {"success", "error"}:
            raise RunnerConfigurationError("model turn status must be success or error")
        for value, name, minimum in (
            (self.attempts, "attempts", 1),
            (self.input_tokens, "input_tokens", 0),
            (self.output_tokens, "output_tokens", 0),
        ):
            if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
                raise RunnerConfigurationError(f"{name} must be an integer >= {minimum}")
        if self.status == "success":
            if not isinstance(self.response_text, str) or not self.response_text.strip():
                raise RunnerConfigurationError("successful turn requires response_text")
            if self.error_message:
                raise RunnerConfigurationError("successful turn cannot contain error_message")
        else:
            if self.response_text is not None:
                raise RunnerConfigurationError("error turn cannot contain response_text")
            if not isinstance(self.error_message, str) or not self.error_message:
                raise RunnerConfigurationError("error turn requires error_message")
        for value, name in (
            (self.provider_model_id, "provider_model_id"),
            (self.provider_response_id, "provider_response_id"),
        ):
            if not isinstance(value, str):
                raise RunnerConfigurationError(f"{name} must be a string")
        if self.provider_created is not None and (
            isinstance(self.provider_created, bool)
            or not isinstance(self.provider_created, int)
            or self.provider_created < 0
        ):
            raise RunnerConfigurationError("provider_created must be a nonnegative integer")


@dataclass(frozen=True, slots=True)
class ACITranscriptEntry:
    step: int
    retry_lineage_id: str
    prompt_sha256: str
    response_sha256: str
    response_text: str
    action: ACIAction | None
    observation_status: str
    observation_message: str
    transport_attempts: int
    input_tokens: int
    output_tokens: int
    provider_model_id: str
    provider_response_id: str
    provider_created: int | None


@dataclass(frozen=True, slots=True)
class ACIRunResult:
    status: str
    terminal_reason: str
    submitted: bool
    task_score: float | None
    success: bool | None
    diff_text: str
    state: ACILoopState
    turns: tuple[ACITranscriptEntry, ...]
    scorer_metrics: tuple[dict[str, Any], ...]
    input_tokens: int
    output_tokens: int
    transport_attempts: int
    elapsed_seconds: float
    common_scaffold_sha256: str
    condition_context_sha256: str
    task_prompt_sha256: str
    private_score_policy: str
    private_score_count: int
    private_feedback_exposed: bool
    public_error: str = ""


class InteractiveACIRunner:
    """Run a frozen JSON-action ACI loop over a read-only overlay workspace."""

    _INVALID_ACTION_MESSAGE = (
        "return exactly one JSON action matching the frozen schema"
    )

    def __init__(
        self,
        *,
        workspace: OverlayWorkspace,
        scorer_bridge: Any,
        model_transport: Any,
        common_scaffold: str,
        condition_context: str,
        task_prompt: str,
        action_limits: ActionLimits,
        max_actions: int,
        max_response_chars: int,
        max_observation_chars: int,
        score_final_state_on_exhaustion: bool = False,
        private_score_policy: str = "interactive",
    ) -> None:
        if not isinstance(workspace, OverlayWorkspace):
            raise RunnerConfigurationError("workspace must be an OverlayWorkspace")
        if not callable(getattr(scorer_bridge, "evaluate", None)):
            raise RunnerConfigurationError("scorer_bridge must provide evaluate")
        if not callable(model_transport):
            raise RunnerConfigurationError("model_transport must be callable")
        for value, name in (
            (common_scaffold, "common_scaffold"),
            (condition_context, "condition_context"),
            (task_prompt, "task_prompt"),
        ):
            if not isinstance(value, str) or not value.strip():
                raise RunnerConfigurationError(f"{name} must be a non-empty string")
        if not isinstance(action_limits, ActionLimits):
            raise RunnerConfigurationError("action_limits must be ActionLimits")
        if not isinstance(score_final_state_on_exhaustion, bool):
            raise RunnerConfigurationError(
                "score_final_state_on_exhaustion must be boolean"
            )
        if private_score_policy not in {"interactive", "final_only"}:
            raise RunnerConfigurationError(
                "private_score_policy must be interactive or final_only"
            )
        for value, name in (
            (max_actions, "max_actions"),
            (max_response_chars, "max_response_chars"),
            (max_observation_chars, "max_observation_chars"),
        ):
            if isinstance(value, bool) or not isinstance(value, int) or value < 1:
                raise RunnerConfigurationError(f"{name} must be a positive integer")
        self._workspace = workspace
        self._scorer_bridge = scorer_bridge
        self._model_transport = model_transport
        self._common_scaffold = common_scaffold.strip()
        self._condition_context = condition_context.strip()
        self._task_prompt = task_prompt.strip()
        self._action_limits = action_limits
        self._max_actions = max_actions
        self._max_response_chars = max_response_chars
        self._max_observation_chars = max_observation_chars
        self._score_final_state_on_exhaustion = score_final_state_on_exhaustion
        self._private_score_policy = private_score_policy

    def run(self, *, retry_lineage_prefix: str) -> ACIRunResult:
        if not isinstance(retry_lineage_prefix, str) or not retry_lineage_prefix:
            raise RunnerConfigurationError("retry_lineage_prefix must be non-empty")
        state = ACILoopState(max_actions=self._max_actions)
        turns: list[ACITranscriptEntry] = []
        scorer_metrics: list[dict[str, Any]] = []
        input_tokens = 0
        output_tokens = 0
        transport_attempts = 0
        started = time.perf_counter()

        while state.remaining_actions:
            turn_index = len(turns) + 1
            retry_lineage_id = f"{retry_lineage_prefix}:turn-{turn_index:03d}"
            prompt = self._build_prompt(turns)
            prompt_sha256 = _sha256(prompt)
            try:
                model_turn = self._model_transport(
                    prompt=prompt,
                    retry_lineage_id=retry_lineage_id,
                    turn_index=turn_index,
                )
            except Exception:  # noqa: BLE001 - provider details stay model-hidden
                return self._finish(
                    status="error",
                    terminal_reason="provider_error",
                    submitted=False,
                    task_score=None,
                    success=None,
                    state=state,
                    turns=turns,
                    scorer_metrics=scorer_metrics,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    transport_attempts=transport_attempts,
                    started=started,
                    public_error="provider_error",
                )
            if not isinstance(model_turn, ModelTurnResult):
                raise RunnerConfigurationError("model_transport must return ModelTurnResult")
            input_tokens += model_turn.input_tokens
            output_tokens += model_turn.output_tokens
            transport_attempts += model_turn.attempts
            if model_turn.status == "error":
                turns.append(
                    self._entry(
                        step=state.actions_used + 1,
                        retry_lineage_id=retry_lineage_id,
                        prompt_sha256=prompt_sha256,
                        model_turn=model_turn,
                        action=None,
                        observation_status="provider_error",
                        observation_message="provider_error",
                    )
                )
                return self._finish(
                    status="error",
                    terminal_reason="provider_error",
                    submitted=False,
                    task_score=None,
                    success=None,
                    state=state,
                    turns=turns,
                    scorer_metrics=scorer_metrics,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    transport_attempts=transport_attempts,
                    started=started,
                    public_error="provider_error",
                )

            response_text = model_turn.response_text or ""
            if len(response_text) > self._max_response_chars:
                action = None
                observation_status = "invalid_action"
                observation_message = self._INVALID_ACTION_MESSAGE
            else:
                try:
                    action = parse_action(response_text, self._action_limits)
                except ActionProtocolError:
                    action = None
                    observation_status = "invalid_action"
                    observation_message = self._INVALID_ACTION_MESSAGE
                else:
                    observation_status, observation_message = "", ""

            if action is None:
                state = state.consume(
                    action=None,
                    status=observation_status,
                    message=observation_message,
                )
                turns.append(
                    self._entry(
                        step=state.actions_used,
                        retry_lineage_id=retry_lineage_id,
                        prompt_sha256=prompt_sha256,
                        model_turn=model_turn,
                        action=None,
                        observation_status=observation_status,
                        observation_message=observation_message,
                    )
                )
                continue

            step = state.actions_used + 1
            if action.action == "submit":
                diff_text = self._workspace.unified_diff()
                if not diff_text:
                    observation_status = "rejected"
                    observation_message = "submit requires a non-empty source diff"
                    state = state.consume(
                        action=action,
                        status=observation_status,
                        message=observation_message,
                    )
                    turns.append(
                        self._entry(
                            step=step,
                            retry_lineage_id=retry_lineage_id,
                            prompt_sha256=prompt_sha256,
                            model_turn=model_turn,
                            action=action,
                            observation_status=observation_status,
                            observation_message=observation_message,
                        )
                    )
                    return self._finish(
                        status="failed",
                        terminal_reason="submitted_without_changes",
                        submitted=True,
                        task_score=0.0,
                        success=False,
                        state=state,
                        turns=turns,
                        scorer_metrics=scorer_metrics,
                        input_tokens=input_tokens,
                        output_tokens=output_tokens,
                        transport_attempts=transport_attempts,
                        started=started,
                    )
                evaluation = self._score(
                    diff_text,
                    evaluation_id=f"submit-{step:02d}",
                )
                if evaluation is None:
                    state = state.consume(
                        action=action,
                        status="scorer_error",
                        message="scorer_error",
                    )
                    turns.append(
                        self._entry(
                            step=step,
                            retry_lineage_id=retry_lineage_id,
                            prompt_sha256=prompt_sha256,
                            model_turn=model_turn,
                            action=action,
                            observation_status="scorer_error",
                            observation_message="scorer_error",
                        )
                    )
                    return self._scorer_error(
                        state=state,
                        turns=turns,
                        scorer_metrics=scorer_metrics,
                        input_tokens=input_tokens,
                        output_tokens=output_tokens,
                        transport_attempts=transport_attempts,
                        started=started,
                    )
                scorer_metrics.append(evaluation.metric)
                observation_status = "scored"
                observation_message = self._cap(evaluation.model_feedback)
                state = state.consume(
                    action=action,
                    status=observation_status,
                    message=observation_message,
                )
                turns.append(
                    self._entry(
                        step=step,
                        retry_lineage_id=retry_lineage_id,
                        prompt_sha256=prompt_sha256,
                        model_turn=model_turn,
                        action=action,
                        observation_status=observation_status,
                        observation_message=observation_message,
                    )
                )
                return self._finish(
                    status="scored",
                    terminal_reason="submitted",
                    submitted=True,
                    task_score=float(evaluation.metric["task_score"]),
                    success=bool(evaluation.metric["success"]),
                    state=state,
                    turns=turns,
                    scorer_metrics=scorer_metrics,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    transport_attempts=transport_attempts,
                    started=started,
                )

            try:
                observation_status, observation_message, metric = self._execute_action(
                    action,
                    step=step,
                )
            except Exception:  # noqa: BLE001 - unexpected scorer details stay hidden
                state = state.consume(
                    action=action,
                    status="scorer_error",
                    message="scorer_error",
                )
                turns.append(
                    self._entry(
                        step=step,
                        retry_lineage_id=retry_lineage_id,
                        prompt_sha256=prompt_sha256,
                        model_turn=model_turn,
                        action=action,
                        observation_status="scorer_error",
                        observation_message="scorer_error",
                    )
                )
                return self._scorer_error(
                    state=state,
                    turns=turns,
                    scorer_metrics=scorer_metrics,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    transport_attempts=transport_attempts,
                    started=started,
                )
            if metric is not None:
                scorer_metrics.append(metric)
            observation_message = self._cap(observation_message)
            state = state.consume(
                action=action,
                status=observation_status,
                message=observation_message,
            )
            turns.append(
                self._entry(
                    step=step,
                    retry_lineage_id=retry_lineage_id,
                    prompt_sha256=prompt_sha256,
                    model_turn=model_turn,
                    action=action,
                    observation_status=observation_status,
                    observation_message=observation_message,
                )
            )

        exhausted_after_scored_test = bool(
            turns
            and turns[-1].action is not None
            and turns[-1].action.action == "test"
            and turns[-1].observation_status == "scored"
            and scorer_metrics
        )
        latest_metric = scorer_metrics[-1] if exhausted_after_scored_test else None
        terminal_reason = (
            "action_budget_exhausted_after_scored_test"
            if latest_metric is not None
            else "action_budget_exhausted"
        )
        if self._score_final_state_on_exhaustion:
            diff_text = self._workspace.unified_diff()
            if diff_text:
                evaluation = self._score(diff_text, evaluation_id="budget-final")
                if evaluation is None:
                    return self._scorer_error(
                        state=state,
                        turns=turns,
                        scorer_metrics=scorer_metrics,
                        input_tokens=input_tokens,
                        output_tokens=output_tokens,
                        transport_attempts=transport_attempts,
                        started=started,
                    )
                scorer_metrics.append(evaluation.metric)
                latest_metric = evaluation.metric
                terminal_reason = "action_budget_exhausted_after_final_score"
        return self._finish(
            status="scored" if latest_metric is not None else "failed",
            terminal_reason=terminal_reason,
            submitted=False,
            task_score=float(latest_metric["task_score"]) if latest_metric is not None else 0.0,
            success=bool(latest_metric["success"]) if latest_metric is not None else False,
            state=state,
            turns=turns,
            scorer_metrics=scorer_metrics,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            transport_attempts=transport_attempts,
            started=started,
        )

    def _execute_action(
        self,
        action: ACIAction,
        *,
        step: int,
    ) -> tuple[str, str, dict[str, Any] | None]:
        try:
            if action.action == "search":
                hits = self._workspace.search(
                    action.query or "",
                    relative_dir=action.path or ".",
                )[: action.max_results]
                message = "\n".join(
                    f"{hit.path}:{hit.line_number}: {hit.text}" for hit in hits
                ) or "no matches"
                return "ok", message, None
            if action.action == "open":
                lines = self._workspace.open_lines(
                    action.path or "",
                    action.start_line or 0,
                    action.end_line or 0,
                )
                message = "\n".join(
                    f"{number}: {line}"
                    for number, line in enumerate(lines, start=action.start_line or 1)
                ) or "empty line window"
                return "ok", message, None
            if action.action == "edit":
                result = self._workspace.replace_exact(
                    action.path or "",
                    action.old_text or "",
                    action.new_text or "",
                )
                return (
                    "ok",
                    json.dumps(
                        {
                            "changed": result.changed,
                            "path": result.path,
                            "replacements": result.replacements,
                        },
                        sort_keys=True,
                        separators=(",", ":"),
                    ),
                    None,
                )
            if action.action == "test":
                if self._private_score_policy == "final_only":
                    return (
                        "unavailable",
                        "private scoring is unavailable before final submission",
                        None,
                    )
                diff_text = self._workspace.unified_diff()
                if not diff_text:
                    return "rejected", "test requires a non-empty source diff", None
                evaluation = self._score(diff_text, evaluation_id=f"step-{step:02d}")
                if evaluation is None:
                    raise RunnerConfigurationError("scorer evaluation failed")
                return "scored", evaluation.model_feedback, evaluation.metric
        except WorkspaceError as error:
            return "workspace_error", str(error), None
        raise RunnerConfigurationError(f"unhandled action: {action.action}")

    def _score(self, diff_text: str, *, evaluation_id: str):
        try:
            return self._scorer_bridge.evaluate(
                diff_text,
                evaluation_id=evaluation_id,
            )
        except Exception:  # noqa: BLE001 - scorer-only paths stay private
            return None

    def _build_prompt(self, turns: list[ACITranscriptEntry]) -> str:
        parts = [
            "# Common ACI Contract",
            self._common_scaffold,
            "# Action Horizon",
            (
                f"Total action budget: {self._max_actions}. "
                f"Actions remaining before this turn: {self._max_actions - len(turns)}."
            ),
            "# Condition Context",
            self._condition_context,
            "# Locked Task",
            self._task_prompt,
        ]
        if self._private_score_policy == "final_only":
            parts.extend(
                [
                    "# Private Score Policy",
                    (
                        "Private scoring is final-only. Do not use the test action; it "
                        "cannot reveal a score. Submit the fixed patch when ready."
                    ),
                ]
            )
        if turns:
            parts.append("# Prior Interaction")
            for turn in turns:
                parts.extend(
                    [
                        f"## Step {turn.step} Model Action",
                        turn.response_text,
                        f"## Step {turn.step} Tool Observation ({turn.observation_status})",
                        turn.observation_message,
                    ]
                )
        parts.extend(
            [
                "# Next Action",
                "Return exactly one JSON action matching the common ACI contract.",
            ]
        )
        return "\n\n".join(parts).strip() + "\n"

    def _entry(
        self,
        *,
        step: int,
        retry_lineage_id: str,
        prompt_sha256: str,
        model_turn: ModelTurnResult,
        action: ACIAction | None,
        observation_status: str,
        observation_message: str,
    ) -> ACITranscriptEntry:
        response_text = model_turn.response_text or ""
        return ACITranscriptEntry(
            step=step,
            retry_lineage_id=retry_lineage_id,
            prompt_sha256=prompt_sha256,
            response_sha256=_sha256(response_text),
            response_text=response_text[: self._max_response_chars],
            action=action,
            observation_status=observation_status,
            observation_message=self._cap(observation_message),
            transport_attempts=model_turn.attempts,
            input_tokens=model_turn.input_tokens,
            output_tokens=model_turn.output_tokens,
            provider_model_id=model_turn.provider_model_id,
            provider_response_id=model_turn.provider_response_id,
            provider_created=model_turn.provider_created,
        )

    def _cap(self, text: str) -> str:
        if len(text) <= self._max_observation_chars:
            return text
        suffix = "...[truncated]"
        return text[: self._max_observation_chars - len(suffix)] + suffix

    def _scorer_error(
        self,
        *,
        state: ACILoopState,
        turns: list[ACITranscriptEntry],
        scorer_metrics: list[dict[str, Any]],
        input_tokens: int,
        output_tokens: int,
        transport_attempts: int,
        started: float,
    ) -> ACIRunResult:
        return self._finish(
            status="error",
            terminal_reason="scorer_error",
            submitted=False,
            task_score=None,
            success=None,
            state=state,
            turns=turns,
            scorer_metrics=scorer_metrics,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            transport_attempts=transport_attempts,
            started=started,
            public_error="scorer_error",
        )

    def _finish(
        self,
        *,
        status: str,
        terminal_reason: str,
        submitted: bool,
        task_score: float | None,
        success: bool | None,
        state: ACILoopState,
        turns: list[ACITranscriptEntry],
        scorer_metrics: list[dict[str, Any]],
        input_tokens: int,
        output_tokens: int,
        transport_attempts: int,
        started: float,
        public_error: str = "",
    ) -> ACIRunResult:
        return ACIRunResult(
            status=status,
            terminal_reason=terminal_reason,
            submitted=submitted,
            task_score=task_score,
            success=success,
            diff_text=self._workspace.unified_diff(),
            state=state,
            turns=tuple(turns),
            scorer_metrics=tuple(scorer_metrics),
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            transport_attempts=transport_attempts,
            elapsed_seconds=round(time.perf_counter() - started, 6),
            common_scaffold_sha256=_sha256(self._common_scaffold),
            condition_context_sha256=_sha256(self._condition_context),
            task_prompt_sha256=_sha256(self._task_prompt),
            private_score_policy=self._private_score_policy,
            private_score_count=len(scorer_metrics),
            private_feedback_exposed=any(
                turn.action is not None
                and turn.action.action == "test"
                and turn.observation_status == "scored"
                for turn in turns
            ),
            public_error=public_error,
        )


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
