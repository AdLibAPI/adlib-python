from __future__ import annotations

from typing import Optional, Sequence, cast

from .. import _endpoints as E
from ..types import BatchCreatedResponse, BatchOptions, BatchResponse, BatchType
from ._base import AsyncResource, SyncResource

__all__ = ["Batch", "AsyncBatch"]


class Batch(SyncResource):
    """Asynchronous batch jobs for many advertisers, domains or ad ids."""

    def create(
        self,
        *,
        type: BatchType,
        items: Sequence[str],
        options: Optional[BatchOptions] = None,
        webhook_url: Optional[str] = None,
    ) -> BatchCreatedResponse:
        """Starts a batch job. ``items`` are advertiser ids (``<platform>:<id>``), domains or ad
        ids; the limit depends on your plan. ``webhook_url`` gets a signed ``batch.completed``
        event. Billed per delivered result (same prices as the synchronous endpoints), not per
        job. Not retried on 5xx, so a job is never started twice."""
        return cast(BatchCreatedResponse, self._request(E.create_batch(type, items, options, webhook_url)))

    def get(self, job_id: str, *, cursor: Optional[str] = None, limit: Optional[int] = None) -> BatchResponse:
        """Job status and results; ``items`` are paginated (``limit`` 1 to 100, default 20).
        Finished jobs are kept for 30 days."""
        return cast(BatchResponse, self._request(E.get_batch(job_id, cursor, limit)))


class AsyncBatch(AsyncResource):
    """Async version of :class:`Batch`."""

    async def create(
        self,
        *,
        type: BatchType,
        items: Sequence[str],
        options: Optional[BatchOptions] = None,
        webhook_url: Optional[str] = None,
    ) -> BatchCreatedResponse:
        """Starts a batch job. ``items`` are advertiser ids (``<platform>:<id>``), domains or ad
        ids; the limit depends on your plan. ``webhook_url`` gets a signed ``batch.completed``
        event. Billed per delivered result (same prices as the synchronous endpoints), not per
        job. Not retried on 5xx, so a job is never started twice."""
        return cast(BatchCreatedResponse, await self._request(E.create_batch(type, items, options, webhook_url)))

    async def get(self, job_id: str, *, cursor: Optional[str] = None, limit: Optional[int] = None) -> BatchResponse:
        """Job status and results; ``items`` are paginated (``limit`` 1 to 100, default 20).
        Finished jobs are kept for 30 days."""
        return cast(BatchResponse, await self._request(E.get_batch(job_id, cursor, limit)))
