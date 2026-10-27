from __future__ import annotations

import re
from pathlib import Path

import httpx
import pytest

from adlib import DEFAULT_BASE_URL, AdLib, AdLibError, ResponseInfo, __version__

from .conftest import MockAPI, json_response


def test_auth_header_and_default_base_url(api: MockAPI) -> None:
    client = api.client(api_key="abc")
    assert client.base_url == DEFAULT_BASE_URL
    client.status()
    req = api.last
    assert str(req.url) == "https://api.adlibapi.com/v1/status"
    assert req.method == "GET"
    assert req.headers["x-api-key"] == "abc"
    assert req.headers["accept"] == "application/json"
    assert req.headers["user-agent"] == f"adlib-python/{__version__}"


def test_env_fallback_and_explicit_wins(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ADLIB_API_KEY", "env-key")
    monkeypatch.setenv("ADLIB_BASE_URL", "http://localhost:8080/")
    api = MockAPI()
    api.client(api_key=None).platforms()
    assert str(api.last.url) == "http://localhost:8080/v1/platforms"
    assert api.last.headers["x-api-key"] == "env-key"

    api.client(api_key="opt", base_url="http://other.test").platforms()
    assert api.last.headers["x-api-key"] == "opt"
    assert api.last.url.host == "other.test"


def test_missing_key_raises() -> None:
    with pytest.raises(AdLibError, match="ADLIB_API_KEY"):
        AdLib()
    with pytest.raises(AdLibError):
        AdLib(api_key="   ")


@pytest.mark.parametrize("url", ["https://h.test/", "https://h.test/v1", "https://h.test/v1/", " https://h.test// "])
def test_base_url_normalized(url: str) -> None:
    assert AdLib(api_key="k", base_url=url).base_url == "https://h.test"


def test_key_not_in_repr() -> None:
    client = AdLib(api_key="secret-key-123")
    assert "secret-key-123" not in repr(client)
    assert "secret-key-123" not in repr(client._config)


def test_invalid_max_retries() -> None:
    with pytest.raises(ValueError):
        AdLib(api_key="k", max_retries=-1)


def test_on_response_reports_billing_headers() -> None:
    infos: list = []
    api = MockAPI(
        json_response(
            {"data": [], "next_cursor": None, "meta": {}},
            headers={
                "X-Billing-Credits": "5",
                "X-Request-Id": "rid-9",
                "X-RateLimit-Limit": "120",
                "X-RateLimit-Remaining": "119",
                "X-RateLimit-Reset": "42",
            },
        )
    )
    api.client(on_response=infos.append).search(q="shoes")
    assert len(infos) == 1
    info: ResponseInfo = infos[0]
    assert info.billed_credits == 5
    assert info.request_id == "rid-9"
    assert info.rate_limit_limit == 120
    assert info.rate_limit_remaining == 119
    assert info.rate_limit_reset == 42
    assert info.method == "GET"
    assert info.status_code == 200


def test_204_returns_none() -> None:
    api = MockAPI(httpx.Response(204))
    assert api.client().watchlists.delete("wl-1") is None
    assert api.last.method == "DELETE"


def test_context_manager(api: MockAPI) -> None:
    with api.client() as client:
        client.status()


async def test_async_auth_header(api: MockAPI) -> None:
    async with api.async_client(api_key="abc") as client:
        await client.status()
    assert api.last.headers["x-api-key"] == "abc"


def test_version_matches_changelog() -> None:
    text = (Path(__file__).parent.parent / "CHANGELOG.md").read_text()
    assert re.search(rf"## \[{re.escape(__version__)}\]", text)
