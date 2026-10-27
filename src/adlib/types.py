"""Response types of the AdLib API v1 (from its OpenAPI spec), as ``TypedDict``\\ s.

Methods return the parsed JSON as plain dicts; these types describe them for type checkers and
editors. Fields a platform does not provide are ``None``, never estimated. Timestamps are RFC 3339
strings.
"""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional, TypedDict, Union

__all__ = [
    "Platform",
    "AdStatus",
    "StatusFilter",
    "Source",
    "Sort",
    "AdFormat",
    "EventType",
    "JobStatus",
    "DeliveryStatus",
    "BatchType",
    "Range",
    "AdvertiserRef",
    "Media",
    "Creative",
    "Targeting",
    "EUData",
    "Derived",
    "Ad",
    "Advertiser",
    "ResolvedAdvertiser",
    "PlatformFailure",
    "EventOut",
    "ListMeta",
    "AdList",
    "AdMeta",
    "AdResponse",
    "Version",
    "Period",
    "AdHistory",
    "AdHistoryResponse",
    "ResolveData",
    "ResolveResponse",
    "AdvertiserResponse",
    "EventListMeta",
    "EventList",
    "DaysRunningStats",
    "WeekCount",
    "AdvertiserStats",
    "AdvertiserStatsResponse",
    "ReportKind",
    "ReportStatus",
    "ResolveReport",
    "ResolveReportResponse",
    "ResolveReportsResponse",
    "CompanyPlatform",
    "Company",
    "CompanyResponse",
    "PlatformCheck",
    "DomainCheck",
    "DomainCheckResponse",
    "BatchOptions",
    "BatchJob",
    "BatchCreatedResponse",
    "BatchItem",
    "BatchResponse",
    "WatchlistEntry",
    "Watchlist",
    "WatchlistResponse",
    "WatchlistsResponse",
    "Delivery",
    "DeliveriesResponse",
    "DeliveryResponse",
    "QueuedResponse",
    "WebhookSecret",
    "WebhookSecretResponse",
    "UsageRow",
    "UsageMonth",
    "Plan",
    "UsageResponse",
    "StatusWindow",
    "SmokeCheck",
    "SmokeResult",
    "PlatformStatus",
    "StatusResponse",
    "Capabilities",
    "PlatformInfo",
    "PlatformsResponse",
    "AdvertiserChangesEvent",
    "BatchCompletedEvent",
    "WebhookPingEvent",
    "WebhookEvent",
]

Platform = Literal["meta", "google", "tiktok", "linkedin", "pinterest", "x"]
AdStatus = Literal["active", "inactive", "unknown"]
StatusFilter = Literal["active", "inactive", "all"]
Source = Literal["live", "history"]
Sort = Literal["newest", "days_running"]
AdFormat = Literal["image", "video", "carousel", "text"]
EventType = Literal["started", "stopped", "changed", "discovered"]
JobStatus = Literal["queued", "running", "done", "failed"]
DeliveryStatus = Literal["pending", "delivered", "failed"]
BatchType = Literal["advertisers", "domains", "ads"]
ReportKind = Literal["wrong_match", "missing_match"]
ReportStatus = Literal["open", "accepted", "rejected"]

# Optional keys live in a total=False base class; the class itself lists the required keys.


class _RangeOpt(TypedDict, total=False):
    currency: str


class Range(_RangeOpt):
    lower: Optional[int]
    upper: Optional[int]


class AdvertiserRef(TypedDict):
    id: str
    name: str
    platform_advertiser_id: str
    domain: Optional[str]
    verified: Optional[bool]


class _MediaOpt(TypedDict, total=False):
    original_url: str
    preview_url: str


class Media(_MediaOpt):
    kind: Literal["image", "video"]
    url: str
    sha256: Optional[str]
    width: Optional[int]
    height: Optional[int]
    duration: Optional[float]


class Creative(TypedDict):
    type: str
    text: Optional[str]
    headline: Optional[str]
    cta: Optional[str]
    landing_url: Optional[str]
    media: Optional[List[Media]]


class _TargetingOpt(TypedDict, total=False):
    other: Dict[str, Optional[List[str]]]


