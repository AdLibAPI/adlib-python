"""Shared logic for the sync and async clients: configuration, request building, error
mapping and retry timing. Nothing in here does I/O."""

from __future__ import annotations

import email.utils
import json
import os
import random
import re
import time
from dataclasses import dataclass
from typing import Any, Dict, Mapping, Optional, Union

import httpx

from ._exceptions import (
    AdLibError,
    APIStatusError,
    AuthenticationError,
    InsufficientCreditsError,
    NotFoundError,
    PermissionDeniedError,
    QuotaExceededError,
    RateLimitError,
    ServerError,
    ValidationError,
)
from ._version import __version__

DEFAULT_BASE_URL = "https://api.example.com"
# Live searches across all platforms can take a while.
DEFAULT_TIMEOUT = 120.0
DEFAULT_MAX_RETRIES = 2

# Backoff for retries without a Retry-After header: 0.5s, 1s, 2s, ... capped, plus jitter.
INITIAL_RETRY_DELAY = 0.5
MAX_RETRY_DELAY = 8.0
# Upper bound for honoring a server-sent Retry-After, so a bad header cannot stall a script.
MAX_RETRY_AFTER = 60.0
RETRYABLE_STATUSES = (502, 503, 504)

ENV_API_KEY = "ADLIB_API_KEY"
ENV_BASE_URL = "ADLIB_BASE_URL"
API_KEY_HEADER = "X-API-Key"

USER_AGENT = f"adlib-python/{__version__}"

TimeoutTypes = Union[float, httpx.Timeout, None]
QueryValue = Union[str, int, float, bool]


@dataclass(frozen=True)
class ClientConfig:
    api_key: str
    base_url: str

    def __repr__(self) -> str:
        return f"ClientConfig(api_key=<hidden>, base_url={self.base_url!r})"


@dataclass(frozen=True)
class ResponseInfo:
    """Billing and rate-limit headers of a successful response (see ``on_response``)."""

    method: str
    url: str
    status_code: int
    request_id: Optional[str]
    """X-Request-Id, for support requests."""
    billed_credits: Optional[int]
    """X-Billing-Credits: what this call cost. Empty results, cached results and platform
    errors are free."""
    rate_limit_limit: Optional[int]
    rate_limit_remaining: Optional[int]
    rate_limit_reset: Optional[int]
    headers: httpx.Headers


