from ..models.common import Owners, Chart, ExternalLink
from pydantic import BaseModel
from typing import Optional
from pydantic.typing import Literal
from pydantic import BaseModel, Field, HttpUrl, EmailStr


class BasicTooltipRow(BaseModel):
    label: Optional[str]
    text: Optional[str]


class BasicTooltipSection(BaseModel):
    title: Optional[str]
    rows: Optional[list[BasicTooltipRow]]


class BasicTooltip(BaseModel):
    sections: Optional[list[BasicTooltipSection]]


class NbrxVolumeLastUpdatedDataRefreshDetails(BaseModel):
    refreshFrequency: Optional[str]
    dataSource: Optional[str]


class NbrxVolumeBySpecialtiesDetailsLastUpdatedData(BaseModel):
    contributionBySpecialty: Optional[NbrxVolumeLastUpdatedDataRefreshDetails]
    currentVsPrevious: Optional[NbrxVolumeLastUpdatedDataRefreshDetails]
    recentGoal: Optional[NbrxVolumeLastUpdatedDataRefreshDetails]


class NbrxVolumeBySpecialtiesDetails(BaseModel):
    label: Optional[str]
    currentVsPrevious: Optional[str]
    recentAvg: Optional[str]
    recentGoal: Optional[str]


class NbrxVolumeBySpecialties(BaseModel):
    status: Literal["red", "green", "yellow", "gray", "inactive"] = Field(
        example="green", default="inactive"
    )
    cardiologists: Optional[list[NbrxVolumeBySpecialtiesDetails]]
    pcps: Optional[list[NbrxVolumeBySpecialtiesDetails]]
    href: Optional[str] = Field(
        example="amgen.com",
    )
    lastUpdatedData: Optional[NbrxVolumeBySpecialtiesDetailsLastUpdatedData]
    tooltip: Optional[BasicTooltip]
    externalLinks: Optional[list[ExternalLink]]


class NbrxFulfillmentDetails(BaseModel):
    label: Optional[str]
    previous: Optional[str]
    current: Optional[str]
    goal: Optional[str]


class NbrxFulFillmentLastUpdatedDataDetails(BaseModel):
    dataSource: Optional[str]
    refreshFrequency: Optional[str]


class NbrxFulfillment(BaseModel):
    status: Literal["red", "green", "yellow", "gray", "inactive"] = Field(
        example="green", default="inactive"
    )
    data: Optional[list[NbrxFulfillmentDetails]]
    href: Optional[str] = Field(
        example="amgen.com",
    )
    lastUpdatedData: Optional[NbrxFulFillmentLastUpdatedDataDetails]
    externalLinks: Optional[list[ExternalLink]]
    tooltip: Optional[BasicTooltip]


class IdnAccountWins(BaseModel):
    status: Literal["red", "green", "yellow", "gray", "inactive"] = Field(
        example="green", default="inactive"
    )


class ShareOfVoice(BaseModel):
    tooltip: Optional[BasicTooltip]
    status: Literal["red", "green", "yellow", "gray", "inactive"] = Field(
        example="green", default="inactive"
    )


class NetSalesSummary(BaseModel):
    ytdLabel: Optional[str]
    ytd: Optional[int]
    ytgLabel: Optional[str]
    ytg: Optional[int]
    status: Optional[str]
    forecast: Optional[int]


class NetSales(BaseModel):
    status: Literal["red", "green", "yellow", "gray", "inactive"] = Field(
        example="green", default="inactive"
    )
    lastUpdated: Optional[str] = Field(example="Weekly (last refreshed  01/13/2023)")
    chart: Optional[list[Chart]]
    netSales: Optional[NetSalesSummary]
    weeklyAverage: Optional[NetSalesSummary]
    href: Optional[str] = Field(
        example="amgen.com",
    )


class Demand(BaseModel):
    status: Literal["red", "green", "yellow", "gray", "inactive"] = Field(
        example="green", default="inactive"
    )
    nbrx: Optional[NetSales]
    trx: Optional[NetSales]
    href: Optional[str] = Field(
        example="amgen.com",
    )


# end Brand metrics


class CommercialBrandSalesDemandSectionTableRow(BaseModel):
    ytdLabel: Optional[str]
    ytd: Optional[str]
    ytgLabel: Optional[str]
    ytg: Optional[str]
    ytgStatus: Optional[str]
    forecastLabel: Optional[str]
    forecast: Optional[str]


class CommercialBrandSalesDemandSectionTable(BaseModel):
    title: Optional[str]
    rows: Optional[list[CommercialBrandSalesDemandSectionTableRow]]


class CommercialBrandSalesDemandSection(BaseModel):
    title: Optional[str]
    status: Optional[str]
    tooltip: Optional[BasicTooltip]
    chartTitle: Optional[str]
    chart: Optional[Chart]
    tables: Optional[list[CommercialBrandSalesDemandSectionTable]]
    externalLinks: Optional[list[ExternalLink]]


class PsoBioNaiveShare(BaseModel):
    tooltip: Optional[BasicTooltip]
    status: Literal["red", "green", "yellow", "gray", "inactive"] = Field(
        example="green", default="inactive"
    )


class SpecPharmNbrxCommFulfillRate(BaseModel):
    tooltip: Optional[BasicTooltip]
    status: Literal["red", "green", "yellow", "gray", "inactive"] = Field(
        example="green", default="inactive"
    )


