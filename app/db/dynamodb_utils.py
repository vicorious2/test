from datetime import datetime, timezone
import json

from pynamodb.models import Model
import time
from app.models.agenda_items import AgendaItemCreate, User

from ..utils.agenda_items_utils_v2 import create_agenda_item_in_db
from ..loggerFactory import LoggerFactory

logger = LoggerFactory.get_logger(__name__)


def create_table(
    table: Model,
    delete_if_exists: bool,
    read_capacity_units: int,
    write_capacity_units: int,
    populate_table: bool,
):
    if not table.exists():
        table.create_table(
            read_capacity_units=read_capacity_units,
            write_capacity_units=write_capacity_units,
            wait=True,
        )
        logger.debug(f"{table.Meta.table_name} table created")
        if populate_table:
            f = open("./json/agenda_items_for_DEV.json")
            data = json.load(f)
            for item in data.get("items"):
                create_agenda_item_in_db(
                    AgendaItemCreate.parse_obj(item),
                    User(email="system@example.com", username="system"),
                )
        return table
    elif delete_if_exists:
        logger.debug(f"{table.Meta.table_name} table already exists")
        logger.debug(f"Deleting {table.Meta.table_name} table")
        table.delete_table()

        # Wait for table to delete
        while table.exists():
            time.sleep(0.5)

        logger.debug(f"{table.Meta.table_name} table deleted")
        table.create_table(
            read_capacity_units=read_capacity_units,
            write_capacity_units=write_capacity_units,
            wait=True,
        )
        logger.debug(f"{table.Meta.table_name} table created")
        if populate_table:
            f = open("./json/agenda_items_for_DEV.json")
            data = json.load(f)
            for item in data.get("items"):
                create_agenda_item_in_db(
                    AgendaItemCreate.parse_obj(item),
                    User(email="system@example.com", username="system"),
                )
        return table
    else:
        logger.debug(f"{table.Meta.table_name} table already exists")
        return table