def _clean(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    value = value.strip()
    return value or None


_V1_SUFFIX = re.compile(r"/v1$", re.IGNORECASE)


def normalize_base_url(value: str) -> str:
    """Strips trailing slashes and a trailing ``/v1``."""
    return _V1_SUFFIX.sub("", value.strip().rstrip("/"))


def resolve_config(
    api_key: Optional[str], base_url: Optional[str], env: Optional[Mapping[str, str]] = None
) -> ClientConfig:
    """Explicit arguments win over the ADLIB_API_KEY and ADLIB_BASE_URL environment variables."""
    env = os.environ if env is None else env
    key = _clean(api_key) or _clean(env.get(ENV_API_KEY))
    if not key:
        raise AdLibError(
            f"No API key found. Pass api_key=... or set the {ENV_API_KEY} environment variable."
        )
    url = _clean(base_url) or _clean(env.get(ENV_BASE_URL)) or DEFAULT_BASE_URL
    return ClientConfig(api_key=key, base_url=normalize_base_url(url))


def build_headers(config: ClientConfig) -> Dict[str, str]:
    return {"Accept": "application/json", "User-Agent": USER_AGENT, API_KEY_HEADER: config.api_key}


def build_url(config: ClientConfig, path: str) -> str:
    return config.base_url + (path if path.startswith("/") else "/" + path)


def clean_params(params: Mapping[str, Optional[QueryValue]]) -> Dict[str, Union[str, int, float]]:
    """Drops ``None`` and empty values; booleans become ``true``/``false``."""
    out: Dict[str, Union[str, int, float]] = {}
    for key, value in params.items():
        if value is None or value == "":
            continue
        out[key] = ("true" if value else "false") if isinstance(value, bool) else value
    return out


def make_timeout(timeout: TimeoutTypes) -> httpx.Timeout:
    if isinstance(timeout, httpx.Timeout):
        return timeout
    return httpx.Timeout(timeout)


# ---------------------------------------------------------------------------
# Responses and errors
# ---------------------------------------------------------------------------


def _parse_body(response: httpx.Response) -> Any:
    text = response.text
    if not text.strip():
        return None
    try:
        return json.loads(text)
    except ValueError:
        return text


def _str(value: Any) -> Optional[str]:
    return value.strip() if isinstance(value, str) and value.strip() else None


def parse_error_body(body: Any) -> Dict[str, Any]:
    """Reads ``{"error": {code, message, request_id, billed, platform, details}}``. Also
    tolerates ``{"error": "..."}``, ``{"message": "..."}`` and plain text."""
    if isinstance(body, dict):
        err = body.get("error")
        if isinstance(err, dict):
            details = err.get("details")
            return {
                "code": _str(err.get("code")),
                "message": _str(err.get("message")),
                "request_id": _str(err.get("request_id")),
                "billed": err.get("billed") if isinstance(err.get("billed"), bool) else None,
                "platform": _str(err.get("platform")),
                "details": [d for d in details if isinstance(d, str)]
                if isinstance(details, list)
                else None,
            }
        message = _str(err) or _str(body.get("message"))
        return {"message": message} if message else {}
    if isinstance(body, str) and body.strip():
        text = body.strip()
        return {"message": text if len(text) <= 500 else text[:500] + "..."}
    return {}


def parse_retry_after(value: Optional[str]) -> Optional[float]:
    """Parses a Retry-After header given in seconds or as an HTTP date."""
    if not value:
        return None
    value = value.strip()
    try:
        seconds = float(value)
    except ValueError:
        try:
            parsed = email.utils.parsedate_to_datetime(value)
        except (TypeError, ValueError, IndexError):
            return None
        if parsed is None:
            return None
        seconds = parsed.timestamp() - time.time()
    return max(seconds, 0.0)


_DEFAULT_MESSAGES = {
    400: "Bad request. Check the parameters you passed.",
    401: "Authentication failed. Check your API key.",
    402: "No credits left on this account.",
    403: "Access denied. The key may be disabled.",
    404: "Not found.",
    422: "Invalid parameters.",
    429: "Rate limit hit. Wait before retrying.",
}


def make_status_error(response: httpx.Response) -> APIStatusError:
    status = response.status_code
    body = _parse_body(response)
    parsed = parse_error_body(body)
    message = parsed.get("message") or _DEFAULT_MESSAGES.get(status) or (
        "The AdLib API returned a server error. This is usually temporary."
        if status >= 500
        else f"Request failed with status {status}."
    )
    kwargs: Dict[str, Any] = {
        "status_code": status,
        "code": parsed.get("code"),
        "request_id": parsed.get("request_id") or response.headers.get("x-request-id"),
        "billed": parsed.get("billed"),
        "platform": parsed.get("platform"),
        "details": parsed.get("details"),
        "body": body,
        "response": response,
    }
    if status in (400, 422):
        return ValidationError(message, **kwargs)
    if status == 401:
        return AuthenticationError(message, **kwargs)
    if status == 402:
        return InsufficientCreditsError(message, **kwargs)
    if status == 403:
        return PermissionDeniedError(message, **kwargs)
    if status == 404:
        return NotFoundError(message, **kwargs)
    if status == 429:
        retry_after = parse_retry_after(response.headers.get("retry-after"))
        cls = QuotaExceededError if kwargs["code"] == "quota_exceeded" else RateLimitError
        return cls(message, retry_after=retry_after, **kwargs)
    if status >= 500:
        return ServerError(message, **kwargs)
    return APIStatusError(message, **kwargs)


def process_response(response: httpx.Response) -> Any:
    """Returns the parsed JSON body (``None`` for 204), or raises the matching exception."""
    if response.status_code >= 400:
        raise make_status_error(response)
    body = _parse_body(response)
    if isinstance(body, str):
        raise AdLibError(
            "Expected a JSON response but got something else.",
            status_code=response.status_code,
            request_id=response.headers.get("x-request-id"),
            body=body,
            response=response,
        )
    return body


def _header_int(headers: httpx.Headers, name: str) -> Optional[int]:
    raw = headers.get(name)
    if raw is None:
        return None
    try:
        return int(raw.strip())
    except ValueError:
        return None


def response_info(response: httpx.Response) -> ResponseInfo:
    return ResponseInfo(
        method=response.request.method,
        url=str(response.request.url),
        status_code=response.status_code,
        request_id=response.headers.get("x-request-id"),
        billed_credits=_header_int(response.headers, "x-billing-credits"),
        rate_limit_limit=_header_int(response.headers, "x-ratelimit-limit"),
        rate_limit_remaining=_header_int(response.headers, "x-ratelimit-remaining"),
        rate_limit_reset=_header_int(response.headers, "x-ratelimit-reset"),
        headers=response.headers,
    )


# ---------------------------------------------------------------------------
# Retries
# ---------------------------------------------------------------------------


def retry_status_error(response: httpx.Response, idempotent: bool) -> Optional[APIStatusError]:
    """The error to retry after, or ``None`` if this response must not be retried.

    429 ``rate_limited`` is rejected before the request is handled, so it is retried for every
    method; ``quota_exceeded`` will not clear by waiting. 502, 503 and 504 are retried only for
    GET and DELETE: a POST may already have been processed.
    """
    status = response.status_code
    if status == 429:
        error = make_status_error(response)
        return None if isinstance(error, QuotaExceededError) else error
    if idempotent and status in RETRYABLE_STATUSES:
        return make_status_error(response)
    return None


# Errors raised before the request was sent, so retrying cannot repeat an action.
_NOT_SENT_ERRORS = (httpx.ConnectError, httpx.ConnectTimeout, httpx.PoolTimeout)


def can_retry_error(exc: Exception, idempotent: bool) -> bool:
    """Whether a timeout or network error may be retried. GET and DELETE always may; POSTs only
    when the connection was never made."""
    return idempotent or isinstance(exc, _NOT_SENT_ERRORS)


def retry_delay(attempt: int, retry_after: Optional[float] = None) -> float:
    """Seconds to wait before retry number ``attempt + 1`` (attempt starts at 0)."""
    if retry_after is not None:
        return min(retry_after, MAX_RETRY_AFTER)
    base: float = min(INITIAL_RETRY_DELAY * (2**attempt), MAX_RETRY_DELAY)
    return base * (1 + random.uniform(0, 0.25))
