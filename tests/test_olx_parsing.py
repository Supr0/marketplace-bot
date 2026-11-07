import json
from pathlib import Path

import pytest

from sources.olx import parse_olx_response

FIXTURE = Path(__file__).parent / "fixtures" / "olx_fixture.json"

@pytest.fixture
def olx_response() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))

def test_parses_all_items(olx_response):
    items, has_next, total = parse_olx_response(olx_response)

    assert items, "parser returns empty list"
    assert has_next
    assert total == 1000

def test_ads_flagged(olx_response):
    items, _, _ = parse_olx_response(olx_response)
    top_flags = [item.top for item in items]
    assert any(top_flags), "fixture must contain top ads"
    assert not all(top_flags), "fixture must not only contain ads"

def test_urls_and_titles(olx_response):
    items, _, _ = parse_olx_response(olx_response)
    titles = [item.title for item in items]
    urls = [item.url.startswith("https://") for item in items]
    assert all(titles), "all items must contain titles"
    assert all(urls), "all items must contain urls"

def test_empty_response():
    items, has_next, total = parse_olx_response({"clientCompatibleListings": {"data": None}})
    assert items == []
    assert has_next is False
    assert total == 0

def test_response_datatypes(olx_response):
    items, _, _ = parse_olx_response(olx_response)
    assert all(isinstance(i.id, int) for i in items)
    assert all(isinstance(i.url, str) for i in items)
    assert all(isinstance(i.price_tag, str) for i in items)
    assert all(isinstance(i.title, str) for i in items)