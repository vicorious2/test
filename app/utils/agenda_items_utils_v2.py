import functools
import json
import os
from sqlite3 import connect
import time
import traceback
from typing import Dict

from ..models.repatha_metrics import Commercial
from app.models.pipeline import Pipeline
from ..dataHelper import DataHelper
from fastapi import HTTPException
from ..constant import Constant
from pynamodb.exceptions import DoesNotExist, PutError, UpdateError, TransactWriteError
from pynamodb.expressions.update import Action
from pynamodb.connection import Connection
from pynamodb.connection.table import TableConnection

# from botocore.session import Session
import botocore.session


from pynamodb.transactions import TransactWrite
from datetime import datetime
from ..db.dynamodb_models import (
    AgendaItemChangeLogDB,
    AgendaItemV2DB,
    SnapshotsDB,
)
from app.models.pipeline import PriorityCriticalPathStudyEnrollmenP

from app.loggerFactory import LoggerFactory
from app.models.agenda_items_v2 import (
    AgendaItem,
    AgendaItemBoardResponse,
    AgendaItemCreate,
    AgendaItemUpdate,
    AgendaItemsBoardUpdate,
    BoxGroup,
    GroupedAgendaItems,
    User,
)
import random
import string

from ..utils.change_log_utils import create_agenda_item_change_event

logger = LoggerFactory.get_logger(__name__)


def compare_groups(group1: BoxGroup, group2: BoxGroup):
    """
    Compare function that enables sorting the agenda item groups for the frontend
    """
    if group1.value != group2.value:
        return group2.value - group1.value
    return group1.focus - group2.focus


def group_agenda_items(items: list[AgendaItem]) -> GroupedAgendaItems:
    """
    Groups agenda items into boxes based on value and focus
    """
    box_group_dict: Dict[tuple, BoxGroup] = {}

    # Create empty box groups for each box
    for i in range(1, 4):
        for j in range(1, 4):
            box_group_dict[(i, j)] = BoxGroup(value=i, focus=j, items=[])

    # Populate each box group with the respective items

    for item in items:
        box_group_dict[(item.value, item.focus)].items.append(
            AgendaItemBoardResponse.parse_obj(item)
        )

    # Sort groups for frontend
    groups = list(box_group_dict.values())
    groups = sorted(groups, key=functools.cmp_to_key(compare_groups))
    return GroupedAgendaItems(groups=groups)


def get_criticalPathStudy_status(
    criticalPathStudy: list[PriorityCriticalPathStudyEnrollmenP],
):
    for item in criticalPathStudy:
        if item.enrStatus == Constant.PA_STATUS_RED or item.enrStatus == "Delayed":
            return Constant.PA_STATUS_RED
        elif item.enrStatus == Constant.PA_STATUS_YELLOW:
            return Constant.PA_STATUS_YELLOW
    return Constant.PA_STATUS_GREEN


