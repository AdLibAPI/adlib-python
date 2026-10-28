from __future__ import annotations

from typing import Optional, Sequence, cast

from .. import _endpoints as E
from .._endpoints import DateLike, PlatformFilter
from ..types import (
    CsvPage,
    AdList,
    AdvertiserResponse,
    AdvertiserStatsResponse,
    EventList,
    EventType,
    ReportKind,
    ReportRole,
    ResolveReportResponse,
    ResolveReportsResponse,
    ResolveResponse,
    Sort,
    Source,
    StatusFilter,
)
from ._base import AsyncResource, SyncResource

__all__ = ["Advertisers", "AsyncAdvertisers"]


class Advertisers(SyncResource):
    """Advertisers: resolve a domain (and report wrong matches), profiles, ads, changes, stats and
    timelines."""

    def resolve(self, domain: str, *, platform: PlatformFilter = None, max_per_platform: Optional[int] = None) -> ResolveResponse:
        """A brand's advertiser ids on Meta, Google, TikTok, LinkedIn, Pinterest and X from its
        domain, each with a confidence ``score`` and ``match_reason``. ``max_per_platform`` 1 to
        10, default 3."""
        return cast(ResolveResponse, self._request(E.resolve_advertisers(domain, platform, max_per_platform)))

    def report_match(
        self,
        domain: str,
        *,
        kind: ReportKind,
        advertiser_id: Optional[str] = None,
        role: Optional[ReportRole] = None,
        note: Optional[str] = None,
    ) -> ResolveReportResponse:
        """Reports a wrong or missing resolve match. ``kind="wrong_match"``: ``advertiser_id``
        (``<platform>:<id>``, required) does not belong to the domain. ``kind="missing_match"``:
        the domain's account is missing (``advertiser_id`` and ``role`` if you know them).
        ``kind="wrong_role"``: the account belongs to the domain but has the wrong role, e.g. an
        agency shown as the brand (``advertiser_id`` and ``role`` required). ``note`` up to 1000
        characters. We review reports; accepted ones change the resolve for everyone. Up to 50
        per day, free. Not retried on 5xx, so it is never sent twice."""
        return cast(ResolveReportResponse, self._request(E.report_match(domain, kind, advertiser_id, role, note)))

    def list_reports(self) -> ResolveReportsResponse:
        """Your last 100 resolve reports and how we resolved them, newest first. Free."""
        return cast(ResolveReportsResponse, self._request(E.list_reports()))

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

    def ads_csv(
        self,
        id: str,
        *,
        status: Optional[StatusFilter] = None,
        source: Optional[Source] = None,
        sort: Optional[Sort] = None,
        cursor: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> CsvPage:
        """Like :meth:`ads`, as CSV (``output=csv``): ``{"csv": ..., "next_cursor": ...}``
        with the cursor of the next page from the X-Next-Cursor header. Billed like JSON."""
        return cast(CsvPage, self._request_csv(E.advertiser_ads(id, status, source, sort, cursor, limit)))

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

    def changes_csv(
        self,
        id: str,
        *,
        since: DateLike,
        types: Optional[Sequence[EventType]] = None,
        cursor: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> CsvPage:
        """Like :meth:`changes`, as CSV (``output=csv``): ``{"csv": ..., "next_cursor": ...}``
        with the cursor of the next page from the X-Next-Cursor header. Billed like JSON."""
        return cast(CsvPage, self._request_csv(E.advertiser_changes(id, since, types, cursor, limit)))

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


    def timeline_csv(
        self,
        id: str,
        *,
        date_from: DateLike = None,
        date_to: DateLike = None,
        cursor: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> CsvPage:
        """Like :meth:`timeline`, as CSV (``output=csv``): ``{"csv": ..., "next_cursor": ...}``
        with the cursor of the next page from the X-Next-Cursor header. Billed like JSON."""
        return cast(CsvPage, self._request_csv(E.advertiser_timeline(id, date_from, date_to, cursor, limit)))

class AsyncAdvertisers(AsyncResource):
    """Async version of :class:`Advertisers`."""

    async def resolve(self, domain: str, *, platform: PlatformFilter = None, max_per_platform: Optional[int] = None) -> ResolveResponse:
        """A brand's advertiser ids on Meta, Google, TikTok, LinkedIn, Pinterest and X from its
        domain, each with a confidence ``score`` and ``match_reason``. ``max_per_platform`` 1 to
        10, default 3."""
        return cast(ResolveResponse, await self._request(E.resolve_advertisers(domain, platform, max_per_platform)))

    async def report_match(
        self,
        domain: str,
        *,
        kind: ReportKind,
        advertiser_id: Optional[str] = None,
        role: Optional[ReportRole] = None,
        note: Optional[str] = None,
    ) -> ResolveReportResponse:
        """Reports a wrong or missing resolve match. ``kind="wrong_match"``: ``advertiser_id``
        (``<platform>:<id>``, required) does not belong to the domain. ``kind="missing_match"``:
        the domain's account is missing (``advertiser_id`` and ``role`` if you know them).
        ``kind="wrong_role"``: the account belongs to the domain but has the wrong role, e.g. an
        agency shown as the brand (``advertiser_id`` and ``role`` required). ``note`` up to 1000
        characters. We review reports; accepted ones change the resolve for everyone. Up to 50
        per day, free. Not retried on 5xx, so it is never sent twice."""
        return cast(ResolveReportResponse, await self._request(E.report_match(domain, kind, advertiser_id, role, note)))

    async def list_reports(self) -> ResolveReportsResponse:
        """Your last 100 resolve reports and how we resolved them, newest first. Free."""
        return cast(ResolveReportsResponse, await self._request(E.list_reports()))

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

    async def ads_csv(
        self,
        id: str,
        *,
        status: Optional[StatusFilter] = None,
        source: Optional[Source] = None,
        sort: Optional[Sort] = None,
        cursor: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> CsvPage:
        """Like :meth:`ads`, as CSV (``output=csv``): ``{"csv": ..., "next_cursor": ...}``
        with the cursor of the next page from the X-Next-Cursor header. Billed like JSON."""
        return cast(CsvPage, await self._request_csv(E.advertiser_ads(id, status, source, sort, cursor, limit)))

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

    async def changes_csv(
        self,
        id: str,
        *,
        since: DateLike,
        types: Optional[Sequence[EventType]] = None,
        cursor: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> CsvPage:
        """Like :meth:`changes`, as CSV (``output=csv``): ``{"csv": ..., "next_cursor": ...}``
        with the cursor of the next page from the X-Next-Cursor header. Billed like JSON."""
        return cast(CsvPage, await self._request_csv(E.advertiser_changes(id, since, types, cursor, limit)))

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

    async def timeline_csv(
        self,
        id: str,
        *,
        date_from: DateLike = None,
        date_to: DateLike = None,
        cursor: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> CsvPage:
        """Like :meth:`timeline`, as CSV (``output=csv``): ``{"csv": ..., "next_cursor": ...}``
        with the cursor of the next page from the X-Next-Cursor header. Billed like JSON."""
        return cast(CsvPage, await self._request_csv(E.advertiser_timeline(id, date_from, date_to, cursor, limit)))
