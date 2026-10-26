from __future__ import annotations

from typing import Optional, cast

from .. import _endpoints as E
from .._endpoints import DateLike, PlatformFilter
from ..types import AdFormat, AdHistoryResponse, AdList, AdResponse, Sort, Source, StatusFilter
from ._base import AsyncResource, SyncResource

__all__ = ["Ads", "AsyncAds"]


class Ads(SyncResource):
    """Ads: search, one ad, and its history."""

    def search(
        self,
        *,
        q: Optional[str] = None,
        advertiser: Optional[str] = None,
        domain: Optional[str] = None,
        platform: PlatformFilter = None,
        country: Optional[str] = None,
        status: Optional[StatusFilter] = None,
        date_from: DateLike = None,
        date_to: DateLike = None,
        format: Optional[AdFormat] = None,
        source: Optional[Source] = None,
        sort: Optional[Sort] = None,
        cursor: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> AdList:
        """Searches ads, across all platforms when ``platform`` is omitted. Paginated.

        Exactly one search mode is required: ``q`` (keyword in the ad text), ``advertiser``
        (name, or our advertiser id ``<platform>:<id>``) or ``domain``. Platforms that fail are
        listed in ``meta["errors"]`` and not billed. ``date_from``/``date_to`` are sent as
        ``from``/``to`` (shown on or after / before, YYYY-MM-DD). ``source="history"`` searches
        the archive, including ads gone from the platforms; with it, ``sort="days_running"``
        puts the longest-running ads (likely winners) first. ``limit`` is a page size hint, 1
        to 100."""
        return cast(
            AdList,
            self._request(
                E.search(
                    q=q,
                    advertiser=advertiser,
                    domain=domain,
                    platform=platform,
                    country=country,
                    status=status,
                    date_from=date_from,
                    date_to=date_to,
                    format=format,
                    source=source,
                    sort=sort,
                    cursor=cursor,
                    limit=limit,
                )
            ),
        )

    def get(self, id: str, *, max_age: Optional[int] = None) -> AdResponse:
        """One ad (``<platform>:<platform_ad_id>``), fetched live from its platform. If the platform
        no longer has it, the archived version is returned (``meta["source"] == "history"``).
        ``max_age``: serve from the archive if seen within this many seconds (0 = always live,
        default 3600)."""
        return cast(AdResponse, self._request(E.get_ad(id, max_age)))

    def history(self, id: str) -> AdHistoryResponse:
        """All observed versions, status periods and events of an ad."""
        return cast(AdHistoryResponse, self._request(E.ad_history(id)))


class AsyncAds(AsyncResource):
    """Async version of :class:`Ads`."""

    async def search(
        self,
        *,
        q: Optional[str] = None,
        advertiser: Optional[str] = None,
        domain: Optional[str] = None,
        platform: PlatformFilter = None,
        country: Optional[str] = None,
        status: Optional[StatusFilter] = None,
        date_from: DateLike = None,
        date_to: DateLike = None,
        format: Optional[AdFormat] = None,
        source: Optional[Source] = None,
        sort: Optional[Sort] = None,
        cursor: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> AdList:
        """Searches ads, across all platforms when ``platform`` is omitted. Paginated.

        Exactly one search mode is required: ``q`` (keyword in the ad text), ``advertiser``
        (name, or our advertiser id ``<platform>:<id>``) or ``domain``. Platforms that fail are
        listed in ``meta["errors"]`` and not billed. ``date_from``/``date_to`` are sent as
        ``from``/``to`` (shown on or after / before, YYYY-MM-DD). ``source="history"`` searches
        the archive, including ads gone from the platforms; with it, ``sort="days_running"``
        puts the longest-running ads (likely winners) first. ``limit`` is a page size hint, 1
        to 100."""
        return cast(
            AdList,
            await self._request(
                E.search(
                    q=q,
                    advertiser=advertiser,
                    domain=domain,
                    platform=platform,
                    country=country,
                    status=status,
                    date_from=date_from,
                    date_to=date_to,
                    format=format,
                    source=source,
                    sort=sort,
                    cursor=cursor,
                    limit=limit,
                )
            ),
        )

    async def get(self, id: str, *, max_age: Optional[int] = None) -> AdResponse:
        """One ad (``<platform>:<platform_ad_id>``), fetched live from its platform. If the platform
        no longer has it, the archived version is returned (``meta["source"] == "history"``).
        ``max_age``: serve from the archive if seen within this many seconds (0 = always live,
        default 3600)."""
        return cast(AdResponse, await self._request(E.get_ad(id, max_age)))

    async def history(self, id: str) -> AdHistoryResponse:
        """All observed versions, status periods and events of an ad."""
        return cast(AdHistoryResponse, await self._request(E.ad_history(id)))
