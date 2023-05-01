import os
from datetime import datetime
from typing import Optional
from unicodedata import decimal
from pydantic import BaseModel, Field, HttpUrl, EmailStr
from pydantic.typing import Literal
from ..models.common import Owners


from app.db.dynamodb_models import ARCHETYPES

env = os.getenv("PA_ENV", "dev")


class Chart(BaseModel):
    label: Optional[str]
    value: Optional[int]
    forecast: Optional[int]


# end Shared


class repatha_hover_data_freequency_details(BaseModel):
    Refresh_Freequency: str = Field(
        alias="Refresh Frequency", Example="Weekly (last refreshed  02/10/2023)"
    )
    Data_Source: str = Field(alias="Data Source", Example="CD&A")


class repatha_hover_data_nbrx_volume_by_specialties(BaseModel):
    c4w_vs_p4w: repatha_hover_data_freequency_details
    volume_by_specialties: repatha_hover_data_freequency_details
    r4w_goal: repatha_hover_data_freequency_details


class repatha_hover_data_us_leading(BaseModel):
    nbrx_volume_by_specialties: repatha_hover_data_nbrx_volume_by_specialties
    nbrx_fulfillment: repatha_hover_data_freequency_details
    idn_account_wins: repatha_hover_data_freequency_details


class repatha_hover_data_worldwide_lrs(BaseModel):
    Last_Refreshed: str = Field(alias="Last Refreshed", Example="02/28/2023")
    Data_Source: str = Field(alias="Data Source", Example="EDW")


class repatha_hover_data_us_execution(BaseModel):
    share_of_voice: repatha_hover_data_freequency_details
    call_attainment: repatha_hover_data_freequency_details


class repatha_hover_data_global_brand_sales_drivers(BaseModel):
    volume_market_mktshare_us: repatha_hover_data_freequency_details
    sales: repatha_hover_data_freequency_details
    volume_market_mktshare_o_us: repatha_hover_data_freequency_details


class repatha_hover_data_us_lagging(BaseModel):
    net_sales: repatha_hover_data_freequency_details
    demand_components_of_growth: repatha_hover_data_freequency_details


class repatha_hover_data_details(BaseModel):
    us_leading: repatha_hover_data_us_leading
    worldwide_lrs: repatha_hover_data_worldwide_lrs
    us_execution: repatha_hover_data_us_execution
    global_brand_sales_drivers: repatha_hover_data_global_brand_sales_drivers
    us_lagging: repatha_hover_data_us_lagging


class repatha_hover_data(BaseModel):
    status: Optional[str]
    message: Optional[str]
    data: Optional[repatha_hover_data_details]


# Supply start


class ANCDetails(BaseModel):
    status: Literal["red", "green", "yellow", "gray"] = Field(
        example="red", default="gray"
    )
    text: Optional[str]


class ANC(BaseModel):
    status: Literal["red", "green", "yellow", "gray"] = Field(
        example="red", default="gray"
    )
    owners: Optional[Owners]
    scope: Optional[ANCDetails]
    timeline: Optional[ANCDetails]
    value: Optional[ANCDetails]
    cost: Optional[ANCDetails]
    risk: Optional[ANCDetails]
    href: Optional[str] = Field(
        example="amgen.com",
        default=f"https://sensing-{env}.nimbus.amgen.com/supply/dashboard",
    )


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


class AOHDetails(BaseModel):
    status: Literal["red", "green", "yellow", "gray"] = Field(
        example="red", default="gray"
    )
    text: Optional[str]


class AOH(BaseModel):
    status: Literal["red", "green", "yellow", "Gray"] = Field(
        example="red", default="gray"
    )
    owners: Optional[Owners]
    scope: Optional[AOHDetails]
    timeline: Optional[AOHDetails]
    value: Optional[AOHDetails]
    cost: Optional[AOHDetails]
    risk: Optional[AOHDetails]
    href: Optional[str] = Field(
        example="amgen.com",
        default=f"https://sensing-{env}.nimbus.amgen.com/supply/dashboard",
    )


