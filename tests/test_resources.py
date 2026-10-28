from __future__ import annotations

import datetime as dt
from typing import Dict, Optional

import httpx

import pytest

from adlib.types import PLATFORMS

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
        political=False,
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
        "political": "false",
        "source": "history",
        "sort": "days_running",
        "cursor": "c",
        "limit": "50",
    }
    client.ads.search(advertiser="meta:15087023444")
    assert params(api.last) == {"advertiser": "meta:15087023444"}


def test_search_new_platforms_aliases_placement_and_removed(api: MockAPI) -> None:
    client = api.client()
    client.search(q="shoes", platform=["snapchat", "apple", "amazon", "microsoft"])
    assert params(api.last) == {"q": "shoes", "platform": "snapchat,apple,amazon,microsoft"}
    client.search(q="shoes", platform="youtube", format="video")
    assert params(api.last) == {"q": "shoes", "platform": "youtube", "format": "video"}
    client.search(domain="nike.com", platform="google", placement="shopping")
    assert params(api.last) == {"domain": "nike.com", "platform": "google", "placement": "shopping"}
    client.ads.search(domain="nike.com", source="history", removed=True)
    assert params(api.last) == {"domain": "nike.com", "source": "history", "removed": "true"}
    with pytest.raises(ValueError, match="placement must be one of"):
        client.search(q="x", placement="tv")  # type: ignore[arg-type]
    assert len(api.requests) == 4


def test_platforms_constant() -> None:
    assert PLATFORMS == (
        "meta", "google", "tiktok", "linkedin", "pinterest", "x", "snapchat", "apple", "amazon", "microsoft"
    )


def test_ads(api: MockAPI) -> None:
    client = api.client()
    client.ads.get("meta:1234567890")
    client.ads.get("google:CR1", max_age=0)
    client.ads.history("meta:1")
    assert calls(api) == ["GET /v1/ads/meta:1234567890", "GET /v1/ads/google:CR1", "GET /v1/ads/meta:1/history"]
    assert params(api.requests[1]) == {"max_age": "0"}


def test_ad_features() -> None:
    api = MockAPI(
        json_response(
            {
                "data": {"version": "1", "method": "rules", "format": "vertical_video", "text": {"hook": "New?"}, "media": []},
                "meta": {"ad_id": "meta:1187430977361020", "cached": True, "analyzed_at": "2026-10-27T10:00:00Z"},
            }
        )
    )
    client = api.client()
    res = client.ads.features("meta:1187430977361020")
    assert calls(api) == ["GET /v1/ads/meta:1187430977361020/features"]
    assert res["data"]["format"] == "vertical_video" and res["meta"]["cached"] is True
    with pytest.raises(ValueError, match="<platform>:<id>"):
        client.ads.features("1187430977361020")


def test_ad_features_waits_while_processing() -> None:
    processing = {"data": None, "meta": {"ad_id": "tiktok:1", "status": "processing", "retry_after": 20, "cached": False}}
    ready = {"data": {"format": "vertical_video", "media": []}, "meta": {"ad_id": "tiktok:1", "status": "ready", "cached": True}}
    api = MockAPI(json_response(processing, 202, {"Retry-After": "20"}), json_response(processing, 202), json_response(ready))
    res = api.client().ads.features("tiktok:1")
    assert len(api.requests) == 3 and api.sleeps == [20.0, 20.0]
    assert res["meta"]["status"] == "ready" and res["data"] is not None

    once = MockAPI(json_response(processing, 202))
    assert once.client().ads.features("tiktok:1", wait=False)["meta"]["status"] == "processing"
    assert len(once.requests) == 1

    capped = MockAPI(json_response(processing, 202))
    assert capped.client().ads.features("tiktok:1", max_wait=30)["meta"]["status"] == "processing"
    assert len(capped.requests) == 2 and capped.sleeps == [20.0]


def test_library_url_and_coverage(api: MockAPI) -> None:
    client = api.client()
    link = "https://www.facebook.com/ads/library/?id=1187430977361020"
    client.library_url(link)
    assert api.last.url.path == "/v1/library-url"
    assert params(api.last) == {"url": link}
    client.coverage()
    assert str(api.last.url) == "https://api.adlibapi.com/public/coverage"
    with pytest.raises(ValueError, match="url must be a non-empty string"):
        client.library_url(" ")


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
    client.advertisers.changes("meta:1", since="2026-10-01", types=["started", "discovered", "removed"], limit=200)
    client.advertisers.changes("meta:1", since=dt.datetime(2026, 10, 1, tzinfo=dt.timezone.utc))
    client.advertisers.stats("meta:1")
    client.advertisers.timeline("meta:1", date_from="2026-01-01", date_to="2026-02-01", cursor="c", limit=10)
    r = api.requests
    assert params(r[0]) == {"domain": "nike.com"}
    assert params(r[1]) == {"domain": "nike.com", "platform": "meta,tiktok", "max_per_platform": "5"}
    assert params(r[2]) == {"refresh": "true"}
    assert params(r[3]) == {"status": "inactive", "source": "history", "sort": "days_running", "limit": "100", "cursor": "c"}
    assert params(r[4]) == {"since": "2026-10-01", "types": "started,discovered,removed", "limit": "200"}
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


