"""Request builders for every endpoint: path, query, JSON body and validation. Shared by the
sync and async resources. Arguments are checked here, before any request is sent."""

from __future__ import annotations

import datetime as _dt
import re
from dataclasses import dataclass, field, replace
from typing import Any, Dict, Iterable, Mapping, Optional, Sequence, Union
from urllib.parse import quote

from ._base import QueryValue
from .types import PLATFORMS


__all__ = ["Request", "PlatformFilter", "DateLike", "as_csv"]

PlatformFilter = Union[str, Sequence[str], None]
DateLike = Union[str, _dt.date, _dt.datetime, None]

STATUSES = ("active", "inactive", "all")
SOURCES = ("live", "history")
SORTS = ("newest", "days_running")
FORMATS = ("image", "video", "carousel", "text")
PLACEMENTS = ("youtube", "search", "shopping", "maps", "play")
DELIVERY_STATUSES = ("pending", "delivered", "failed")
BATCH_TYPES = ("advertisers", "domains", "ads")
EVENT_TYPES = ("started", "stopped", "changed", "discovered", "removed")
REPORT_KINDS = ("wrong_match", "missing_match", "wrong_role")
REPORT_ROLES = ("brand", "agency", "reseller", "partner")


@dataclass(frozen=True)
class Request:
    method: str
    path: str
    params: Mapping[str, Optional[QueryValue]] = field(default_factory=dict)
    body: Optional[Dict[str, Any]] = None
    #: Ask for CSV (``output=csv``) instead of JSON.
    csv: bool = False

    @property
    def idempotent(self) -> bool:
        return self.method != "POST"  # GET, PATCH and DELETE are safe to repeat


def as_csv(request: Request) -> Request:
    """The same request, answered as CSV (``output=csv``)."""
    return replace(request, params={**request.params, "output": "csv"}, csv=True)


# ---------------------------------------------------------------------------
# Validation helpers. ValueError for bad arguments, like twittrapi.
# ---------------------------------------------------------------------------


def _seg(value: str) -> str:
    """Encodes a path segment; colons stay (ids look like meta:1234567890)."""
    return quote(value, safe=":")


def _non_empty(name: str, value: Any) -> str:
    if isinstance(value, int) and not isinstance(value, bool):
        return str(value)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value.strip()


# Ids use the ten libraries (YouTube and Play ads are google: ids).
_PREFIXED_ID = re.compile(rf"^({'|'.join(PLATFORMS)}):\S.*$")


def _prefixed_id(name: str, value: Any) -> str:
    s = _non_empty(name, value)
    if not _PREFIXED_ID.match(s):
        raise ValueError(
            f"{name} must look like <platform>:<id>, e.g. meta:1234567890, with platform one of "
            f"{', '.join(PLATFORMS)} (got {s!r})"
        )
    return s


def _int_range(name: str, value: Optional[int], lo: int, hi: Optional[int]) -> Optional[int]:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int) or value < lo or (hi is not None and value > hi):
        upper = f" to {hi}" if hi is not None else " or more"
        raise ValueError(f"{name} must be an integer from {lo}{upper}")
    return value


def _number_range(name: str, value: Optional[float], lo: float, hi: float) -> Optional[float]:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not lo <= value <= hi:
        raise ValueError(f"{name} must be a number from {lo:g} to {hi:g}")
    return value


def _one_of(name: str, value: Optional[str], allowed: Iterable[str]) -> Optional[str]:
    if value is None:
        return None
    allowed = tuple(allowed)
    if value not in allowed:
        raise ValueError(f"{name} must be one of {', '.join(allowed)}")
    return value


def _csv(name: str, value: PlatformFilter, allowed: Optional[Iterable[str]] = None) -> Optional[str]:
    if value is None:
        return None
    items = [v.strip() for v in value.split(",")] if isinstance(value, str) else [str(v).strip() for v in value]
    items = [v for v in items if v]
    if allowed is not None:
        allowed = tuple(allowed)
        bad = [v for v in items if v not in allowed]
        if bad:
            raise ValueError(f"{name} must be from {', '.join(allowed)} (got {', '.join(bad)})")
    return ",".join(items) or None