def calculate_pipline_status(pipeline: Pipeline) -> string:
    pipeline.reason = ""
    npl = "Next Priority "
    npm = "Next Priority Milestone, "
    npcsp = "Priority Study Critical Path Enrollment, "
    dateStr = ""
    if pipeline.nextLaunch.e2lLauDesc == "Launch":
        dateStr = " Date"
    if (
        pipeline == None
        or pipeline.nextLaunch == None
        or pipeline.nextMilestone == None
        or pipeline.criticalPathStudy == None
    ):
        if pipeline.nextLaunch == None:
            pipeline.reason = (
                pipeline.reason + npl + pipeline.nextLaunch.e2lLauDesc + dateStr + ", "
            )
        if pipeline.nextMilestone == None:
            pipeline.reason = pipeline.reason + npm
        if pipeline.criticalPathStudy == None:
            pipeline.reason = pipeline.reason + npcsp
        pipeline.reason = pipeline.reason[0 : len(pipeline.reason) - 2] + "."
        pipeline.status = Constant.PA_STATUS_GRAY
        return Constant.PA_STATUS_GRAY

    criticalPathStudy_status = get_criticalPathStudy_status(pipeline.criticalPathStudy)
    if (
        pipeline.nextLaunch.status == Constant.PA_STATUS_RED
        or pipeline.nextMilestone.status == Constant.PA_STATUS_RED
        or criticalPathStudy_status == Constant.PA_STATUS_RED
    ):
        if pipeline.nextLaunch.status == Constant.PA_STATUS_RED:
            pipeline.reason = (
                pipeline.reason + npl + pipeline.nextLaunch.e2lLauDesc + dateStr + ", "
            )
        if pipeline.nextMilestone.status == Constant.PA_STATUS_RED:
            pipeline.reason = pipeline.reason + npm
        if criticalPathStudy_status == Constant.PA_STATUS_RED:
            pipeline.reason = pipeline.reason + npcsp
        pipeline.reason = pipeline.reason[0 : len(pipeline.reason) - 2]
        if pipeline.reason.count(",") > 0:
            old = ","
            new = " and "
            maxreplace = 1
            pipeline.reason = new.join(pipeline.reason.rsplit(old, maxreplace))
        pipeline.reason = pipeline.reason + "."
        pipeline.status = Constant.PA_STATUS_RED
        return Constant.PA_STATUS_RED

    elif (
        pipeline.nextLaunch.status == Constant.PA_STATUS_YELLOW
        or pipeline.nextMilestone.status == Constant.PA_STATUS_YELLOW
        or criticalPathStudy_status == Constant.PA_STATUS_YELLOW
    ):
        if pipeline.nextLaunch.status == Constant.PA_STATUS_YELLOW:
            pipeline.reason = (
                pipeline.reason + npl + pipeline.nextLaunch.e2lLauDesc + dateStr + ", "
            )
        if pipeline.nextMilestone.status == Constant.PA_STATUS_YELLOW:
            pipeline.reason = pipeline.reason + npm
        if criticalPathStudy_status == Constant.PA_STATUS_YELLOW:
            pipeline.reason = pipeline.reason + npcsp
        pipeline.reason = pipeline.reason[0 : len(pipeline.reason) - 2]
        if pipeline.reason.count(",") > 0:
            old = ","
            new = " and "
            maxreplace = 1
            pipeline.reason = new.join(pipeline.reason.rsplit(old, maxreplace))
        pipeline.reason = pipeline.reason + "."
        pipeline.status = Constant.PA_STATUS_YELLOW
        return Constant.PA_STATUS_YELLOW

    if pipeline.nextLaunch.e2lLauDesc == None:
        pipeline.nextLaunch.e2lLauDesc = ""
    pipeline.reason = (
        npl + pipeline.nextLaunch.e2lLauDesc + dateStr + ", " + npm + npcsp
    )
    pipeline.reason = pipeline.reason[0 : len(pipeline.reason) - 2]
    if pipeline.reason.count(",") > 0:
        old = ","
        new = " and "
        maxreplace = 1
        pipeline.reason = new.join(pipeline.reason.rsplit(old, maxreplace))
    pipeline.reason = pipeline.reason + "."
    return Constant.PA_STATUS_GREEN


