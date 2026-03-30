# Zillow Scraping

## Summary

Zillow actively blocks automated data fetching. After trying multiple approaches, the app no longer attempts to scrape listing data. Instead, the address is parsed client-side from the URL slug, and all other fields are entered manually.

The scraping infrastructure remains in `app/services/zillow_scraper.py` in case it becomes useful in the future.

## What Was Tried

### 1. Plain HTTP (httpx)

The first approach used `httpx` with realistic browser headers:

```python
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)...",
    "Accept": "text/html,application/xhtml+xml...",
    "Accept-Language": "en-US,en;q=0.9",
}
async with httpx.AsyncClient(headers=headers) as client:
    response = await client.get(url)
```

**Result:** HTTP 403 Forbidden. Zillow uses Akamai Bot Manager, which fingerprints TLS handshakes and detects non-browser clients regardless of headers.

### 2. Playwright (Headless Browser)

The second approach used Playwright to drive a real Chromium browser:

```python
browser = await p.chromium.launch(headless=True)
context = await browser.new_context(
    user_agent="Mozilla/5.0...",
    viewport={"width": 1280, "height": 800},
    locale="en-US",
)
page = await context.new_page()
await page.goto(url, wait_until="domcontentloaded", timeout=30000)
```

This required adding Chromium to the Docker image (~300MB of system deps) and the `playwright==1.51.0` Python package.

**Result:** "Access to this page has been denied." Zillow detects headless Chromium via browser API fingerprinting (missing `window.chrome`, navigator quirks, WebGL anomalies, etc.) even with a realistic User-Agent.

### 3. playwright-stealth

`playwright-stealth` patches several known headless detection signals (navigator.webdriver, chrome runtime, etc.) and was tested in the running container.

**Result:** Still blocked. Zillow's bot detection is sophisticated enough that common stealth patches don't reliably bypass it.

## Why Scraping Is Hard

Zillow pays for Akamai Bot Manager specifically to prevent scrapers. Detection happens at multiple layers:

- **TLS fingerprinting** — `httpx` and Python's SSL stack produce a different TLS ClientHello than a real browser
- **Browser API fingerprinting** — headless Chrome lacks `window.chrome`, has `navigator.webdriver = true` by default, and differs in WebGL renderer strings
- **Behavioral analysis** — no mouse movement, no scroll events, instant page load timing
- **IP reputation** — cloud/residential IP ranges are treated differently

None of these are trivially bypassed without paid residential proxy networks or services that maintain up-to-date stealth patches.

## What the Scraper Code Does (If Ever Used)

`app/services/zillow_scraper.py` implements a two-stage approach with multiple HTML parsing fallbacks:

### Parsing Strategy

Zillow is a Next.js app. When a page loads successfully, listing data is embedded in a `<script id="__NEXT_DATA__">` tag as JSON. The scraper tries three extraction paths in order:

1. **`gdpClientCache`** — a JSON string within the Next.js props containing the full property object
2. **`pageProps.property`** — a simpler direct property path sometimes present
3. **`hdpApolloPreloadedData`** — Apollo GraphQL cache, another encoded JSON blob

If none of those yield data, it falls back to:

4. **OpenGraph meta tags** — `og:title` (address), `og:image` (photo), `og:description` (price/beds/baths via regex)

### Field Extraction

The property object uses different field names across Zillow page versions:

| Data | Fields tried |
|------|-------------|
| Price | `price`, `zestimate` |
| Living area | `livingArea`, `livingAreaValue` |
| Image | `photos[0].mixedSources.jpeg[-1].url`, `photos[0].url`, `imgSrc`, `hiResImageLink` |

All numeric conversions are wrapped in `try/except` to handle `None`, strings, or unexpected types.

## Current Approach

Since scraping is unreliable, the app uses a different UX:

### Client-Side URL Parsing

When a Zillow URL is pasted into the add modal, JavaScript extracts the address from the URL slug with no network request:

```
Input:  https://www.zillow.com/homedetails/141-Leigh-Rd-Cumberland-RI-02864/96393932_zpid/
Output: 141 Leigh Rd, Cumberland, RI 02864
```

The slug is parsed by:
1. Extracting the path segment after `/homedetails/`
2. Stripping the trailing ZPID (`-96393932_zpid`)
3. Splitting on `-`
4. Identifying the zip code (5 digits) and state (2 letters) at the end
5. Working backwards from the state to find the street/city boundary using a set of common street suffixes (`rd`, `st`, `ave`, `blvd`, `dr`, `ln`, `ct`, etc.)

This handles the vast majority of US residential Zillow URLs and is instant.

The same logic exists server-side in `extract_address_from_url()` for use in tests and any future server-side flows.

### Manual Entry

Price, beds, baths, sqft, and image URL are entered manually. The form is pre-focused and the address field is pre-filled from the URL, so in practice only 2–3 fields need to be typed.

## If You Want to Re-Enable Scraping

The scraping code is still wired up in `zillow_scraper.py`. To expose it in the UI:

1. Add an optional "Auto-fill from Zillow" button to the add modal
2. On click, POST to a new endpoint that calls `scrape_zillow_listing(url)`
3. Return pre-filled form fields on success, or show the manual form on failure

This would require the Zillow scraping problem to be solved first (e.g. a paid proxy service, a browser extension approach, or a change in Zillow's policy).