class Targeting(_TargetingOpt):
    ages: Optional[List[str]]
    genders: Optional[List[str]]
    locations: Optional[List[str]]


class _EUDataOpt(TypedDict, total=False):
    reach_by_country_range: Dict[str, Range]
    reach_range: Range


class EUData(_EUDataOpt):
    reach_total: Optional[int]
    reach_by_country: Dict[str, int]
    targeting: Targeting
    payer: Optional[str]
    beneficiary: Optional[str]


class Derived(TypedDict):
    days_running: Optional[int]
    is_long_running: Optional[bool]
    language: Optional[str]
    variant_count: Optional[int]


class _AdOpt(TypedDict, total=False):
    library_url: str
    raw_ref: str
    extra: Dict[str, Any]


class Ad(_AdOpt):
    id: str
    platform: Platform
    platform_ad_id: str
    advertiser: AdvertiserRef
    status: AdStatus
    first_shown: Optional[str]
    last_shown: Optional[str]
    first_seen_by_us: Optional[str]
    last_seen_by_us: Optional[str]
    formats: Optional[List[str]]
    creatives: Optional[List[Creative]]
    placements: Optional[List[str]]
    countries: Optional[List[str]]
    eu_data: EUData
    spend_range: Range
    impressions_range: Range
    political: Optional[bool]
    """Political or issue ad. Meta only; ``None`` where the platform doesn't label it."""
    derived: Derived


class _AdvertiserOpt(TypedDict, total=False):
    extra: Dict[str, Any]


class Advertiser(_AdvertiserOpt):
    id: str
    platform: str
    platform_advertiser_id: str
    name: str
    domain: Optional[str]
    verified: Optional[bool]
    country: Optional[str]
    profile_url: Optional[str]
    avatar_url: Optional[str]
    active_ads: Optional[int]
    total_ads_known: int
    first_seen_by_us: Optional[str]
    last_seen_by_us: Optional[str]


class ResolvedAdvertiser(Advertiser):
    score: float
    match_reason: Literal["domain", "name", "history", "manual"]
    """``manual`` = confirmed by us (or from a customer report we accepted)."""


class PlatformFailure(TypedDict):
    platform: str
    code: str
    message: str


class _EventOutOpt(TypedDict, total=False):
    ad_id: str
    ad: Ad


class EventOut(_EventOutOpt):
    type: EventType
    at: str


class _ListMetaOpt(TypedDict, total=False):
    platforms: Optional[List[str]]
    errors: Optional[List[PlatformFailure]]


class ListMeta(_ListMetaOpt):
    count: int
    cached: bool
    source: Source


class AdList(TypedDict):
    data: Optional[List[Ad]]
    next_cursor: Optional[str]
    meta: ListMeta


class AdMeta(TypedDict):
    source: Literal["live", "cache", "history"]


class AdResponse(TypedDict):
    data: Ad
    meta: AdMeta


class Version(TypedDict):
    valid_from: str
    valid_to: Optional[str]
    creatives: Optional[List[Creative]]


class Period(TypedDict):
    active_from: str
    active_to: Optional[str]


class AdHistory(TypedDict):
    ad_id: str
    versions: Optional[List[Version]]
    status_periods: Optional[List[Period]]
    events: Optional[List[EventOut]]


class AdHistoryResponse(TypedDict):
    data: AdHistory


class _ResolveDataOpt(TypedDict, total=False):
    errors: Optional[List[PlatformFailure]]


class ResolveData(_ResolveDataOpt):
    domain: str
    advertisers: Optional[List[ResolvedAdvertiser]]


class ResolveResponse(TypedDict):
    data: ResolveData


class AdvertiserResponse(TypedDict):
    data: Advertiser


class EventListMeta(TypedDict):
    count: int
    summary: Dict[str, int]


class EventList(TypedDict):
    data: Optional[List[EventOut]]
    next_cursor: Optional[str]
    meta: EventListMeta


class DaysRunningStats(TypedDict):
    median: Optional[float]
    p90: Optional[float]
    max: Optional[int]
    long_running: int
    known: int


class WeekCount(TypedDict):
    week: str
    count: int