def _date(value: DateLike) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, _dt.datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=_dt.timezone.utc)
        return value.isoformat().replace("+00:00", "Z")
    if isinstance(value, _dt.date):
        return value.isoformat()
    return value


def _compact(body: Dict[str, Any]) -> Dict[str, Any]:
    return {k: v for k, v in body.items() if v is not None}


def _id_list(name: str, values: Any) -> list:  # type: ignore[type-arg]
    if isinstance(values, str) or not isinstance(values, (list, tuple)) or not values:
        raise ValueError(f"{name} must be a non-empty list")
    return [_prefixed_id(f"{name}[{i}]", v) for i, v in enumerate(values)]


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


def search(
    *,
    q: Optional[str],
    advertiser: Optional[str],
    domain: Optional[str],
    platform: PlatformFilter,
    country: Optional[str],
    status: Optional[str],
    date_from: DateLike,
    date_to: DateLike,
    format: Optional[str],
    placement: Optional[str],
    political: Optional[bool],
    removed: Optional[bool],
    source: Optional[str],
    sort: Optional[str],
    cursor: Optional[str],
    limit: Optional[int],
) -> Request:
    modes = [v for v in (q, advertiser, domain) if isinstance(v, str) and v.strip()]
    if len(modes) != 1:
        raise ValueError("Pass exactly one of q, advertiser or domain")
    return Request(
        "GET",
        "/v1/search",
        {
            "q": q.strip() if q else None,
            "advertiser": advertiser.strip() if advertiser else None,
            "domain": domain.strip() if domain else None,
            "platform": _csv("platform", platform),
            "country": country,
            "status": _one_of("status", status, STATUSES),
            "from": _date(date_from),
            "to": _date(date_to),
            "format": _one_of("format", format, FORMATS),
            "placement": _one_of("placement", placement, PLACEMENTS),
            "political": political,
            "removed": removed,
            "source": _one_of("source", source, SOURCES),
            "sort": _one_of("sort", sort, SORTS),
            "cursor": cursor,
            "limit": _int_range("limit", limit, 1, 100),
        },
    )


def get_ad(id: str, max_age: Optional[int]) -> Request:
    return Request(
        "GET", f"/v1/ads/{_seg(_prefixed_id('id', id))}", {"max_age": _int_range("max_age", max_age, 0, None)}
    )


def ad_history(id: str) -> Request:
    return Request("GET", f"/v1/ads/{_seg(_prefixed_id('id', id))}/history")


def ad_features(id: str) -> Request:
    return Request("GET", f"/v1/ads/{_seg(_prefixed_id('id', id))}/features")


def library_url(url: str) -> Request:
    return Request("GET", "/v1/library-url", {"url": _non_empty("url", url)})


def coverage() -> Request:
    return Request("GET", "/public/coverage")


def resolve_advertisers(domain: str, platform: PlatformFilter, max_per_platform: Optional[int]) -> Request:
    return Request(
        "GET",
        "/v1/advertisers/resolve",
        {
            "domain": _non_empty("domain", domain),
            "platform": _csv("platform", platform),
            "max_per_platform": _int_range("max_per_platform", max_per_platform, 1, 10),
        },
    )


def report_match(
    domain: str, kind: str, advertiser_id: Optional[str], role: Optional[str], note: Optional[str]
) -> Request:
    if _one_of("kind", kind, REPORT_KINDS) is None:
        raise ValueError("kind is required")
    if kind in ("wrong_match", "wrong_role") and advertiser_id is None:
        raise ValueError(f"advertiser_id is required for kind {kind}")
    if _one_of("role", role, REPORT_ROLES) is None and kind == "wrong_role":
        raise ValueError("role is required for kind wrong_role")
    if note is not None and len(note) > 1000:
        raise ValueError("note must be at most 1000 characters")
    return Request(
        "POST",
        "/v1/advertisers/resolve/reports",
        body=_compact(
            {
                "domain": _non_empty("domain", domain),
                "kind": kind,
                "advertiser_id": _prefixed_id("advertiser_id", advertiser_id) if advertiser_id is not None else None,
                "role": role,
                "note": note,
            }
        ),
    )


