import json


def format_response_agenda_items_v1():
    f = open("./json/agenda_items.json")
    data = json.load(f)
    return data