class CopayEnrollmentRate(BaseModel):
    tooltip: Optional[BasicTooltip]
    status: Literal["red", "green", "yellow", "gray", "inactive"] = Field(
        example="green", default="inactive"
    )


class TargetsAtFrequency(BaseModel):
    tooltip: Optional[BasicTooltip]
    status: Literal["red", "green", "yellow", "gray", "inactive"] = Field(
        example="green", default="inactive"
    )


class Frequency(BaseModel):
    tooltip: Optional[BasicTooltip]
    status: Literal["red", "green", "yellow", "gray", "inactive"] = Field(
        example="green", default="inactive"
    )


class Brand(BaseModel):
    salesDemandSections: Optional[list[CommercialBrandSalesDemandSection]]
    idnAccountWins: Optional[IdnAccountWins]
    nbrxFulfillment: Optional[NbrxFulfillment]
    nbrxVolume: Optional[NbrxVolumeBySpecialties]

    psoBioNaiveShare: Optional[PsoBioNaiveShare]
    specPharmNbrxCommFulfillRate: Optional[SpecPharmNbrxCommFulfillRate]
    copayEnrollmentRate: Optional[CopayEnrollmentRate]
    targetsAtFrequency: Optional[TargetsAtFrequency]
    frequency: Optional[Frequency]
    shareOfVoice: Optional[ShareOfVoice]


class brand_hover_data_freequency_details(BaseModel):
    Refresh_Freequency: str = Field(
        alias="Refresh Frequency", Example="Weekly (last refreshed  02/10/2023)"
    )
    Data_Source: str = Field(alias="Data Source", Example="CD&A")


class brand_hover_data_nbrx_volume_by_specialties(BaseModel):
    c4w_vs_p4w: brand_hover_data_freequency_details
    volume_by_specialties: brand_hover_data_freequency_details
    r4w_goal: brand_hover_data_freequency_details


class brand_hover_data_us_leading(BaseModel):
    nbrx_volume_by_specialties: brand_hover_data_nbrx_volume_by_specialties
    nbrx_fulfillment: brand_hover_data_freequency_details
    idn_account_wins: brand_hover_data_freequency_details


class brand_hover_data_worldwide_lrs(BaseModel):
    Last_Refreshed: str = Field(alias="Last Refreshed", Example="02/28/2023")
    Data_Source: str = Field(alias="Data Source", Example="EDW")


class brand_hover_data_us_execution(BaseModel):
    share_of_voice: brand_hover_data_freequency_details
    call_attainment: brand_hover_data_freequency_details


class brand_hover_data_global_brand_sales_drivers(BaseModel):
    volume_market_mktshare_us: brand_hover_data_freequency_details
    sales: brand_hover_data_freequency_details
    volume_market_mktshare_o_us: brand_hover_data_freequency_details


class brand_hover_data_us_lagging(BaseModel):
    net_sales: brand_hover_data_freequency_details
    demand_components_of_growth: brand_hover_data_freequency_details


class brand_hover_data_details(BaseModel):
    us_leading: brand_hover_data_us_leading
    worldwide_lrs: brand_hover_data_worldwide_lrs
    us_execution: brand_hover_data_us_execution
    global_brand_sales_drivers: brand_hover_data_global_brand_sales_drivers
    us_lagging: brand_hover_data_us_lagging


class brand_hover_data(BaseModel):
    status: Optional[str]
    message: Optional[str]
    data: Optional[brand_hover_data_details]


class brand_hover_data_freequency_details(BaseModel):
    Refresh_Freequency: str = Field(
        alias="Refresh Frequency", Example="Weekly (last refreshed  02/10/2023)"
    )
    Data_Source: str = Field(alias="Data Source", Example="CD&A")


class brand_hover_data_nbrx_volume_by_specialties(BaseModel):
    c4w_vs_p4w: brand_hover_data_freequency_details
    volume_by_specialties: brand_hover_data_freequency_details
    r4w_goal: brand_hover_data_freequency_details


class brand_hover_data_us_leading(BaseModel):
    nbrx_volume_by_specialties: brand_hover_data_nbrx_volume_by_specialties
    nbrx_fulfillment: brand_hover_data_freequency_details
    idn_account_wins: brand_hover_data_freequency_details


class brand_hover_data_worldwide_lrs(BaseModel):
    Last_Refreshed: str = Field(alias="Last Refreshed", Example="02/28/2023")
    Data_Source: str = Field(alias="Data Source", Example="EDW")


class brand_hover_data_us_execution(BaseModel):
    share_of_voice: brand_hover_data_freequency_details
    call_attainment: brand_hover_data_freequency_details


class brand_hover_data_global_brand_sales_drivers(BaseModel):
    volume_market_mktshare_us: brand_hover_data_freequency_details
    sales: brand_hover_data_freequency_details
    volume_market_mktshare_o_us: brand_hover_data_freequency_details


class brand_hover_data_us_lagging(BaseModel):
    net_sales: brand_hover_data_freequency_details
    demand_components_of_growth: brand_hover_data_freequency_details


class brand_hover_data_details(BaseModel):
    us_leading: brand_hover_data_us_leading
    worldwide_lrs: brand_hover_data_worldwide_lrs
    us_execution: brand_hover_data_us_execution
    global_brand_sales_drivers: brand_hover_data_global_brand_sales_drivers
    us_lagging: brand_hover_data_us_lagging


class brand_hover_data(BaseModel):
    status: Optional[str]
    message: Optional[str]
    data: Optional[brand_hover_data_details]