def list_reports() -> Request:
    return Request("GET", "/v1/advertisers/resolve/reports")


def get_advertiser(id: str, refresh: Optional[bool]) -> Request:
    return Request("GET", f"/v1/advertisers/{_seg(_prefixed_id('id', id))}", {"refresh": refresh})


def advertiser_ads(
    id: str,
    status: Optional[str],
    source: Optional[str],
    sort: Optional[str],
    cursor: Optional[str],
    limit: Optional[int],
) -> Request:
    return Request(
        "GET",
        f"/v1/advertisers/{_seg(_prefixed_id('id', id))}/ads",
        {
            "status": _one_of("status", status, STATUSES),
            "source": _one_of("source", source, SOURCES),
            "sort": _one_of("sort", sort, SORTS),
            "cursor": cursor,
            "limit": _int_range("limit", limit, 1, 100),
        },
    )


def advertiser_changes(
    id: str, since: DateLike, types: PlatformFilter, cursor: Optional[str], limit: Optional[int]
) -> Request:
    return Request(
        "GET",
        f"/v1/advertisers/{_seg(_prefixed_id('id', id))}/changes",
        {
            "since": _non_empty("since", _date(since)),
            "types": _csv("types", types, EVENT_TYPES),
            "cursor": cursor,
            "limit": _int_range("limit", limit, 1, 200),
        },
    )


def advertiser_stats(id: str) -> Request:
    return Request("GET", f"/v1/advertisers/{_seg(_prefixed_id('id', id))}/stats")


def advertiser_timeline(
    id: str, date_from: DateLike, date_to: DateLike, cursor: Optional[str], limit: Optional[int]
) -> Request:
    return Request(
        "GET",
        f"/v1/advertisers/{_seg(_prefixed_id('id', id))}/timeline",
        {
            "from": _date(date_from),
            "to": _date(date_to),
            "cursor": cursor,
            "limit": _int_range("limit", limit, 1, 200),
        },
    )


def check_domain(domain: str, platform: PlatformFilter) -> Request:
    return Request(
        "GET", f"/v1/domains/{_seg(_non_empty('domain', domain))}/check", {"platform": _csv("platform", platform)}
    )


def suggest_domains(q: str, limit: Optional[int]) -> Request:
    s = _non_empty("q", q)
    if not 2 <= len(s) <= 100:
        raise ValueError("q must be 2 to 100 characters")
    return Request("GET", "/v1/domains/suggest", {"q": s, "limit": _int_range("limit", limit, 1, 20)})


def get_company(
    domain: str,
    platform: PlatformFilter,
    min_score: Optional[float],
    max_per_platform: Optional[int],
    include_related: Optional[bool],
) -> Request:
    return Request(
        "GET",
        f"/v1/companies/{_seg(_non_empty('domain', domain))}",
        {
            "platform": _csv("platform", platform),
            "min_score": _number_range("min_score", min_score, 0, 1),
            "max_per_platform": _int_range("max_per_platform", max_per_platform, 1, 10),
            "include_related": include_related,
        },
    )


def create_batch(
    type: str, items: Sequence[str], options: Optional[Mapping[str, Any]], webhook_url: Optional[str]
) -> Request:
    if _one_of("type", type, BATCH_TYPES) is None:
        raise ValueError("type is required")
    if isinstance(items, str) or not isinstance(items, (list, tuple)) or not items:
        raise ValueError("items must be a non-empty list")
    clean = [_non_empty(f"items[{i}]", v) for i, v in enumerate(items)]
    if options is not None and "max_pages" in options:
        _int_range("options['max_pages']", options["max_pages"], 0, 20)
    return Request(
        "POST",
        "/v1/batch",
        body=_compact(
            {
                "type": type,
                "items": clean,
                "options": dict(options) if options is not None else None,
                "webhook_url": webhook_url,
            }
        ),
    )


