from __future__ import annotations

from typing import Optional, cast

from .. import _endpoints as E
from .._endpoints import PlatformFilter
from ..types import CompanyResponse
from ._base import AsyncResource, SyncResource

__all__ = ["Companies", "AsyncCompanies"]


class Companies(SyncResource):
    """Companies: all ad accounts of a domain across platforms, with combined stats."""

    def get(
        self,
        domain: str,
        *,
        platform: PlatformFilter = None,
        min_score: Optional[float] = None,
        max_per_platform: Optional[int] = None,
    ) -> CompanyResponse:
        """Resolves the domain (like ``advertisers.resolve``, including our manual corrections),
        keeps accounts with score >= ``min_score`` (0 to 1, default 0.75) and aggregates their
        history: totals, platforms, countries, formats, weekly launches and the longest-running
        ads. Accounts below the threshold are listed as ``candidates``. ``max_per_platform`` 1 to
        10, default 5. Costs one resolve plus one stats call."""
        return cast(CompanyResponse, self._request(E.get_company(domain, platform, min_score, max_per_platform)))


class AsyncCompanies(AsyncResource):
    """Async version of :class:`Companies`."""

    async def get(
        self,
        domain: str,
        *,
        platform: PlatformFilter = None,
        min_score: Optional[float] = None,
        max_per_platform: Optional[int] = None,
    ) -> CompanyResponse:
        """Resolves the domain (like ``advertisers.resolve``, including our manual corrections),
        keeps accounts with score >= ``min_score`` (0 to 1, default 0.75) and aggregates their
        history: totals, platforms, countries, formats, weekly launches and the longest-running
        ads. Accounts below the threshold are listed as ``candidates``. ``max_per_platform`` 1 to
        10, default 5. Costs one resolve plus one stats call."""
        return cast(CompanyResponse, await self._request(E.get_company(domain, platform, min_score, max_per_platform)))