def calculate_commercial_repatha_status(commercial: Commercial) -> string:
    try:
        if (
            commercial.brand.netSales.status == Constant.PA_STATUS_RED
            or commercial.brand.nbrxDemand.status == Constant.PA_STATUS_RED
            or commercial.brand.trxDemand.status == Constant.PA_STATUS_RED
            or commercial.brand.idnAccountWins.status == Constant.PA_STATUS_RED
            or commercial.brand.nbrxFulfillment.status == Constant.PA_STATUS_RED
            or commercial.brand.nbrxVolume.status == Constant.PA_STATUS_RED
            or commercial.brand.shareOfVoice.status == Constant.PA_STATUS_RED
            or commercial.pipeline.status == Constant.PA_STATUS_RED
            or commercial.supply.anc.status == Constant.PA_STATUS_RED
            or commercial.supply.aoh.status == Constant.PA_STATUS_RED
            or commercial.supply.cogsReduction.status == Constant.PA_STATUS_RED
            or commercial.supply.inventoryBelowTarget.status == Constant.PA_STATUS_RED
            or commercial.people.engagementScore.status == Constant.PA_STATUS_RED
            or commercial.people.talentAcquisition.status == Constant.PA_STATUS_RED
            or commercial.people.turnover.status == Constant.PA_STATUS_RED
        ):
            setStatusReasonCommercial(commercial, Constant.PA_STATUS_RED)
            return Constant.PA_STATUS_RED
        if (
            commercial.brand.netSales.status == Constant.PA_STATUS_YELLOW
            or commercial.brand.nbrxDemand.status == Constant.PA_STATUS_YELLOW
            or commercial.brand.trxDemand.status == Constant.PA_STATUS_YELLOW
            or commercial.brand.idnAccountWins.status == Constant.PA_STATUS_YELLOW
            or commercial.brand.nbrxFulfillment.status == Constant.PA_STATUS_YELLOW
            or commercial.brand.nbrxVolume.status == Constant.PA_STATUS_YELLOW
            or commercial.brand.shareOfVoice.status == Constant.PA_STATUS_YELLOW
            or commercial.pipeline.status == Constant.PA_STATUS_YELLOW
            or commercial.supply.anc.status == Constant.PA_STATUS_YELLOW
            or commercial.supply.aoh.status == Constant.PA_STATUS_YELLOW
            or commercial.supply.cogsReduction.status == Constant.PA_STATUS_YELLOW
            or commercial.supply.inventoryBelowTarget.status
            == Constant.PA_STATUS_YELLOW
            or commercial.people.engagementScore.status == Constant.PA_STATUS_YELLOW
            or commercial.people.talentAcquisition.status == Constant.PA_STATUS_YELLOW
            or commercial.people.turnover.status == Constant.PA_STATUS_YELLOW
        ):
            setStatusReasonCommercial(commercial, Constant.PA_STATUS_YELLOW)
            return Constant.PA_STATUS_YELLOW
        if (
            commercial.brand.netSales.status == Constant.PA_STATUS_GRAY
            and commercial.brand.nbrxDemand.status == Constant.PA_STATUS_GRAY
            and commercial.brand.trxDemand.status == Constant.PA_STATUS_GRAY
            and commercial.brand.idnAccountWins.status == Constant.PA_STATUS_GRAY
            and commercial.brand.nbrxFulfillment.status == Constant.PA_STATUS_GRAY
            and commercial.brand.nbrxVolume.status == Constant.PA_STATUS_GRAY
            and commercial.brand.shareOfVoice.status == Constant.PA_STATUS_GRAY
            and commercial.pipeline.status == Constant.PA_STATUS_GRAY
            and commercial.supply.anc.status == Constant.PA_STATUS_GRAY
            and commercial.supply.aoh.status == Constant.PA_STATUS_GRAY
            and commercial.supply.cogsReduction.status == Constant.PA_STATUS_GRAY
            and commercial.supply.inventoryBelowTarget.status == Constant.PA_STATUS_GRAY
            and commercial.people.engagementScore.status == Constant.PA_STATUS_GRAY
            and commercial.people.talentAcquisition.status == Constant.PA_STATUS_GRAY
            and commercial.people.turnover.status == Constant.PA_STATUS_GRAY
        ):
            setStatusReasonCommercial(commercial, Constant.PA_STATUS_GRAY)
            return Constant.PA_STATUS_GRAY
        commercial.reason = " Brand, Pipeline, Supply and People metrics."
        return Constant.PA_STATUS_GREEN
    except:
        logger.debug(traceback.print_exc())
        commercial.reason = " an error occurred calculating the status or you do not have permissions to calculate status"
        return Constant.PA_STATUS_GRAY


def setStatusReasonCommercial(commercial: Commercial, status: str):
    commercial.reason = ""
    if (
        commercial.brand.netSales.status == status
        or commercial.brand.nbrxDemand.status == status
        or commercial.brand.trxDemand.status == status
        or commercial.brand.idnAccountWins.status == status
        or commercial.brand.nbrxFulfillment.status == status
        or commercial.brand.nbrxVolume.status == status
        or commercial.brand.shareOfVoice.status == status
    ):
        commercial.reason = commercial.reason + " Brand,"
    if commercial.pipeline.status == status:
        commercial.reason = commercial.reason + " Pipeline,"
    if (
        commercial.supply.anc.status == status
        or commercial.supply.aoh.status == status
        or commercial.supply.cogsReduction.status == status
        or commercial.supply.inventoryBelowTarget.status == status
    ):
        commercial.reason = commercial.reason + " Supply,"

    if (
        commercial.people.engagementScore.status == status
        or commercial.people.talentAcquisition.status == status
        or commercial.people.turnover.status == status
    ):
        commercial.reason = commercial.reason + " People,"

    commercial.reason = commercial.reason[0 : len(commercial.reason) - 1]
    if commercial.reason.count(",") > 0:
        old = ","
        new = " and"
        maxreplace = 1
        commercial.reason = new.join(commercial.reason.rsplit(old, maxreplace))
    commercial.reason = commercial.reason + " metrics."


