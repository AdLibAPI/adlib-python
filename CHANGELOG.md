# Changelog

All notable changes to this package are listed here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.4.0] - 2026-10-28

### Changed

- `ads.features()` waits while the API is still analysing an ad's media: a new video analysis now
  answers 202 with `meta.status` = `processing` and `retry_after` (free), and the SDK asks again
  until the data is ready, for up to 2 minutes. `wait=False` returns the first answer as it is,
  `max_wait` changes the limit.
- `AdFeaturesResponse`: `data` is null while processing; `meta.status` (`ready` | `processing`)
  and `meta.retry_after` are new, `meta.analyzed_at` is optional.
- `OCRResult.timeline` (new `OCRSpan`): for videos, when each on-screen text appears and
  disappears (`start`, `end` in seconds, `text`).
- The features docs no longer describe how the features are computed.

## [0.3.0] - 2026-10-28

### Added

- CSV output (`output=csv`): `ads.search_csv`, `advertisers.ads_csv`, `advertisers.changes_csv`,
  `advertisers.timeline_csv`, `domains.check_csv` and `request_csv(path)` for any other GET
  endpoint, sync and async. They return `{"csv": ..., "next_cursor": ...}` (`CsvPage`), with the
  cursor of the next page from the `X-Next-Cursor` header.
- README: credits per ad for all twelve platforms (1 on Meta, TikTok, Pinterest, X, Snapchat,
  Apple, Amazon and Microsoft; 2 on Google, YouTube and Play; 3 on LinkedIn), the 2-credit features
  price, the free endpoints, and Slack and Discord webhook URLs on watchlists.

### Changed

- Ad and advertiser ids are checked against the ten platform prefixes (`meta`, `google`, `tiktok`,
  `linkedin`, `pinterest`, `x`, `snapchat`, `apple`, `amazon`, `microsoft`) before a request is
  sent; YouTube and Play ads have `google:` ids.

## [0.2.0] - 2026-10-28

### Added

- Platforms `snapchat`, `apple`, `amazon` and `microsoft` (beta) in `Platform` and
  `adlib.types.PLATFORMS`; `youtube` and `play` as search aliases for Google, and the `placement`
  search filter (`youtube`, `search`, `shopping`, `maps`, `play`).
- `ads.features(id)` for `GET /v1/ads/{id}/features`: creative features (hook, offers, urgency,
  social proof, format, video length, cuts, on-image text), with `AdFeatures` types.
- `client.library_url(url)` for `GET /v1/library-url`: turns an ad library link into an AdLib id.
- `client.coverage()` for `GET /public/coverage` and `domains.suggest(q)` for
  `GET /v1/domains/suggest`.
- `watchlists.update(id, name=, webhook_url=, email_alerts=)` for `PATCH /v1/watchlists/{id}`, and
  `email_alerts` on `watchlists.create`; `Watchlist["email_alerts"]`.
- `removed` search filter (source history only), `Ad["removed_from_library_at"]`, the `removed`
  event type in changes, and `removed` in `advertiser.changes` webhook events.
- `derived["signals"]` and `derived["stage"]` on ads, `meta["platform_totals"]` on lists,
  `columns` on domain checks, `reach` on ad history, `family` on companies and
  `Plan["min_interval_hours"]`.
- `companies.get(domain, ...)` for `GET /v1/companies/{domain}`: all ad accounts of a domain
  across platforms with combined stats, plus candidates below `min_score`. Sync and async.
- `advertisers.report_match(...)` and `advertisers.list_reports()` for
  `/v1/advertisers/resolve/reports`.
- `political` search filter, `Ad["political"]` and `AdvertiserStats["political_ads"]`.
- `role` and `role_source` on resolved advertisers, `Company["related"]`, `include_related` on
  `companies.get`, and `kind="wrong_role"` with `role` on `advertisers.report_match`.
- `match_reason` `"manual"` on resolved advertisers, `Plan["history_days"]`, and the
  `history_limit` error code (403, `PermissionDeniedError`).

### Changed

- PATCH requests are retried like GET and DELETE.
- `Watchlist["interval_seconds"]` is now `interval_hours`; watchlists also have
  `advertiser_count`. `watchlists.list()` returns them without `advertisers` entries; use
  `watchlists.get(id)`.

## [0.1.0] - 2026-10-26

### Added

- `AdLib` (sync) and `AsyncAdLib` (async) clients for every public `/v1` endpoint of the AdLib
  API: search, ads and ad history, advertisers (resolve, get, ads, changes, stats, timeline),
  domain checks, batch jobs, watchlists, webhook deliveries, test events and signing secret,
  usage, status and platforms.
- `TypedDict` types for every response in `adlib.types`.
- Exceptions from the API's `{"error": {code, message, request_id, billed}}` shape, including
  `QuotaExceededError` for `quota_exceeded`.
- Retries with exponential backoff for 429 `rate_limited` (honouring `Retry-After`) and, on GET
  and DELETE, for 502, 503, 504, timeouts and network errors.
- `paginate` and `paginate_items` following `next_cursor`.
- `verify_webhook_signature`, `construct_webhook_event` and `sign_webhook_payload` for
  `X-AdLib-Signature`.
- `on_response` hook with `X-Billing-Credits`, `X-Request-Id` and rate-limit headers.
