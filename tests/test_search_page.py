import asyncio
import json
from pathlib import Path

import pytest
from core.models import SearchQuery
import sources.olx as olx_module

FIXTURE = Path(__file__).parent / "fixtures" / "olx_fixture.json"


@pytest.fixture
def requests_sent(monkeypatch):
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    calls = []

    async def fake_post(request):
        calls.append(request)
        return {"data": payload}

    monkeypatch.setattr(olx_module, "_post_json", fake_post)
    return calls


def test_search_page_returns_listings(requests_sent):
    page = asyncio.run(olx_module.OlxSource().search(SearchQuery(query="iphone", limit=20)))
    assert len(page.items) == 15
    assert page.total == 1000
    assert page.next_cursor is not None
    assert page.next_cursor == "25"
    assert not(any(item.top for item in page.items))

def test_search_page_sends_filters(requests_sent):
    asyncio.run(olx_module.OlxSource().search(SearchQuery(query="iphone",
                                                      price_from=1000,
                                                      price_to=5000,
                                                      sorting="ascending")))

    params = {p["key"]: p["value"] for p in requests_sent[0]["variables"]["searchParameters"]}
    assert params["query"] == "iphone"
    assert params["filter_float_price:from"] == "1000"
    assert params["filter_float_price:to"] == "5000"
    assert params["sort_by"] == "filter_float_price:asc"
    assert params["offset"] == "0"
