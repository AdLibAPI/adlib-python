# Changelog

All notable changes to this package are listed here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/).

## [Unreleased]

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
