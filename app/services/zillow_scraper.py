import json
import re
from typing import Optional

import httpx
from selectolax.parser import HTMLParser

from app.models.house import ZillowData


class ZillowScrapeError(Exception):
    pass


def extract_address_from_url(url: str) -> str:
    """Parse address from Zillow URL slug, e.g.
    .../141-Leigh-Rd-Cumberland-RI-02864/... -> '141 Leigh Rd, Cumberland, RI 02864'
    """
    match = re.search(r'/homedetails/([^/]+)', url)
    if not match:
        return ""
    slug = match.group(1)
    # Remove trailing zpid if present
    slug = re.sub(r'-\d+_zpid$', '', slug)
    parts = slug.split('-')
    # Heuristic: last part is zip (5 digits), second-to-last is state (2 letters)
    if (len(parts) >= 3
            and re.match(r'^\d{5}$', parts[-1])
            and re.match(r'^[A-Z]{2}$', parts[-2], re.IGNORECASE)):
        zipcode = parts[-1]
        state = parts[-2].upper()
        # Find the city: work backwards from state, city words are title-cased
        # Street number is first part if it's a digit
        remaining = parts[:-2]
        # Try to split street from city at a reasonable boundary
        # Simple approach: last 1-2 words before state are city
        city_words = []
        street_words = []
        # Walk backwards from state, collect city words until we hit a known street suffix
        street_suffixes = {'rd', 'st', 'ave', 'blvd', 'dr', 'ln', 'ct', 'pl', 'way',
                           'ter', 'cir', 'hwy', 'pike', 'run', 'trail', 'loop'}
        boundary = len(remaining)
        for i in range(len(remaining) - 1, -1, -1):
            if remaining[i].lower() in street_suffixes:
                boundary = i + 1
                break
        street_words = remaining[:boundary]
        city_words = remaining[boundary:]
        street = ' '.join(street_words).title()
        city = ' '.join(city_words).title()
        if city:
            return f"{street}, {city}, {state} {zipcode}"
        return f"{street}, {state} {zipcode}"
    # Fallback: just title-case the whole slug
    return ' '.join(parts).title()


async def scrape_zillow_listing(url: str) -> ZillowData:
    """Scrape a Zillow listing using Playwright (real browser, bypasses bot detection).
    Falls back to httpx if Playwright is unavailable.
    """
    try:
        return await _scrape_with_playwright(url)
    except ImportError:
        pass
    except Exception as e:
        # Playwright available but failed — re-raise so caller shows manual form
        raise ZillowScrapeError(str(e)) from e

    # httpx fallback (likely to be blocked, but worth trying)
    return await _scrape_with_httpx(url)


async def _scrape_with_playwright(url: str) -> ZillowData:
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 800},
            locale="en-US",
        )
        page = await context.new_page()

        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            html = await page.content()
        finally:
            await browser.close()

    parser = HTMLParser(html)
    data = _extract_next_data(parser) or _extract_opengraph(parser, html)
    if data is None:
        raise ZillowScrapeError("Could not extract listing data from page")
    return data


async def _scrape_with_httpx(url: str) -> ZillowData:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }
    async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=15.0) as client:
        response = await client.get(url)

    if response.status_code != 200:
        raise ZillowScrapeError(f"Failed to fetch Zillow page: HTTP {response.status_code}")

    parser = HTMLParser(response.text)
    data = _extract_next_data(parser) or _extract_opengraph(parser, response.text)
    if data is None:
        raise ZillowScrapeError("Could not extract listing data from page")
    return data


def _extract_next_data(parser: HTMLParser) -> Optional[ZillowData]:
    script = parser.css_first("script#__NEXT_DATA__")
    if script is None:
        return None
    try:
        raw = json.loads(script.text())
    except (json.JSONDecodeError, AttributeError):
        return None

    prop = _find_property_in_next_data(raw)
    if prop is None:
        return None
    return _parse_property_data(prop)


