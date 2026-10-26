from __future__ import annotations

import hashlib
import hmac
import json
import time

import pytest

from adlib import (
    WebhookSignatureError,
    construct_webhook_event,
    sign_webhook_payload,
    verify_webhook_signature,
)

SECRET = "whsec_0123456789abcdef0123456789abcdef0123456789abcdef"
BODY = json.dumps({"event": "webhook.ping", "sent_at": "2026-10-26T10:00:00Z", "message": "hi"}).encode()
T = 1_800_000_000


def go_sign(key: str, payload: bytes, ts: int) -> str:
    """Same construction as the API's worker.Sign: HMAC-SHA256(key, "<t>." + body), hex."""
    mac = hmac.new(key.encode(), f"{ts}.".encode() + payload, hashlib.sha256).hexdigest()
    return f"t={ts},v1={mac}"


def test_sign_matches_api_construction() -> None:
    assert sign_webhook_payload(SECRET, BODY, T) == go_sign(SECRET, BODY, T)
    assert sign_webhook_payload(SECRET, BODY.decode(), T) == go_sign(SECRET, BODY, T)


def test_accepts_valid_signature_bytes_str_bytearray() -> None:
    sig = go_sign(SECRET, BODY, T)
    assert verify_webhook_signature(BODY, sig, SECRET, now=T + 10) is True
    assert verify_webhook_signature(BODY.decode(), sig, SECRET, now=T) is True
    assert verify_webhook_signature(bytearray(BODY), sig, SECRET, now=T) is True


def test_accepts_any_v1_with_spaces_and_case() -> None:
    good = go_sign(SECRET, BODY, T).split("v1=")[1]
    sig = f"t={T}, v1={'0' * 64}, v1={good.upper()}"
    assert verify_webhook_signature(BODY, sig, SECRET, now=T)


def test_rejects_wrong_secret_body_or_timestamp() -> None:
    sig = go_sign(SECRET, BODY, T)
    with pytest.raises(WebhookSignatureError, match="does not match"):
        verify_webhook_signature(BODY, sig, "whsec_other", now=T)
    with pytest.raises(WebhookSignatureError, match="does not match"):
        verify_webhook_signature(BODY + b" ", sig, SECRET, now=T)
    v1 = sig.split(",")[1]
    with pytest.raises(WebhookSignatureError, match="does not match"):
        verify_webhook_signature(BODY, f"t={T + 1},{v1}", SECRET, now=T)


def test_tolerance_is_five_minutes() -> None:
    sig = go_sign(SECRET, BODY, T)
    assert verify_webhook_signature(BODY, sig, SECRET, now=T + 300)
    with pytest.raises(WebhookSignatureError, match="tolerance"):
        verify_webhook_signature(BODY, sig, SECRET, now=T + 301)
    with pytest.raises(WebhookSignatureError, match="tolerance"):
        verify_webhook_signature(BODY, sig, SECRET, now=T - 301)
    assert verify_webhook_signature(BODY, sig, SECRET, now=T + 1000, tolerance=2000)


def test_default_now() -> None:
    assert verify_webhook_signature(BODY, sign_webhook_payload(SECRET, BODY), SECRET)
    with pytest.raises(WebhookSignatureError):
        verify_webhook_signature(BODY, go_sign(SECRET, BODY, int(time.time()) - 600), SECRET)


@pytest.mark.parametrize(
    "header",
    [None, "", "garbage", f"t={T}", "v1=abc", f"t=abc,v1={'0' * 64}", f"t={T},v1=xyz"],
)
def test_rejects_missing_or_malformed_header(header: object) -> None:
    with pytest.raises(WebhookSignatureError):
        verify_webhook_signature(BODY, header, SECRET, now=T)  # type: ignore[arg-type]


def test_requires_secret_and_raw_body() -> None:
    sig = go_sign(SECRET, BODY, T)
    with pytest.raises(WebhookSignatureError):
        verify_webhook_signature(BODY, sig, "", now=T)
    with pytest.raises(WebhookSignatureError, match="raw request body"):
        verify_webhook_signature(json.loads(BODY), sig, SECRET, now=T)  # type: ignore[arg-type]


def test_construct_event() -> None:
    event = construct_webhook_event(BODY, go_sign(SECRET, BODY, T), SECRET, now=T)
    assert event["event"] == "webhook.ping"
    bad = b"not json"
    with pytest.raises(WebhookSignatureError, match="not valid JSON"):
        construct_webhook_event(bad, go_sign(SECRET, bad, T), SECRET, now=T)
