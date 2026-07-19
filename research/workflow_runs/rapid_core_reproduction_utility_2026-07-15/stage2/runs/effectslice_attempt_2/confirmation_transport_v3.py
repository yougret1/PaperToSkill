"""Bound direct-HTTPS transport for the EffectSlice confirmation-v3 run."""

from __future__ import annotations

import json
import math
import re
import time
import urllib.error
import urllib.request
from typing import Any, Callable

from effectslice.aci_runner import ModelTurnResult


REGISTERED_BASE_URL = "https://api.deepseek.com"
REGISTERED_MODEL_ALIAS = "deepseek-v4-flash"
REGISTERED_WIRE_API = "openai_chat_completions"
REGISTERED_MAX_TOKENS = 8192
REGISTERED_TIMEOUT_SECONDS = 240.0
REGISTERED_MAX_ATTEMPTS = 5
REGISTERED_RETRY_DELAY_SECONDS = 2.0
REGISTERED_PROXY_POLICY = "disabled"
MAX_RESPONSE_BYTES = 2_000_000


class ConfirmationTransportError(ValueError):
    """Raised when the registered confirmation transport is misconfigured."""


def _require_exact(value: Any, expected: Any, label: str) -> None:
    if type(value) is not type(expected) or value != expected:
        raise ConfirmationTransportError(f"{label} must be {expected!r}")


def _direct_request_json(
    url: str,
    api_key: str,
    method: str = "POST",
    body: dict[str, Any] | None = None,
    *,
    extra_headers: dict[str, str] | None = None,
    timeout_seconds: float = REGISTERED_TIMEOUT_SECONDS,
) -> tuple[int, dict[str, Any]]:
    """Issue one HTTPS request with all environment proxy discovery disabled."""
    if not isinstance(url, str) or not url.startswith("https://"):
        raise RuntimeError("provider_transport_error")
    if not isinstance(api_key, str) or not api_key:
        raise RuntimeError("provider_transport_error")
    data = None if body is None else json.dumps(body).encode("utf-8")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    if extra_headers:
        headers.update(extra_headers)
    request = urllib.request.Request(
        url, data=data, headers=headers, method=method
    )
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    try:
        with opener.open(request, timeout=timeout_seconds) as response:
            payload = response.read(MAX_RESPONSE_BYTES + 1)
            if len(payload) > MAX_RESPONSE_BYTES:
                raise RuntimeError("provider_response_too_large")
            decoded = payload.decode("utf-8")
            parsed = json.loads(decoded) if decoded else {}
            if not isinstance(parsed, dict):
                raise RuntimeError("invalid_provider_json")
            return int(response.status), parsed
    except urllib.error.HTTPError as exc:
        raise RuntimeError(
            json.dumps({"http_error": int(exc.code)}, separators=(",", ":"))
        ) from None
    except RuntimeError:
        raise
    except Exception as exc:
        raise RuntimeError("provider_transport_error") from exc


def _is_retryable_error(message: str) -> bool:
    match = re.search(r'"?http_error"?\s*:\s*(\d{3})', message)
    if not match:
        return True
    return int(match.group(1)) in {429, 502, 503, 504}


def _extract_content(response: dict[str, Any]) -> str:
    choices = response.get("choices") if isinstance(response, dict) else None
    if not isinstance(choices, list) or not choices:
        return ""
    first = choices[0]
    if not isinstance(first, dict):
        return ""
    message = first.get("message")
    if not isinstance(message, dict):
        return ""
    content = message.get("content")
    return content if isinstance(content, str) else ""


def _safe_token_count(value: Any) -> int:
    return (
        value
        if isinstance(value, int) and not isinstance(value, bool) and value >= 0
        else 0
    )


def _normalize_usage(response: dict[str, Any]) -> tuple[int, int]:
    usage = response.get("usage", {}) if isinstance(response, dict) else {}
    if not isinstance(usage, dict):
        return 0, 0
    return (
        _safe_token_count(usage.get("prompt_tokens", 0)),
        _safe_token_count(usage.get("completion_tokens", 0)),
    )


