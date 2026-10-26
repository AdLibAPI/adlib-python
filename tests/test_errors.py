from __future__ import annotations

import httpx
import pytest

from adlib import (
    AdLibError,
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    InsufficientCreditsError,
    NotFoundError,
    PermissionDeniedError,
    QuotaExceededError,
    RateLimitError,
    ServerError,
    ValidationError,
)

from .conftest import MockAPI, api_error, json_response


def test_parses_api_error_shape() -> None:
    api = MockAPI(api_error(404, "not_found", "advertiser meta:1 not found"))
    with pytest.raises(NotFoundError) as info:
        api.client().advertisers.get("meta:1")
    err = info.value
    assert isinstance(err, APIStatusError) and isinstance(err, AdLibError)
    assert err.status_code == 404
    assert err.code == "not_found"
    assert err.message == "advertiser meta:1 not found"
    assert err.request_id == "req-1"
    assert err.billed is False
    assert str(err) == "advertiser meta:1 not found (HTTP 404, not_found, request_id req-1)"


@pytest.mark.parametrize(
    "status,code,cls",
    [
        (400, "bad_request", ValidationError),
        (422, "unsupported", ValidationError),
        (401, "unauthorized", AuthenticationError),
        (402, "payment_required", InsufficientCreditsError),
        (403, "forbidden", PermissionDeniedError),
        (404, "not_found", NotFoundError),
        (429, "rate_limited", RateLimitError),
        (429, "quota_exceeded", QuotaExceededError),
        (500, "internal", ServerError),
        (418, "teapot", APIStatusError),
    ],
)
def test_status_mapping(status: int, code: str, cls: type) -> None:
    api = MockAPI(api_error(status, code))
    with pytest.raises(cls) as info:
        api.client(max_retries=0).status()
    assert info.value.code == code


def test_rate_limited_is_not_quota() -> None:
    api = MockAPI(api_error(429, "rate_limited", headers={"Retry-After": "7"}))
    with pytest.raises(RateLimitError) as info:
        api.client(max_retries=0).status()
    assert not isinstance(info.value, QuotaExceededError)
    assert info.value.retry_after == 7.0


def test_platform_details_and_header_request_id() -> None:
    api = MockAPI(
        json_response(
            {"error": {"code": "upstream_error", "message": "meta failed", "platform": "meta", "details": ["x"], "billed": False}},
            502,
            {"X-Request-Id": "hdr-id"},
        )
    )
    with pytest.raises(ServerError) as info:
        api.client(max_retries=0).status()
    assert info.value.platform == "meta"
    assert info.value.details == ["x"]
    assert info.value.request_id == "hdr-id"


def test_plain_text_and_empty_bodies() -> None:
    api = MockAPI(httpx.Response(400, content=b"bad thing"))
    with pytest.raises(ValidationError, match="bad thing"):
        api.client().status()
    api = MockAPI(httpx.Response(401))
    with pytest.raises(AuthenticationError, match="Check your API key"):
        api.client().status()


def test_non_json_success() -> None:
    api = MockAPI(httpx.Response(200, content=b"<html>"))
    with pytest.raises(AdLibError, match="Expected a JSON response"):
        api.client().status()


def test_connection_and_timeout_errors() -> None:
    with pytest.raises(APIConnectionError):
        MockAPI(httpx.ConnectError("refused")).client(max_retries=0).status()
    with pytest.raises(APITimeoutError):
        MockAPI(httpx.ReadTimeout("slow")).client(max_retries=0).status()


def test_arguments_validated_before_sending(api: MockAPI) -> None:
    client = api.client()
    bad = [
        lambda: client.ads.get("1234"),
        lambda: client.search(),
        lambda: client.search(q="a", domain="b.com"),
        lambda: client.search(q="a", limit=101),
        lambda: client.search(q="a", status="nope"),  # type: ignore[arg-type]
        lambda: client.advertisers.resolve(""),
        lambda: client.advertisers.changes("meta:1", since=""),
        lambda: client.advertisers.changes("meta:1", since="2026-01-01", types=["bogus"]),  # type: ignore[list-item]
        lambda: client.watchlists.create(advertisers=[]),
        lambda: client.watchlists.create(advertisers=["nike"]),
        lambda: client.watchlists.create(advertisers="meta:1"),  # type: ignore[arg-type]
        lambda: client.watchlists.create(advertisers=["meta:1"], interval_hours=169),
        lambda: client.batch.create(type="ads", items=[]),
        lambda: client.batch.create(type="bogus", items=["x"]),  # type: ignore[arg-type]
        lambda: client.batch.create(type="advertisers", items=["meta:1"], options={"max_pages": 21}),
        lambda: client.webhooks.delivery("abc"),
        lambda: client.usage(days=93),
    ]
    for call in bad:
        with pytest.raises(ValueError):
            call()
    assert api.requests == []