class AdvertiserStats(TypedDict):
    advertiser_id: str
    total_ads: int
    political_ads: int
    """Ads the platform labels political or issue ads (Meta only)."""
    by_status: Dict[str, int]
    by_format: Dict[str, int]
    by_country: Dict[str, int]
    by_language: Dict[str, int]
    days_running: DaysRunningStats
    new_ads_weekly: Optional[List[WeekCount]]
    first_ad_at: Optional[str]
    latest_ad_at: Optional[str]
    longest_running_ads: Optional[List[Ad]]


class AdvertiserStatsResponse(TypedDict):
    data: AdvertiserStats


class ResolveReport(TypedDict):
    id: int
    domain: str
    advertiser_id: Optional[str]
    kind: ReportKind
    note: Optional[str]
    status: ReportStatus
    resolution: Optional[str]
    """Our answer when the report was reviewed."""
    created_at: str
    resolved_at: Optional[str]


class ResolveReportResponse(TypedDict):
    data: ResolveReport


class ResolveReportsResponse(TypedDict):
    data: Optional[List[ResolveReport]]


class CompanyPlatform(TypedDict):
    platform: str
    accounts: int
    total_ads_known: int
    active_ads: int


class _CompanyOpt(TypedDict, total=False):
    errors: Optional[List[PlatformFailure]]


class Company(_CompanyOpt):
    domain: str
    name: str
    """Name of the most confident account."""
    accounts: Optional[List[ResolvedAdvertiser]]
    """Accounts with score >= min_score."""
    candidates: Optional[List[ResolvedAdvertiser]]
    """Possible accounts below min_score; report wrong ones with ``advertisers.report_match``."""
    platforms: Optional[List[CompanyPlatform]]
    stats: AdvertiserStats
    """Combined history of all accounts (``advertiser_id`` is the domain)."""


class CompanyResponse(TypedDict):
    data: Company


class _PlatformCheckOpt(TypedDict, total=False):
    advertiser: str
    advertiser_id: str
    score: float
    error: str


class PlatformCheck(_PlatformCheckOpt):
    platform: str
    advertising: Optional[bool]
    active_ads: Optional[int]
    latest_ad_at: Optional[str]
    sample_ad_ids: Optional[List[str]]


class DomainCheck(TypedDict):
    domain: str
    advertising: Optional[bool]
    platforms: Optional[List[PlatformCheck]]
    checked_at: str


class DomainCheckResponse(TypedDict):
    data: DomainCheck


class BatchOptions(TypedDict, total=False):
    """Options of a batch job (sent as given)."""

    country: str
    include_ads: bool
    """domains: also fetch the first page of ads of each matched advertiser."""
    max_pages: int
    """advertisers: pages per advertiser (0 to 20, default 3)."""
    platforms: List[str]
    """domains: restrict resolution to these platforms."""
    status: Literal["active", "inactive", ""]


class BatchJob(TypedDict):
    job_id: str
    status: JobStatus
    kind: str
    params: Any
    webhook_url: Optional[str]
    total: int
    done: int
    failed: int
    credits_billed: int
    created_at: str
    started_at: Optional[str]
    finished_at: Optional[str]


class BatchCreatedResponse(TypedDict):
    data: BatchJob


class BatchItem(TypedDict):
    input: str
    status: JobStatus
    error: Optional[str]
    ads: Optional[List[Ad]]
    advertisers: Optional[List[Advertiser]]


class BatchResponse(TypedDict):
    data: BatchJob
    items: Optional[List[BatchItem]]
    next_cursor: Optional[str]


class WatchlistEntry(TypedDict):
    advertiser_id: str
    name: str
    last_crawl_at: Optional[str]
    next_crawl_at: str
    last_error: Optional[str]
    active_ads_known: int


class Watchlist(TypedDict):
    id: str
    name: str
    webhook_url: Optional[str]
    interval_hours: int
    archive_videos: bool
    created_at: str
    advertiser_count: int
    advertisers: Optional[List[WatchlistEntry]]
    """Empty in ``watchlists.list()``; ``watchlists.get(id)`` has the entries."""


class WatchlistResponse(TypedDict):
    data: Watchlist


class WatchlistsResponse(TypedDict):
    data: Optional[List[Watchlist]]


class _DeliveryOpt(TypedDict, total=False):
    next_attempt: str
    payload: Any