def _find_property_in_next_data(data: dict) -> Optional[dict]:
    try:
        cache_str = (
            data.get("props", {})
            .get("pageProps", {})
            .get("componentProps", {})
            .get("gdpClientCache", "")
        )
        if cache_str:
            cache = json.loads(cache_str) if isinstance(cache_str, str) else cache_str
            for value in cache.values():
                if isinstance(value, str):
                    value = json.loads(value)
                if isinstance(value, dict) and "property" in value:
                    return value["property"]
    except (json.JSONDecodeError, AttributeError, TypeError):
        pass

    try:
        props = data.get("props", {}).get("pageProps", {})
        if "property" in props:
            return props["property"]
        initial = props.get("initialData", {}).get("building", {})
        if initial:
            return initial
    except (AttributeError, TypeError):
        pass

    try:
        apollo_str = (
            data.get("props", {})
            .get("pageProps", {})
            .get("componentProps", {})
            .get("hdpApolloPreloadedData", "")
        )
        if apollo_str:
            apollo = json.loads(apollo_str) if isinstance(apollo_str, str) else apollo_str
            for value in apollo.values():
                if isinstance(value, str):
                    try:
                        value = json.loads(value)
                    except json.JSONDecodeError:
                        continue
                if isinstance(value, dict):
                    prop = value.get("property") or value.get("data", {}).get("property")
                    if prop:
                        return prop
    except (json.JSONDecodeError, AttributeError, TypeError):
        pass

    return None


def _parse_property_data(prop: dict) -> ZillowData:
    address_parts = []
    addr = prop.get("address", {})
    if isinstance(addr, dict):
        street = addr.get("streetAddress", "")
        city = addr.get("city", "")
        state = addr.get("state", "")
        zipcode = addr.get("zipcode", "")
        if street:
            address_parts.append(street)
        if city:
            address_parts.append(city)
        if state and zipcode:
            address_parts.append(f"{state} {zipcode}")
        elif state:
            address_parts.append(state)
    elif isinstance(addr, str):
        address_parts.append(addr)

    address = ", ".join(address_parts) if address_parts else ""

    price = prop.get("price") or prop.get("zestimate")
    try:
        price = int(price) if price is not None else None
    except (ValueError, TypeError):
        price = None

    beds = prop.get("bedrooms")
    try:
        beds = int(beds) if beds is not None else None
    except (ValueError, TypeError):
        beds = None

    baths = prop.get("bathrooms")
    try:
        baths = float(baths) if baths is not None else None
    except (ValueError, TypeError):
        baths = None

    sqft = prop.get("livingArea") or prop.get("livingAreaValue")
    try:
        sqft = int(sqft) if sqft is not None else None
    except (ValueError, TypeError):
        sqft = None

    image_url = None
    photos = prop.get("photos") or prop.get("responsivePhotos") or []
    if photos and isinstance(photos, list):
        first = photos[0]
        if isinstance(first, dict):
            mixed = first.get("mixedSources", {}).get("jpeg", [])
            if mixed:
                image_url = mixed[-1].get("url")
            if not image_url:
                image_url = first.get("url") or first.get("fullUrl")
        elif isinstance(first, str):
            image_url = first
    if not image_url:
        image_url = prop.get("imgSrc") or prop.get("hiResImageLink")

    return ZillowData(
        address=address,
        price=price,
        beds=beds,
        baths=baths,
        sqft=sqft,
        image_url=image_url,
    )


def _extract_opengraph(parser: HTMLParser, html: str) -> Optional[ZillowData]:
    og_title = _get_meta(parser, "og:title")
    og_image = _get_meta(parser, "og:image")
    og_description = _get_meta(parser, "og:description")

    if not og_title:
        return None

    address = og_title.split("|")[0].strip()
    price = _extract_price_from_text(og_description or "") or _extract_price_from_text(html)
    beds, baths, sqft = _extract_details_from_text(og_description or "")

    return ZillowData(
        address=address,
        price=price,
        beds=beds,
        baths=baths,
        sqft=sqft,
        image_url=og_image,
    )


def _get_meta(parser: HTMLParser, property_name: str) -> Optional[str]:
    node = parser.css_first(f'meta[property="{property_name}"]')
    return node.attributes.get("content") if node else None


def _extract_price_from_text(text: str) -> Optional[int]:
    match = re.search(r'\$[\d,]+(?:\.\d{2})?', text)
    if match:
        price_str = match.group().replace('$', '').replace(',', '').split('.')[0]
        try:
            price = int(price_str)
            if price > 10000:
                return price
        except ValueError:
            pass
    return None


def _extract_details_from_text(text: str) -> tuple[Optional[int], Optional[float], Optional[int]]:
    beds = baths = sqft = None

    m = re.search(r'(\d+)\s*(?:bd|bed|bedroom)', text, re.IGNORECASE)
    if m:
        beds = int(m.group(1))

    m = re.search(r'([\d.]+)\s*(?:ba|bath|bathroom)', text, re.IGNORECASE)
    if m:
        baths = float(m.group(1))

    m = re.search(r'([\d,]+)\s*(?:sqft|sq\s*ft|square\s*feet)', text, re.IGNORECASE)
    if m:
        sqft = int(m.group(1).replace(',', ''))

    return beds, baths, sqft
