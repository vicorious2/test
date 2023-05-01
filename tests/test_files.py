from app import files
import json


def test_sql_key_upcoming_events_v2():
    try:
        content = files.read_file("../sql/keyEvents/key_events_v2.sql")
        assert len(content) > 0
    except OSError:
        assert False


def test_bad_sql_key_upcoming_events_v2():
    try:
        content = files.read_file("../sql/key_Events/key_events_v2.sql")
        assert False
    except OSError:
        assert True


def test_sql_key_upcoming_events_v3():
    try:
        content = files.read_file("../sql/keyEvents/key_events_ci.sql")
        assert len(content) > 0
    except OSError:
        assert False


def test_filter_products_all():
    try:
        content = files.read_file("../sql/filterProducts/filter_products_all.sql")
        assert len(content) > 0
    except OSError:
        assert False


def test_filter_products_details():
    try:
        content = files.read_file("../sql/filterProducts/filter_projects_details.sql")
        assert len(content) > 0
    except OSError:
        assert False


def test_filter_products_tpp():
    try:
        content = files.read_file("../sql/filterProducts/filter_products_tpp.sql")
        assert len(content) > 0
    except OSError:
        assert False


def test_get_agenda_items_json():
    try:
        f = open("./json/agenda_items.json")
        data = json.load(f)
        assert "items" in data
        assert len(data["items"]) > 0
    except Exception as err:
        assert False