def test_resolve_reports() -> None:
    api = MockAPI(
        json_response({"data": {"id": 7, "kind": "wrong_match", "status": "open"}}, 201),
        json_response({"data": {"id": 8}}, 201),
        json_response({"data": {"id": 9}}, 201),
        json_response({"data": []}),
    )
    client = api.client()
    created = client.advertisers.report_match(
        "audi.de",
        kind="wrong_match",
        advertiser_id="google:AR01700036858500612097",
        note="agency account, not the brand",
    )
    assert created["data"]["id"] == 7
    client.advertisers.report_match("audi.de", kind="missing_match")
    client.advertisers.report_match("audi.de", kind="wrong_role", advertiser_id="meta:42", role="agency")
    client.advertisers.list_reports()
    r = api.requests
    assert body(r[0]) == {
        "domain": "audi.de",
        "kind": "wrong_match",
        "advertiser_id": "google:AR01700036858500612097",
        "note": "agency account, not the brand",
    }
    assert body(r[1]) == {"domain": "audi.de", "kind": "missing_match"}
    assert body(r[2]) == {"domain": "audi.de", "kind": "wrong_role", "advertiser_id": "meta:42", "role": "agency"}
    assert calls(api) == [
        "POST /v1/advertisers/resolve/reports",
        "POST /v1/advertisers/resolve/reports",
        "POST /v1/advertisers/resolve/reports",
        "GET /v1/advertisers/resolve/reports",
    ]


def test_companies() -> None:
    api = MockAPI(json_response({"data": {"domain": "audi.de"}}))
    client = api.client()
    assert client.companies.get("audi.de")["data"]["domain"] == "audi.de"
    client.companies.get("audi.de", platform=["meta", "google"], min_score=0.5, max_per_platform=10)
    client.companies.get("audi.de", min_score=0)
    client.companies.get("audi.de", include_related=True)
    r = api.requests
    assert calls(api) == ["GET /v1/companies/audi.de"] * 4
    assert params(r[0]) == {}
    assert params(r[1]) == {"platform": "meta,google", "min_score": "0.5", "max_per_platform": "10"}
    assert params(r[2]) == {"min_score": "0"}
    assert params(r[3]) == {"include_related": "true"}


def test_domains(api: MockAPI) -> None:
    client = api.client()
    client.domains.check("nike.com")
    client.domains.check("nike.com", platform=["linkedin"])
    assert calls(api) == ["GET /v1/domains/nike.com/check"] * 2
    assert params(api.last) == {"platform": "linkedin"}


def test_domain_suggest(api: MockAPI) -> None:
    client = api.client()
    client.domains.suggest("nik")
    assert api.last.url.path == "/v1/domains/suggest"
    assert params(api.last) == {"q": "nik"}
    client.domains.suggest("adid", limit=20)
    assert params(api.last) == {"q": "adid", "limit": "20"}
    with pytest.raises(ValueError, match="q must be 2 to 100 characters"):
        client.domains.suggest("n")
    with pytest.raises(ValueError, match="limit must be an integer"):
        client.domains.suggest("nike", limit=21)


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
        email_alerts=True,
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
        "email_alerts": True,
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


