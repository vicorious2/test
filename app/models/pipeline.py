from typing import Optional
from pydantic import BaseModel, Field, HttpUrl, EmailStr
from pydantic.typing import Literal
from ..models.common import Owners, ExternalLink

from app.db.dynamodb_models import ARCHETYPES


class pipeline_product_tpp_data(BaseModel):
    tppSummaryOfChange: Optional[str] = Field(example="Initial entry")
    tppLink: Optional[str] = Field(
        example="https://amgen.sharepoint.com/sites/CRDC_PM/CMZO/CMZX/_layouts/Doc.aspx?sourcedoc=%7B78FD61A5-949F-482F-9CDE-4865169F2C1C%7D&file=AMG%20340%20TPP%20Nov%202022%20update.pptx&action=edit&mobileredirect=true"
    )
    indications: Optional[str] = Field(example="Prostate Cancer")
    keyMarketsOfEntry: Optional[str] = Field(example="US, EU, Japan")
    ceoStaffSponsor: Optional[str] = Field(example="David Reese")
    operatingTeamOwner: Optional[str] = Field(example="Rob Lenz")
    businessLead: Optional[str] = Field(
        example="Margit (Maggie) Janat-Amsbury (Early Development Lead)"
    )
    name: Optional[str] = Field(example="5474024.01")


class pipeline_product_tpp_model(BaseModel):
    data: list[pipeline_product_tpp_data]


class pipeline_key_products_ipp_pub_data(BaseModel):
    product: Optional[str] = Field(example="bemarituzumab")
    name: Optional[str] = Field(example="5465082.01")
    names: Optional[str] = Field(example="5465082.02,5465082.01")
    amgNumber: Optional[str] = Field(example="AMG 552")
    description: Optional[str] = Field(
        example="AMG 552 1L Gastric Cancer (BEMA + mFOLFOX)"
    )
    ippShortName: Optional[str] = Field(example="AMG 552 1L Gastric(BEMA+mFOLFOX)")
    ippShortNames: Optional[str] = Field(
        example="AMG 552 1L Gastric(BEMA+mFOLFOX+NIVO),AMG 552 1L Gastric(BEMA+mFOLFOX)"
    )
    projectStatus: Optional[str] = Field(example="At Risk")
    currentPhase: Optional[str] = Field(example="Phase 3")
    e2lLauDate: Optional[str] = Field(example="2025-08-12")
    e2lLauDesc: Optional[str] = Field(example="Launch")
    e2lLauStatus: Optional[str] = Field(example="On Track")
    e2lLauDateVariance: Optional[str] = Field(example="0")
    e2lSnapDate: Optional[str] = Field(example="2023-01-20k")
    e2lIppShortName: Optional[str] = Field(example="AMG 552 1L Gastric(BEMA+mFOLFOX)")
    e2lTransitionDateReason: Optional[str] = Field(example="None")
    nkmDescription: Optional[str] = Field(example="AMG 552 1L Gastric(BEMA+mFOLFOX)")
    nkmMilestoneShortName: Optional[str] = Field(example="LSE")
    nkmDate: Optional[str] = Field(example="2023-12-01")
    nkmStatus: Optional[str] = Field(example="On Track")
    nkmDateVariance: Optional[str] = Field(example="0")
    nkmStudyShortDescription: Optional[str] = Field(
        example="Ph3 Bema+mFOLFOX in 1L Gastric Cancer "
    )
    nkmAnapDate: Optional[str] = Field(example="2023-01-20")
    nkmTransitionDateReason: Optional[str] = Field(example="0")


class pipeline_key_products_ipp_pub_model(BaseModel):
    data: list[pipeline_key_products_ipp_pub_data]


