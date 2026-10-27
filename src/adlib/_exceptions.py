"""Exceptions raised by the AdLib client.

Every exception the client raises on purpose is a subclass of :class:`AdLibError`, so
``except adlib.AdLibError`` catches all of them. API errors carry the fields of the API's error
shape ``{"error": {"code", "message", "request_id", "billed"}}``.
"""

from __future__ import annotations

from typing import Any, List, Optional

import httpx

__all__ = [
    "AdLibError",
    "APIConnectionError",
    "APITimeoutError",
    "APIStatusError",
    "ValidationError",
    "AuthenticationError",
    "PermissionDeniedError",
    "InsufficientCreditsError",
    "NotFoundError",
    "RateLimitError",
    "QuotaExceededError",
    "ServerError",
    "WebhookSignatureError",
]


class AdLibError(Exception):
    """Base class for all errors raised by this package."""

    message: str
    status_code: Optional[int]
    code: Optional[str]
    request_id: Optional[str]
    billed: Optional[bool]
    platform: Optional[str]
    details: Optional[List[str]]
    body: Any
    response: Optional[httpx.Response]

    def __init__(
        self,
        message: str,
        *,
        status_code: Optional[int] = None,
        code: Optional[str] = None,
        request_id: Optional[str] = None,
        billed: Optional[bool] = None,
        platform: Optional[str] = None,
        details: Optional[List[str]] = None,
        body: Any = None,
        response: Optional[httpx.Response] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.code = code
        self.request_id = request_id
        self.billed = billed
        self.platform = platform
        self.details = details
        self.body = body
        self.response = response

    def __str__(self) -> str:
        parts = []
        if self.status_code is not None:
            parts.append(f"HTTP {self.status_code}")
        if self.code:
            parts.append(self.code)
        if self.request_id:
            parts.append(f"request_id {self.request_id}")
        return f"{self.message} ({', '.join(parts)})" if parts else self.message


class APIConnectionError(AdLibError):
    """The request never got a response (DNS, connection refused, TLS, dropped connection)."""


class APITimeoutError(APIConnectionError):
    """The request timed out."""


class APIStatusError(AdLibError):
    """The API answered with a 4xx or 5xx status. More specific subclasses exist for common codes."""

    status_code: int


class ValidationError(APIStatusError):
    """400 or 422: the API rejected the parameters. ``code == "unsupported"`` means the platform
    cannot do this query or filter (see ``client.platforms()``)."""


class AuthenticationError(APIStatusError):
    """401: the API key is missing or wrong."""


class PermissionDeniedError(APIStatusError):
    """403: the key is disabled or not allowed to make this call. ``code == "history_limit"``
    means the ad is older than your plan's archive window (free 90 days, starter 365 days, growth
    and up unlimited)."""


class InsufficientCreditsError(APIStatusError):
    """402: no credits left on the account."""


class NotFoundError(APIStatusError):
    """404: unknown ad, advertiser, job, watchlist or delivery id."""


class RateLimitError(APIStatusError):
    """429 ``rate_limited``: too many requests. ``retry_after`` is the wait in seconds, if sent."""

    retry_after: Optional[float]

    def __init__(self, message: str, *, retry_after: Optional[float] = None, **kwargs: Any) -> None:
        super().__init__(message, **kwargs)
        self.retry_after = retry_after


class QuotaExceededError(RateLimitError):
    """429 ``quota_exceeded``: the monthly credit quota of the plan is used up. Never retried."""


class ServerError(APIStatusError):
    """5xx. 502 and 503 usually mean an ad platform failed or is paused; retry later or use
    ``source="history"``."""


class WebhookSignatureError(AdLibError):
    """A webhook signature is missing, malformed, too old, or does not match."""