def get_agenda_items_query(is_active: bool = True) -> list[AgendaItem]:
    """
    Get all agenda items in the Dynamodb table
    """

    tic = time.perf_counter()
    try:
        if is_active:
            result = AgendaItemV2DB.query(
                hash_key="agenda_items_v2",
                consistent_read=True,
                filter_condition=AgendaItemV2DB.isActive == True,
            )
        else:
            result = AgendaItemV2DB.query(
                hash_key="agenda_items_v2",
                consistent_read=True,
                filter_condition=AgendaItemV2DB.isActive == False,
            )

    except Exception as err:
        raise err

    items = []
    for item in result:
        items.append(AgendaItem(**json.loads(item.to_json())))
        # if item.name == "Repatha":
        #    item.status = calculate_commercial_repatha_status_OLD()
        # if item.name == "Tarlatamab":
        #    item.status = calculate_tarlatamab_status()

    toc = time.perf_counter()

    logger.debug(f"Query for all agenda items took {toc - tic:0.4f} seconds")

    return items


def get_agenda_item_db_by_id(id: int) -> AgendaItemV2DB | None:
    try:
        tic = time.perf_counter()
        item = AgendaItemV2DB.get(
            hash_key="agenda_items_v2", range_key=f"agenda_item_{id}"
        )
        toc = time.perf_counter()
        logger.debug(f"Getting agenda item took {toc - tic:0.4f} seconds")
        return item
    except DoesNotExist:
        return None


def get_agenda_item_by_id(id: int) -> AgendaItem | None:
    """
    Get agenda item by id
    """
    item = get_agenda_item_db_by_id(id)
    if item is not None:
        return AgendaItem(**json.loads(item.to_json()))
    else:
        return None


def delete_agenda_item_by_id(id: int, user: User) -> AgendaItem | None:
    """
    Delete agenda item by id
    """
    agendaItem = get_agenda_item_db_by_id(id)
    update_time = datetime.utcnow()

    if agendaItem is not None:
        agendaItem.update(
            actions=[
                AgendaItemV2DB.updatedBy.set(user.dict()),
                AgendaItemV2DB.updatedDate.set(update_time),
                AgendaItemV2DB.isActive.set(False),
            ]
        )

        return get_agenda_item_by_id(id)
    else:
        return None


def create_agenda_item_in_db(item: AgendaItem, user: User) -> AgendaItem:
    """
    Add a new agenda_item to the Dynamodb table
    """
    try:
        tic = time.perf_counter()
        existing_ids = get_all_agendaItemIds()

        # Set unique id number for agenda item
        if len(existing_ids) == 0:
            id = 1
        else:
            id = max(existing_ids) + 1

        # Check if agenda item already exists in db
        condition = AgendaItemV2DB.agendaItemId.does_not_exist()
        aiDict = item.dict()
        aiDict.pop("agendaItemId")
        aiDict.pop("createdBy")
        aiDict.pop("updatedBy")
        aiDict.pop("version")

        # Save agenda item in db
        AgendaItemV2DB(
            hash_key=f"agenda_items_v2",
            range_key=f"agenda_item_{id}",
            agendaItemId=id,
            createdBy=user.dict(),
            updatedBy=user.dict(),
            **aiDict,
        ).save(condition=condition)
        toc = time.perf_counter()
        logger.debug(f"Creating agenda item took {toc - tic:0.4f} seconds")

        agenda_item_in_db = get_agenda_item_by_id(id)
        return agenda_item_in_db

    except PutError as err:
        raise err


def update_agenda_item_in_db(item: AgendaItem, user: User) -> AgendaItem:
    """
    Update an agenda item's metadata
    """
    current_item = get_agenda_item_db_by_id(item.agendaItemId)
    if current_item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    # TODDO FIX UPDATED DATE
    update_time = datetime.utcnow()
    item.updatedDate = update_time
    item.updatedBy = user.dict()
    aiDict = item.dict()

    # Save agenda item in db
    AgendaItemV2DB(
        hash_key=f"agenda_items_v2",
        range_key=f"agenda_item_{item.agendaItemId}",
        **aiDict,
    ).save()
    # toc = time.perf_counter()
    # logger.debug(f"Creating agenda item took {toc - tic:0.4f} seconds")

    agenda_item_in_db = get_agenda_item_by_id(item.agendaItemId)
    return agenda_item_in_db


