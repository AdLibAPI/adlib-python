from __future__ import annotations

from typing import Optional, Sequence, cast

from .. import _endpoints as E
from ..types import WatchlistResponse, WatchlistsResponse
from ._base import AsyncResource, SyncResource

__all__ = ["Watchlists", "AsyncWatchlists"]


class Watchlists(SyncResource):
    """Watchlists: advertisers are crawled regularly; changes go to your webhook or by email."""

    def list(self) -> WatchlistsResponse:
        """Your watchlists."""
        return cast(WatchlistsResponse, self._request(E.list_watchlists()))

    def create(
        self,
        *,
        advertisers: Sequence[str],
        name: Optional[str] = None,
        webhook_url: Optional[str] = None,
        interval_hours: Optional[int] = None,
        archive_videos: Optional[bool] = None,
        email_alerts: Optional[bool] = None,
    ) -> WatchlistResponse:
        """Creates a watchlist. ``advertisers`` are ids ``<platform>:<id>`` (find them with
        ``advertisers.resolve``). ``webhook_url`` receives ``advertiser.changes`` events.
        ``interval_hours`` 1 to 168 (default 24). ``archive_videos`` keeps full video files
        (default true). ``email_alerts`` mails a digest of each crawl's changes (new, stopped,
        changed, removed ads) to your account's email. Not retried on 5xx, so it is never created
        twice."""
        return cast(WatchlistResponse, self._request(E.create_watchlist(advertisers, name, webhook_url, interval_hours, archive_videos, email_alerts)))

    def get(self, id: str) -> WatchlistResponse:
        """A watchlist with the crawl status of each advertiser."""
        return cast(WatchlistResponse, self._request(E.get_watchlist(id)))

    def update(
        self,
        id: str,
        *,
        name: Optional[str] = None,
        webhook_url: Optional[str] = None,
        email_alerts: Optional[bool] = None,
    ) -> WatchlistResponse:
        """Changes a watchlist's name, webhook or email alerts; arguments left out stay as they are.
        ``webhook_url=""`` removes the webhook (Slack and Discord webhooks get a readable
        message)."""
        return cast(WatchlistResponse, self._request(E.update_watchlist(id, name, webhook_url, email_alerts)))

    def delete(self, id: str) -> None:
        """Deletes a watchlist."""
        self._request(E.delete_watchlist(id))

    def add_advertisers(self, id: str, advertisers: Sequence[str]) -> WatchlistResponse:
        """Adds advertisers to a watchlist."""
        return cast(WatchlistResponse, self._request(E.add_watchlist_advertisers(id, advertisers)))

    def remove_advertiser(self, id: str, advertiser_id: str) -> None:
        """Removes an advertiser from a watchlist."""
        self._request(E.remove_watchlist_advertiser(id, advertiser_id))


class AsyncWatchlists(AsyncResource):
    """Async version of :class:`Watchlists`."""

    async def list(self) -> WatchlistsResponse:
        """Your watchlists."""
        return cast(WatchlistsResponse, await self._request(E.list_watchlists()))

    async def create(
        self,
        *,
        advertisers: Sequence[str],
        name: Optional[str] = None,
        webhook_url: Optional[str] = None,
        interval_hours: Optional[int] = None,
        archive_videos: Optional[bool] = None,
        email_alerts: Optional[bool] = None,
    ) -> WatchlistResponse:
        """Creates a watchlist. ``advertisers`` are ids ``<platform>:<id>`` (find them with
        ``advertisers.resolve``). ``webhook_url`` receives ``advertiser.changes`` events.
        ``interval_hours`` 1 to 168 (default 24). ``archive_videos`` keeps full video files
        (default true). ``email_alerts`` mails a digest of each crawl's changes (new, stopped,
        changed, removed ads) to your account's email. Not retried on 5xx, so it is never created
        twice."""
        return cast(WatchlistResponse, await self._request(E.create_watchlist(advertisers, name, webhook_url, interval_hours, archive_videos, email_alerts)))

    async def get(self, id: str) -> WatchlistResponse:
        """A watchlist with the crawl status of each advertiser."""
        return cast(WatchlistResponse, await self._request(E.get_watchlist(id)))

    async def update(
        self,
        id: str,
        *,
        name: Optional[str] = None,
        webhook_url: Optional[str] = None,
        email_alerts: Optional[bool] = None,
    ) -> WatchlistResponse:
        """Changes a watchlist's name, webhook or email alerts; arguments left out stay as they are.
        ``webhook_url=""`` removes the webhook (Slack and Discord webhooks get a readable
        message)."""
        return cast(WatchlistResponse, await self._request(E.update_watchlist(id, name, webhook_url, email_alerts)))

    async def delete(self, id: str) -> None:
        """Deletes a watchlist."""
        await self._request(E.delete_watchlist(id))

    async def add_advertisers(self, id: str, advertisers: Sequence[str]) -> WatchlistResponse:
        """Adds advertisers to a watchlist."""
        return cast(WatchlistResponse, await self._request(E.add_watchlist_advertisers(id, advertisers)))

    async def remove_advertiser(self, id: str, advertiser_id: str) -> None:
        """Removes an advertiser from a watchlist."""
        await self._request(E.remove_watchlist_advertiser(id, advertiser_id))
