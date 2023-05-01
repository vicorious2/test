from typing import Optional
from pydantic import BaseModel, Field
from pydantic.typing import Literal
from .common import Chart, ExternalLink


class KeyProductEngagement(BaseModel):
    benchmark: Optional[int]
    product_engagement_score: Optional[int]
    product_change: Optional[int]
    date: Optional[str]
    previous_date: Optional[str]


class KeyProductEngagementData(BaseModel):
    status: Optional[str]
    message: Optional[str]
    data: Optional[list[KeyProductEngagement]]


class EngagementHistoricalTrend(BaseModel):
    date: Optional[str]
    benchmark: Optional[int]
    amgen_value: Optional[int]


class EngagementHistoricalTrendData(BaseModel):
    status: Optional[str]
    message: Optional[str]
    data: Optional[list[EngagementHistoricalTrend]]


class EngagementScore(BaseModel):
    status: Literal["red", "green", "yellow", "gray"] = Field(
        example="red", default="gray"
    )
    benchmark: Optional[int]
    productEngagementScore: Optional[int]
    productChange: Optional[int]
    date: Optional[str]
    previousDate: Optional[str]
    amgenAverage: Optional[int] = Field(default=73)
    href: Optional[str] = Field(
        example="amgen.com",
    )
    externalLinks: Optional[list[ExternalLink]]


class PeopleWhenTooltip(BaseModel):
    greenText: Optional[str]
    redText: Optional[str]


class CommercialPeopleEngagementScore(BaseModel):
    status: Literal["red", "green", "yellow", "gray"] = Field(
        example="red", default="gray"
    )
    tooltip: Optional[PeopleWhenTooltip]
    benchmark: Optional[int]
    productEngagementScore: Optional[int]
    productChange: Optional[int]
    date: Optional[str]
    previousDate: Optional[str]
    amgenAverage: Optional[int] = Field(default=73)
    href: Optional[str] = Field(
        example="amgen.com",
    )
    externalLinks: Optional[list[ExternalLink]]


class TalentAcquisition(BaseModel):
    status: Literal["red", "green", "yellow", "gray"] = Field(
        example="red", default="gray"
    )
    openRequisitions: Optional[int]
    avgOpenDays: Optional[int]
    amgenOpenRequisitions: Optional[int]
    amgenAvgOpenDays: Optional[int]
    href: Optional[str] = Field(
        example="amgen.com",
    )
    externalLinks: Optional[list[ExternalLink]]


class Turnover(BaseModel):
    status: Literal["red", "green", "yellow", "gray"] = Field(
        example="red", default="gray"
    )
    chart: Optional[list[Chart]]
    # chartAmgen: Optional[list[Chart]]
    href: Optional[str] = Field(
        example="amgen.com",
    )
    externalLinks: Optional[list[ExternalLink]]


class People(BaseModel):
    engagementScore: Optional[EngagementScore]
    talentAcquisition: Optional[TalentAcquisition]
    turnover: Optional[Turnover]
