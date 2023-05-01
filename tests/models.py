from app.models.agenda_items import (
    AgendaItem,
    AgendaItemCreate,
    AgendaItemUpdate,
    User,
)

agenda_item = AgendaItem(
    agenda_item_id=1,
    name="Agenda Item",
    archetype="Pipeline",
    created_by=User(username=f"John Doe", email=f"example@example.com"),
    created_date="2023-02-02 13:20:35.983495",
    updated_date="2023-02-02 13:20:35.983495",
    updated_by=User(username=f"John Doe", email=f"example@example.com"),
    value=1,
    focus=1,
    order=1,
    status="Yellow",
    status_details={"Yellow": "mid", "Green": "good", "Red": "bad"},
    is_active=True,
)

agenda_item_2 = AgendaItem(
    name="Agenda Item",
    agenda_item_id=1,
    archetype="Commercial",
    created_by=User(username=f"John Doe", email=f"example@example.com"),
    created_date="2023-02-02 13:20:35.983495",
    updated_date="2023-02-02 13:20:35.983495",
    updated_by=User(username=f"John Doe", email=f"example@example.com"),
    value=1,
    focus=1,
    order=1,
    status="Green",
    status_details={"Yellow": "mid", "Green": "good", "Red": "bad"},
    is_active=True,
)

agenda_item_update = AgendaItemUpdate(
    agenda_item_id=1,
    is_active=True,
    status="Green",
    status_details={"Yellow": "mid", "Green": "very good", "Red": "bad"},
)

agenda_item_update_2 = AgendaItemUpdate(
    agenda_item_id=2,
    is_active=True,
    status="Green",
    status_details={"Yellow": "mid", "Green": "very good", "Red": "bad"},
)


agenda_item_create = AgendaItemCreate(
    name=f"Agenda Item",
    archetype="Pipeline",
    created_by=User(username=f"John Doe", email=f"example@example.com"),
    created_date="2023-02-02 13:20:35.983495",
    updated_date="2023-02-02 13:20:35.983495",
    updated_by=User(username=f"John Doe", email=f"example@example.com"),
    value=1,
    focus=1,
    order=1,
    status="Yellow",
    status_details={"Yellow": "mid", "Green": "good", "Red": "bad"},
    is_active=True,
)
