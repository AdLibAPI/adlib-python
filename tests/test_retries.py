from __future__ import annotations

import httpx
import pytest

from adlib import (
    APIConnectionError,
    APITimeoutError,
    QuotaExceededError,
    ServerError,
    ValidationError,
)
from adlib._base import MAX_RETRY_AFTER, retry_delay

from .conftest import MockAPI, api_error, json_response


def ok() -> httpx.Response:
    return json_response({"status": "operational"})


def test_retries_429_and_honours_retry_after() -> None:
    api = MockAPI(api_error(429, "rate_limited", headers={"Retry-After": "3"}), ok())
    assert api.client().status() == {"status": "operational"}
    assert len(api.requests) == 2
    assert api.sleeps == [3.0]


@pytest.mark.parametrize("status", [502, 503, 504])
def test_retries_gateway_errors_with_backoff(status: int) -> None:
    api = MockAPI(api_error(status, "upstream"), api_error(status, "upstream"), ok())
    assert api.client().status() == {"status": "operational"}
    assert len(api.requests) == 3
    assert 0.5 <= api.sleeps[0] <= 0.625
    assert 1.0 <= api.sleeps[1] <= 1.25


def test_no_retry_for_500() -> None:
    api = MockAPI(api_error(500, "internal"), ok())
    with pytest.raises(ServerError):
        api.client().status()
    assert len(api.requests) == 1


def test_gives_up_after_max_retries() -> None:
    api = MockAPI(api_error(503, "unavailable"))
    with pytest.raises(ServerError):
        api.client(max_retries=3).status()
    assert len(api.requests) == 4


def test_max_retries_zero() -> None:
    api = MockAPI(api_error(429, "rate_limited"))
    with pytest.raises(Exception):
        api.client(max_retries=0).status()
    assert len(api.requests) == 1
    assert api.sleeps == []


def test_never_retries_quota_exceeded() -> None:
    api = MockAPI(api_error(429, "quota_exceeded", "monthly quota used up"), ok())
    with pytest.raises(QuotaExceededError):
        api.client().status()
    assert len(api.requests) == 1


@pytest.mark.parametrize("status", [400, 401, 402, 403, 404, 422])
def test_no_retry_for_other_4xx(status: int) -> None:
    api = MockAPI(api_error(status, "x"), ok())
    with pytest.raises(Exception):
        api.client().status()
    assert len(api.requests) == 1


def test_retries_network_errors_on_get() -> None:
    api = MockAPI(httpx.ConnectError("refused"), httpx.ReadTimeout("slow"), ok())
    assert api.client().status() == {"status": "operational"}
    assert len(api.requests) == 3


def test_post_retries_429_but_not_5xx_or_read_errors() -> None:
    api = MockAPI(api_error(429, "rate_limited", headers={"Retry-After": "1"}), json_response({"data": {"job_id": "j"}}, 202))
    api.client().batch.create(type="domains", items=["nike.com"])
    assert len(api.requests) == 2

    api = MockAPI(api_error(503, "unavailable"), json_response({}))
    with pytest.raises(ServerError):
        api.client().watchlists.create(advertisers=["meta:1"])
    assert len(api.requests) == 1

    api = MockAPI(httpx.ReadTimeout("slow"), json_response({}))
    with pytest.raises(APITimeoutError):
        api.client().webhooks.rotate_secret()
    assert len(api.requests) == 1


def test_post_retries_when_connection_never_made() -> None:
    api = MockAPI(httpx.ConnectError("refused"), json_response({"delivery_id": 1, "status": "queued"}, 202))
    assert api.client().webhooks.test("https://hooks.test/x")["delivery_id"] == 1
    assert len(api.requests) == 2


def test_delete_retried_like_get() -> None:
    api = MockAPI(api_error(502, "bad_gateway"), httpx.Response(204))
    api.client().watchlists.remove_advertiser("wl", "meta:1")
    assert len(api.requests) == 2


def test_retry_after_and_backoff_caps() -> None:
    assert retry_delay(0, 3600) == MAX_RETRY_AFTER
    assert retry_delay(0, 2.5) == 2.5
    assert retry_delay(20) <= 8.0 * 1.25


def test_network_error_exhausts_retries() -> None:
    api = MockAPI(httpx.ConnectError("refused"))
    with pytest.raises(APIConnectionError):
        api.client(max_retries=1).status()
    assert len(api.requests) == 2


async def test_async_retries() -> None:
    api = MockAPI(api_error(429, "rate_limited", headers={"Retry-After": "1"}), httpx.ConnectError("x"), ok())
    assert await api.async_client().status() == {"status": "operational"}
    assert len(api.requests) == 3
    assert api.sleeps[0] == 1.0


async def test_async_no_retry_on_422() -> None:
    api = MockAPI(api_error(422, "unsupported"), ok())
    with pytest.raises(ValidationError):
        await api.async_client().status()
    assert len(api.requests) == 1
