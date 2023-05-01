from datetime import datetime
from pydantic import Field, HttpUrl, EmailStr
from pydantic.typing import Literal
from typing import Optional

from app.db.dynamodb_models import ARCHETYPES
from app.models.common import CamelModel


class User(CamelModel):
    email: Optional[EmailStr]
    username: Optional[str]


class AgendaItemUpdate(CamelModel):
    agenda_item_id: Optional[int] = Field(ge=1)
    is_active: Optional[bool] = Field(default=True, example=True)
    status: Optional[
        Literal[
            "Red",
            "Yellow",
            "Green",
            "Grey",
            "Gray",
            "gray",
            "red",
            "yellow",
            "green",
            "grey",
        ]
    ] = Field(example="Red")
    status_details: Optional[dict] = Field(
        default={},
        example={
            "Red": "Lower than 10%",
            "Yellow": "Between 10% and 80%",
            "Green": "Greater than 80%",
        },
    )
    href: Optional[HttpUrl] | None = Field(
        default=None, example="https://www.google.com"
    )
    description: Optional[str] | None = Field(
        default=None, example="This is a description of the agenda item"
    )
    ceo_staff_sponsor: Optional[str] | None = Field(default=None, example="John Doe")
    op_team_owner: Optional[str] | None = Field(default=None, example="Steve Smith")


class AgendaItemCreate(CamelModel):
    name: str = Field(example="My example name")
    archetype: ARCHETYPES = Field(example="Pipeline")
    value: Literal[1, 2, 3] = Field(example=2)
    focus: Literal[1, 2, 3] = Field(example=3)
    order: int = Field(ge=1, example=1)
    status: Literal[
        "Red",
        "Yellow",
        "Green",
        "Grey",
        "Gray",
        "gray",
        "red",
        "yellow",
        "green",
        "grey",
    ] = Field(example="Red")
    status_details: dict = Field(
        default={},
        example={
            "Red": "Lower than 10%",
            "Yellow": "Between 10% and 80%",
            "Green": "Greater than 80%",
        },
    )
    href: HttpUrl | None = Field(default=None, example="https://www.google.com")
    description: str | None = Field(
        default=None, example="This is a description of the agenda item"
    )
    ceo_staff_sponsor: str | None = Field(default=None, example="John Doe")
    op_team_owner: str | None = Field(default=None, example="Steve Smith")


class AgendaItem(AgendaItemCreate):
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


class AgendaItemBoardResponse(CamelModel):
    agenda_item_id: int = Field(ge=1)
    name: str = Field(example="My example name")
    archetype: ARCHETYPES = Field(example="Pipeline")
    value: Literal[1, 2, 3] = Field(example=2)
    focus: Literal[1, 2, 3] = Field(example=3)
    order: int = Field(ge=1, example=1)
    status: Literal[
        "Red",
        "Yellow",
        "Green",
        "Grey",
        "Gray",
        "gray",
        "red",
        "yellow",
        "green",
        "grey",
    ] = Field(example="Red")
    href: HttpUrl | None = Field(default=None, example="https://www.google.com")


class BoxGroup(CamelModel):
    value: int = Field(example=1)
    focus: int = Field(example=2)
    items: list[AgendaItemBoardResponse]


class AgendaItemPosition(CamelModel):
    value: int = Field(example=1)
    focus: int = Field(example=2)
    order: int = Field(example=2)
    agenda_item_id: int = Field(ge=1)


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
