"""Webhook signature verification.

Every delivery carries ``X-AdLib-Signature: t=<unix>,v1=<hex>``, where ``v1`` is the hex
HMAC-SHA256 of ``"<t>.<raw body>"`` keyed with your webhook secret (``whsec_...``, from
``client.webhooks.secret()``). Verify it against the raw request body, before parsing JSON::

    from adlib import construct_webhook_event, WebhookSignatureError

    try:
        event = construct_webhook_event(
            payload=request.body,                        # bytes, exactly as received
            signature=request.headers["X-AdLib-Signature"],
            secret=os.environ["ADLIB_WEBHOOK_SECRET"],
        )
    except WebhookSignatureError:
        return 400
"""

from __future__ import annotations

import hashlib
import hmac
import json
import time
from typing import Any, List, Optional, Tuple, Union, cast

from ._exceptions import WebhookSignatureError
from .types import WebhookEvent

__all__ = [
    "SIGNATURE_HEADER",
    "DEFAULT_TOLERANCE",
    "sign_webhook_payload",
    "verify_webhook_signature",
    "construct_webhook_event",
]

SIGNATURE_HEADER = "X-AdLib-Signature"
DEFAULT_TOLERANCE = 300
"""Deliveries whose timestamp is more than 5 minutes off are rejected (replay protection)."""

Payload = Union[bytes, bytearray, memoryview, str]


def _to_bytes(payload: Any) -> bytes:
    if isinstance(payload, str):
        return payload.encode("utf-8")
    if isinstance(payload, (bytes, bytearray, memoryview)):
        return bytes(payload)
    raise WebhookSignatureError(
        "payload must be the raw request body (bytes or str), not parsed JSON: "
        "re-serializing changes the bytes"
    )


def _mac(secret: str, timestamp: int, payload: bytes) -> str:
    return hmac.new(
        secret.encode("utf-8"), str(timestamp).encode("ascii") + b"." + payload, hashlib.sha256
    ).hexdigest()


def sign_webhook_payload(secret: str, payload: Payload, timestamp: Optional[int] = None) -> str:
    """Builds the ``X-AdLib-Signature`` value for a body. Useful in tests of your own handler."""
    t = int(time.time()) if timestamp is None else int(timestamp)
    return f"t={t},v1={_mac(secret, t, _to_bytes(payload))}"


def _parse(header: str) -> Tuple[int, List[str]]:
    timestamp: Optional[int] = None
    signatures: List[str] = []
    for part in header.split(","):
        key, sep, value = part.partition("=")
        if not sep:
            continue
        key, value = key.strip(), value.strip()
        if key == "t" and value.isdigit():
            timestamp = int(value)
        elif key == "v1" and len(value) == 64 and all(c in "0123456789abcdefABCDEF" for c in value):
            signatures.append(value.lower())
    if timestamp is None or not signatures:
        raise WebhookSignatureError(
            f"Malformed {SIGNATURE_HEADER} header: expected t=<unix>,v1=<hex>"
        )
    return timestamp, signatures


def verify_webhook_signature(
    payload: Payload,
    signature: Optional[str],
    secret: str,
    *,
    tolerance: int = DEFAULT_TOLERANCE,
    now: Optional[float] = None,
) -> bool:
    """Verifies the ``X-AdLib-Signature`` of a webhook delivery.

    Checks the HMAC-SHA256 of ``"<t>.<raw body>"`` with ``secret`` (constant-time compare) and
    that ``t`` is no more than ``tolerance`` seconds (default 300) from now. Raises
    :class:`~adlib.WebhookSignatureError` if the check fails; returns ``True`` otherwise.
    ``tolerance=0`` disables the timestamp check.
    """
    if not secret:
        raise WebhookSignatureError("secret is required")
    if not signature:
        raise WebhookSignatureError(f"Missing {SIGNATURE_HEADER} header")
    body = _to_bytes(payload)
    timestamp, signatures = _parse(signature)
    current = time.time() if now is None else now
    if tolerance > 0 and abs(current - timestamp) > tolerance:
        raise WebhookSignatureError(f"Signature timestamp is outside the tolerance of {tolerance} s")
    expected = _mac(secret, timestamp, body)
    if not any(hmac.compare_digest(expected, sig) for sig in signatures):
        raise WebhookSignatureError("Signature does not match")
    return True


def construct_webhook_event(
    payload: Payload,
    signature: Optional[str],
    secret: str,
    *,
    tolerance: int = DEFAULT_TOLERANCE,
    now: Optional[float] = None,
) -> WebhookEvent:
    """Verifies the signature (see :func:`verify_webhook_signature`) and returns the parsed event:
    ``advertiser.changes``, ``batch.completed`` or ``webhook.ping``."""
    verify_webhook_signature(payload, signature, secret, tolerance=tolerance, now=now)
    try:
        return cast(WebhookEvent, json.loads(_to_bytes(payload).decode("utf-8")))
    except ValueError as exc:
        raise WebhookSignatureError("Webhook body is not valid JSON") from exc
