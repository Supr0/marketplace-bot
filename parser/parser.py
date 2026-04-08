import random
import time
from typing import Any

import requests
from bs4 import BeautifulSoup
from requests import Session

OLX_URL = "https://www.olx.ua/uk/"
OLX_ENDPOINT = "https://www.olx.ua/apigateway/graphql"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "uk-UA,uk;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://www.google.com/",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

GRAPH_QL_HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Referer": "https://www.olx.ua/uk/list/"
}

GRAPH_QL_QUEUE = """
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
        title
        url
        description
        photos { link }
        params {
          key
          name
          type
          value {
            __typename
            ... on PriceParam {
              value
              label
              currency
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
        next { href }
      }
    }
    ... on ListingError {
      __typename
      error { code detail status title }
    }
  }
}
"""

PAGE_LIMIT = 20


def string_to_url(query: str) -> str:
    return OLX_URL + "/list/q-" + query.replace(" ", "-") + "/"


def parse_olx_endpoint(query: str, offset: int) -> dict:
    session = requests.Session()
    session.headers.update(GRAPH_QL_HEADERS)

    time.sleep(random.uniform(2, 5))

    request = {
        "query":"query ListingSearchQuery(\n  $searchParameters: [SearchParameter!] = []\n  $fetchJobSummary: Boolean = false\n  $fetchPayAndShip: Boolean = false\n) {\n  clientCompatibleListings(searchParameters: $searchParameters) {\n    __typename\n    ... on ListingSuccess {\n      __typename\n      data {\n        id\n        location {\n          city {\n            id\n            name\n            normalized_name\n            _nodeId\n          }\n          district {\n            id\n            name\n            normalized_name\n            _nodeId\n          }\n          region {\n            id\n            name\n            normalized_name\n            _nodeId\n          }\n        }\n        last_refresh_time\n        delivery {\n          rock {\n            active\n            mode\n            offer_id\n          }\n        }\n        created_time\n        category {\n          id\n          type\n          _nodeId\n        }\n        contact {\n          courier\n          chat\n          name\n          negotiation\n          phone\n        }\n        business\n        omnibus_pushup_time\n        photos {\n          link\n          height\n          rotation\n          width\n        }\n        promotion {\n          highlighted\n          top_ad\n          options\n          premium_ad_page\n          urgent\n          b2c_ad_page\n        }\n        protect_phone\n        shop {\n          subdomain\n        }\n        title\n        status\n        url\n        user {\n          id\n          uuid\n          _nodeId\n          about\n          b2c_business_page\n          banner_desktop\n          banner_mobile\n          company_name\n          created\n          is_online\n          last_seen\n          logo\n          logo_ad_page\n          name\n          other_ads_enabled\n          photo\n          seller_type\n          social_network_account_type\n          verification {\n            status\n          }\n        }\n        offer_type\n        params {\n          key\n          name\n          type\n          value {\n            __typename\n            ... on GenericParam {\n              key\n              label\n            }\n            ... on CheckboxesParam {\n              label\n              checkboxParamKey: key\n            }\n            ... on PriceParam {\n              value\n              type\n              previous_value\n              previous_label\n              negotiable\n              label\n              currency\n              converted_value\n              converted_previous_value\n              converted_currency\n              arranged\n              budget\n            }\n            ... on SalaryParam {\n              from\n              to\n              arranged\n              converted_currency\n              converted_from\n              converted_to\n              currency\n              gross\n              type\n            }\n            ... on DynamicMultiChoiceCompatibilityListParam {\n              __typename\n            }\n            ... on ErrorParam {\n              message\n            }\n          }\n        }\n        _nodeId\n        description\n        external_url\n        key_params\n        partner {\n          code\n        }\n        map {\n          lat\n          lon\n          radius\n          show_detailed\n          zoom\n        }\n        safedeal {\n          allowed_quantity\n          weight_grams\n        }\n        valid_to_time\n        isGpsrAvailable\n        jobSummary @include(if: $fetchJobSummary) {\n          whyApply\n          whyApplyTags\n        }\n        payAndShip @include(if: $fetchPayAndShip) {\n          sellerPaidDeliveryEnabled\n        }\n      }\n      metadata {\n        filter_suggestions {\n          clear_on_change\n          break_line\n          category\n          label\n          name\n          type\n          unit\n          values {\n            label\n            value\n          }\n          constraints {\n            type\n          }\n          search_label\n          option {\n            ranges\n            order\n            orderForSearch\n            fakeCategory\n          }\n        }\n        x_request_id\n        search_id\n        total_elements\n        visible_total_count\n        source\n        search_suggestion {\n          url\n          type\n          changes {\n            category_id\n            city_id\n            distance\n            district_id\n            query\n            region_id\n            strategy\n            excluded_category_id\n          }\n        }\n        facets {\n          category {\n            id\n            count\n            label\n            url\n          }\n          category_id_1 {\n            count\n            id\n            label\n            url\n          }\n          category_id_2 {\n            count\n            id\n            label\n            url\n          }\n          category_without_exclusions {\n            count\n            id\n            label\n            url\n          }\n          category_id_3_without_exclusions {\n            id\n            count\n            label\n            url\n          }\n          city {\n            count\n            id\n            label\n            url\n          }\n          district {\n            count\n            id\n            label\n            url\n          }\n          owner_type {\n            count\n            id\n            label\n            url\n          }\n          region {\n            id\n            count\n            label\n            url\n          }\n          scope {\n            id\n            count\n            label\n            url\n          }\n        }\n        new\n        promoted\n      }\n      links {\n        first {\n          href\n        }\n        next {\n          href\n        }\n        previous {\n          href\n        }\n        self {\n          href\n        }\n      }\n    }\n    ... on ListingError {\n      __typename\n      error {\n        code\n        detail\n        status\n        title\n        validation {\n          detail\n          field\n          title\n        }\n      }\n    }\n  }\n}\n",
        "variables": {
            "searchParameters": [
                {"key": "offset", "value": str(offset)},
                {"key": "limit", "value": str(PAGE_LIMIT)},
                {"key": "query", "value": query},
                {"key": "suggest_filters", "value":"true"},
                {"key": "sl","value": "19ab61ee5a7x555c86f7"}
            ],
        "fetchJobSummary":False,
        "fetchPayAndShip":True}
    }
    response = session.post(OLX_ENDPOINT, headers=GRAPH_QL_HEADERS, json=request)
    response.raise_for_status()

    return response.json()["data"]

def parse_olx_response(response: dict) -> tuple[list[Any], bool, int]:
    listing = response["clientCompatibleListings"]["data"]
    items = []
    for item in listing:
        parsed_item = {}
        parsed_item.update({"title": item["title"]})
        parsed_item.update({"url": item["url"]})
        parsed_item.update({"description": item["description"]})
        if item["photos"] is not None:
            parsed_item.update({"photos": item["photos"]})
        for param in item["params"]:
            if param["key"] == "price":
                parsed_item.update({"price": param["value"]["value"],
                                    "price_tag": param["value"]["label"],
                                    "negotiable": param["value"]["negotiable"],
                                    "arranged": param["value"]["arranged"]})
        items.append(parsed_item)

    has_next = bool(response["clientCompatibleListings"].get("links", {}).get("next", {}).get("href"))
    total = response["clientCompatibleListings"].get("metadata", {}).get("total_elements", 0)
    items = items[:PAGE_LIMIT]

    return items, has_next, total


if __name__ == "__main__":

    print(parse_olx_response(parse_olx_endpoint("iphone 13",1)))
