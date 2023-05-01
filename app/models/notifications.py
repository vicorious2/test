from pydantic import Field, HttpUrl, EmailStr
from pydantic.typing import Literal
from typing import Optional

from ..db.dynamodb_models import ARCHETYPES
from .common import CamelModel, Owners
from .agenda_items_v2 import ExternalLink


class data_metric_notification(CamelModel):
    type: Optional[str]
    metricName: Optional[str]
    status: Optional[str]


class agenda_item_notification(CamelModel):
    agendaItemId: Optional[int]
    title: Optional[str]
    status: Literal["red", "green", "yellow", "grey"] = Field(
        example="red", default="red"
    )
    reason: Optional[str]
    scope: Optional[str]
    keyInsights: Optional[str]
    metrics: Optional[list[data_metric_notification]]
    externalLink: Optional[ExternalLink]