class ProviderTransport:
    """Stateless registered Chat Completions transport with bounded retries."""

    def __init__(
        self,
        *,
        base_url: str,
        api_key: str,
        model_alias: str,
        wire_api: str,
        max_tokens: int,
        timeout_seconds: float,
        max_attempts: int,
        retry_delay_seconds: float,
        request_function: Callable[..., tuple[int, dict[str, Any]]] | None = None,
        sleep_function: Callable[[float], None] = time.sleep,
    ) -> None:
        if not isinstance(base_url, str):
            raise ConfirmationTransportError("base_url must be a string")
        _require_exact(
            base_url.rstrip("/"), REGISTERED_BASE_URL, "base_url"
        )
        if not isinstance(api_key, str) or not api_key:
            raise ConfirmationTransportError("api_key must be nonempty")
        _require_exact(model_alias, REGISTERED_MODEL_ALIAS, "model_alias")
        _require_exact(wire_api, REGISTERED_WIRE_API, "wire_api")
        _require_exact(max_tokens, REGISTERED_MAX_TOKENS, "max_tokens")
        _require_exact(
            float(timeout_seconds),
            REGISTERED_TIMEOUT_SECONDS,
            "timeout_seconds",
        )
        _require_exact(max_attempts, REGISTERED_MAX_ATTEMPTS, "max_attempts")
        _require_exact(
            float(retry_delay_seconds),
            REGISTERED_RETRY_DELAY_SECONDS,
            "retry_delay_seconds",
        )
        if not math.isfinite(float(timeout_seconds)):
            raise ConfirmationTransportError("timeout_seconds must be finite")
        if not math.isfinite(float(retry_delay_seconds)):
            raise ConfirmationTransportError(
                "retry_delay_seconds must be finite"
            )
        if request_function is not None and not callable(request_function):
            raise ConfirmationTransportError("request_function must be callable")
        if not callable(sleep_function):
            raise ConfirmationTransportError("sleep_function must be callable")
        self._base_url = REGISTERED_BASE_URL
        self._api_key = api_key
        self._model_alias = REGISTERED_MODEL_ALIAS
        self._max_tokens = REGISTERED_MAX_TOKENS
        self._timeout_seconds = REGISTERED_TIMEOUT_SECONDS
        self._max_attempts = REGISTERED_MAX_ATTEMPTS
        self._retry_delay_seconds = REGISTERED_RETRY_DELAY_SECONDS
        self._request_function = request_function or _direct_request_json
        self._sleep_function = sleep_function

    def public_config(self) -> dict[str, Any]:
        return {
            "base_url": self._base_url,
            "model_alias": self._model_alias,
            "wire_api": REGISTERED_WIRE_API,
            "max_tokens": self._max_tokens,
            "timeout_seconds": self._timeout_seconds,
            "max_attempts": self._max_attempts,
            "retry_delay_seconds": self._retry_delay_seconds,
            "temperature": 0,
            "direct_connection": True,
            "proxy_policy": REGISTERED_PROXY_POLICY,
        }

    def __call__(
        self,
        *,
        prompt: str,
        retry_lineage_id: str,
        turn_index: int,
    ) -> ModelTurnResult:
        del retry_lineage_id, turn_index
        body = {
            "model": self._model_alias,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Follow the bounded ACI contract and return one JSON "
                        "action only."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0,
            "max_tokens": self._max_tokens,
        }
        endpoint = f"{self._base_url}/chat/completions"
        input_tokens = 0
        output_tokens = 0
        last_error = "retryable_provider_error_exhausted"
        for attempt in range(1, self._max_attempts + 1):
            try:
                _, response = self._request_function(
                    endpoint,
                    self._api_key,
                    method="POST",
                    body=body,
                    extra_headers=None,
                    timeout_seconds=self._timeout_seconds,
                )
            except RuntimeError as exc:
                if not _is_retryable_error(str(exc)):
                    return ModelTurnResult(
                        status="error",
                        response_text=None,
                        attempts=attempt,
                        input_tokens=input_tokens,
                        output_tokens=output_tokens,
                        error_message="deterministic_provider_error",
                    )
            except Exception:
                pass
            else:
                attempt_input, attempt_output = _normalize_usage(response)
                input_tokens += attempt_input
                output_tokens += attempt_output
                content = _extract_content(response).strip()
                model_id = response.get("model")
                response_id = response.get("id")
                if content and (
                    model_id != self._model_alias
                    or not isinstance(response_id, str)
                    or not response_id
                ):
                    return ModelTurnResult(
                        status="error",
                        response_text=None,
                        attempts=attempt,
                        input_tokens=input_tokens,
                        output_tokens=output_tokens,
                        error_message="provider_identity_mismatch",
                    )
                if content:
                    created = response.get("created")
                    return ModelTurnResult(
                        status="success",
                        response_text=content,
                        attempts=attempt,
                        input_tokens=input_tokens,
                        output_tokens=output_tokens,
                        provider_model_id=model_id,
                        provider_response_id=response_id,
                        provider_created=(
                            created
                            if isinstance(created, int)
                            and not isinstance(created, bool)
                            and created >= 0
                            else None
                        ),
                    )
                last_error = "empty_response_content"
            if attempt < self._max_attempts:
                self._sleep_function(self._retry_delay_seconds)
        return ModelTurnResult(
            status="error",
            response_text=None,
            attempts=self._max_attempts,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            error_message=last_error,
        )
