from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException, Query

from ..models.agenda_items_v2 import (
    AgendaItem,
    AgendaItemCreate,
    AgendaItemsBoardUpdate,
    AgendaItemUpdate,
    ExportLink,
    GroupedAgendaItems,
    User,
)
from app.models.change_logs import ChangeLogResponse
from ..utils.agenda_items_utils_v2 import (
    create_agenda_item_in_db,
    delete_agenda_item_by_id,
    get_agenda_item_by_id,
    get_agenda_items_query,
    get_export_link_db,
    group_agenda_items,
    update_agenda_item_in_db,
    update_board,
    update_board_wo_transaction,
)
from app.utils.change_log_utils import get_change_logs_query, get_snapshot_db

from ..AuthUtil import get_user_name_and_email, is_authorized

router = APIRouter(
    prefix="/api",
    tags=["Agenda Items v2"],
    dependencies=[Depends(is_authorized)],
)

# 3x3 grid
@router.get(
    "/v2/agenda_items/borad", response_model=GroupedAgendaItems, include_in_schema=False
)
@router.get("/v2/agenda_items/board", response_model=GroupedAgendaItems)
def get_agenda_items(is_active: bool = True) -> GroupedAgendaItems:
    agenda_items = get_agenda_items_query(is_active)
    return group_agenda_items(agenda_items)


@router.put(
    "/v2/agenda_items/board/",
    response_model=GroupedAgendaItems,
    include_in_schema=False,
)
@router.put("/v2/agenda_items/board", response_model=GroupedAgendaItems)
def update_agenda_items_board(
    items: AgendaItemsBoardUpdate, user: User = Depends(get_user_name_and_email)
) -> AgendaItem:
    update_time = datetime.utcnow()
    updated_items = update_board_wo_transaction(items, user, update_time)

    return updated_items


@router.put("/v3/agenda_items/board", response_model=GroupedAgendaItems)
def update_agenda_items_board(
    items: AgendaItemsBoardUpdate, user: User = Depends(get_user_name_and_email)
) -> AgendaItem:
    update_time = datetime.utcnow()
    updated_items = update_board(items, user, update_time)

    return updated_items


# agenda item
@router.post("/v2/agenda_item/", response_model=AgendaItem, include_in_schema=False)
@router.post("/v2/agenda_item", response_model=AgendaItem)
def create_agenda_item(
    item: AgendaItem, user: User = Depends(get_user_name_and_email)
) -> AgendaItem:
    saved_item = create_agenda_item_in_db(item, user)
    return saved_item


# agenda items
@router.post(
    "/v2/agenda_items/", response_model=list[AgendaItem], include_in_schema=False
)
@router.post("/v2/agenda_items", response_model=list[AgendaItem])
def create_agenda_items(
    items: list[AgendaItem], user: User = Depends(get_user_name_and_email)
) -> list[AgendaItem]:
    for agendaItem in items:
        create_agenda_item_in_db(agendaItem, user)
    return items


@router.put("/v2/agenda_item/", response_model=AgendaItem, include_in_schema=False)
@router.put("/v2/agenda_item", response_model=AgendaItem)
def update_agenda_item(
    item: AgendaItem, user: User = Depends(get_user_name_and_email)
) -> AgendaItem:
    updated_item = update_agenda_item_in_db(item, user)

    return updated_item


@router.get(
    "/v2/agenda_item/{item_id:int}/",
    response_model=AgendaItem,
    include_in_schema=False,
)
@router.get("/v2/agenda_item/{item_id:int}", response_model=AgendaItem)
def get_agenda_item(item_id: int) -> AgendaItem:
    agenda_item = get_agenda_item_by_id(item_id)
    if agenda_item == None:
        raise HTTPException(status_code=404, detail="Item not found")
    return agenda_item


@router.delete(
    "/v2/agenda_item/{item_id}/", response_model=AgendaItem, include_in_schema=False
)
@router.delete("/v2/agenda_item/{item_id}", response_model=AgendaItem)
def delete_agenda_item(
    item_id: int, user: User = Depends(get_user_name_and_email)
) -> AgendaItem:
    agenda_item = delete_agenda_item_by_id(item_id, user)
    if agenda_item == None:
        raise HTTPException(status_code=404, detail="Item not found")
    return agenda_item


# change log section
@router.get(
    "/v2/agenda_items/change_logs/",
    response_model=ChangeLogResponse,
    include_in_schema=False,
)
@router.get("/v2/agenda_items/change_logs", response_model=ChangeLogResponse)
def get_change_logs(
    item_id: int | None = Query(default=None),
    limit: int | None = Query(default=None),
):
    changes = get_change_logs_query(item_id, limit=limit)

    return ChangeLogResponse(changes=changes)


@router.get(
    "/v2/agenda_items/export-link/", response_model=ExportLink, include_in_schema=False
)
@router.get("/v2/agenda_items/export-link", response_model=ExportLink)
def get_export_link():
    link = get_export_link_db()
    return {"url": link}


@router.get("/v2/agenda_items/snapshot", response_model=GroupedAgendaItems)
def get_snapshot(date: date = Query(example="2023-02-16")):
    snapshot = get_snapshot_db(date.isoformat())
    if snapshot:
        return snapshot
    else:
        raise HTTPException(404, f"Snapshot not found for date {date}")
