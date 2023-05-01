import json
import os
import time
from typing import Dict

from pynamodb.exceptions import DoesNotExist, PutError, UpdateError
from pynamodb.expressions.update import Action
from pynamodb.connection import Connection
from pynamodb.transactions import TransactWrite
from datetime import datetime

from app.db.dynamodb_models import AgendaItemDB
from app.loggerFactory import LoggerFactory
from app.models.agenda_items import (
    AgendaItem,
    AgendaItemCreate,
    BoxGroup,
    GroupedAgendaItems,
    User,
)
import random
import string

logger = LoggerFactory.get_logger(__name__)


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
        box_group_dict[(item.value, item.focus)].items.append(item)

    return GroupedAgendaItems(groups=list(box_group_dict.values()))


def get_agenda_items_scan() -> list[AgendaItem]:
    """
    Get all agenda items in the Dynamodb table
    """
    tic = time.perf_counter()
    try:
        result = AgendaItemDB.scan(limit=100, consistent_read=True)
    except Exception as err:
        raise err

    items = []
    for item in result:
        items.append(AgendaItem(**json.loads(item.to_json())))
    toc = time.perf_counter()

    logger.debug(f"Scan for all agenda items took {toc - tic:0.4f} seconds")

    return items


def get_agenda_item_db_by_id(id: int) -> AgendaItemDB | None:
    try:
        tic = time.perf_counter()
        item = AgendaItemDB.get(hash_key="agenda_items", range_key=f"agenda_item_{id}")
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


def create_agenda_item_in_db(item: AgendaItemCreate, user: User) -> AgendaItem:
    """
    Add a new agenda_item to the Dynamodb table
    """
    try:
        tic = time.perf_counter()
        existing_ids = get_all_agenda_item_ids()

        # Set unique id number for agenda item
        if len(existing_ids) == 0:
            id = 1
        else:
            id = max(existing_ids) + 1

        # Check if agenda item already exists in db
        condition = AgendaItemDB.agenda_item_id.does_not_exist()

        # Save agenda item in db
        AgendaItemDB(
            hash_key=f"agenda_items",
            range_key=f"agenda_item_{id}",
            agenda_item_id=id,
            created_by=user.dict(),
            updated_by=user.dict(),
            **item.dict(),
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
    current_item = get_agenda_item_db_by_id(item.agenda_item_id)
    current_item_parsed = AgendaItem(**json.loads(current_item.to_json()))
    actions = compare_items(current_item_parsed, item)

    actions.append(AgendaItemDB.updated_by.set(user.dict()))
    actions.append(AgendaItemDB.updated_date.set(datetime.utcnow()))
    try:
        current_item.update(actions=actions)
    except UpdateError as err:
        raise err

    current_item.refresh(consistent_read=True)
    return AgendaItem(**json.loads(current_item.to_json()))


def compare_items(original_object: AgendaItem, new_object: AgendaItem) -> list[Action]:
    """
    Compare two AgendaItems and return a list of actions to update the item
    """
    actions = []

    if original_object.archetype != new_object.archetype:
        actions.append(AgendaItemDB.archetype.set(new_object.archetype))

    if original_object.status != new_object.status:
        actions.append(AgendaItemDB.status.set(new_object.status))

    if original_object.status_details != new_object.status_details:
        actions.append(AgendaItemDB.status_details.set(new_object.status_details))

    if original_object.href != new_object.href:
        actions.append(AgendaItemDB.href.set(new_object.href))

    if original_object.description != new_object.description:
        actions.append(AgendaItemDB.description.set(new_object.description))

    if original_object.is_active != new_object.is_active:
        actions.append(AgendaItemDB.is_active.set(new_object.is_active))

    return actions


def get_all_agenda_item_ids() -> list[int]:
    """
    Get all agenda item ids in the DynamoDB table
    """
    try:
        tic = time.perf_counter()
        res = AgendaItemDB.query(
            hash_key="agenda_items", attributes_to_get=["agenda_item_id"]
        )
        ids = []
        for i in res:
            ids.append(i.agenda_item_id)
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


def update_board(new_items: GroupedAgendaItems) -> GroupedAgendaItems:
    """
    Update the positions of all changed agenda items
    """
    list_of_new_items = convert_grouped_items_to_list(new_items)
    dict_of_new_items: Dict[int, AgendaItem] = {}

    # Create dictionary of new items with id as the key
    for item in list_of_new_items:
        if item.agenda_item_id not in dict_of_new_items:
            dict_of_new_items[int(item.agenda_item_id)] = item
        else:
            raise ValueError(
                f"Duplicate agenda item with id {item.agenda_item_id} found"
            )

    existing_items = get_agenda_items_scan()
    dict_of_existing_items: Dict[int, AgendaItem] = {}

    # Create dictionary of existing items with id as the key
    for item in existing_items:
        if item.agenda_item_id not in dict_of_existing_items:
            dict_of_existing_items[int(item.agenda_item_id)] = item
        else:
            raise ValueError(
                f"Duplicate agenda item with id {item.agenda_item_id} found"
            )

    keys = dict_of_new_items.keys()

    # Determine actions needed to update items in db
    update_operations = []
    for key in keys:
        new_item = dict_of_new_items.get(key)
        existing_item = dict_of_existing_items.get(key)

        actions = []

        if new_item.value != existing_item.value:
            actions.append(AgendaItemDB.value.set(new_item.value))

        if new_item.focus != existing_item.focus:
            actions.append(AgendaItemDB.focus.set(new_item.focus))

        if new_item.order != existing_item.order:
            actions.append(AgendaItemDB.order.set(new_item.order))

        if len(actions) > 0:
            update_operations.append(
                {"item": AgendaItemDB(new_item.agenda_item_id), "actions": actions}
            )

    # Perform all update operations

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

    if len(update_operations) > 0:
        with TransactWrite(
            connection=connection, client_request_token=client_request_token
        ) as transaction:
            for operation in update_operations:
                item = operation["item"]
                actions = operation["actions"]

                transaction.update(model=item, actions=actions)

    updated_items = get_agenda_items_scan()
    return group_agenda_items(updated_items)