def update_agenda_item_in_db_OLD(item: AgendaItemUpdate, user: User) -> AgendaItem:
    """
    Update an agenda item's metadata
    """
    current_item = get_agenda_item_db_by_id(item.agendaItemId)
    if current_item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    current_item_parsed = AgendaItem(**json.loads(current_item.to_json()))
    update_time = datetime.utcnow()

    actions, change_log = compare_items_for_update(
        current_item_parsed, item, user, update_time
    )

    if len(actions) > 0:
        actions.append(AgendaItemV2DB.set(user.dict()))
        actions.append(AgendaItemV2DB.updated_date.set(update_time))

        # FIX THIS: Connection() requires AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY to be set
        # THIS MAY HAVE UNINTENDED CONSEQUENCES
        os.environ["AWS_ACCESS_KEY_ID"] = os.environ["AWS_DYNAMO_ACCESS_KEY_ID"]
        os.environ["AWS_SECRET_ACCESS_KEY"] = os.environ["AWS_DYNAMO_SECRET_ACCESS_KEY"]

        # Perform all update operations
        connection = Connection(
            region="us-west-2",
        )

        # TransactWrite ensures all of the operations take place as one single operation or they all fail together
        # # https://docs.aws.amazon.com/amazondynamodb/latest/APIReference/API_TransactWriteItems.html#DDB-TransactWriteItems-request-ClientRequestToken
        client_request_token = "".join(random.choices(string.ascii_lowercase, k=5))

        with TransactWrite(
            connection=connection, client_request_token=client_request_token
        ) as transaction:
            transaction.update(model=current_item, actions=actions)
            transaction.save(model=change_log)

        current_item.refresh(consistent_read=True)
    return AgendaItem(**json.loads(current_item.to_json()))


def compare_items_for_update(
    original_object: AgendaItem,
    new_object: AgendaItemUpdate,
    user: User,
    update_time: datetime,
) -> tuple[list[Action], AgendaItemChangeLogDB]:
    """
    Compare two AgendaItems and return a list of actions to update the item
    """
    actions = []
    change_log_events = []
    if original_object.status != new_object.status:
        actions.append(AgendaItemV2DB.status.set(new_object.status))
        change_log_events.append(
            create_agenda_item_change_event(original_object, new_object, "status")
        )

    if original_object.status_details != new_object.status_details:
        actions.append(AgendaItemV2DB.status_details.set(new_object.status_details))
        change_log_events.append(
            create_agenda_item_change_event(
                original_object, new_object, "status_details"
            )
        )

    if original_object.href != new_object.href:
        actions.append(AgendaItemV2DB.href.set(new_object.href))
        change_log_events.append(
            create_agenda_item_change_event(
                original_object,
                new_object,
                "href",
            )
        )

    if original_object.description != new_object.description:
        actions.append(AgendaItemV2DB.description.set(new_object.description))
        change_log_events.append(
            create_agenda_item_change_event(
                original_object,
                new_object,
                "description",
            )
        )

    if original_object.is_active != new_object.is_active:
        actions.append(AgendaItemV2DB.is_active.set(new_object.is_active))
        change_log_events.append(
            create_agenda_item_change_event(original_object, new_object, "is_active")
        )

    change_log = None
    if len(actions) > 0:
        change_log = AgendaItemChangeLogDB(
            hash_key="agenda_items_change_log",
            sort_key=f"agenda_item_{new_object.agendaItemId}#{update_time}",
            timestamp=update_time,
            user=user.dict(),
            events=change_log_events,
        )

    return actions, change_log


def get_all_agendaItemIds() -> list[int]:
    """
    Get all agenda item ids in the DynamoDB table
    """
    try:
        tic = time.perf_counter()
        res = AgendaItemV2DB.query(
            hash_key="agenda_items_v2", attributes_to_get=["agendaItemId"]
        )
        ids = []
        for i in res:
            ids.append(i.agendaItemId)
        toc = time.perf_counter()
        logger.debug(f"Query for all agenda item ids took {toc - tic:0.4f} seconds")
        return ids
    except Exception as err:
        raise err


