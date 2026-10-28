"""Official Python client for the AdLib API: one REST API for the public ad libraries of Meta
(Facebook/Instagram), Google, TikTok, LinkedIn, Pinterest, X, Snapchat, Apple, Amazon and Microsoft,
with ad history, creative features, watchlists and webhooks.

    from adlib import AdLib

    client = AdLib(api_key="...")  # or ADLIB_API_KEY
    resolved = client.advertisers.resolve("nike.com")
    page = client.search(advertiser="meta:15087023444", status="active")
"""

from ._base import DEFAULT_BASE_URL, ResponseInfo
from ._client import AdLib, AsyncAdLib
from ._exceptions import (
    AdLibError,
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    InsufficientCreditsError,
    NotFoundError,
    PermissionDeniedError,
    QuotaExceededError,
    RateLimitError,
    ServerError,
    ValidationError,
    WebhookSignatureError,
)
from ._version import __version__
from .pagination import DEFAULT_MAX_PAGES, next_cursor, page_items
from .webhooks import (
    DEFAULT_TOLERANCE,
    SIGNATURE_HEADER,
    construct_webhook_event,
    sign_webhook_payload,
    verify_webhook_signature,
)

__all__ = [
    "__version__",
    "AdLib",
    "AsyncAdLib",
    "ResponseInfo",
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
    "verify_webhook_signature",
    "construct_webhook_event",
    "sign_webhook_payload",
    "SIGNATURE_HEADER",
    "DEFAULT_TOLERANCE",
    "DEFAULT_BASE_URL",
    "DEFAULT_MAX_PAGES",
    "next_cursor",
    "page_items",
]