def test_watchlist_update() -> None:
    api = MockAPI(json_response({"data": {"id": "wl-1", "email_alerts": True}}))
    client = api.client()
    res = client.watchlists.update("wl-1", name="Rivals", webhook_url="", email_alerts=True)
    assert res["data"]["email_alerts"] is True
    assert api.last.method == "PATCH" and api.last.url.path == "/v1/watchlists/wl-1"
    assert api.last.headers["content-type"] == "application/json"
    assert body(api.last) == {"name": "Rivals", "webhook_url": "", "email_alerts": True}
    client.watchlists.update("wl-1", email_alerts=False)
    assert body(api.last) == {"email_alerts": False}
    with pytest.raises(ValueError, match="at least one of"):
        client.watchlists.update("wl-1")
    with pytest.raises(ValueError, match="at most 200"):
        client.watchlists.update("wl-1", name="x" * 201)
    assert len(api.requests) == 2


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
    await client.advertisers.report_match("audi.de", kind="missing_match")
    await client.advertisers.list_reports()
    await client.companies.get("audi.de", min_score=0.9)
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
    await client.ads.features("meta:1")
    await client.library_url("https://www.tiktok.com/@nike/video/1")
    await client.coverage()
    await client.domains.suggest("nik")
    await client.watchlists.update("w", email_alerts=True)
    await client.aclose()
    assert len(api.requests) == 35
    assert calls(api)[30:] == [
        "GET /v1/ads/meta:1/features",
        "GET /v1/library-url",
        "GET /public/coverage",
        "GET /v1/domains/suggest",
        "PATCH /v1/watchlists/w",
    ]
    assert calls(api)[9:13] == [
        "POST /v1/advertisers/resolve/reports",
        "GET /v1/advertisers/resolve/reports",
        "GET /v1/companies/audi.de",
        "GET /v1/domains/nike.com/check",
    ]
    assert calls(api)[13] == "POST /v1/batch"


def csv_response(text: str, headers: Optional[dict] = None) -> httpx.Response:
    return httpx.Response(
        200, content=text.encode(), headers={"content-type": "text/csv; charset=utf-8", **(headers or {})}
    )


def test_ids_accept_every_platform_prefix(api: MockAPI) -> None:
    client = api.client()
    for p in PLATFORMS:
        client.ads.get(f"{p}:123")
    assert api.last.url.path == "/v1/ads/microsoft:123"
    assert len(api.requests) == 10
    with pytest.raises(ValueError, match="must look like <platform>:<id>"):
        client.ads.get("youtube:123")
    with pytest.raises(ValueError, match="platform one of meta, google"):
        client.advertisers.stats("facebook:1")


def test_search_csv(api: MockAPI) -> None:
    api.replies = [csv_response("id,platform\nmeta:1,meta\n", {"x-next-cursor": "c2"})]
    client = api.client()
    page = client.ads.search_csv(q="shoes", platform=["meta", "youtube"], limit=50)
    assert page == {"csv": "id,platform\nmeta:1,meta\n", "next_cursor": "c2"}
    assert api.last.url.path == "/v1/search"
    assert params(api.last) == {"q": "shoes", "platform": "meta,youtube", "limit": "50", "output": "csv"}
    assert api.last.headers["accept"] == "text/csv"


def test_csv_endpoints(api: MockAPI) -> None:
    api.replies = [csv_response("id\n")]
    client = api.client()
    assert client.advertisers.ads_csv("meta:1", source="history") == {"csv": "id\n", "next_cursor": None}
    client.advertisers.changes_csv("meta:1", since="2026-10-01", types=["removed"])
    client.advertisers.timeline_csv("meta:1", date_from="2026-01-01")
    client.domains.check_csv("nike.com")
    client.request_csv("/v1/watchlists")
    assert [str(r.url).split("adlibapi.com")[1] for r in api.requests] == [
        "/v1/advertisers/meta:1/ads?source=history&output=csv",
        "/v1/advertisers/meta:1/changes?since=2026-10-01&types=removed&output=csv",
        "/v1/advertisers/meta:1/timeline?from=2026-01-01&output=csv",
        "/v1/domains/nike.com/check?output=csv",
        "/v1/watchlists?output=csv",
    ]


def test_csv_errors_stay_json(api: MockAPI) -> None:
    from adlib import AdLibError, NotFoundError

    from .conftest import api_error

    api.replies = [api_error(404, "not_found"), json_response({"data": None})]
    client = api.client()
    with pytest.raises(NotFoundError):
        client.advertisers.ads_csv("meta:1")
    with pytest.raises(AdLibError, match="Expected a CSV response"):
        client.domains.check_csv("nike.com")


async def test_async_csv(api: MockAPI) -> None:
    api.replies = [csv_response("id\n", {"x-next-cursor": "n"})]
    client = api.async_client()
    assert await client.ads.search_csv(domain="nike.com") == {"csv": "id\n", "next_cursor": "n"}
    await client.advertisers.ads_csv("meta:1")
    await client.advertisers.changes_csv("meta:1", since="2026-10-01")
    await client.advertisers.timeline_csv("meta:1")
    await client.domains.check_csv("nike.com")
    await client.request_csv("/v1/usage", params={"days": 7})
    assert all(r.url.params["output"] == "csv" for r in api.requests)
    assert api.last.url.path == "/v1/usage"
    await client.aclose()
