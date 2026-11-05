import asyncio
import logging
import random
from typing import Any

import aiohttp

OLX_URL = "https://www.olx.ua/uk/"
OLX_ENDPOINT = "https://www.olx.ua/apigateway/graphql"

GRAPH_QL_HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Referer": "https://www.olx.ua/uk/list/"
}

_session: aiohttp.ClientSession | None = None

logger = logging.getLogger(__name__)

GRAPH_QL_QUERY = """
query ListingSearchQuery(
  $searchParameters: [SearchParameter!] = []
) {
  clientCompatibleListings(searchParameters: $searchParameters) {
    __typename
    ... on ListingSuccess {
      data {
        id
        title
        url
        photos {
          link
        }
        promotion {
          top_ad
        }
        location {
          city {
            name
          }
          region {
            name
          }
        }
        params {
          key
          type
          value {
            ... on PriceParam {
              value
              label
              currency
              converted_value
              converted_currency
              negotiable
              arranged
            }
          }
        }
      }
      metadata {
        total_elements
        visible_total_count
      }
      links {
        next {
          href
        }
      }
    }
    ... on ListingError {
      error {
        code
        detail
        status
        title
      }
    }
  }
}
"""

GRAPH_QL_QUERY_EXAMPLE = """
query ListingSearchQuery(
  $searchParameters: [SearchParameter!] = []
  $fetchJobSummary: Boolean = false
  $fetchPayAndShip: Boolean = false
) {
  clientCompatibleListings(searchParameters: $searchParameters) {
    __typename
    ... on ListingSuccess {
      __typename
      data {
        id
        location {
          city {
            id
            name
            normalized_name
            _nodeId
          }
          district {
            id
            name
            normalized_name
            _nodeId
          }
          region {
            id
            name
            normalized_name
            _nodeId
          }
        }
        last_refresh_time
        delivery {
          rock {
            active
            mode
            offer_id
          }
        }
        created_time
        category {
          id
          type
          _nodeId
        }
        contact {
          courier
          chat
          name
          negotiation
          phone
        }
        business
        omnibus_pushup_time
        photos {
          link
          height
          rotation
          width
        }
        promotion {
          highlighted
          top_ad
          options
          premium_ad_page
          urgent
          b2c_ad_page
        }
        protect_phone
        shop {
          subdomain
        }
        title
        status
        url
        user {
          id
          uuid
          _nodeId
          about
          b2c_business_page
          banner_desktop
          banner_mobile
          company_name
          created
          is_online
          last_seen
          logo
          logo_ad_page
          name
          other_ads_enabled
          photo
          seller_type
          social_network_account_type
          verification {
            status
          }
        }
        offer_type
        params {
          key
          name
          type
          value {
            __typename
            ... on GenericParam {
              key
              label
            }
            ... on CheckboxesParam {
              label
              checkboxParamKey: key
            }
            ... on PriceParam {
              value
              type
              previous_value
              previous_label
              negotiable
              label
              currency
              converted_value
              converted_previous_value
              converted_currency
              arranged
              budget
            }
            ... on SalaryParam {
              from
              to
              arranged
              converted_currency
              converted_from
              converted_to
              currency
              gross
              type
            }
            ... on DynamicMultiChoiceCompatibilityListParam {
              __typename
            }
            ... on ErrorParam {
              message
            }
          }
        }
        _nodeId
        description
        external_url
        key_params
        partner {
          code
        }
        map {
          lat
          lon
          radius
          show_detailed
          zoom
        }
        safedeal {
          allowed_quantity
          weight_grams
        }
        valid_to_time
        isGpsrAvailable
        jobSummary @include(if: $fetchJobSummary) {
          whyApply
          whyApplyTags
        }
        payAndShip @include(if: $fetchPayAndShip) {
          sellerPaidDeliveryEnabled
        }
      }
      metadata {
        filter_suggestions {
          clear_on_change
          break_line
          category
          label
          name
          type
          unit
          values {
            label
            value
          }
          constraints {
            type
          }
          search_label
          option {
            ranges
            order
            orderForSearch
            fakeCategory
          }
        }
        x_request_id
        search_id
        total_elements
        visible_total_count
        source
        search_suggestion {
          url
          type
          changes {
            category_id
            city_id
            distance
            district_id
            query
            region_id
            strategy
            excluded_category_id
          }
        }
        facets {
          category {
            id
            count
            label
            url
          }
          category_id_1 {
            count
            id
            label
            url
          }
          category_id_2 {
            count
            id
            label
            url
          }
          category_without_exclusions {
            count
            id
            label
            url
          }
          category_id_3_without_exclusions {
            id
            count
            label
            url
          }
          city {
            count
            id
            label
            url
          }
          district {
            count
            id
            label
            url
          }
          owner_type {
            count
            id
            label
            url
          }
          region {
            id
            count
            label
            url
          }
          scope {
            id
            count
            label
            url
          }
        }
        new
        promoted
      }
      links {
        first {
          href
        }
        next {
          href
        }
        previous {
          href
        }
        self {
          href
        }
      }
    }
    ... on ListingError {
      __typename
      error {
        code
        detail
        status
        title
        validation {
          detail
          field
          title
        }
      }
    }
  }
}
"""

