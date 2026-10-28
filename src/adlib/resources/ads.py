from __future__ import annotations

from typing import Optional, cast

from .. import _endpoints as E
from .._endpoints import DateLike, PlatformFilter
from ..types import (
    AdFeaturesResponse,
    AdFormat,
    AdHistoryResponse,
    AdList,
    AdResponse,
    Placement,
    Sort,
    Source,
    StatusFilter,
)
from ._base import AsyncResource, SyncResource

__all__ = ["Ads", "AsyncAds"]


class Ads(SyncResource):
    """Ads: search, one ad, its history and its creative features."""

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
        placement: Optional[Placement] = None,
        political: Optional[bool] = None,
        removed: Optional[bool] = None,
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
        puts the longest-running ads (likely winners) first. ``political=True`` returns only
        political or issue ads, ``False`` none (only Meta labels them, so ``True`` limits results
        to Meta). ``platform`` also accepts ``youtube`` and ``play`` (Google ads on YouTube or Google
        Play); ``placement`` (Google only) is one of youtube, search, shopping, maps, play.
        ``removed`` (with ``source="history"``): ``True`` = only ads the platforms' libraries no
        longer show, which we kept; ``False`` = only ads still there. ``limit`` is a page size
        hint, 1 to 100."""
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
                    placement=placement,
                    political=political,
                    removed=removed,
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
        """All observed versions, status periods, events and daily EU reach of an ad."""
        return cast(AdHistoryResponse, self._request(E.ad_history(id)))

    def features(self, id: str) -> AdFeaturesResponse:
        """Creative features of an ad: hook, offers, urgency, social proof, format, video length,
        cuts and on-image text. Rule-based and measured, no AI model: every text tag carries the
        text it matched. Kept per ad version. Costs the features price (default 2 credits), plus
        the ad itself if it has to be fetched live."""
        return cast(AdFeaturesResponse, self._request(E.ad_features(id)))


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
        placement: Optional[Placement] = None,
        political: Optional[bool] = None,
        removed: Optional[bool] = None,
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
        puts the longest-running ads (likely winners) first. ``political=True`` returns only
        political or issue ads, ``False`` none (only Meta labels them, so ``True`` limits results
        to Meta). ``platform`` also accepts ``youtube`` and ``play`` (Google ads on YouTube or Google
        Play); ``placement`` (Google only) is one of youtube, search, shopping, maps, play.
        ``removed`` (with ``source="history"``): ``True`` = only ads the platforms' libraries no
        longer show, which we kept; ``False`` = only ads still there. ``limit`` is a page size
        hint, 1 to 100."""
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
                    placement=placement,
                    political=political,
                    removed=removed,
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
        """All observed versions, status periods, events and daily EU reach of an ad."""
        return cast(AdHistoryResponse, await self._request(E.ad_history(id)))

    async def features(self, id: str) -> AdFeaturesResponse:
        """Creative features of an ad: hook, offers, urgency, social proof, format, video length,
        cuts and on-image text. Rule-based and measured, no AI model: every text tag carries the
        text it matched. Kept per ad version. Costs the features price (default 2 credits), plus
        the ad itself if it has to be fetched live."""
        return cast(AdFeaturesResponse, await self._request(E.ad_features(id)))
