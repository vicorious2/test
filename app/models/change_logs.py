from datetime import datetime
from pydantic import Field


from app.models.agenda_items import User
from app.models.common import CamelModel


class ChangeLogEvent(CamelModel):
    field: str = Field(example="value")
    original_value: str = Field(example="1")
    new_value: str = Field(example="2")


class ChangeLog(CamelModel):
    events: list[ChangeLogEvent]
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, example=datetime.utcnow()
    )
    user: User = Field(example=User(email="user@example.com", username="testusername"))
    agenda_item_id: int = Field(ge=1, example=1)


class ChangeLogResponse(CamelModel):
    changes: list[ChangeLog] = Field(default=[])
