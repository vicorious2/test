import os
from typing import Optional
from pydantic import BaseModel, Field
from pydantic.typing import Literal
from ..models.common import Owners, ExternalLink

env = os.getenv("PA_ENV", "dev")


class FDP(BaseModel):
    status: str = Field(example="red", default="gray")
    statusText: str = Field(example="red", default="gray")
    countries: Optional[list[str]]
    reasonCodes: Optional[list[str]]
    value: Optional[int]


class InventoryBelowTarget(BaseModel):
    status: Literal["red", "green", "yellow", "gray"] = Field(
        example="red", default="gray"
    )
    fdp: Optional[FDP]
    href: Optional[str] = Field(
        example="amgen.com",
        default=f"https://sensing-{env}.nimbus.amgen.com/supply/dashboard",
    )
    externalLinks: Optional[list[ExternalLink]]


class LocationDetails(BaseModel):
    status: Literal["red", "green", "yellow", "gray"] = Field(
        example="red", default="gray"
    )
    text: Optional[str]


class Location(BaseModel):
    title: Optional[str]
    status: Literal["red", "green", "yellow", "gray"] = Field(
        example="red", default="gray"
    )
    owners: Optional[Owners]
    scope: Optional[LocationDetails]
    timeline: Optional[LocationDetails]
    value: Optional[LocationDetails]
    cost: Optional[LocationDetails]
    risk: Optional[LocationDetails]
    href: Optional[str] = Field(
        example="amgen.com",
        default=f"https://sensing-{env}.nimbus.amgen.com/supply/dashboard",
    )
    externalLinks: Optional[list[ExternalLink]]


class CogsReduction(BaseModel):
    status: Literal["red", "green", "yellow", "gray", "inactive"] = Field(
        example="red", default="inactive"
    )


class Supply(BaseModel):
    locations: Optional[list[Location]]
    cogsReduction: CogsReduction = Field(default=CogsReduction())
    inventoryBelowTarget: Optional[InventoryBelowTarget]
