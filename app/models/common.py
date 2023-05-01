from pydantic import BaseModel
from typing import Optional


def to_camel(string: str) -> str:
    components = string.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


class CamelModel(BaseModel):
    """
    Extends BaseModel to automatically convert items to camelCase
    """

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True


class Owners(BaseModel):
    ceoStaffSponsors: Optional[list[str]]
    operatingTeamOwners: Optional[list[str]]


class Chart(BaseModel):
    label: Optional[str]
    value: Optional[int]
    forecast: Optional[int]


class SummaryInfo(BaseModel):
    status: Optional[str]
    reason: Optional[str]
    scope: Optional[str]
    keyInsights: Optional[str]


class ExternalLink(BaseModel):
    label: Optional[str]
    href: Optional[str]
    isSensingExternal: Optional[str]
