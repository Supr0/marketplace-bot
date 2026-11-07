from dataclasses import dataclass
from typing import Literal

Sorting = Literal["ascending", "descending"]

@dataclass(frozen=True, slots=True)
class Listing:
    id: int
    title: str
    url: str
    price: float
    price_tag: str
    negotiable: bool
    arranged: bool
    top: bool

@dataclass(frozen=True, slots=True)
class SearchQuery:
    query: str
    price_from: float | None = None
    price_to: float| None = None
    sorting: Sorting | None = None
    limit: int | None = 20
    cursor: str | None = None

@dataclass(frozen=True, slots=True)
class Page:
    items: list[Listing]
    total: int
    next_cursor: str | None = None