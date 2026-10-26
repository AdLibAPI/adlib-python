from __future__ import annotations

from typing import cast

from .. import _endpoints as E
from .._endpoints import PlatformFilter
from ..types import DomainCheckResponse
from ._base import AsyncResource, SyncResource

__all__ = ["Domains", "AsyncDomains"]


class Domains(SyncResource):
    """Domains: is this company advertising right now, and where?"""

    def check(self, domain: str, *, platform: PlatformFilter = None) -> DomainCheckResponse:
        """Resolves the domain on all platforms and checks for current ads. Built for lead
        enrichment: one flat price per check, free if nothing could be checked."""
        return cast(DomainCheckResponse, self._request(E.check_domain(domain, platform)))


class AsyncDomains(AsyncResource):
    """Async version of :class:`Domains`."""

    async def check(self, domain: str, *, platform: PlatformFilter = None) -> DomainCheckResponse:
        """Resolves the domain on all platforms and checks for current ads. Built for lead
        enrichment: one flat price per check, free if nothing could be checked."""
        return cast(DomainCheckResponse, await self._request(E.check_domain(domain, platform)))
