from __future__ import annotations

import datetime as dt
from typing import Dict

import httpx

from .conftest import MockAPI, body, json_response


def params(req: httpx.Request) -> Dict[str, str]:
    return dict(req.url.params)


def calls(api: MockAPI) -> list:
    return [f"{r.method} {r.url.path}" for r in api.requests]


def test_search_sends_every_filter(api: MockAPI) -> None:
    client = api.client()
    client.search(
        q=" running shoes ",
        platform=["meta", "google"],
        country="DE",
        status="active",
        date_from="2026-01-01",
        date_to=dt.date(2026, 2, 1),
        format="video",
        source="history",
        sort="days_running",
        cursor="c",
        limit=50,
    )
    assert api.last.url.path == "/v1/search"
    assert params(api.last) == {
        "q": "running shoes",
        "platform": "meta,google",
        "country": "DE",
        "status": "active",
        "from": "2026-01-01",
        "to": "2026-02-01",
        "format": "video",
        "source": "history",
        "sort": "days_running",
        "cursor": "c",
        "limit": "50",
    }
    client.ads.search(advertiser="meta:15087023444")
    assert params(api.last) == {"advertiser": "meta:15087023444"}


def test_ads(api: MockAPI) -> None:
    client = api.client()
    client.ads.get("meta:1234567890")
    client.ads.get("google:CR1", max_age=0)
    client.ads.history("meta:1")
    assert calls(api) == ["GET /v1/ads/meta:1234567890", "GET /v1/ads/google:CR1", "GET /v1/ads/meta:1/history"]
    assert params(api.requests[1]) == {"max_age": "0"}


def test_path_segments_are_encoded_but_keep_colons(api: MockAPI) -> None:
    api.client().advertisers.get("x:a/b#c")
    assert api.last.url.raw_path == b"/v1/advertisers/x:a%2Fb%23c"
    # Pinterest advertiser ids are names and may contain spaces and dots.
    api.client().advertisers.stats("pinterest:Nike S.r.l.")
    assert api.last.url.raw_path == b"/v1/advertisers/pinterest:Nike%20S.r.l./stats"


def test_advertisers(api: MockAPI) -> None:
    client = api.client()
    client.advertisers.resolve("nike.com")
    client.advertisers.resolve("nike.com", platform="meta,tiktok", max_per_platform=5)
    client.advertisers.get("meta:15087023444", refresh=True)
    client.advertisers.ads("meta:15087023444", status="inactive", source="history", sort="days_running", limit=100, cursor="c")
    client.advertisers.changes("meta:1", since="2026-10-01", types=["started", "discovered"], limit=200)
    client.advertisers.changes("meta:1", since=dt.datetime(2026, 10, 1, tzinfo=dt.timezone.utc))
    client.advertisers.stats("meta:1")
    client.advertisers.timeline("meta:1", date_from="2026-01-01", date_to="2026-02-01", cursor="c", limit=10)
    r = api.requests
    assert params(r[0]) == {"domain": "nike.com"}
    assert params(r[1]) == {"domain": "nike.com", "platform": "meta,tiktok", "max_per_platform": "5"}
    assert params(r[2]) == {"refresh": "true"}
    assert params(r[3]) == {"status": "inactive", "source": "history", "sort": "days_running", "limit": "100", "cursor": "c"}
    assert params(r[4]) == {"since": "2026-10-01", "types": "started,discovered", "limit": "200"}
    assert params(r[5]) == {"since": "2026-10-01T00:00:00Z"}
    assert params(r[7]) == {"from": "2026-01-01", "to": "2026-02-01", "cursor": "c", "limit": "10"}
    assert calls(api) == [
        "GET /v1/advertisers/resolve",
        "GET /v1/advertisers/resolve",
        "GET /v1/advertisers/meta:15087023444",
        "GET /v1/advertisers/meta:15087023444/ads",
        "GET /v1/advertisers/meta:1/changes",
        "GET /v1/advertisers/meta:1/changes",
        "GET /v1/advertisers/meta:1/stats",
        "GET /v1/advertisers/meta:1/timeline",
    ]


def test_domains(api: MockAPI) -> None:
    client = api.client()
    client.domains.check("nike.com")
    client.domains.check("nike.com", platform=["linkedin"])
    assert calls(api) == ["GET /v1/domains/nike.com/check"] * 2
    assert params(api.last) == {"platform": "linkedin"}


def test_batch() -> None:
    api = MockAPI(json_response({"data": {"job_id": "j1"}}, 202))
    client = api.client()
    created = client.batch.create(
        type="domains",
        items=["nike.com", "adidas.com"],
        options={"include_ads": True, "platforms": ["meta"]},
        webhook_url="https://hooks.test/adlib",
    )
    assert created["data"]["job_id"] == "j1"
    assert api.last.method == "POST" and api.last.url.path == "/v1/batch"
    assert api.last.headers["content-type"] == "application/json"
    assert body(api.last) == {
        "type": "domains",
        "items": ["nike.com", "adidas.com"],
        "options": {"include_ads": True, "platforms": ["meta"]},
        "webhook_url": "https://hooks.test/adlib",
    }
    client.batch.get("8d3c-uuid", cursor="c", limit=5)
    assert api.last.url.path == "/v1/batch/8d3c-uuid"
    assert params(api.last) == {"cursor": "c", "limit": "5"}


