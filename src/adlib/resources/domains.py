from __future__ import annotations

from typing import Optional, cast

from .. import _endpoints as E
from .._endpoints import PlatformFilter
from ..types import DomainCheckResponse, DomainSuggestionsResponse
from ._base import AsyncResource, SyncResource

__all__ = ["Domains", "AsyncDomains"]


class Domains(SyncResource):
    """Domains: is this company advertising right now, and where?"""

    def check(self, domain: str, *, platform: PlatformFilter = None) -> DomainCheckResponse:
        """Resolves the domain on all platforms and checks for current ads. Built for lead
        enrichment: one flat price per check, free if nothing could be checked."""
        return cast(DomainCheckResponse, self._request(E.check_domain(domain, platform)))

    def suggest(self, q: str, *, limit: Optional[int] = None) -> DomainSuggestionsResponse:
        """Domain suggestions from our index while typing (free). Prefix match on domains and
        advertiser names we already know, most archived ads first. ``q`` 2 to 100 characters,
        ``limit`` 1 to 20 (default 8)."""
        return cast(DomainSuggestionsResponse, self._request(E.suggest_domains(q, limit)))


class AsyncDomains(AsyncResource):
    """Async version of :class:`Domains`."""

    async def check(self, domain: str, *, platform: PlatformFilter = None) -> DomainCheckResponse:
        """Resolves the domain on all platforms and checks for current ads. Built for lead
        enrichment: one flat price per check, free if nothing could be checked."""
        return cast(DomainCheckResponse, await self._request(E.check_domain(domain, platform)))

    async def suggest(self, q: str, *, limit: Optional[int] = None) -> DomainSuggestionsResponse:
        """Domain suggestions from our index while typing (free). Prefix match on domains and
        advertiser names we already know, most archived ads first. ``q`` 2 to 100 characters,
        ``limit`` 1 to 20 (default 8)."""
        return cast(DomainSuggestionsResponse, await self._request(E.suggest_domains(q, limit)))
