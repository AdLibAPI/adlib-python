from __future__ import annotations

from typing import List

import pytest

from adlib import next_cursor, page_items

from .conftest import MockAPI, json_response, page


def test_follows_next_cursor_until_none() -> None:
    api = MockAPI(page(["a", "b"], "c1"), page(["c"], "c2"), page(["d"], None))
    client = api.client()
    pages = list(client.paginate(client.ads.search, q="shoes", limit=2))
    assert [p["next_cursor"] for p in pages] == ["c1", "c2", None]
    assert [r.url.params.get("cursor") for r in api.requests] == [None, "c1", "c2"]
    assert all(r.url.params["q"] == "shoes" and r.url.params["limit"] == "2" for r in api.requests)


def test_stops_at_max_pages() -> None:
    counter = iter(range(1000))
    api = MockAPI(lambda req: page(["x"], f"c{next(counter)}"))
    client = api.client()
    assert len(list(client.paginate(client.ads.search, q="x"))) == 10
    assert len(list(client.paginate(client.ads.search, q="x", max_pages=2))) == 2


def test_stops_when_cursor_repeats() -> None:
    api = MockAPI(page(["a"], "same"))
    client = api.client()
    pages = list(client.paginate(client.ads.search, q="x", cursor="start", max_pages=None))
    assert len(pages) == 2
    assert api.requests[0].url.params["cursor"] == "start"


def test_paginate_items_yields_ads() -> None:
    api = MockAPI(page(["a", "b"], "c1"), page(["c"], None))
    client = api.client()
    ids = [ad["id"] for ad in client.paginate_items(client.advertisers.ads, "meta:1", source="history")]
    assert ids == ["a", "b", "c"]
    assert api.requests[0].url.path == "/v1/advertisers/meta:1/ads"


def test_paginate_items_yields_batch_items() -> None:
    api = MockAPI(
        json_response({"data": {"job_id": "j"}, "items": [{"input": "nike.com"}], "next_cursor": "n"}),
        json_response({"data": {"job_id": "j"}, "items": [{"input": "adidas.com"}], "next_cursor": None}),
    )
    client = api.client()
    assert [i["input"] for i in client.paginate_items(client.batch.get, "j")] == ["nike.com", "adidas.com"]


def test_invalid_max_pages(api: MockAPI) -> None:
    client = api.client()
    with pytest.raises(ValueError):
        list(client.paginate(client.ads.search, q="x", max_pages=0))


def test_helpers() -> None:
    assert next_cursor({"next_cursor": "a"}) == "a"
    assert next_cursor({"next_cursor": None}) is None
    assert next_cursor({"next_cursor": ""}) is None
    assert next_cursor(None) is None
    assert page_items({"items": [1], "data": {}}) == [1]
    assert page_items({"data": [2]}) == [2]
    assert page_items({"data": None}) == []


async def test_async_paginate_items() -> None:
    api = MockAPI(page(["a"], "c1"), page(["b"], None))
    client = api.async_client()
    ids: List[str] = []
    async for ad in client.paginate_items(client.ads.search, domain="nike.com"):
        ids.append(ad["id"])
    assert ids == ["a", "b"]
    pages = [p async for p in client.paginate(client.webhooks.deliveries, status="failed", max_pages=1)]
    assert len(pages) == 1