class CogsReduction(BaseModel):
    status: Literal["red", "green", "yellow", "gray"] = Field(
        example="red", default="gray"
    )


class Supply(BaseModel):
    anc: Optional[ANC]
    aoh: Optional[AOH]
    cogsReduction: CogsReduction = Field(default=CogsReduction())
    inventoryBelowTarget: Optional[InventoryBelowTarget]


# Supply End
# Pipeline Start:


class PipelineCSP(BaseModel):
    status: Literal["red", "green", "yellow", "gray"] = Field(
        example="Red", default="gray"
    )
    statusLabel: Literal[
        "red", "green", "yellow", "ray", "enrollment complete"
    ] = Field(example="red", default="enrollment complete")
    name: str = Field(example="some study name", default="20170625_VESALIUS - CV")
    lse: str = Field(example="11/26/2021", default="11/26/2021")
    latestPlannedCumulativeSitesActivated: Optional[int]
    latestPlannedCumulativeSubjectsEnrolled: Optional[int]
    percToPlanSiteActivation: Optional[float]
    percToPlanSubjectEnrollment: Optional[float]


class PipelineMilestone(BaseModel):
    status: Literal["red", "green", "yellow", "gray"] = Field(
        example="red", default="gray"
    )
    statusLabel: Literal[
        "red", "green", "yellow", "gray", "enrollment Complete"
    ] = Field(example="red", default="enrollment complete")
    studyName: str = Field(example="some study name", default="20170625_VESALIUS  CV")
    msDate: Optional[datetime]
    msShortName: Optional[str]
    dateVariance: Optional[int]
    nkmSnapDate: Optional[datetime]
    nkmTransitionDateReason: Optional[str]
    geographicArea: Optional[str]


class Pipeline(BaseModel):
    status: Literal["red", "green", "yellow", "gray"] = Field(
        example="red", default="green"
    )
    owners: Optional[Owners]
    csp: Optional[PipelineCSP]
    npm: Optional[PipelineMilestone]
    nf: Optional[PipelineMilestone]
    nal: Optional[PipelineMilestone]
    href: Optional[str] = Field(
        example="amgen.com",
        default=f"https://portfolio-analytics.amgen.com/dashboard/program-level?Product=Repatha&Prioritized%20Agenda%20Toggle=Entire%20Portfolio&Project=Repatha%20VESALIUS%20CV",
    )


# Pipeline End
# Brand Start:


class RepathaNbrxVolumeLastUpdatedDataRefreshDetails(BaseModel):
    refreshFrequency: Optional[str]
    dataSource: Optional[str]


class RepathaNbrxVolumeBySpecialtiesDetailsLastUpdatedData(BaseModel):
    contributionBySpecialty: Optional[RepathaNbrxVolumeLastUpdatedDataRefreshDetails]
    currentVsPrevious: Optional[RepathaNbrxVolumeLastUpdatedDataRefreshDetails]
    recentGoal: Optional[RepathaNbrxVolumeLastUpdatedDataRefreshDetails]


class RepathaNbrxVolumeBySpecialtiesDetails(BaseModel):
    label: Optional[str]
    currentVsPrevious: Optional[str]
    recentAvg: Optional[str]
    recentGoal: Optional[str]


class RepathaNbrxVolumeBySpecialties(BaseModel):
    status: Literal["red", "green", "yellow", "grey"] = Field(
        example="green", default="gray"
    )
    cardiologists: Optional[list[RepathaNbrxVolumeBySpecialtiesDetails]]
    pcps: Optional[list[RepathaNbrxVolumeBySpecialtiesDetails]]
    href: Optional[str] = Field(
        example="amgen.com",
        default=f"https://sensing-{env}.nimbus.amgen.com/brand#repatha",
    )
    lastUpdatedData: Optional[RepathaNbrxVolumeBySpecialtiesDetailsLastUpdatedData]


class NbrxFulfillmentDetails(BaseModel):
    label: Optional[str]
    previous: Optional[str]
    current: Optional[str]
    goal: Optional[str]


