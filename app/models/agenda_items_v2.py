from datetime import datetime
from pydantic import Field, HttpUrl, EmailStr
from pydantic.typing import Literal
from typing import Optional

from ..db.dynamodb_models import ARCHETYPES
from .common import CamelModel, Owners


class User(CamelModel):
    email: Optional[EmailStr]
    username: Optional[str]


# TODO: make shred
class ExternalLink(CamelModel):
    label: str
    href: str


class AgendaItem(CamelModel):
    agendaItemId: Optional[int]
    name: str = Field(example="My example name")
    archetype: ARCHETYPES = Field(example="Pipeline")
    archetypeLinkId: Optional[str]
    value: Literal[1, 2, 3] = Field(example=2)
    focus: Literal[1, 2, 3] = Field(example=3)
    order: int = Field(ge=1, example=1)
    status: str = Field(
        default="gray"
    )  # "red" | "yellow" | "green" | "gray" | null //null means "auto calculate"
    statusType: Optional[str]
    statusReason: Optional[str]
    keyInsights: Optional[str]
    scope: Optional[str]
    owners: Optional[Owners]
    externalLinks: Optional[list[ExternalLink]]
    isActive: bool = Field(default=True, example=True)
    createdBy: Optional[User] = Field(
        example=User(email="user@example.com", username="testusername")
    )
    updatedBy: Optional[User] = Field(
        example=User(email="user@example.com", username="testusername")
    )
    createdDate: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updatedDate: Optional[datetime] = Field(default_factory=datetime.utcnow)
    version: Optional[int] | None


class AgendaItemBoardResponse(CamelModel):
    agenda_item_id: int = Field(ge=1)
    name: str = Field(example="My example name")
    archetype: ARCHETYPES = Field(example="Pipeline")
    value: Literal[1, 2, 3] = Field(example=2)
    focus: Literal[1, 2, 3] = Field(example=3)
    order: int = Field(ge=1, example=1)
    status: Literal[
        "gray",
        "red",
        "yellow",
        "green",
    ] = Field(example="red")


class AgendaItemUpdate(CamelModel):
    agenda_item_id: Optional[int] = Field(ge=1)
    name: Optional[str] = Field(example="My example name")
    product: Optional[str]
    is_active: Optional[bool] = Field(default=True, example=True)
    status: Optional[
        Literal[
            "gray",
            "red",
            "yellow",
            "green",
        ]
    ] = Field(example="red")
    href: Optional[HttpUrl] | None = Field(
        default=None, example="https://www.google.com"
    )
    owners: Optional[Owners]


class AgendaItemCreate(CamelModel):
    name: str = Field(example="My example name")
    product: Optional[str]
    archetype: ARCHETYPES = Field(example="Pipeline")
    value: Literal[1, 2, 3] = Field(example=2)
    focus: Literal[1, 2, 3] = Field(example=3)
    order: int = Field(ge=1, example=1)
    status: Literal[
        "gray",
        "red",
        "yellow",
        "green",
        "grey",
    ] = Field(example="red")
    href: HttpUrl | None = Field(default=None, example="https://www.google.com")
    owners: Optional[Owners]


class AgendaItemOLD(AgendaItemCreate):
    agenda_item_id: int = Field(ge=1)
    is_active: bool = Field(default=True, example=True)
    created_by: User = Field(
        example=User(email="user@example.com", username="testusername")
    )
    updated_by: User = Field(
        example=User(email="user@example.com", username="testusername")
    )
    created_date: datetime = Field(default_factory=datetime.utcnow)
    updated_date: datetime = Field(default_factory=datetime.utcnow)
    version: int | None


class BoxGroup(CamelModel):
    value: int = Field(example=1)
    focus: int = Field(example=2)
    items: list[AgendaItemBoardResponse]


class AgendaItemPosition(CamelModel):
    value: int = Field(example=1)
    focus: int = Field(example=2)
    order: int = Field(example=2)
    agendaItemId: int = Field(ge=1)


class BoxGroupUpdate(CamelModel):
    value: int = Field(example=1)
    focus: int = Field(example=2)
    items: list[AgendaItemPosition]


class AgendaItemsBoardUpdate(CamelModel):
    groups: list[BoxGroupUpdate]


class GroupedAgendaItems(CamelModel):
    groups: list[BoxGroup]


class ExportLink(CamelModel):
    url: HttpUrl | None = Field(example="https://www.google.com")
