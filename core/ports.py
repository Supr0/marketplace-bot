from typing import Protocol

from core.models import Page, SearchQuery


class MarketplaceSource(Protocol):
    name: str
    async def search(self, query: SearchQuery) -> Page:
        pass