class RepathaNbrxFulFillmentLastUpdatedDataDetails(BaseModel):
    dataSource: Optional[str]
    refreshFrequency: Optional[str]


class NbrxFulfillment(BaseModel):
    status: Literal["red", "green", "yellow", "grey"] = Field(
        example="green", default="gray"
    )
    data: Optional[list[NbrxFulfillmentDetails]]
    href: Optional[str] = Field(
        example="amgen.com",
        default=f"https://sensing-{env}.nimbus.amgen.com/brand#repatha",
    )
    lastUpdatedData: Optional[RepathaNbrxFulFillmentLastUpdatedDataDetails]


class IdnAccountWins(BaseModel):
    status: Literal["red", "green", "yellow", "gray"] = Field(
        example="red", default="gray"
    )


class ShareOfVoice(BaseModel):
    status: Literal["red", "green", "yellow", "gray"] = Field(
        example="red", default="gray"
    )


class NetSalesSummary(BaseModel):
    ytdLabel: Optional[str]
    ytd: Optional[int]
    ytgLabel: Optional[str]
    ytg: Optional[int]
    status: Optional[str]
    forecast: Optional[int]


class RepathaNetSalesLastUpdatedDetails(BaseModel):
    dataSource: Optional[str]
    refreshFreequency: Optional[str]


class NetSales(BaseModel):
    status: Literal["red", "green", "yellow", "gray"] = Field(
        example="red", default="gray"
    )
    lastUpdated: Optional[str] = Field(example="Weekly (last refreshed  01/13/2023)")
    lastUpdatedData: Optional[RepathaNetSalesLastUpdatedDetails]
    chart: Optional[list[Chart]]
    netSales: Optional[NetSalesSummary]
    weeklyAverage: Optional[NetSalesSummary]
    href: Optional[str] = Field(
        example="amgen.com",
        default=f"https://sensing-{env}.nimbus.amgen.com/brand#repatha",
    )


class Demand(BaseModel):
    status: Literal["red", "green", "yellow", "gray"] = Field(
        example="red", default="gray"
    )
    nbrx: Optional[NetSales]
    trx: Optional[NetSales]
    href: Optional[str] = Field(
        example="amgen.com",
        default=f"https://sensing-{env}.nimbus.amgen.com/brand#repatha",
    )


class Brand(BaseModel):
    netSales: Optional[NetSales]
    nbrxDemand: Optional[NetSales]
    trxDemand: Optional[NetSales]
    idnAccountWins: Optional[IdnAccountWins]
    nbrxFulfillment: Optional[NbrxFulfillment]
    nbrxVolume: Optional[RepathaNbrxVolumeBySpecialties]
    shareOfVoice: Optional[ShareOfVoice]


# end Brand metrics
# people metrics:


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
        default=f"https://sensing-{env}.nimbus.amgen.com/people",
    )


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
        default=f"https://sensing-{env}.nimbus.amgen.com/people",
    )


class Turnover(BaseModel):
    status: Literal["red", "green", "yellow", "gray"] = Field(
        example="red", default="gray"
    )
    chart: Optional[list[Chart]]
    # chartAmgen: Optional[list[Chart]]
    href: Optional[str] = Field(
        example="amgen.com",
        default=f"https://sensing-{env}.nimbus.amgen.com/people",
    )


class People(BaseModel):
    engagementScore: Optional[EngagementScore]
    talentAcquisition: Optional[TalentAcquisition]
    turnover: Optional[Turnover]


# end people metrics


class Commercial(BaseModel):
    agendaItemId: Optional[int]
    title: Optional[str]
    status: Literal["red", "green", "yellow", "grey"] = Field(
        example="red", default="red"
    )
    reason: Optional[str]
    statusReason: Optional[str]
    scope: Optional[str]
    keyInsights: Optional[str]
    owners: Optional[Owners]
    brand: Optional[Brand]
    pipeline: Optional[Pipeline]
    supply: Optional[Supply]
    people: Optional[People]