class pipeline_key_products_csp_current_month_data(BaseModel):
    product: Optional[str] = Field(example="bemarituzumab")
    project: Optional[str] = Field(example="5411060.01")
    ippShortName: Optional[str] = Field(example="AMG 133 Obesity")
    ippStudyNumber: Optional[str] = Field(example="20190218")
    studyShortDescription: Optional[str] = Field(example="P2 Obesity")
    fseDate: Optional[str] = Field(example="2023-01-18")
    cspFsaDate: Optional[str] = Field(example="2022-12-13")
    cspFseDate: Optional[str] = Field(example="2023-01-18")
    cspLseDate: Optional[str] = Field(example="2023-10-08")
    latestPlannedCumulativeSubjectsEnrolled: Optional[str] = Field(example="2")
    actualCumulativeSubjectsEnrolled: Optional[str] = Field(example="0")
    actualCumulativeSitesActivated: Optional[str] = Field(example="3")
    latestPlannedCumulativeSitesActivated: Optional[str] = Field(example="0")
    percToPlanSubjectEnrollment: Optional[str] = Field(example="1.0")
    enrStatus: Optional[str] = Field(example="green")
    percToPlanSiteActivation: Optional[str] = Field(example="0.38")
    sitesActivatedStatus: Optional[str] = Field(example="red")


class pipeline_key_products_csp_current_month_model(BaseModel):
    data: list[pipeline_key_products_csp_current_month_data]


class CriticalToolTip(BaseModel):
    studyNumber: Optional[float]
    study: Optional[str]
    lastMonthPctEnr: Optional[float]
    lastMonthActualEnr: Optional[str]
    lastMonthPlanEnr: Optional[str]


class PriorityCriticalPathStudyEnrollmenP(BaseModel):
    study: Optional[str]
    fseDate: Optional[str]
    isEnrollmentStarted: Optional[bool] = False
    tooltip: Optional[CriticalToolTip]
    enrStatus: Optional[str]


class NextToolTip(BaseModel):
    varianceDays: Optional[str]
    baselineDate: Optional[str]
    reason: Optional[str]


class NextPriorityMilestone(BaseModel):
    nkmDescription: Optional[str]
    nkmMilestoneShortName: Optional[str]
    nkmDate: Optional[str]
    nkmStatus: Optional[str]
    nkmDateVariance: Optional[str]
    nkmStudyShortDescription: Optional[str]
    nkmSnapDate: Optional[str]
    nkmTransitionDateReason: Optional[str]
    status: Optional[str]
    tooltip: Optional[NextToolTip]


class NextPriorityLaunch(BaseModel):
    e2lLauDate: Optional[str]
    e2lLauDesc: Optional[str]
    e2lLauStatus: Optional[str]
    e2lLauDateVariance: Optional[str]
    e2lSnapDate: Optional[str]
    e2lIppShortName: Optional[str]
    e2lTransitionDateReason: Optional[str]
    status: Optional[str]
    tooltip: Optional[NextToolTip]


class Pipeline(BaseModel):
    agendaItemId: Optional[str]
    title: Optional[str]
    status: Optional[str]
    statusReason: Optional[str]
    scope: Optional[str]
    keyInsights: Optional[str]
    statusText: Optional[str]
    reason: Optional[str]
    href: Optional[str]
    owners: Optional[Owners]
    nextLaunch: Optional[NextPriorityLaunch]
    nextMilestone: Optional[NextPriorityMilestone]
    criticalPathStudy: Optional[list[PriorityCriticalPathStudyEnrollmenP]]


class CommercialPipelineStatusTooltip(BaseModel):
    varianceDays: Optional[str]
    baselineDate: Optional[str]
    reason: Optional[str]
    dataSource: Optional[str]


class CommercialPipelineProjectSection(BaseModel):
    title: Optional[str]
    textLines: Optional[list[str]]
    date: Optional[str]
    status: Optional[str]
    statusTooltip: Optional[CommercialPipelineStatusTooltip]


class CommercialPipelineProject(BaseModel):
    title: Optional[str]
    status: Optional[str]
    owners: Optional[Owners]
    sections: Optional[list[CommercialPipelineProjectSection]]
    externalLinks: Optional[list[ExternalLink]]


class CommercialPipeline(BaseModel):
    projects: Optional[list[CommercialPipelineProject]]
