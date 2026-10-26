from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .._endpoints import Request

if TYPE_CHECKING:
    from .._client import AdLib, AsyncAdLib


class SyncResource:
    def __init__(self, client: "AdLib") -> None:
        self._client = client

    def _request(self, request: Request) -> Any:
        return self._client._send(request)


class AsyncResource:
    def __init__(self, client: "AsyncAdLib") -> None:
        self._client = client

    async def _request(self, request: Request) -> Any:
        return await self._client._send(request)
