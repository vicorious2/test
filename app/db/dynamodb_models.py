import os
import time
from datetime import datetime, timezone

from pydantic.typing import Literal
from pynamodb.attributes import (
    BooleanAttribute,
    DiscriminatorAttribute,
    ListAttribute,
    MapAttribute,
    NumberAttribute,
    UnicodeAttribute,
    UTCDateTimeAttribute,
    VersionAttribute,
)
from pynamodb.models import Model
from pynamodb.indexes import GlobalSecondaryIndex, AllProjection

env = os.getenv("PA_ENV", "dev")

ARCHETYPES = Literal["Pipeline", "NPBI", "Commercial", "PS", "Standalone"]

AWS_REGION = "us-west-2"
AWS_ACCESS_KEY = os.environ["AWS_DYNAMO_ACCESS_KEY_ID"]
AWS_SECRET_KEY = os.environ["AWS_DYNAMO_SECRET_ACCESS_KEY"]
AGENDA_ITEMS_DYNAMODB_TABLE_NAME = env + "-prioritized-agend-agenda-items"


class ChangeLogIndex(GlobalSecondaryIndex):
    """
    This class represents a global secondary index

    hash_key = agenda_items_change_log

    sort_key = 2023-02-13T22:21:39.109Z
    """

    class Meta:
        read_capacity_units = 2
        write_capacity_units = 1
        # All attributes are projected
        projection = AllProjection()

    hash_key = UnicodeAttribute(hash_key=True)
    timestamp = UTCDateTimeAttribute(range_key=True)


class ParentModel(Model):
    class Meta:
        table_name = AGENDA_ITEMS_DYNAMODB_TABLE_NAME
        region = AWS_REGION
        aws_access_key_id = AWS_ACCESS_KEY
        aws_secret_access_key = AWS_SECRET_KEY

    hash_key = UnicodeAttribute(
        hash_key=True
    )  # metrics, agenda_items, agenda_items_snapshots, agenda_items_change_log
    sort_key = UnicodeAttribute(
        range_key=True
    )  # agenda_item_1, agenda_item_2, agenda_item_1#aoh, agenda_item_1#net_sales, 02/07/2023 # other unique identifiers
    cls = DiscriminatorAttribute()

    # For the change log index
    timestamp = UTCDateTimeAttribute(null=True)
    change_log_index = ChangeLogIndex()


class User(MapAttribute):
    email = UnicodeAttribute(null=True)
    username = UnicodeAttribute(null=True)


class OwnersMap(MapAttribute):
    ceoStaffSponsors = ListAttribute(of=UnicodeAttribute, null=True)
    operatingTeamOwners = ListAttribute(of=UnicodeAttribute, null=True)


class ExternalLinkMap(MapAttribute):
    label = UnicodeAttribute(null=True)
    href = UnicodeAttribute(null=True)


class AgendaItemV2DB(ParentModel, discriminator="AgendaItemsV2"):
    """
    hash_key = agenda_items_v2

    sort_key = agenda_item_1, agenda_item_2, agenda_item_3
        ListAttribute(of=OfficeEmployeeMap)
    """

    agendaItemId = NumberAttribute()
    name = UnicodeAttribute()
    archetype = UnicodeAttribute()
    archetypeLinkId = UnicodeAttribute(null=True)
    value = NumberAttribute()
    focus = NumberAttribute()
    order = NumberAttribute()
    status = UnicodeAttribute()
    statusType = UnicodeAttribute(null=True)
    statusReason = UnicodeAttribute(null=True)
    keyInsights = UnicodeAttribute(null=True)
    scope = UnicodeAttribute(null=True)
    owners = OwnersMap()
    externalLinks = ListAttribute(of=ExternalLinkMap)
    isActive = BooleanAttribute(default_for_new=True)
    createdBy = User()
    updatedBy = User()
    createdDate = UTCDateTimeAttribute(default_for_new=datetime.utcnow)
    updatedDate = UTCDateTimeAttribute(default_for_new=datetime.utcnow)
    version = VersionAttribute()


class AgendaItemDB(ParentModel, discriminator="AgendaItems"):
    """
    hash_key = agenda_items

    sort_key = agenda_item_1, agenda_item_2, agenda_item_3

    """

    name = UnicodeAttribute()
    agenda_item_id = NumberAttribute()
    archetype = UnicodeAttribute()
    created_by = User()
    updated_by = User()
    created_date = UTCDateTimeAttribute(default_for_new=datetime.utcnow)
    updated_date = UTCDateTimeAttribute(default_for_new=datetime.utcnow)
    value = NumberAttribute()
    focus = NumberAttribute()
    order = NumberAttribute()
    status = UnicodeAttribute()
    status_details = MapAttribute(default={})
    href = UnicodeAttribute(null=True)
    description = UnicodeAttribute(null=True)
    is_active = BooleanAttribute(default_for_new=True)
    version = VersionAttribute()
    ceo_staff_sponsor = UnicodeAttribute(null=True)
    op_team_owner = UnicodeAttribute(null=True)


class SnapshotsDB(ParentModel, discriminator="AgendaItemSnapshots"):
    """
    hash_key = snapshots

    sort_key = 2023-02-13T22:21:39.109Z
    """

    snapshot_data = MapAttribute(default={})


class MetricsDB(ParentModel, discriminator="Metrics"):
    """
    hash_key = snapshots

    sort_key = 2023-02-13T22:21:39.109Z
    """

    status = UnicodeAttribute()
    status_details = MapAttribute(default={})
    ceo_staff_sponsor = UnicodeAttribute(null=True)
    operating_team_owner = UnicodeAttribute(null=True)
    metric_data = MapAttribute(default={})


class AgendaItemChangeLogEventDB(MapAttribute):
    field = UnicodeAttribute()
    original_value = UnicodeAttribute()
    new_value = UnicodeAttribute()


class AgendaItemChangeLogDB(ParentModel, discriminator="AgendaItemChangeLog"):
    """
    hash_key = agenda_items_change_log

    sort_key = agenda_item_1#2023-02-13T22:21:39.109Z
    """

    events = ListAttribute(of=AgendaItemChangeLogEventDB, default=[])
    user = User()
