from datetime import datetime, date
import json

from fastapi import HTTPException
from app.db.dynamodb_models import (
    AgendaItemChangeLogDB,
    AgendaItemChangeLogEventDB,
    SnapshotsDB,
)
from app.models.agenda_items import (
    AgendaItem,
    AgendaItemUpdate,
    GroupedAgendaItems,
)
from app.models.change_logs import ChangeLog


def create_agenda_item_change_event(
    original_object: AgendaItem,
    new_object: AgendaItemUpdate,
    field: str,
) -> AgendaItemChangeLogEventDB:
    """
    Create a change log event for a given agenda item field change
    """
    original_object_dict = original_object.dict()
    new_object_dict = new_object.dict()

    change_event = AgendaItemChangeLogEventDB(
        field=field,
        original_value=str(original_object_dict.get(field)),
        new_value=str(new_object_dict.get(field)),
    )
    return change_event


def get_change_logs_query(
    agenda_item_id: int | None = None,
    limit: int | None = None,
) -> list[ChangeLog]:
    """
    Get the change logs for all agenda items or a specific agenda item
    """
    if agenda_item_id != None:
        events = AgendaItemChangeLogDB.query(
            hash_key="agenda_items_change_log",
            range_key_condition=AgendaItemChangeLogDB.sort_key.startswith(
                f"agenda_item_{agenda_item_id}"
            ),
        )
    else:
        events = AgendaItemChangeLogDB.change_log_index.query(
            hash_key="agenda_items_change_log",
            scan_index_forward=False,
            limit=limit,
        )

    return_events = []

    for event in events:
        item_id = event.sort_key.split("#")[0].split("agenda_item_")[1]
        return_events.append(
            ChangeLog(**json.loads(event.to_json()), agenda_item_id=item_id)
        )

    return return_events


def get_snapshot_db(date_to_get: str) -> GroupedAgendaItems | None:
    """
    Get a the last snapshot on a given date
    """
    dates = get_snapshot_dates()
    days = {}
    for date_iter in dates:
        day = datetime.fromisoformat(date_iter).strftime("%Y-%m-%d")
        if day in days:
            days[day].append(date_iter)
        else:
            days[day] = [date_iter]

    if date_to_get in days:
        timestamp = days[date_to_get][0]
        snapshot = SnapshotsDB.get(hash_key="snapshots", range_key=timestamp)
        groups = GroupedAgendaItems.parse_obj(snapshot.snapshot_data.as_dict())
        return groups
    else:
        return None


def get_snapshot_dates() -> list[str]:
    """
    Get all dates of all snapshots
    """
    return_dates = []
    dates = SnapshotsDB.query(hash_key="snapshots", attributes_to_get="sort_key")
    dates_sorted = sorted(
        dates, key=lambda x: datetime.fromisoformat(x.sort_key), reverse=True
    )
    for date in dates_sorted:
        return_dates.append(date.sort_key)
    return return_dates
