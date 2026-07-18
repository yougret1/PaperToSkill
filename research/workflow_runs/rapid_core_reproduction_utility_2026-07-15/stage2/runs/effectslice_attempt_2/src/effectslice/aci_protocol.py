from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any


class ActionProtocolError(ValueError):
    """Raised when a model response violates the frozen ACI action contract."""


class ActionBudgetExhausted(ActionProtocolError):
    """Raised when another observation would exceed the action budget."""


@dataclass(frozen=True, slots=True)
class ActionLimits:
    max_query_chars: int = 200
    max_path_chars: int = 512
    max_edit_chars: int = 20_000
    max_open_lines: int = 200
    max_search_results: int = 20

    def __post_init__(self) -> None:
        for name in (
            "max_query_chars",
            "max_path_chars",
            "max_edit_chars",
            "max_open_lines",
            "max_search_results",
        ):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value < 1:
                raise ActionProtocolError(f"{name} must be a positive integer")


@dataclass(frozen=True, slots=True)
class ACIAction:
    action: str
    query: str | None = None
    path: str | None = None
    max_results: int | None = None
    start_line: int | None = None
    end_line: int | None = None
    old_text: str | None = None
    new_text: str | None = None


@dataclass(frozen=True, slots=True)
class ACIObservation:
    step: int
    action: ACIAction | None
    status: str
    message: str


@dataclass(frozen=True, slots=True)
class ACILoopState:
    max_actions: int
    observations: tuple[ACIObservation, ...] = ()

    def __post_init__(self) -> None:
        if (
            isinstance(self.max_actions, bool)
            or not isinstance(self.max_actions, int)
            or self.max_actions < 1
        ):
            raise ActionProtocolError("max_actions must be a positive integer")
        if not isinstance(self.observations, tuple) or any(
            not isinstance(item, ACIObservation) for item in self.observations
        ):
            raise ActionProtocolError("observations must be ACIObservation records")
        if len(self.observations) > self.max_actions:
            raise ActionProtocolError("observations exceed max_actions")

    @property
    def actions_used(self) -> int:
        return len(self.observations)

    @property
    def remaining_actions(self) -> int:
        return self.max_actions - self.actions_used

    def consume(
        self,
        *,
        action: ACIAction | None,
        status: str,
        message: str,
    ) -> "ACILoopState":
        if self.remaining_actions == 0:
            raise ActionBudgetExhausted("action budget exhausted")
        if action is not None and not isinstance(action, ACIAction):
            raise ActionProtocolError("action must be an ACIAction or None")
        for value, name in ((status, "status"), (message, "message")):
            if not isinstance(value, str) or not value:
                raise ActionProtocolError(f"{name} must be a non-empty string")
        observation = ACIObservation(
            step=self.actions_used + 1,
            action=action,
            status=status,
            message=message,
        )
        return ACILoopState(
            max_actions=self.max_actions,
            observations=(*self.observations, observation),
        )


_FENCED_JSON = re.compile(
    r"\s*```(?:json)?\s*(\{.*\})\s*```\s*",
    flags=re.IGNORECASE | re.DOTALL,
)


def parse_action(response_text: str, limits: ActionLimits | None = None) -> ACIAction:
    if not isinstance(response_text, str) or not response_text.strip():
        raise ActionProtocolError("model response must contain one JSON object")
    active_limits = limits or ActionLimits()
    match = _FENCED_JSON.fullmatch(response_text)
    raw_json = match.group(1) if match else response_text.strip()
    try:
        payload = json.loads(raw_json, object_pairs_hook=_unique_object)
    except (json.JSONDecodeError, TypeError) as error:
        raise ActionProtocolError("model response is not exactly one JSON object") from error
    if not isinstance(payload, dict):
        raise ActionProtocolError("action payload must be a JSON object")
    return _validate_payload(payload, active_limits)


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    for key, value in pairs:
        if key in payload:
            raise ActionProtocolError(f"duplicate JSON field: {key}")
        payload[key] = value
    return payload


def _validate_payload(payload: dict[str, Any], limits: ActionLimits) -> ACIAction:
    action = payload.get("action")
    if not isinstance(action, str) or action not in {
        "search",
        "open",
        "edit",
        "test",
        "submit",
    }:
        raise ActionProtocolError("unknown or missing action")

    if action == "search":
        _check_fields(
            payload,
            required={"action", "query"},
            optional={"path", "max_results"},
        )
        query = _bounded_text(
            payload["query"],
            name="query",
            maximum=limits.max_query_chars,
            allow_empty=False,
        )
        path = _bounded_text(
            payload.get("path", "."),
            name="path",
            maximum=limits.max_path_chars,
            allow_empty=False,
        )
        max_results = payload.get("max_results", limits.max_search_results)
        _bounded_integer(
            max_results,
            name="max_results",
            minimum=1,
            maximum=limits.max_search_results,
        )
        return ACIAction(
            action="search",
            query=query,
            path=path,
            max_results=max_results,
        )

    if action == "open":
        _check_fields(
            payload,
            required={"action", "path", "start_line", "end_line"},
        )
        path = _bounded_text(
            payload["path"],
            name="path",
            maximum=limits.max_path_chars,
            allow_empty=False,
        )
        start_line = payload["start_line"]
        end_line = payload["end_line"]
        _bounded_integer(start_line, name="start_line", minimum=1)
        _bounded_integer(end_line, name="end_line", minimum=start_line)
        if end_line - start_line + 1 > limits.max_open_lines:
            raise ActionProtocolError("open line window exceeds max_open_lines")
        return ACIAction(
            action="open",
            path=path,
            start_line=start_line,
            end_line=end_line,
        )

    if action == "edit":
        _check_fields(
            payload,
            required={"action", "path", "old_text", "new_text"},
        )
        return ACIAction(
            action="edit",
            path=_bounded_text(
                payload["path"],
                name="path",
                maximum=limits.max_path_chars,
                allow_empty=False,
            ),
            old_text=_bounded_text(
                payload["old_text"],
                name="old_text",
                maximum=limits.max_edit_chars,
                allow_empty=False,
            ),
            new_text=_bounded_text(
                payload["new_text"],
                name="new_text",
                maximum=limits.max_edit_chars,
                allow_empty=True,
            ),
        )

    _check_fields(payload, required={"action"})
    return ACIAction(action=action)


def _check_fields(
    payload: dict[str, Any],
    *,
    required: set[str],
    optional: set[str] | None = None,
) -> None:
    allowed = required | (optional or set())
    missing = required - payload.keys()
    extra = payload.keys() - allowed
    if missing or extra:
        details = []
        if missing:
            details.append(f"missing fields: {', '.join(sorted(missing))}")
        if extra:
            details.append(f"extra fields: {', '.join(sorted(extra))}")
        raise ActionProtocolError("; ".join(details))


def _bounded_text(
    value: Any,
    *,
    name: str,
    maximum: int,
    allow_empty: bool,
) -> str:
    if not isinstance(value, str):
        raise ActionProtocolError(f"{name} must be a string")
    if not allow_empty and not value:
        raise ActionProtocolError(f"{name} must be non-empty")
    if "\x00" in value:
        raise ActionProtocolError(f"{name} cannot contain NUL")
    if len(value) > maximum:
        raise ActionProtocolError(f"{name} exceeds its character limit")
    return value


def _bounded_integer(
    value: Any,
    *,
    name: str,
    minimum: int,
    maximum: int | None = None,
) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ActionProtocolError(f"{name} must be an integer")
    if value < minimum or (maximum is not None and value > maximum):
        raise ActionProtocolError(f"{name} is outside the allowed range")