def convert_grouped_items_to_list(items: GroupedAgendaItems) -> list[AgendaItem]:
    """
    Convert a GroupedAgendaItems object to a list of AgendaItems
    """
    agenda_items = []
    for group in items.groups:
        for item in group.items:
            agenda_items.append(item)

    return agenda_items


def update_board_wo_transaction(
    new_items: AgendaItemsBoardUpdate, user: User, update_time: datetime
) -> GroupedAgendaItems:
    """
    Update the positions of all changed agenda items
    """
    list_of_new_items = convert_grouped_items_to_list(new_items)
    dict_of_new_items: Dict[int, AgendaItem] = {}

    # Create dictionary of new items with id as the key
    for item in list_of_new_items:
        if item.agendaItemId not in dict_of_new_items:
            dict_of_new_items[int(item.agendaItemId)] = item
        else:
            raise ValueError(f"Duplicate agenda item with id {item.agendaItemId} found")

    existing_items = get_agenda_items_query()
    dict_of_existing_items: Dict[int, AgendaItem] = {}

    # Create dictionary of existing items with id as the key
    for item in existing_items:
        if item.agendaItemId not in dict_of_existing_items:
            dict_of_existing_items[int(item.agendaItemId)] = item
        else:
            raise ValueError(f"Duplicate agenda item with id {item.agendaItemId} found")

    keys = dict_of_new_items.keys()

    # Determine actions needed to update items in db
    update_operations = []
    for key in keys:
        new_item = dict_of_new_items.get(key)
        existing_item = dict_of_existing_items.get(key)

        actions = []
        change_log_events = []
        if new_item.value != existing_item.value:
            actions.append(AgendaItemV2DB.value.set(new_item.value))
            change_log_events.append(
                create_agenda_item_change_event(existing_item, new_item, "value")
            )

        if new_item.focus != existing_item.focus:
            actions.append(AgendaItemV2DB.focus.set(new_item.focus))
            change_log_events.append(
                create_agenda_item_change_event(existing_item, new_item, "focus")
            )

        if new_item.order != existing_item.order:
            actions.append(AgendaItemV2DB.order.set(new_item.order))
            change_log_events.append(
                create_agenda_item_change_event(existing_item, new_item, "order")
            )

        if len(actions) > 0:
            print(key, flush=True)
            agendaItem = get_agenda_item_db_by_id(key)
            agendaItem.update(
                actions=[
                    AgendaItemV2DB.updatedBy.set(user.dict()),
                    AgendaItemV2DB.updatedDate.set(update_time),
                    AgendaItemV2DB.value.set(new_item.value),
                    AgendaItemV2DB.focus.set(new_item.focus),
                    AgendaItemV2DB.order.set(new_item.order),
                ]
            )

    updated_items = get_agenda_items_query()
    return group_agenda_items(updated_items)


