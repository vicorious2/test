from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException, Query

from ..models.notifications import agenda_item_notification, data_metric_notification
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

from ..models.agenda_items_v2 import ExternalLink

from ..AuthUtil import get_user_name_and_email, is_authorized

router = APIRouter(
    prefix="/api",
    tags=["Notifications"],
    # dependencies=[Depends(is_authorized)],
)

# 3x3 grid
@router.get(
    "/notifications", response_model=agenda_item_notification, include_in_schema=False
)
@router.get("/notifications", response_model=agenda_item_notification)
def get_agenda_items(agendaItemId: int = 0) -> agenda_item_notification:
    notification = agenda_item_notification()
    notification.agendaItemId = 100
    notification.status = "red"

    notification.reason = "reason"
    notification.keyInsights = "insights for an Agenda Item"
    externalLink = ExternalLink(href="", label="")
    externalLink.href = "https://sensing-dev.nimbus.amgen.com"
    externalLink.label = "sensing portal"
    notification.externalLink = externalLink
    notification.metrics = list[data_metric_notification]()
    notification.metrics.append(
        data_metric_notification(type="brand", metricName="NetSales", status="gray")
    )
    notification.metrics.append(
        data_metric_notification(
            type="Supply",
            metricName="InventoryBelowTarget",
            status="Enrollment Started",
        )
    )

    return notification