def get_batch(job_id: str, cursor: Optional[str], limit: Optional[int]) -> Request:
    return Request(
        "GET",
        f"/v1/batch/{_seg(_non_empty('job_id', job_id))}",
        {"cursor": cursor, "limit": _int_range("limit", limit, 1, 100)},
    )


def list_watchlists() -> Request:
    return Request("GET", "/v1/watchlists")


def create_watchlist(
    advertisers: Sequence[str],
    name: Optional[str],
    webhook_url: Optional[str],
    interval_hours: Optional[int],
    archive_videos: Optional[bool],
    email_alerts: Optional[bool] = None,
) -> Request:
    if name is not None and len(name) > 200:
        raise ValueError("name must be at most 200 characters")
    return Request(
        "POST",
        "/v1/watchlists",
        body=_compact(
            {
                "advertisers": _id_list("advertisers", advertisers),
                "name": name,
                "webhook_url": webhook_url,
                "interval_hours": _int_range("interval_hours", interval_hours, 1, 168),
                "archive_videos": archive_videos,
                "email_alerts": email_alerts,
            }
        ),
    )


def get_watchlist(id: str) -> Request:
    return Request("GET", f"/v1/watchlists/{_seg(_non_empty('id', id))}")


def update_watchlist(
    id: str, name: Optional[str], webhook_url: Optional[str], email_alerts: Optional[bool]
) -> Request:
    if name is not None and len(name) > 200:
        raise ValueError("name must be at most 200 characters")
    body = _compact({"name": name, "webhook_url": webhook_url, "email_alerts": email_alerts})
    if not body:
        raise ValueError("Pass at least one of name, webhook_url or email_alerts")
    return Request("PATCH", f"/v1/watchlists/{_seg(_non_empty('id', id))}", body=body)


def delete_watchlist(id: str) -> Request:
    return Request("DELETE", f"/v1/watchlists/{_seg(_non_empty('id', id))}")


def add_watchlist_advertisers(id: str, advertisers: Sequence[str]) -> Request:
    return Request(
        "POST",
        f"/v1/watchlists/{_seg(_non_empty('id', id))}/advertisers",
        body={"advertisers": _id_list("advertisers", advertisers)},
    )


def remove_watchlist_advertiser(id: str, advertiser_id: str) -> Request:
    return Request(
        "DELETE",
        f"/v1/watchlists/{_seg(_non_empty('id', id))}/advertisers/{_seg(_prefixed_id('advertiser_id', advertiser_id))}",
    )


def _delivery_id(value: Union[int, str]) -> str:
    s = _non_empty("id", value)
    if not s.isdigit():
        raise ValueError("delivery id must be a positive integer")
    return s


def list_deliveries(status: Optional[str], cursor: Optional[str], limit: Optional[int]) -> Request:
    return Request(
        "GET",
        "/v1/webhooks/deliveries",
        {
            "status": _one_of("status", status, DELIVERY_STATUSES),
            "cursor": cursor,
            "limit": _int_range("limit", limit, 1, 100),
        },
    )


def get_delivery(id: Union[int, str]) -> Request:
    return Request("GET", f"/v1/webhooks/deliveries/{_delivery_id(id)}")


def redeliver(id: Union[int, str]) -> Request:
    return Request("POST", f"/v1/webhooks/deliveries/{_delivery_id(id)}/redeliver")


def test_webhook(url: str) -> Request:
    return Request("POST", "/v1/webhooks/test", body={"url": _non_empty("url", url)})


def webhook_secret() -> Request:
    return Request("GET", "/v1/webhooks/secret")


def rotate_webhook_secret() -> Request:
    return Request("POST", "/v1/webhooks/secret/rotate")


def usage(days: Optional[int]) -> Request:
    return Request("GET", "/v1/usage", {"days": _int_range("days", days, 1, 92)})


def status() -> Request:
    return Request("GET", "/v1/status")


def platforms() -> Request:
    return Request("GET", "/v1/platforms")


