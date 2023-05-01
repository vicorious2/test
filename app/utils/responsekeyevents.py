"""
Format response for key events controller
"""
from ..constant import Constant
from itertools import groupby
from operator import itemgetter


def format_response_V2(response: any, key_group: any):
    """
    method for format_response from AWS Athena
    ---
    responses:
    {
        "clickthrough": {
        "href": "https://app.smartsheet.com/dashboards/cCf6jcggx6q3vHrCGxgWWpjc8qFmV32cjv5hjv91"
    },
    "series": [
    {
      "key_event_label": "Flash Memos",
      "total_count": 15,
      "items": [
        {
          "product": "TEZSPIRE",
          "milestone_category": "Clinical",
          "description": "Tezepelumab Chronic Obstructive Pulmonary Disease (COPD)",
          "date_of_the_day": "2022-07-29T17:30:00.000Z",
          "geographic_area": null,
          "project_type": "New Indication / Disease State",
          "activity_type": "PRI_AN_FLASH"
        }
      ]}]
    }
    """
    # items_sorted = sorted(response[1], key= itemgetter(key_group)) ##key_events_label
    if response is None:
        return []
    onject = {}
    items = []
    categories = []
    dictionary = {"clickthrough": {"href": Constant.CLICKTROUGH}, "series": []}
    group_by_array = groupby(response[1], key=itemgetter(key_group))

    for key, value in group_by_array:
        if len(items) > 0:
            onject["items"] = items
            items = []
            dictionary["series"].append(onject)
            onject = {}
        onject["key_event_label"] = key
        categories.append(key)
        for k in value:
            onject["total_count"] = k["rec_count"]
            item = {
                "ipp_short_name": k["ipp_short_name"],
                #'competitor': k['competitor'],
                "data_readout_type": k["data_readout_type"],
                #'competitor_asset': k['competitor_asset'],
                "description": k["description"],
                "end_date": k["end_date"],
                "geographic_area": k["geographic_area"],
            }
            items.append(item)
    # Last item
    if len(items) > 0:
        onject["items"] = items
        items = []
        dictionary["series"].append(onject)
        onject = {}
    # Default JSONCategories (If response no contains any categorie.
    # we add those categories with total_count "0" and items empty)
    not_intersection = list(
        set(Constant.CATEGORIES_V2).symmetric_difference(categories)
    )
    for value in not_intersection:
        onject = {"key_event_label": value, "total_count": "0", "items": []}
        dictionary["series"].append(onject)

    dictionary["series"] = list(
        sorted(
            dictionary["series"],
            key=lambda word: Constant.CATEGORIES.index(word["key_event_label"]),
        )
    )
    return dictionary


def format_response_V3(response: any, key_group: any):
    """
    method for format_response from AWS Athena
    ---
    """
    # items_sorted = sorted(response[1], key= itemgetter(key_group)) ##key_events_label
    if response is None:
        return []
    onject = {}
    items = []
    group_by_array = groupby(response[1], key=itemgetter(key_group))

    for key, value in group_by_array:
        if len(items) > 0:
            onject["items"] = items
            items = []
            onject = {}
        onject["key_event_label"] = key
        for k in value:
            onject["total_count"] = k["rec_count"]
            item = {
                "competitor": k["competitor"],
                "product": k["product"],
                "competitor_asset": k["competitor_asset"],
                "brief_title": k["brief_title"],
                "prioritized": k["prioritized"],
                "end_date": k["end_date"],
                "start_date": k["start_date"],
                "geographic_area": k["country"],
            }
            items.append(item)
    # Last item
    if len(items) > 0:
        onject["items"] = items
        items = []

    return onject


def format_response_key_events_v4(response: any):
    """
    method for format_response_key_products_csp from AWS Athena
    ---
    """
    # items_sorted = sorted(response[1], key= itemgetter(key_group)) ##key_events_label
    if response is None:
        return []
    onject = {}
    items = []
    categories = []
    dictionary = {"clickthrough": {"href": Constant.CLICKTROUGH}, "series": []}
    group_by_array = groupby(response[1], key=itemgetter("key_events_label"))

    for key, value in group_by_array:
        if len(items) > 0:
            onject["items"] = items
            items = []
            dictionary["series"].append(onject)
            onject = {}
        onject["key_event_label"] = key
        categories.append(key)
        for d in value:
            onject["total_count"] = d["rec_count"]
            item = {
                "event_list_order": d["event_list_order"],
                "key_events_label": d["key_events_label"],
                "rec_count": d["rec_count"],
                "ipp_short_name": d["ipp_short_name"],
                "data_readout_type": d["data_readout_type"],
                "description": d["description"],
                "geographic_area": d["geographic_area"],
                "end_date": d["end_date"],
                "amg_number": d["amg_number"],
                "product": d["product"],
                "competitor": d["competitor"],
                "brief_title": d["brief_title"],
                "country": d["country"],
                "start_date": d["start_date"],
                "competitor_asset": d["competitor_asset"],
                "sort_date": d["sort_date"],
                "prioritized": d["prioritized"],
            }
            items.append(item)
    # Last item
    if len(items) > 0:
        onject["items"] = items
        items = []
        dictionary["series"].append(onject)
        onject = {}
    # Default JSONCategories (If response no contains any categorie.
    # we add those categories with total_count "0" and items empty)
    not_intersection = list(set(Constant.CATEGORIES).symmetric_difference(categories))
    for value in not_intersection:
        onject = {"key_event_label": value, "total_count": "0", "items": []}
        dictionary["series"].append(onject)

    dictionary["series"] = list(
        sorted(
            dictionary["series"],
            key=lambda word: Constant.CATEGORIES.index(word["key_event_label"]),
        )
    )
    return dictionary
