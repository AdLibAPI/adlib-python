from __future__ import annotations

import json
from typing import Any, Callable, List, Optional, Union

import httpx
import pytest

from adlib import AdLib, AsyncAdLib

Reply = Union[httpx.Response, Exception, Callable[[httpx.Request], httpx.Response]]


def json_response(data: Any, status: int = 200, headers: Optional[dict] = None) -> httpx.Response:
    return httpx.Response(status, content=json.dumps(data).encode(), headers=headers or {})


def api_error(status: int, code: str, message: str = "boom", headers: Optional[dict] = None) -> httpx.Response:
    return json_response(
        {"error": {"code": code, "message": message, "request_id": "req-1", "billed": False}},
        status,
        headers,
    )


def page(ids: List[str], next_cursor: Optional[str]) -> httpx.Response:
    return json_response(
        {
            "data": [{"id": i} for i in ids],
            "next_cursor": next_cursor,
            "meta": {"count": len(ids), "cached": False, "source": "live"},
        }
    )


class MockAPI:
    """Records requests and answers them from a queue (the last reply repeats)."""

    def __init__(self, *replies: Reply) -> None:
        self.replies: List[Reply] = list(replies) or [json_response({"ok": True})]
        self.requests: List[httpx.Request] = []
        self.sleeps: List[float] = []

    def handler(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        reply = self.replies.pop(0) if len(self.replies) > 1 else self.replies[0]
        if isinstance(reply, Exception):
            raise reply
        if callable(reply):
            return reply(request)
        return reply

    @property
    def last(self) -> httpx.Request:
        return self.requests[-1]

    def client(self, **kwargs: Any) -> AdLib:
        kwargs.setdefault("api_key", "test-key")
        client = AdLib(http_client=httpx.Client(transport=httpx.MockTransport(self.handler)), **kwargs)
        client._sleep = self.sleeps.append
        return client

    def async_client(self, **kwargs: Any) -> AsyncAdLib:
        kwargs.setdefault("api_key", "test-key")
        client = AsyncAdLib(
            http_client=httpx.AsyncClient(transport=httpx.MockTransport(self.handler)), **kwargs
        )

        async def fake_sleep(seconds: float) -> None:
            self.sleeps.append(seconds)

        client._sleep = fake_sleep
        return client


def body(request: httpx.Request) -> Any:
    return json.loads(request.content)


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in ("ADLIB_API_KEY", "ADLIB_BASE_URL"):
        monkeypatch.delenv(name, raising=False)


@pytest.fixture
def api() -> MockAPI:
    return MockAPI()
