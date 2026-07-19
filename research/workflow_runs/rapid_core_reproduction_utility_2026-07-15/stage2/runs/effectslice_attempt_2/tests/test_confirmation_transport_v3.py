from __future__ import annotations

import json
import sys
from pathlib import Path


RUN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RUN_ROOT))
sys.path.insert(0, str(RUN_ROOT / "src"))

import confirmation_transport_v3 as transport  # noqa: E402


def registered_transport(request_function, sleep_function=lambda _seconds: None):
    return transport.ProviderTransport(
        base_url="https://api.deepseek.com",
        api_key="test-secret-key",
        model_alias="deepseek-v4-flash",
        wire_api="openai_chat_completions",
        max_tokens=8192,
        timeout_seconds=240.0,
        max_attempts=5,
        retry_delay_seconds=2.0,
        request_function=request_function,
        sleep_function=sleep_function,
    )


def response_payload(*, model="deepseek-v4-flash", response_id="resp-1"):
    return {
        "id": response_id,
        "model": model,
        "created": 1,
        "choices": [
            {"message": {"content": json.dumps({"action": "submit"})}}
        ],
        "usage": {"prompt_tokens": 11, "completion_tokens": 3},
    }


def test_direct_request_disables_environment_proxy_discovery(monkeypatch):
    captured = {}

    class Response:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def read(self, _limit):
            return json.dumps(response_payload()).encode("utf-8")

    class Opener:
        def open(self, request, *, timeout):
            captured["url"] = request.full_url
            captured["timeout"] = timeout
            return Response()

    def build_opener(handler):
        captured["proxies"] = handler.proxies
        return Opener()

    monkeypatch.setattr(transport.urllib.request, "build_opener", build_opener)
    status, payload = transport._direct_request_json(
        "https://api.deepseek.com/chat/completions",
        "test-secret-key",
        body={"model": "deepseek-v4-flash"},
        timeout_seconds=240.0,
    )

    assert status == 200
    assert payload["model"] == "deepseek-v4-flash"
    assert captured == {
        "proxies": {},
        "url": "https://api.deepseek.com/chat/completions",
        "timeout": 240.0,
    }


def test_public_config_freezes_endpoint_retry_and_proxy_policy():
    instance = registered_transport(lambda *_args, **_kwargs: (200, {}))

    assert instance.public_config() == {
        "base_url": "https://api.deepseek.com",
        "model_alias": "deepseek-v4-flash",
        "wire_api": "openai_chat_completions",
        "max_tokens": 8192,
        "timeout_seconds": 240.0,
        "max_attempts": 5,
        "retry_delay_seconds": 2.0,
        "temperature": 0,
        "direct_connection": True,
        "proxy_policy": "disabled",
    }
    assert "test-secret-key" not in json.dumps(instance.public_config())


def test_success_requires_registered_provider_identity():
    success = registered_transport(
        lambda *_args, **_kwargs: (200, response_payload())
    )(
        prompt="prompt",
        retry_lineage_id="lineage",
        turn_index=1,
    )
    mismatch = registered_transport(
        lambda *_args, **_kwargs: (
            200,
            response_payload(model="unexpected-model"),
        )
    )(
        prompt="prompt",
        retry_lineage_id="lineage",
        turn_index=1,
    )

    assert success.status == "success"
    assert success.provider_model_id == "deepseek-v4-flash"
    assert success.provider_response_id == "resp-1"
    assert mismatch.status == "error"
    assert mismatch.error_message == "provider_identity_mismatch"


def test_retryable_error_retries_same_registered_request():
    calls = []
    sleeps = []

    def request(*_args, **_kwargs):
        calls.append(1)
        if len(calls) == 1:
            raise RuntimeError('{"http_error":503}')
        return 200, response_payload(response_id="resp-retry")

    result = registered_transport(request, sleeps.append)(
        prompt="prompt",
        retry_lineage_id="lineage",
        turn_index=1,
    )

    assert result.status == "success"
    assert result.attempts == 2
    assert len(calls) == 2
    assert sleeps == [2.0]
