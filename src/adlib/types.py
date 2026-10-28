"""Response types of the AdLib API v1 (from its OpenAPI spec), as ``TypedDict``\\ s.

Methods return the parsed JSON as plain dicts; these types describe them for type checkers and
editors. Fields a platform does not provide are ``None``, never estimated. Timestamps are RFC 3339
strings.
"""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional, Tuple, TypedDict, Union

__all__ = [
    "Platform",
    "PLATFORMS",
    "PlatformAlias",
    "Placement",
    "AdStage",
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
    "FeatureMatch",
    "TextFeatures",
    "OCRResult",
    "MediaFeatures",
    "LandingFeatures",
    "AdFeatures",
    "AdFeaturesMeta",
    "AdFeaturesResponse",
    "LibraryUrl",
    "LibraryUrlResponse",
    "CsvPage",
    "ReachPoint",
    "FamilyBrand",
    "CompanyFamily",
    "DomainSuggestion",
    "DomainSuggestionsResponse",
    "CoveragePlatform",
    "Coverage",
    "CoverageResponse",
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
    "AdvertiserRole",
    "ReportKind",
    "ReportRole",
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

Platform = Literal[
    "meta", "google", "tiktok", "linkedin", "pinterest", "x", "snapchat", "apple", "amazon", "microsoft"
]
PLATFORMS: Tuple[Platform, ...] = (
    "meta",
    "google",
    "tiktok",
    "linkedin",
    "pinterest",
    "x",
    "snapchat",
    "apple",
    "amazon",
    "microsoft",
)
"""Every platform ads can come from. ``microsoft`` is in beta."""
PlatformAlias = Literal["youtube", "play"]
"""Search-only aliases: Google ads on YouTube or Google Play (same as ``platform="google"`` with
that ``placement``)."""
Placement = Literal["youtube", "search", "shopping", "maps", "play"]
"""Google only: where the ad ran."""
AdStage = Literal["testing", "scaling", "proven"]
AdStatus = Literal["active", "inactive", "unknown"]
StatusFilter = Literal["active", "inactive", "all"]
Source = Literal["live", "history"]
Sort = Literal["newest", "days_running"]
AdFormat = Literal["image", "video", "carousel", "text"]
EventType = Literal["started", "stopped", "changed", "discovered", "removed"]
"""``removed``: the platform's library no longer shows the ad (we keep it)."""
JobStatus = Literal["queued", "running", "done", "failed"]
DeliveryStatus = Literal["pending", "delivered", "failed"]
BatchType = Literal["advertisers", "domains", "ads"]
AdvertiserRole = Literal["brand", "agency", "reseller", "partner", "unknown"]
ReportKind = Literal["wrong_match", "missing_match", "wrong_role"]
ReportRole = Literal["brand", "agency", "reseller", "partner"]
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
    signals: Optional[List[str]]
    """Why this ad likely performs, from public facts only: ``long_running`` (running > 30 days),
    ``still_running_90d`` (active and running > 90 days), ``scaled`` (3+ variants with the same
    text), ``wide_reach`` (EU reach >= 100,000), ``multi_country`` (shown in 5+ countries)."""
    stage: Optional[AdStage]
    """``testing`` = no signal yet, ``scaling`` = one signal, ``proven`` = two or more. ``None``
    when the run length is unknown."""


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
    removed_from_library_at: Optional[str]
    """When the platform's library stopped showing this ad (taken down, deleted by the advertiser
    or past the library's retention). We keep it; ``None`` while the library still has it."""
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
    role: AdvertiserRole
    """The account's relation to the domain: the brand itself, or an agency, reseller (dealer,
    importer) or partner running ads for it."""
    role_source: Literal["manual", "inferred"]
    """``manual`` = set by us; ``inferred`` = from the account name."""


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
    platform_totals: Dict[str, int]
    """Matching ads per platform as the platform reports them, where it does."""


class ListMeta(_ListMetaOpt):
    count: int
    cached: bool
    source: Source


class CsvPage(TypedDict):
    """A page as CSV (``output=csv``)."""

    #: Header row plus one row per item of ``data`` (an object becomes one row).
    csv: str
    #: From the X-Next-Cursor header; pass it back as ``cursor``. None on the last page.
    next_cursor: Optional[str]


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


class _ReachPointOpt(TypedDict, total=False):
    reach_by_country: Dict[str, int]


class ReachPoint(_ReachPointOpt):
    day: str
    reach_total: int


class AdHistory(TypedDict):
    ad_id: str
    versions: Optional[List[Version]]
    status_periods: Optional[List[Period]]
    events: Optional[List[EventOut]]
    reach: Optional[List[ReachPoint]]
    """EU reach per day (Meta ads delivered in the EU), oldest first."""


class AdHistoryResponse(TypedDict):
    data: AdHistory


# Creative features (GET /v1/ads/{id}/features). Rule-based and measured, no AI model.


class FeatureMatch(TypedDict):
    """A text tag with the exact text it matched."""

    rule: str
    text: str


class TextFeatures(TypedDict):
    hook: str
    """First sentence of the primary text."""
    hook_is_question: bool
    chars: int
    words: int
    emojis: int
    uppercase_ratio: float
    hashtags: Optional[List[str]]
    mentions: Optional[List[str]]
    numbers: Optional[List[str]]
    prices: Optional[List[str]]
    discounts: Optional[List[str]]
    free_shipping: Optional[List[FeatureMatch]]
    urgency: Optional[List[FeatureMatch]]
    social_proof: Optional[List[FeatureMatch]]
    guarantee: Optional[List[FeatureMatch]]
    free_offer: Optional[List[FeatureMatch]]
    novelty: Optional[List[FeatureMatch]]


class OCRResult(TypedDict):
    text: str
    """Text read on the image (for videos: on the first frame and at 3 s)."""
    confidence: float
    """Mean word confidence 0..1; below 0.6 the text is dropped."""
    languages: str


class _MediaFeaturesOpt(TypedDict, total=False):
    width: int
    height: int
    aspect: str
    """9:16, 4:5, 1:1, 16:9 or WxH reduced."""
    orientation: Literal["vertical", "square", "horizontal"]
    duration_s: float
    has_audio: bool
    scene_cuts: int
    """Hard cuts detected (ffmpeg scene score > 0.4)."""
    cuts_per_minute: float
    ocr: OCRResult
    error: str


class MediaFeatures(_MediaFeaturesOpt):
    kind: Literal["image", "video"]
    url: str


class LandingFeatures(TypedDict):
    url: str
    domain: str
    path: str
    utm: Dict[str, str]


class _AdFeaturesOpt(TypedDict, total=False):
    headline: str
    cta: str
    landing: LandingFeatures
    ocr_text: str


class AdFeatures(_AdFeaturesOpt):
    version: str
    method: str
    """``rules`` = text rules with evidence, ``measurement`` = ffprobe/ffmpeg, ``ocr`` = tesseract."""
    format: str
    """From the measured media: vertical_video, horizontal_video, square_video, vertical_image,
    square_image, horizontal_image, carousel, text_only."""
    text: TextFeatures
    media: Optional[List[MediaFeatures]]


class AdFeaturesMeta(TypedDict):
    ad_id: str
    cached: bool
    """Served from an earlier analysis of the same ad version."""
    analyzed_at: str


class AdFeaturesResponse(TypedDict):
    data: AdFeatures
    meta: AdFeaturesMeta


class LibraryUrl(TypedDict):
    kind: Literal["ad", "advertiser"]
    platform: str
    id: str
    """``<platform>:<id>``, usable in every endpoint."""
    href: str
    """The AdLib call that fetches it, e.g. ``/v1/ads/meta:1187430977361020``."""


class LibraryUrlResponse(TypedDict):
    data: LibraryUrl


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
    role: Optional[ReportRole]
    """wrong_role / missing_match: the role the account should have."""
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


class FamilyBrand(TypedDict):
    name: str
    domain: str


class CompanyFamily(TypedDict):
    """The parent company and its other brands, when known (reviewed by us)."""

    parent: str
    parent_domain: Optional[str]
    brands: Optional[List[FamilyBrand]]


class _CompanyOpt(TypedDict, total=False):
    errors: Optional[List[PlatformFailure]]
    family: CompanyFamily


class Company(_CompanyOpt):
    domain: str
    name: str
    """Name of the most confident account."""
    accounts: Optional[List[ResolvedAdvertiser]]
    """The company's own accounts (role brand or unknown) with score >= min_score."""
    related: Optional[List[ResolvedAdvertiser]]
    """Agencies, resellers and partners running ads for the domain; not in platforms and stats
    unless ``include_related``."""
    candidates: Optional[List[ResolvedAdvertiser]]
    """Possible accounts below min_score; report wrong ones with ``advertisers.report_match``."""
    platforms: Optional[List[CompanyPlatform]]
    stats: AdvertiserStats
    """Combined history of the accounts, plus related with ``include_related`` (``advertiser_id``
    is the domain)."""


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
    columns: Dict[str, Any]
    """Flat view for Clay, Sheets or Zapier: ``advertising``, ``platforms_advertising``
    (comma-separated), ``total_active_ads``, ``latest_ad_at``, and per platform
    ``<platform>_advertising``, ``<platform>_active_ads`` and ``<platform>_advertiser_id``."""
    checked_at: str


class DomainCheckResponse(TypedDict):
    data: DomainCheck


class DomainSuggestion(TypedDict):
    domain: str
    name: str
    """Most common advertiser name for the domain."""
    platforms: Optional[List[str]]
    advertisers: int
    ads_known: int


class DomainSuggestionsResponse(TypedDict):
    data: Optional[List[DomainSuggestion]]


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
    email_alerts: bool
    """A digest of each crawl's changes goes to the account's email."""
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
    min_interval_hours: int
    """Shortest watchlist crawl interval of the plan."""


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


class CoveragePlatform(TypedDict):
    platform: str
    ads: int
    active_ads: int
    new_7d: int


class Coverage(TypedDict):
    ads: int
    """Ads in the archive."""
    active_ads: int
    ad_versions: int
    """Creative versions kept (every change is a version)."""
    media: int
    """Images and videos stored permanently."""
    advertisers: int
    tracked_advertisers: int
    """Advertisers we crawl on a schedule."""
    tracked_domains: int
    removed_kept: int
    """Ads the platforms' libraries no longer show that we keep."""
    eu_reach_points: int
    crawled_24h: int
    last_crawl: Optional[str]
    platforms: Optional[List[CoveragePlatform]]
    updated_at: str


class CoverageResponse(TypedDict):
    data: Coverage


class _ChangeSummary(TypedDict):
    new: int
    started: int
    stopped: int
    changed: int
    removed: int


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
    removed: List[EventOut]
    """Ads the platform's library no longer shows (we keep them)."""


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
