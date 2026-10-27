from __future__ import annotations

import asyncio
import time
from types import TracebackType
from typing import (
    Any,
    AsyncIterator,
    Awaitable,
    Callable,
    Dict,
    Iterator,
    Optional,
    Set,
    Type,
    cast,
)

import httpx

from . import _base
from . import _endpoints as E
from ._base import DEFAULT_MAX_RETRIES, DEFAULT_TIMEOUT, ClientConfig, ResponseInfo, TimeoutTypes
from ._endpoints import DateLike, PlatformFilter, Request
from ._exceptions import APIConnectionError, APITimeoutError, RateLimitError
from .pagination import DEFAULT_MAX_PAGES, check_max_pages, next_cursor, page_items
from .resources import (
    Ads,
    Advertisers,
    AsyncAds,
    AsyncAdvertisers,
    AsyncBatch,
    AsyncDomains,
    AsyncWatchlists,
    AsyncWebhooks,
    Batch,
    Domains,
    Watchlists,
    Webhooks,
)
from .types import (
    AdFormat,
    AdList,
    PlatformsResponse,
    Sort,
    Source,
    StatusFilter,
    StatusResponse,
    UsageResponse,
)

__all__ = ["AdLib", "AsyncAdLib"]

OnResponse = Callable[[ResponseInfo], None]


def _check_max_retries(max_retries: int) -> int:
    if isinstance(max_retries, bool) or not isinstance(max_retries, int) or max_retries < 0:
        raise ValueError("max_retries must be an integer >= 0")
    return max_retries


class _ClientMixin:
    _config: ClientConfig
    max_retries: int
    _on_response: Optional[OnResponse]

    @property
    def base_url(self) -> str:
        return self._config.base_url

    def _request_args(self, request: Request) -> Dict[str, Any]:
        args: Dict[str, Any] = {
            "url": _base.build_url(self._config, request.path),
            "params": _base.clean_params(request.params),
            "headers": _base.build_headers(self._config),
        }
        if request.body is not None:
            args["json"] = request.body  # httpx sets Content-Type: application/json
        return args

    def _finish(self, response: httpx.Response) -> Any:
        body = _base.process_response(response)
        if self._on_response is not None:
            self._on_response(_base.response_info(response))
        return body

    def __repr__(self) -> str:
        return f"{type(self).__name__}(base_url={self.base_url!r})"