class Delivery(_DeliveryOpt):
    id: int
    url: str
    event: str
    status: DeliveryStatus
    attempts: int
    response_status: Optional[int]
    last_error: Optional[str]
    created_at: str
    delivered_at: Optional[str]


class DeliveriesResponse(TypedDict):
    data: Optional[List[Delivery]]
    next_cursor: Optional[str]


class DeliveryResponse(TypedDict):
    data: Delivery


class QueuedResponse(TypedDict):
    delivery_id: int
    status: str


class WebhookSecret(TypedDict):
    secret: str
    version: int


class WebhookSecretResponse(TypedDict):
    data: WebhookSecret


class UsageRow(TypedDict):
    day: str
    endpoint: str
    requests: int
    units: int


class UsageMonth(TypedDict):
    month: str
    endpoint: str
    requests: int
    units: int


class Plan(TypedDict):
    name: str
    requests_per_minute: int
    monthly_credits: int
    max_batch_items: int
    max_watchlist_advertisers: int
    history_access: bool
    history_days: int
    """How far back archived ads are available; 0 = unlimited."""


class UsageResponse(TypedDict):
    owner: str
    plan: Plan
    credits_this_month: int
    data: Optional[List[UsageRow]]
    monthly: Optional[List[UsageMonth]]


class StatusWindow(TypedDict):
    requests: int
    ok: int
    errors: int
    blocked: int
    success_rate: Optional[float]
    avg_latency_ms: Optional[int]
    proxy_bytes: int
    proxy_cost_usd: Optional[float]
    results: int
    bytes_per_result: Optional[int]
    proxy_cost_per_1k_results_usd: Optional[float]


class _SmokeCheckOpt(TypedDict, total=False):
    error: str


class SmokeCheck(_SmokeCheckOpt):
    name: str
    ok: bool
    latency_ms: int
    results: int


class SmokeResult(TypedDict):
    platform: str
    at: str
    ok: bool
    checks: Optional[List[SmokeCheck]]


class _PlatformStatusOpt(TypedDict, total=False):
    proxy_tier: str


class PlatformStatus(_PlatformStatusOpt):
    platform: str
    enabled: bool
    state: Literal["operational", "degraded", "down", "disabled"]
    circuit_breaker: str
    last_hour: StatusWindow
    last_24h: StatusWindow
    last_smoke_test: SmokeResult


class StatusResponse(TypedDict):
    status: Literal["operational", "degraded", "down"]
    platforms: Optional[List[PlatformStatus]]
    version: str


class _CapabilitiesOpt(TypedDict, total=False):
    beta: bool


class Capabilities(_CapabilitiesOpt):
    """Field names are as the API sends them (PascalCase, except ``beta``)."""

    SearchKeyword: bool
    SearchAdvertiser: bool
    SearchAdvertiserID: bool
    SearchDomain: bool
    GetAd: bool
    FilterCountry: bool
    FilterDate: bool
    FilterFormat: bool
    FilterStatus: bool
    Regions: Optional[List[str]]
    EUOnly: bool


class PlatformInfo(TypedDict):
    platform: str
    enabled: bool
    capabilities: Capabilities


class PlatformsResponse(TypedDict):
    data: Optional[List[PlatformInfo]]


class _ChangeSummary(TypedDict):
    new: int
    started: int
    stopped: int
    changed: int


class AdvertiserChangesEvent(TypedDict):
    """Sent to a watchlist's webhook after a crawl found changes."""

    event: Literal["advertiser.changes"]
    watchlist_id: str
    advertiser_id: str
    crawled_at: str
    summary: _ChangeSummary
    new: List[EventOut]
    started: List[EventOut]
    stopped: List[EventOut]
    changed: List[EventOut]


class BatchCompletedEvent(TypedDict):
    """Sent to a batch job's webhook_url when it finishes."""

    event: Literal["batch.completed"]
    job: BatchJob


class WebhookPingEvent(TypedDict):
    """Sent by ``client.webhooks.test(url)``."""

    event: Literal["webhook.ping"]
    sent_at: str
    message: str


WebhookEvent = Union[AdvertiserChangesEvent, BatchCompletedEvent, WebhookPingEvent]
