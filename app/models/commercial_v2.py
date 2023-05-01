from .common import Owners, SummaryInfo
from typing import Optional
from .brand import Brand
from .supply import Supply
from .people import People
from .pipeline import CommercialPipeline
from pydantic import BaseModel, Field, HttpUrl, EmailStr


class SupplyTemp(BaseModel):
    locations: Optional[list]
    cogsReduction: Optional[str]
    inventoryBelowTarget: Optional[str]


class PeopleTemp(BaseModel):
    engagementScore: Optional[str]
    talentAcquisition: Optional[str]
    turnover: Optional[str]


class CommercialV2(BaseModel):
    title: Optional[str]
    agendaItemId: Optional[int]
    summaryInfo: Optional[SummaryInfo]
    owners: Optional[Owners]
    brand: Optional[Brand]
    pipeline: Optional[CommercialPipeline]
    supply: Optional[Supply]
    people: Optional[People]