class AdLib(_ClientMixin):
    """Synchronous AdLib API client.

    ``api_key`` defaults to the ``ADLIB_API_KEY`` environment variable and is sent as the
    ``X-API-Key`` header. ``base_url`` defaults to ``ADLIB_BASE_URL``, else
    ``https://api.adlibapi.com`` (a trailing ``/v1`` is ignored).

    Every method returns the parsed JSON as dicts (typed with :mod:`adlib.types`).
    ``429 rate_limited`` is retried for every request (honouring ``Retry-After``); 502, 503,
    504, timeouts and network errors only for GET and DELETE. ``quota_exceeded`` is never
    retried. ``on_response`` is called with a :class:`~adlib.ResponseInfo` (billed credits,
    request id, rate limit) after every successful call.

    Use it as a context manager, or call :meth:`close` when done.
    """

    ads: Ads
    advertisers: Advertisers
    domains: Domains
    batch: Batch
    watchlists: Watchlists
    webhooks: Webhooks

    def __init__(
        self,
        api_key: Optional[str] = None,
        *,
        base_url: Optional[str] = None,
        timeout: TimeoutTypes = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        http_client: Optional[httpx.Client] = None,
        on_response: Optional[OnResponse] = None,
    ) -> None:
        self._config = _base.resolve_config(api_key, base_url)
        self.max_retries = _check_max_retries(max_retries)
        self.timeout = _base.make_timeout(timeout)
        self._on_response = on_response
        self._owns_http = http_client is None
        self._http = http_client or httpx.Client(timeout=self.timeout)
        self._sleep: Callable[[float], None] = time.sleep

        self.ads = Ads(self)
        self.advertisers = Advertisers(self)
        self.domains = Domains(self)
        self.batch = Batch(self)
        self.watchlists = Watchlists(self)
        self.webhooks = Webhooks(self)

    def _send(self, request: Request) -> Any:
        args = self._request_args(request)
        idempotent = request.idempotent
        attempt = 0
        while True:
            try:
                response = self._http.request(request.method, timeout=self.timeout, **args)
            except httpx.TimeoutException as exc:
                if attempt < self.max_retries and _base.can_retry_error(exc, idempotent):
                    self._sleep(_base.retry_delay(attempt))
                    attempt += 1
                    continue
                raise APITimeoutError(f"Request to the AdLib API timed out: {exc}") from exc
            except httpx.TransportError as exc:
                if attempt < self.max_retries and _base.can_retry_error(exc, idempotent):
                    self._sleep(_base.retry_delay(attempt))
                    attempt += 1
                    continue
                raise APIConnectionError(f"Could not reach the AdLib API: {exc}") from exc

            if attempt < self.max_retries:
                error = _base.retry_status_error(response, idempotent)
                if error is not None:
                    retry_after = error.retry_after if isinstance(error, RateLimitError) else None
                    self._sleep(_base.retry_delay(attempt, retry_after))
                    attempt += 1
                    continue
            return self._finish(response)

    def request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Sends a request to an endpoint this SDK does not wrap yet, with the same auth,
        retries and error handling."""
        return self._send(Request(method.upper(), path, params or {}, json))

    # --- top-level endpoints -------------------------------------------------

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
        """Searches ads. Same as :meth:`adlib.resources.Ads.search`. Paginated."""
        return self.ads.search(
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

    def usage(self, *, days: Optional[int] = None) -> UsageResponse:
        """Your billed credits per day and endpoint. ``days`` 1 to 92, default 30."""
        return cast(UsageResponse, self._send(E.usage(days)))

    def status(self) -> StatusResponse:
        """Health per platform (success rate, latency, last smoke test). Not billed."""
        return cast(StatusResponse, self._send(E.status()))

    def platforms(self) -> PlatformsResponse:
        """Supported search modes and filters per platform. Not billed."""
        return cast(PlatformsResponse, self._send(E.platforms()))

    # --- pagination -----------------------------------------------------------

    def paginate(
        self,
        method: Callable[..., Any],
        *args: Any,
        max_pages: Optional[int] = DEFAULT_MAX_PAGES,
        **kwargs: Any,
    ) -> Iterator[Any]:
        """Calls a paginated method repeatedly, following ``next_cursor``, and yields each page.

        ``method`` is any method that takes ``cursor``, e.g. ``client.ads.search``. Other
        arguments are passed through; pass ``cursor=`` to start from a saved cursor. Stops when
        ``next_cursor`` is ``None``, when it repeats, or after ``max_pages`` pages (default 10,
        ``None`` for no limit). Every page is a billed call.
        """
        check_max_pages(max_pages)
        cursor: Optional[str] = kwargs.pop("cursor", None)
        seen: Set[str] = set()
        pages = 0
        while max_pages is None or pages < max_pages:
            page = method(*args, cursor=cursor, **kwargs)
            pages += 1
            yield page
            nxt = next_cursor(page)
            if not nxt or nxt in seen or nxt == cursor:
                return
            seen.add(nxt)
            cursor = nxt

    def paginate_items(
        self,
        method: Callable[..., Any],
        *args: Any,
        max_pages: Optional[int] = DEFAULT_MAX_PAGES,
        **kwargs: Any,
    ) -> Iterator[Any]:
        """Like :meth:`paginate`, but yields the items of each page one by one (``data`` of
        list responses, ``items`` of a batch job)."""
        for page in self.paginate(method, *args, max_pages=max_pages, **kwargs):
            yield from page_items(page)

    def close(self) -> None:
        """Closes the underlying HTTP client (unless you passed your own ``http_client``)."""
        if self._owns_http:
            self._http.close()

    def __enter__(self) -> "AdLib":
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc: Optional[BaseException],
        tb: Optional[TracebackType],
    ) -> None:
        self.close()


class AsyncAdLib(_ClientMixin):
    """Asynchronous AdLib API client. Same arguments and methods as :class:`AdLib`, but every
    API method is a coroutine and :meth:`paginate` / :meth:`paginate_items` are async iterators.

    Use it as an async context manager, or call ``await client.aclose()`` when done.
    """

    ads: AsyncAds
    advertisers: AsyncAdvertisers
    domains: AsyncDomains
    batch: AsyncBatch
    watchlists: AsyncWatchlists
    webhooks: AsyncWebhooks

    def __init__(
        self,
        api_key: Optional[str] = None,
        *,
        base_url: Optional[str] = None,
        timeout: TimeoutTypes = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        http_client: Optional[httpx.AsyncClient] = None,
        on_response: Optional[OnResponse] = None,
    ) -> None:
        self._config = _base.resolve_config(api_key, base_url)
        self.max_retries = _check_max_retries(max_retries)
        self.timeout = _base.make_timeout(timeout)
        self._on_response = on_response
        self._owns_http = http_client is None
        self._http = http_client or httpx.AsyncClient(timeout=self.timeout)
        self._sleep: Callable[[float], Awaitable[None]] = asyncio.sleep

        self.ads = AsyncAds(self)
        self.advertisers = AsyncAdvertisers(self)
        self.domains = AsyncDomains(self)
        self.batch = AsyncBatch(self)
        self.watchlists = AsyncWatchlists(self)
        self.webhooks = AsyncWebhooks(self)

    async def _send(self, request: Request) -> Any:
        args = self._request_args(request)
        idempotent = request.idempotent
        attempt = 0
        while True:
            try:
                response = await self._http.request(request.method, timeout=self.timeout, **args)
            except httpx.TimeoutException as exc:
                if attempt < self.max_retries and _base.can_retry_error(exc, idempotent):
                    await self._sleep(_base.retry_delay(attempt))
                    attempt += 1
                    continue
                raise APITimeoutError(f"Request to the AdLib API timed out: {exc}") from exc
            except httpx.TransportError as exc:
                if attempt < self.max_retries and _base.can_retry_error(exc, idempotent):
                    await self._sleep(_base.retry_delay(attempt))
                    attempt += 1
                    continue
                raise APIConnectionError(f"Could not reach the AdLib API: {exc}") from exc

            if attempt < self.max_retries:
                error = _base.retry_status_error(response, idempotent)
                if error is not None:
                    retry_after = error.retry_after if isinstance(error, RateLimitError) else None
                    await self._sleep(_base.retry_delay(attempt, retry_after))
                    attempt += 1
                    continue
            return self._finish(response)

    async def request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Sends a request to an endpoint this SDK does not wrap yet."""
        return await self._send(Request(method.upper(), path, params or {}, json))

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
        """Searches ads. Same as :meth:`adlib.resources.AsyncAds.search`. Paginated."""
        return await self.ads.search(
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

    async def usage(self, *, days: Optional[int] = None) -> UsageResponse:
        """Your billed credits per day and endpoint. ``days`` 1 to 92, default 30."""
        return cast(UsageResponse, await self._send(E.usage(days)))

    async def status(self) -> StatusResponse:
        """Health per platform (success rate, latency, last smoke test). Not billed."""
        return cast(StatusResponse, await self._send(E.status()))

    async def platforms(self) -> PlatformsResponse:
        """Supported search modes and filters per platform. Not billed."""
        return cast(PlatformsResponse, await self._send(E.platforms()))

    async def paginate(
        self,
        method: Callable[..., Awaitable[Any]],
        *args: Any,
        max_pages: Optional[int] = DEFAULT_MAX_PAGES,
        **kwargs: Any,
    ) -> AsyncIterator[Any]:
        """Async version of :meth:`AdLib.paginate`."""
        check_max_pages(max_pages)
        cursor: Optional[str] = kwargs.pop("cursor", None)
        seen: Set[str] = set()
        pages = 0
        while max_pages is None or pages < max_pages:
            page = await method(*args, cursor=cursor, **kwargs)
            pages += 1
            yield page
            nxt = next_cursor(page)
            if not nxt or nxt in seen or nxt == cursor:
                return
            seen.add(nxt)
            cursor = nxt

    async def paginate_items(
        self,
        method: Callable[..., Awaitable[Any]],
        *args: Any,
        max_pages: Optional[int] = DEFAULT_MAX_PAGES,
        **kwargs: Any,
    ) -> AsyncIterator[Any]:
        """Async version of :meth:`AdLib.paginate_items`."""
        async for page in self.paginate(method, *args, max_pages=max_pages, **kwargs):
            for item in page_items(page):
                yield item

    async def aclose(self) -> None:
        """Closes the underlying HTTP client (unless you passed your own ``http_client``)."""
        if self._owns_http:
            await self._http.aclose()

    async def __aenter__(self) -> "AsyncAdLib":
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc: Optional[BaseException],
        tb: Optional[TracebackType],
    ) -> None:
        await self.aclose()