def update_board(
    new_items: AgendaItemsBoardUpdate, user: User, update_time: datetime
) -> GroupedAgendaItems:
    """
    Update the positions of all changed agenda items
    """
    list_of_new_items = convert_grouped_items_to_list(new_items)
    dict_of_new_items: Dict[int, AgendaItem] = {}

    # Create dictionary of new items with id as the key
    for item in list_of_new_items:
        if item.agendaItemId not in dict_of_new_items:
            dict_of_new_items[int(item.agendaItemId)] = item
        else:
            raise ValueError(f"Duplicate agenda item with id {item.agendaItemId} found")

    existing_items = get_agenda_items_query()
    dict_of_existing_items: Dict[int, AgendaItem] = {}

    # Create dictionary of existing items with id as the key
    for item in existing_items:
        if item.agendaItemId not in dict_of_existing_items:
            dict_of_existing_items[int(item.agendaItemId)] = item
        else:
            raise ValueError(f"Duplicate agenda item with id {item.agendaItemId} found")

    keys = dict_of_new_items.keys()

    # Determine actions needed to update items in db
    update_operations = []
    for key in keys:
        new_item = dict_of_new_items.get(key)
        existing_item = dict_of_existing_items.get(key)

        actions = []
        change_log_events = []
        if new_item.value != existing_item.value:
            actions.append(AgendaItemV2DB.value.set(new_item.value))
            change_log_events.append(
                create_agenda_item_change_event(existing_item, new_item, "value")
            )

        if new_item.focus != existing_item.focus:
            actions.append(AgendaItemV2DB.focus.set(new_item.focus))
            change_log_events.append(
                create_agenda_item_change_event(existing_item, new_item, "focus")
            )

        if new_item.order != existing_item.order:
            actions.append(AgendaItemV2DB.order.set(new_item.order))
            change_log_events.append(
                create_agenda_item_change_event(existing_item, new_item, "order")
            )

        if len(actions) > 0:
            actions.append(AgendaItemV2DB.updatedBy.set(user.dict()))
            actions.append(AgendaItemV2DB.updatedDate.set(update_time))
            update_operations.append(
                {
                    "item": AgendaItemV2DB(
                        hash_key="agenda_items_v2",
                        range_key=f"agenda_item_{new_item.agendaItemId}",
                        version=existing_item.version,
                    ),
                    "actions": actions,
                }
            )
            change_log = AgendaItemChangeLogDB(
                hash_key="agenda_items_change_log",
                sort_key=f"agenda_item_{new_item.agendaItemId}#{update_time}",
                timestamp=update_time,
                user=user.dict(),
                events=change_log_events,
            )

    # Perform all update operations
    logger.debug(f"update v2 prior to transaction")
    # TODO: FIX THIS: Connection() requires AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY to be set
    # THIS MAY HAVE UNINTENDED CONSEQUENCES
    os.environ["AWS_ACCESS_KEY_ID"] = os.environ["AWS_DYNAMO_ACCESS_KEY_ID"]
    os.environ["AWS_SECRET_ACCESS_KEY"] = os.environ["AWS_DYNAMO_SECRET_ACCESS_KEY"]
    logger.debug(f"after trying to to set os env")
    # Perform all update operations

    # TransactWrite ensures all of the operations take place as one single operation or they all fail together
    # # https://docs.aws.amazon.com/amazondynamodb/latest/APIReference/API_TransactWriteItems.html#DDB-TransactWriteItems-request-ClientRequestToken
    client_request_token = "".join(random.choices(string.ascii_lowercase, k=5))

    connection = Connection(
        region="us-west-2",
        aws_access_key_id=os.environ["AWS_DYNAMO_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["AWS_DYNAMO_SECRET_ACCESS_KEY"],
        aws_session_token=client_request_token,
    )

    # connection.add_meta_table(AgendaItemV2DB.Meta)
    # SESSION = botocore.session.get_session()

    # client = SESSION.create_client(
    #    "dynamodb",
    #    endpoint_url="https://dynamodb.us-west-2.amazonaws.com",
    #    region_name="us-west-2",
    #    aws_access_key_id=os.environ["AWS_DYNAMO_ACCESS_KEY_ID"],
    #    aws_secret_access_key=os.environ["AWS_DYNAMO_SECRET_ACCESS_KEY"],
    #    aws_session_token=client_request_token,
    # )
    # connection._client = client
    # connection._convert_to_request_dict__endpoint_url = True
    # print(connection.region, flush=True)
    # print(connection._client, flush=True)
    print("post connection create", flush=True)

    # connection = TableConnection(AgendaItemV2DB.Meta)
    # connection = Connection()

    logger.debug(f"client_request_token set")
    if len(update_operations) > 0:
        try:
            with TransactWrite(connection=connection) as transaction:
                for operation in update_operations:
                    item = operation["item"]
                    actions = operation["actions"]

                    transaction.update(model=item, actions=actions)
                    if change_log:
                        transaction.save(model=change_log)

        except TransactWriteError as err:
            logger.debug(f"failed to write transaction")
            logger.debug(traceback.print_exc())
            raise HTTPException(500, detail="Error updating items in database")

        updated_items = get_agenda_items_query()
        groups = group_agenda_items(updated_items)

        snapshot = SnapshotsDB(
            hash_key="snapshots",
            range_key=update_time.isoformat(),
            snapshot_data=json.loads(groups.json()),
        )

        snapshot.save()
        return groups

    updated_items = get_agenda_items_query()
    return group_agenda_items(updated_items)


def get_export_link_db():
    """
    Returns the export link for the frontend
    """
    return "https://amgen.sharepoint.com/:f:/r/sites/ADISensing-ADISensing-FinanceApp/Shared%20Documents/Orange%20(Prioritized%20Agenda)/00%20-%20Orange%20Team%20Artifacts/Prioritized%20Agenda?csf=1&web=1&e=MPSecE"