def test_watchlists() -> None:
    api = MockAPI(*([json_response({"data": {}})] * 5), httpx.Response(204), httpx.Response(204))
    client = api.client()
    client.watchlists.create(advertisers=["meta:15087023444"])
    client.watchlists.create(
        advertisers=["meta:1", "tiktok:2"],
        name="Competitors",
        webhook_url="https://hooks.test/w",
        interval_hours=12,
        archive_videos=False,
    )
    client.watchlists.list()
    client.watchlists.get("wl-1")
    client.watchlists.add_advertisers("wl-1", ["google:AR1"])
    client.watchlists.remove_advertiser("wl-1", "google:AR1")
    client.watchlists.delete("wl-1")
    r = api.requests
    assert body(r[0]) == {"advertisers": ["meta:15087023444"]}
    assert body(r[1]) == {
        "advertisers": ["meta:1", "tiktok:2"],
        "name": "Competitors",
        "webhook_url": "https://hooks.test/w",
        "interval_hours": 12,
        "archive_videos": False,
    }
    assert body(r[4]) == {"advertisers": ["google:AR1"]}
    assert calls(api) == [
        "POST /v1/watchlists",
        "POST /v1/watchlists",
        "GET /v1/watchlists",
        "GET /v1/watchlists/wl-1",
        "POST /v1/watchlists/wl-1/advertisers",
        "DELETE /v1/watchlists/wl-1/advertisers/google:AR1",
        "DELETE /v1/watchlists/wl-1",
    ]


def test_webhooks(api: MockAPI) -> None:
    client = api.client()
    client.webhooks.deliveries()
    client.webhooks.deliveries(status="failed", limit=10, cursor="c")
    client.webhooks.delivery(42)
    client.webhooks.redeliver("42")
    client.webhooks.test("https://hooks.test/x")
    client.webhooks.secret()
    client.webhooks.rotate_secret()
    assert calls(api) == [
        "GET /v1/webhooks/deliveries",
        "GET /v1/webhooks/deliveries",
        "GET /v1/webhooks/deliveries/42",
        "POST /v1/webhooks/deliveries/42/redeliver",
        "POST /v1/webhooks/test",
        "GET /v1/webhooks/secret",
        "POST /v1/webhooks/secret/rotate",
    ]
    assert params(api.requests[1]) == {"status": "failed", "limit": "10", "cursor": "c"}
    assert body(api.requests[4]) == {"url": "https://hooks.test/x"}
    assert api.requests[3].content == b""


def test_usage_status_platforms(api: MockAPI) -> None:
    client = api.client()
    client.usage()
    client.usage(days=7)
    client.status()
    client.platforms()
    assert [r.url.path + ("?" + r.url.query.decode() if r.url.query else "") for r in api.requests] == [
        "/v1/usage",
        "/v1/usage?days=7",
        "/v1/status",
        "/v1/platforms",
    ]


def test_raw_request(api: MockAPI) -> None:
    api.client().request("get", "/v1/new", params={"a": 1})
    assert str(api.last.url) == "https://api.adlibapi.com/v1/new?a=1"


async def test_async_endpoints(api: MockAPI) -> None:
    client = api.async_client()
    await client.search(domain="nike.com")
    await client.ads.get("meta:1")
    await client.ads.history("meta:1")
    await client.advertisers.resolve("nike.com")
    await client.advertisers.get("meta:1")
    await client.advertisers.ads("meta:1")
    await client.advertisers.changes("meta:1", since="2026-10-01")
    await client.advertisers.stats("meta:1")
    await client.advertisers.timeline("meta:1")
    await client.domains.check("nike.com")
    await client.batch.create(type="ads", items=["meta:1"])
    await client.batch.get("j")
    await client.watchlists.list()
    await client.watchlists.create(advertisers=["meta:1"])
    await client.watchlists.get("w")
    await client.watchlists.add_advertisers("w", ["meta:2"])
    await client.watchlists.remove_advertiser("w", "meta:2")
    await client.watchlists.delete("w")
    await client.webhooks.deliveries()
    await client.webhooks.delivery(1)
    await client.webhooks.redeliver(1)
    await client.webhooks.test("https://h.test")
    await client.webhooks.secret()
    await client.webhooks.rotate_secret()
    await client.usage()
    await client.status()
    await client.platforms()
    await client.aclose()
    assert len(api.requests) == 27
    assert calls(api)[10] == "POST /v1/batch"
