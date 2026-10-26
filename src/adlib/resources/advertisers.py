from __future__ import annotations

from typing import Optional, Sequence, cast

from .. import _endpoints as E
from .._endpoints import DateLike, PlatformFilter
from ..types import AdList, AdvertiserResponse, AdvertiserStatsResponse, EventList, EventType, ResolveResponse, Sort, Source, StatusFilter
from ._base import AsyncResource, SyncResource

__all__ = ["Advertisers", "AsyncAdvertisers"]


class Advertisers(SyncResource):
    """Advertisers: resolve a domain, profiles, ads, changes, stats and timelines."""

    def resolve(self, domain: str, *, platform: PlatformFilter = None, max_per_platform: Optional[int] = None) -> ResolveResponse:
        """A brand's advertiser ids on Meta, Google, TikTok, LinkedIn, Pinterest and X from its
        domain, each with a confidence ``score`` and ``match_reason``. ``max_per_platform`` 1 to
        10, default 3."""
        return cast(ResolveResponse, self._request(E.resolve_advertisers(domain, platform, max_per_platform)))

    def get(self, id: str, *, refresh: Optional[bool] = None) -> AdvertiserResponse:
        """An advertiser incl. active ads and ads known in the archive. ``refresh=True`` crawls the
        first page of its ads live before answering."""
        return cast(AdvertiserResponse, self._request(E.get_advertiser(id, refresh)))

    def ads(
        self,
        id: str,
        *,
        status: Optional[StatusFilter] = None,
        source: Optional[Source] = None,
        sort: Optional[Sort] = None,
        cursor: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> AdList:
        """All ads of an advertiser, live (default) or from history (``source="history"``, includes
        ads that vanished from the platform). ``limit`` 1 to 100. Paginated."""
        return cast(AdList, self._request(E.advertiser_ads(id, status, source, sort, cursor, limit)))

    def changes(
        self,
        id: str,
        *,
        since: DateLike,
        types: Optional[Sequence[EventType]] = None,
        cursor: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> EventList:
        """New, stopped and changed ads since a point in time (YYYY-MM-DD, RFC 3339, a date or a
        datetime). ``types`` defaults to started, stopped, changed. ``limit`` 1 to 200.
        Paginated."""
        return cast(EventList, self._request(E.advertiser_changes(id, since, types, cursor, limit)))

    def stats(self, id: str) -> AdvertiserStatsResponse:
        """Analytics from the history: ads by status, format, country and language; run-time
        distribution; new ads per week; and the 5 longest-running ads (likely winners)."""
        return cast(AdvertiserStatsResponse, self._request(E.advertiser_stats(id)))

    def timeline(
        self,
        id: str,
        *,
        date_from: DateLike = None,
        date_to: DateLike = None,
        cursor: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> EventList:
        """When which ads started and stopped. ``limit`` 1 to 200. Paginated."""
        return cast(EventList, self._request(E.advertiser_timeline(id, date_from, date_to, cursor, limit)))


class AsyncAdvertisers(AsyncResource):
    """Async version of :class:`Advertisers`."""

    async def resolve(self, domain: str, *, platform: PlatformFilter = None, max_per_platform: Optional[int] = None) -> ResolveResponse:
        """A brand's advertiser ids on Meta, Google, TikTok, LinkedIn, Pinterest and X from its
        domain, each with a confidence ``score`` and ``match_reason``. ``max_per_platform`` 1 to
        10, default 3."""
        return cast(ResolveResponse, await self._request(E.resolve_advertisers(domain, platform, max_per_platform)))

    async def get(self, id: str, *, refresh: Optional[bool] = None) -> AdvertiserResponse:
        """An advertiser incl. active ads and ads known in the archive. ``refresh=True`` crawls the
        first page of its ads live before answering."""
        return cast(AdvertiserResponse, await self._request(E.get_advertiser(id, refresh)))

    async def ads(
        self,
        id: str,
        *,
        status: Optional[StatusFilter] = None,
        source: Optional[Source] = None,
        sort: Optional[Sort] = None,
        cursor: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> AdList:
        """All ads of an advertiser, live (default) or from history (``source="history"``, includes
        ads that vanished from the platform). ``limit`` 1 to 100. Paginated."""
        return cast(AdList, await self._request(E.advertiser_ads(id, status, source, sort, cursor, limit)))

    async def changes(
        self,
        id: str,
        *,
        since: DateLike,
        types: Optional[Sequence[EventType]] = None,
        cursor: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> EventList:
        """New, stopped and changed ads since a point in time (YYYY-MM-DD, RFC 3339, a date or a
        datetime). ``types`` defaults to started, stopped, changed. ``limit`` 1 to 200.
        Paginated."""
        return cast(EventList, await self._request(E.advertiser_changes(id, since, types, cursor, limit)))

    async def stats(self, id: str) -> AdvertiserStatsResponse:
        """Analytics from the history: ads by status, format, country and language; run-time
        distribution; new ads per week; and the 5 longest-running ads (likely winners)."""
        return cast(AdvertiserStatsResponse, await self._request(E.advertiser_stats(id)))

    async def timeline(
        self,
        id: str,
        *,
        date_from: DateLike = None,
        date_to: DateLike = None,
        cursor: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> EventList:
        """When which ads started and stopped. ``limit`` 1 to 200. Paginated."""
        return cast(EventList, await self._request(E.advertiser_timeline(id, date_from, date_to, cursor, limit)))
