from pathlib import Path

from selectolax.parser import HTMLParser

from app.services.zillow_scraper import (
    _extract_next_data,
    _extract_opengraph,
    _extract_price_from_text,
    _extract_details_from_text,
)


FIXTURES = Path(__file__).parent.parent / "fixtures"


class TestExtractNextData:
    def test_parses_sample_page(self):
        html = (FIXTURES / "sample_zillow_page.html").read_text()
        parser = HTMLParser(html)
        data = _extract_next_data(parser)
        assert data is not None
        assert data.address == "123 Main St, Springfield, IL 62701"
        assert data.price == 350000
        assert data.beds == 3
        assert data.baths == 2.5
        assert data.sqft == 2200
        assert "large.jpg" in data.image_url

    def test_returns_none_when_no_script(self):
        parser = HTMLParser("<html><body></body></html>")
        assert _extract_next_data(parser) is None

    def test_returns_none_on_invalid_json(self):
        html = '<script id="__NEXT_DATA__">not json</script>'
        parser = HTMLParser(html)
        assert _extract_next_data(parser) is None


class TestExtractOpengraph:
    def test_parses_og_tags(self):
        html = (FIXTURES / "sample_zillow_page.html").read_text()
        parser = HTMLParser(html)
        data = _extract_opengraph(parser, html)
        assert data is not None
        assert "123 Main St" in data.address
        assert data.price == 350000
        assert data.image_url == "https://photos.zillowstatic.com/fp/og-image.jpg"

    def test_returns_none_without_og_tags(self):
        parser = HTMLParser("<html><head></head><body></body></html>")
        assert _extract_opengraph(parser, "") is None

    def test_extracts_beds_baths_sqft_from_description(self):
        html = """<html><head>
        <meta property="og:title" content="Test House | Zillow">
        <meta property="og:description" content="3 bd, 2 ba, 1,500 sqft">
        </head></html>"""
        parser = HTMLParser(html)
        data = _extract_opengraph(parser, html)
        assert data is not None
        assert data.beds == 3
        assert data.baths == 2.0
        assert data.sqft == 1500


class TestExtractPrice:
    def test_standard_format(self):
        assert _extract_price_from_text("Listed for $350,000") == 350000

    def test_no_commas(self):
        assert _extract_price_from_text("$450000") == 450000

    def test_returns_none_for_small_numbers(self):
        assert _extract_price_from_text("$50") is None

    def test_returns_none_for_no_price(self):
        assert _extract_price_from_text("No price here") is None


class TestExtractDetails:
    def test_beds_baths_sqft(self):
        beds, baths, sqft = _extract_details_from_text("3 bd, 2.5 ba, 2,200 sqft")
        assert beds == 3
        assert baths == 2.5
        assert sqft == 2200

    def test_partial_data(self):
        beds, baths, sqft = _extract_details_from_text("3 bedrooms")
        assert beds == 3
        assert baths is None
        assert sqft is None

    def test_no_data(self):
        beds, baths, sqft = _extract_details_from_text("Nice house for sale")
        assert beds is None
        assert baths is None
        assert sqft is None