QUERY_LIMIT = 20

def get_session() -> aiohttp.ClientSession:
    global _session
    if _session is None or _session.closed:
        _session = aiohttp.ClientSession(
            headers=GRAPH_QL_HEADERS,
            timeout=aiohttp.ClientTimeout(total=25, connect=5),
        )
    return _session

async def close_session() -> None:
    global _session
    if _session is not None and not _session.closed:
        await _session.close()
    _session = None


RETRY_STATUSES = {429, 500, 502, 503, 504}
RETRY_ATTEMPTS = 3

async def _post_json(payload: dict) -> dict:
    session = get_session()
    last_error: Exception | None = None
    for attempt in range(1, RETRY_ATTEMPTS + 1):
        try:
            async with session.post(OLX_ENDPOINT, json=payload) as resp:
                if resp.status in RETRY_STATUSES and attempt < RETRY_ATTEMPTS:
                    last_error = RuntimeError(f"Olx returned {resp.status}")
                else:
                    resp.raise_for_status()
                    return await resp.json(content_type=None)
        except (aiohttp.ClientError, asyncio.TimeoutError) as exc:
            last_error = exc
        if attempt < RETRY_ATTEMPTS:
            delay = 1.5 ** attempt
            logger.warning("OLX attempt %d failed: %r retry in %.1fs", attempt, last_error, delay)
            await asyncio.sleep(delay)
    raise last_error


async def parse_olx_endpoint(query: str, offset: int = 0, price_from: int = None,
                       price_to: int = None, sorting: str = None,
                       enum_state: str = None) -> dict:
    request = {
        "query": GRAPH_QL_QUERY,
        "variables": {
            "searchParameters": [
                {"key": "offset", "value": str(offset)},
                {"key": "limit", "value": str(QUERY_LIMIT)},
                {"key": "query", "value": query},
                {"key": "suggest_filters", "value":"true"},
                {"key": "sl","value": "19ab61ee5a7x555c86f7"}
            ],
            "fetchJobSummary":False,
            "fetchPayAndShip":True
        }
    }
    if price_to is not None:
        request["variables"]["searchParameters"].append({"key": "filter_float_price:to",
                                                         "value": str(price_to)})
    if price_from is not None:
        request["variables"]["searchParameters"].append({"key": "filter_float_price:from",
                                                         "value": str(price_from)})
    if enum_state is not None:
        request["variables"]["searchParameters"].append({"key": "filter_enum_state[0]",
                                                         "value": str(enum_state)})
    if sorting is not None:
        if sorting == "ascending":
            request["variables"]["searchParameters"].append({"key": "sort_by",
                                                             "value": "filter_float_price:asc"})
        else:
            request["variables"]["searchParameters"].append({"key": "sort_by",
                                                             "value": "filter_float_price:desc"})
    await asyncio.sleep(random.uniform(0.5, 1.5))
    logger.debug("OLX query=%r price_from=%s price_to=%s", query, price_from, price_to)
    return (await _post_json(request))["data"]


def parse_olx_response(response: dict) -> tuple[list[Any], bool, int]:
    listing = response.get("clientCompatibleListings", {}).get("data", {})
    items = []
    for item in listing:
        parsed_item = {
            "title": item.get("title", 0),
            "url": item.get("url", 0),
            "top": item.get("promotion", {}).get("top_ad", 0),
        }
        for param in item.get("params") or []:
            if param["key"] == "price":
                value = param.get("value", {})
                parsed_item.update({
                    "price": value.get("value", 0),
                    "price_tag": value.get("label", 0),
                    "negotiable": value.get("negotiable", 0),
                    "arranged": value.get("arranged", 0),
                })
        items.append(parsed_item)

    links = response.get("clientCompatibleListings", {}).get("links") or {}
    has_next = bool((links.get("next") or {}).get("href"))
    total = response.get("clientCompatibleListings", {}).get("metadata", {}).get("total_elements", 0)
    return items, has_next, total


async def search_page(query: str, offset: int = 0, price_from: int = None,
                           price_to: int = None, sorting: str = None):
    page, has_next, total = parse_olx_response(
        await parse_olx_endpoint(query, offset, price_from, price_to, sorting)
    )
    items = [item for item in page if not (item.get("top"))]
    return items, has_next, total, offset + len(page)


if __name__ == "__main__":
    items, has_next, total, _ = asyncio.run(search_page("iphone",
                                                     0, 1000,
                                                     5000, "ascending"))
    for item in items:
        print(item.get("price", 0))
        print(item.get("top", False))
    print(has_next)
    print(total)
