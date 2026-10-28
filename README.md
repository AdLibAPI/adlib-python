# adlib-api – Ad library API client for Python

[![PyPI](https://img.shields.io/pypi/v/adlib-api.svg)](https://pypi.org/project/adlib-api/) [![Python](https://img.shields.io/pypi/pyversions/adlib-api.svg)](https://pypi.org/project/adlib-api/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/AdLibAPI/adlib-python/blob/main/LICENSE)

Official Python client for the **AdLib API**, one REST API for the public ad libraries of
**Meta (Facebook/Instagram), Google (incl. YouTube and Google Play), TikTok, LinkedIn, Pinterest, X,
Snapchat, Apple, Amazon and Microsoft** (Microsoft in beta). Find a brand's advertiser accounts on
every platform from its domain, search and read ads, see how long they ran and what changed, break a
creative down into its features, and set up watchlists that report new, stopped, changed and removed
ads to your webhook or by email.

Ads that disappear from a platform's library stay in the AdLib archive, with their run time,
creative versions and permanently archived images, and are marked with `removed_from_library_at`.

> **Get an API key:** [adlibapi.com](https://adlibapi.com) (the free plan includes 5,000 credits a month) · Docs: [api.adlibapi.com/docs](https://api.adlibapi.com/docs)

**SDKs and integrations:** [Node.js](https://github.com/AdLibAPI/adlib-node) · [MCP server](https://www.npmjs.com/package/adlib-mcp)

- Sync (`AdLib`) and async (`AsyncAdLib`) clients with the same methods
- Every public `/v1` endpoint, with `TypedDict` types for every response
- Retries 429 and 502/503/504 with backoff, honouring `Retry-After`
- Typed exceptions from the API's error shape
- Cursor-following paginators and webhook signature verification
- Python 3.9+, one dependency (`httpx`), fully type-annotated

## Install

```bash
pip install adlib-api
```

The package is imported as `adlib`.

## Quickstart

```python
from adlib import AdLib

client = AdLib(api_key="YOUR_KEY")  # or set ADLIB_API_KEY

# 1. A brand's advertiser accounts on all platforms, from its domain
resolved = client.advertisers.resolve("nike.com")
for a in resolved["data"]["advertisers"] or []:
    print(a["id"], a["name"], a["score"], a["match_reason"], a["active_ads"])

# 2. Their ads (one search mode: q, advertiser or domain)
page = client.search(advertiser="meta:15087023444", status="active", limit=25)
for ad in page["data"] or []:
    print(ad["id"], ad["status"], ad["derived"]["days_running"], ad["derived"]["stage"])
if page["meta"].get("errors"):
    print("platforms that failed (not billed):", page["meta"]["errors"])

# 3. Watch them: we crawl regularly and POST new, stopped and changed ads to your webhook
watchlist = client.watchlists.create(
    name="Competitors",
    advertisers=["meta:15087023444", "tiktok:7012345678901234567"],
    webhook_url="https://your-app.example/webhooks/adlib",
    interval_hours=24,
    email_alerts=True,  # also mail a digest of each crawl's changes
)
print(watchlist["data"]["id"])

# 4. What makes their longest-running ad work: hook, offers, urgency, format, cuts, on-image text
features = client.ads.features("meta:1187430977361020")["data"]
print(features["format"], features["text"]["hook"], features["text"]["urgency"])
```

Requests go to `https://api.adlibapi.com` with an `X-API-Key` header. Ids are
`<platform>:<platform_id>` everywhere, e.g. `meta:15087023444` or `google:AR18378488041124659201`,
with one of the ten libraries as prefix (YouTube and Google Play ads have `google:` ids).

### Verify webhooks

Every delivery carries `X-AdLib-Signature: t=<unix>,v1=<hex>`, an HMAC-SHA256 of `"<t>.<raw body>"`
with your webhook secret (`client.webhooks.secret()`). Verify it against the **raw** body:

```python
import os
from flask import Flask, request
from adlib import WebhookSignatureError, construct_webhook_event

app = Flask(__name__)

@app.post("/webhooks/adlib")
def adlib_webhook():
    try:
        event = construct_webhook_event(
            payload=request.get_data(),  # raw bytes, not parsed JSON
            signature=request.headers.get("X-AdLib-Signature"),
            secret=os.environ["ADLIB_WEBHOOK_SECRET"],
        )
    except WebhookSignatureError:
        return "", 400
    if event["event"] == "advertiser.changes":
        print(event["advertiser_id"], event["summary"])  # new, started, stopped, changed, removed
    return "", 200
```

`verify_webhook_signature(payload, signature, secret)` does the same check without parsing.
Signatures are compared in constant time, and timestamps more than 5 minutes off are rejected
(`tolerance=` to change). `client.webhooks.test(url)` sends a signed `webhook.ping` to your endpoint,
and `sign_webhook_payload(secret, body)` builds a header for your own tests. Events:
`advertiser.changes` (watchlists), `batch.completed` (batch jobs with `webhook_url`) and
`webhook.ping`.

### Async

```python
import asyncio
from adlib import AsyncAdLib

async def main() -> None:
    async with AsyncAdLib() as client:
        check = await client.domains.check("nike.com")
        print(check["data"]["advertising"])

asyncio.run(main())
```

## Credits

The free plan includes **5,000 credits a month**. Calls are billed in credits per delivered result
(the `X-Billing-Credits` response header):

| Platform                                                              | Credits per ad |
| --------------------------------------------------------------------- | -------------- |
| Meta, TikTok, Pinterest, X, Snapchat, Apple, Amazon, Microsoft (beta) | 1              |
| Google, YouTube, Google Play                                          | 2              |
| LinkedIn                                                              | 3              |

Archived ads last shown more than a year ago cost double. A live search page costs at most 5 ads'
worth per platform (5 credits on Meta, 10 on Google, 15 on LinkedIn), however many ads it returns.
`ads.features(id)` costs 2 credits (plus the ad if it has to be fetched live). `library_url`,
`domains.suggest`, `advertisers.report_match` and `advertisers.list_reports` are free.
**Empty results, cached results, platform errors and API errors are free.**

`paginate` and `paginate_items` fetch at most 10 pages unless you raise `max_pages`. To see what each
call cost, pass `on_response`:

```python
client = AdLib(on_response=lambda r: print(r.url, r.billed_credits, r.rate_limit_remaining, r.request_id))
```

## Options

```python
AdLib(
    api_key="...",            # or ADLIB_API_KEY
    base_url="...",           # or ADLIB_BASE_URL; default https://api.adlibapi.com (a trailing /v1 is ignored)
    timeout=120.0,            # seconds, or an httpx.Timeout; live searches over all platforms can be slow
    max_retries=2,            # see Retries
    http_client=None,         # your own httpx.Client (httpx.AsyncClient for AsyncAdLib)
    on_response=None,         # called with a ResponseInfo after every successful call
)
```

Without a key the constructor raises `AdLibError`. Use the client as a context manager, or call
`close()` (`await aclose()` for the async client).

## Usage

Every method returns the parsed JSON as dicts, typed with the `TypedDict`s in `adlib.types`
(`AdList`, `Ad`, `ResolveResponse`, `Watchlist`, ...). Fields a platform does not provide are
`None`, never estimated. Invalid arguments raise `ValueError` before any request is sent.

### Search

```python
client.search(q="running shoes", platform=["meta", "tiktok"], country="US")
client.search(domain="nike.com", status="active", format="video")
client.search(advertiser="Nike", date_from="2026-01-01", date_to="2026-04-01")
# Only political or issue ads (Meta labels them; False excludes them)
client.search(q="election", political=True)
# Our archive, including ads gone from the platforms; longest-running first
client.search(advertiser="meta:15087023444", source="history", sort="days_running")
# Ads the platforms' libraries no longer show (taken down, deleted or aged out) that we kept
client.search(domain="nike.com", source="history", removed=True)
# YouTube video ads (youtube and play are aliases for Google with that placement)
client.search(advertiser="Nike", platform="youtube", format="video")
client.search(domain="nike.com", platform="google", placement="shopping")
# The newer platforms
client.search(q="running shoes", platform=["snapchat", "amazon", "microsoft"])
```

`client.search` is the same as `client.ads.search`. `date_from` and `date_to` are sent as `from`
and `to` and accept strings or `date`/`datetime`. Without `platform`, all platforms that support the
query are asked in parallel; failed ones are listed in `meta["errors"]` and not billed, and
`meta["platform_totals"]` holds the number of matching ads per platform where the platform reports
it. See `client.platforms()` for the search modes and filters each platform supports.

Platforms: `meta`, `google`, `tiktok`, `linkedin`, `pinterest`, `x`, `snapchat`, `apple`, `amazon`
and `microsoft` (beta), as `adlib.types.PLATFORMS`. In search, `youtube` and `play` are accepted
too. `placement` (Google only) is one of `youtube`, `search`, `shopping`, `maps` and `play`.

### Ads

```python
client.ads.get("meta:1234567890")              # live, or the archived version
client.ads.get("meta:1234567890", max_age=0)   # always fetch live
client.ads.history("meta:1234567890")          # versions, status periods, events, EU reach per day
client.ads.features("meta:1234567890")         # creative features (default 2 credits)

# Got a link from an ad library? Turn it into an AdLib id (free)
ref = client.library_url("https://www.facebook.com/ads/library/?id=1187430977361020")["data"]
print(ref["kind"], ref["id"], ref["href"])  # ad meta:1187430977361020 /v1/ads/meta:1187430977361020
```

Every ad has `derived["signals"]` (why it likely performs, from public facts: `long_running`,
`still_running_90d`, `scaled`, `wide_reach`, `multi_country`) and `derived["stage"]` (`testing`,
`scaling` or `proven`). `removed_from_library_at` is set once the platform's library stops showing
the ad; we keep it.

`ads.features(id)` is rule-based and measured, no AI model: every text tag (`urgency`,
`social_proof`, `guarantee`, `free_offer`, `free_shipping`, `novelty`) carries the exact text it
matched, media are measured with ffprobe/ffmpeg (aspect, duration, scene cuts, audio) and on-image
text is read with OCR. Results are kept per ad version.

### Advertisers

```python
client.advertisers.resolve("nike.com", platform="meta,google", max_per_platform=3)
client.advertisers.get("meta:15087023444", refresh=True)
client.advertisers.ads("meta:15087023444", source="history", status="inactive")
client.advertisers.changes("meta:15087023444", since="2026-10-01", types=["started", "stopped", "removed"])
client.advertisers.stats("meta:15087023444")   # by status/format/country/language, winners
client.advertisers.timeline("meta:15087023444", date_from="2026-01-01")

# A wrong or missing resolve match? Report it (free, up to 50 per day). Accepted reports fix the
# resolve for everyone and show up as match_reason "manual".
client.advertisers.report_match(
    "nike.com",
    kind="wrong_match",  # or "missing_match" (advertiser_id and role optional)
    advertiser_id="google:AR18378488041124659201",
    note="not this brand",
)
# The account belongs to the domain but has the wrong role (advertiser_id and role required)
client.advertisers.report_match("nike.com", kind="wrong_role", advertiser_id="meta:42", role="agency")
client.advertisers.list_reports()  # your reports and how we resolved them
```

### Companies

```python
# All ad accounts of a domain across platforms, with combined stats
company = client.companies.get("audi.de")["data"]
client.companies.get("audi.de", platform=["meta", "google"], min_score=0.75, max_per_platform=5)
print(company["name"], company["stats"]["total_ads"], [(p["platform"], p["accounts"], p["active_ads"]) for p in company["platforms"] or []])
print(company["related"])     # agencies, resellers and partners running ads for the domain
print(company["candidates"])  # accounts below min_score, not part of the totals
client.companies.get("audi.de", include_related=True)  # count related in platforms and stats
```

`accounts` holds the company's own accounts (`role` brand or unknown); every resolved advertiser has
a `role` and a `role_source` (manual or inferred). Costs one resolve plus one stats call.
`stats["advertiser_id"]` is the domain.

### Domains

```python
check = client.domains.check("nike.com")  # is this company advertising right now, and where?
print(check["data"]["advertising"], [(p["platform"], p["active_ads"]) for p in check["data"]["platforms"] or []])
print(check["data"]["columns"])  # flat dict for spreadsheets: advertising, total_active_ads, meta_active_ads, ...
client.domains.suggest("nik")    # autocomplete from domains we know (free)
```

### Batch jobs

```python
job = client.batch.create(
    type="domains",
    items=["nike.com", "adidas.com"],
    options={"include_ads": True},
    webhook_url="https://your-app.example/webhooks/adlib",  # batch.completed
)
result = client.batch.get(job["data"]["job_id"])  # status and paginated items
```

### Watchlists

```python
client.watchlists.list()               # advertiser_count per watchlist; advertisers is empty here
client.watchlists.get(watchlist_id)    # incl. the crawl status of each advertiser
client.watchlists.update(watchlist_id, name="Rivals", webhook_url="", email_alerts=True)  # "" removes the webhook
# webhook_url may also be a Slack or Discord incoming webhook: those get a readable message
client.watchlists.update(watchlist_id, webhook_url="https://hooks.slack.com/services/T000/B000/XXXX")
client.watchlists.add_advertisers(watchlist_id, ["google:AR18378488041124659201"])
client.watchlists.remove_advertiser(watchlist_id, "google:AR18378488041124659201")
client.watchlists.delete(watchlist_id)
```

### Webhooks

```python
client.webhooks.deliveries(status="failed")  # newest first, kept 30 days
client.webhooks.delivery(42)                 # incl. its payload
client.webhooks.redeliver(42)
client.webhooks.test("https://your-app.example/webhooks/adlib")
client.webhooks.secret()          # {"data": {"secret": "whsec_...", "version": 1}}
client.webhooks.rotate_secret()   # the old secret stops working immediately
```

### Account and status

```python
client.usage(days=30)   # plan, credits this month, daily rows
client.status()         # health per platform (not billed)
client.platforms()      # search modes and filters per platform
client.coverage()       # archive size and freshness (public)
```

### CSV

Any `/v1` endpoint answers as CSV with `output=csv`, billed the same as JSON. `data` is flattened:
one row per item, nested objects as dotted columns (`advertiser.name`), value lists joined with `|`,
of object lists only the first item (`creatives.0.text`) plus a `creatives_count` column.

```python
page = client.ads.search_csv(domain="nike.com", source="history")
print(page["csv"], page["next_cursor"])  # cursor from the X-Next-Cursor header; pass it as cursor=
client.advertisers.ads_csv("meta:15087023444")
client.advertisers.changes_csv("meta:15087023444", since="2026-10-01")
client.advertisers.timeline_csv("meta:15087023444")
client.domains.check_csv("nike.com")             # one row with the flat columns
client.request_csv("/v1/watchlists")             # any other GET endpoint
```

Errors are still raised as typed exceptions. The async client has the same methods.

### Endpoints not wrapped yet

```python
client.request("GET", "/v1/new-endpoint", params={"a": 1})
```

## Pagination

List endpoints return `next_cursor`; pass it back as `cursor`, `None` means last page.

```python
# Page by page
for page in client.paginate(client.ads.search, q="running shoes", max_pages=3):
    print(len(page["data"] or []), page["next_cursor"])

# Item by item (ads, events, deliveries, or a batch job's items)
for ad in client.paginate_items(client.advertisers.ads, "meta:15087023444", source="history"):
    print(ad["id"])

# Async
async for ad in async_client.paginate_items(async_client.ads.search, domain="nike.com"):
    print(ad["id"])
```

Works with `ads.search`, `advertisers.ads`, `advertisers.changes`, `advertisers.timeline`,
`batch.get` and `webhooks.deliveries`. Iteration stops when `next_cursor` is `None`, when it repeats,
or after `max_pages` (default 10, `None` for no limit). Every page is a billed call.

## Errors

API errors have the shape `{"error": {"code", "message", "request_id", "billed"}}`. Every exception
extends `AdLibError`, which has `message`, `status_code`, `code`, `request_id`, `billed`, `platform`,
`details`, `body` and `response`.

| Exception                  | When                                                                 |
| -------------------------- | -------------------------------------------------------------------- |
| `ValidationError`          | 400 or 422 (`code == "unsupported"`: the platform cannot do this query or filter) |
| `AuthenticationError`      | 401: key missing or wrong                                            |
| `InsufficientCreditsError` | 402: no credits left                                                 |
| `PermissionDeniedError`    | 403: key disabled, or `history_limit`: the ad is older than your plan's archive window (free 90 days, starter 365, growth and up unlimited) |
| `NotFoundError`            | 404: unknown id. Try `source="history"` or `advertisers.resolve`     |
| `RateLimitError`           | 429 `rate_limited`. `retry_after` holds the wait in seconds          |
| `QuotaExceededError`       | 429 `quota_exceeded`: monthly credits used up (subclass of `RateLimitError`) |
| `ServerError`              | 5xx. 502/503: an ad platform failed or is paused                     |
| `APIConnectionError`       | Network failure, no response                                         |
| `APITimeoutError`          | The request timed out                                                |
| `WebhookSignatureError`    | Webhook signature missing, malformed, too old or wrong               |

All HTTP errors also extend `APIStatusError`.

```python
from adlib import AdLibError, NotFoundError, QuotaExceededError, RateLimitError

try:
    client.advertisers.get("meta:1")
except NotFoundError:
    print("Unknown advertiser")
except QuotaExceededError:
    print("Monthly credits used up")
except RateLimitError as e:
    print(f"Retry in {e.retry_after} s")
except AdLibError as e:
    print(e.status_code, e.code, e.message, e.request_id)
```

### Retries

Up to `max_retries` times (default 2), with exponential backoff from 0.5 s (capped at 8 s, with
jitter):

- **429 `rate_limited`** on every request, waiting `Retry-After` (capped at 60 s). The API rejects
  these before doing anything, so retrying a POST is safe.
- **502, 503, 504, timeouts and network errors** on GET, PATCH and DELETE. POSTs (batch jobs, watchlists,
  test events, secret rotation) are retried only when the connection was never made.
- Never: `quota_exceeded`, 500 and other 4xx errors.

## Development

```bash
python -m venv .venv && . .venv/bin/activate
pip install -e ".[dev]"
pytest -q   # against httpx.MockTransport, no network
mypy
```

## License

MIT
