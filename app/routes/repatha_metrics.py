from datetime import datetime
import time
import os
from decimal import Decimal
import re
import traceback
from ..dataHelper import DataHelper
from ..files import read_file
from ..constant import Constant
from . import pipeline_metrics
from ..models.common import Owners

from ..utils.agenda_items_utils_v2 import calculate_commercial_repatha_status
from fastapi import APIRouter, Depends, HTTPException
import requests
from ..models.repatha_metrics import (
    Commercial,
    Brand,
    RepathaNbrxVolumeBySpecialties,
    RepathaNbrxVolumeBySpecialtiesDetails,
    RepathaNbrxVolumeBySpecialtiesDetailsLastUpdatedData,
    RepathaNbrxVolumeLastUpdatedDataRefreshDetails,
    RepathaNbrxFulFillmentLastUpdatedDataDetails,
    RepathaNetSalesLastUpdatedDetails,
    NbrxFulfillment,
    NbrxFulfillmentDetails,
    Pipeline,
    ANC,
    Supply,
    ANCDetails,
    InventoryBelowTarget,
    AOHDetails,
    AOH,
    IdnAccountWins,
    ShareOfVoice,
    Chart,
    NetSalesSummary,
    repatha_hover_data,
    NetSales,
    PipelineCSP,
    PipelineMilestone,
    People,
    Turnover,
    TalentAcquisition,
    EngagementScore,
    FDP,
)

from ..AuthUtil import is_authorized, get_page_permissions
from ..loggerFactory import LoggerFactory
from ..routes.agenda_items_v2 import get_agenda_item

logger = LoggerFactory.get_logger(__name__)

env = os.getenv("PA_ENV", "not found")

env_brand = ""
env_people = ""
env_pipline = env  # currently not used
env_supply = ""

env_brand_href = ""
env_people_href = ""
env_pipline_href = env  # currently not used
env_supply_href = ""

if env == "dev" or env == "test":
    env_brand = "api-" + env
    env_people = "api-" + env
    env_supply = "api-" + env

    env_brand_href = "-" + env
    env_people_href = "-" + env
    env_pipline_href = "-" + env
    env_supply_href = "-" + env
elif env == "staging":
    env_brand = "api-stg"
    env_people = "api-stg"
    env_supply = "api-" + env

    env_brand_href = "-stg"
    env_people_href = "-stg"
    env_pipline_href = "-stg"
    env_supply_href = "-stg"
elif env == "rts":
    env_brand = "api"
    env_people = "api"
    env_supply = env


envAlt = env
if env == "staging":
    envAlt = "stg"


router = APIRouter(
    prefix="/api",
    tags=["Repatha Metrics"],
)


# BRAND
def get_repatha_nbrx_volume_by_specialties(token):
    logger.debug(f"Brand get_repatha_nbrx_volume_by_specialties: start")
    try:
        headers = {
            "Authorization": "Bearer " + token.credentials,
            "content-type": "application/json",
        }
        data = {"brand_name": "REPATHA"}
        response = requests.post(
            f"https://brand-{env_brand}.nimbus.amgen.com/brand_services/us_leading/nbrx_writer_pcp_card",
            headers=headers,
            json=data,
        )
        if response.status_code != 200:
            logger.debug(
                f"Brand _nbrx_volume_by_specialties response code: {response.status_code}"
            )
            return None

        cardRecentAvg = 0.0
        cardRecentGoal = 0.0
        cardStatus = "gray"
        pcpRecentAvg = 0.0
        pcpRecentGoal = 0.0
        pcpStatus = "gray"

        j = response.json()
        cardiologists = []
        pcps = []
        for d in j["data"]:
            if "NBRx Writer - CARD" in d:
                for card in d["NBRx Writer - CARD"]:
                    det = RepathaNbrxVolumeBySpecialtiesDetails()
                    det.label = card["Name"]
                    det.currentVsPrevious = card["C4W_P4W"]
                    det.recentAvg = card["R4W"]
                    det.recentGoal = card["R4W_Goal"]
                    cardiologists.append(det)
                    if card["Name"] == "Avg NBRx/Writer":
                        cardRecentAvg = Decimal(det.recentAvg)
                        cardRecentGoal = Decimal(det.recentGoal)
            if "NBRx Writer - PCP" in d:
                for pcp in d["NBRx Writer - PCP"]:
                    det = RepathaNbrxVolumeBySpecialtiesDetails()
                    det.label = pcp["Name"]
                    det.currentVsPrevious = pcp["C4W_P4W"]
                    det.recentAvg = pcp["R4W"]
                    det.recentGoal = pcp["R4W_Goal"]
                    pcps.append(det)
                    if pcp["Name"] == "Avg NBRx/Writer":
                        pcpRecentAvg = Decimal(det.recentAvg)
                        pcpRecentGoal = Decimal(det.recentGoal)

        # TODO: Refactor
        repathaNbrxVolumeBySpecialties = RepathaNbrxVolumeBySpecialties()
        if cardRecentGoal + cardRecentAvg * Decimal("0.02") < cardRecentAvg:
            cardStatus = "green"
        elif cardRecentGoal - cardRecentAvg * Decimal("0.02") > cardRecentAvg:
            cardStatus = "red"
        else:
            cardStatus = "yellow"

        if pcpRecentGoal + pcpRecentAvg * Decimal("0.02") < pcpRecentAvg:
            pcpStatus = "green"
        elif pcpRecentGoal - pcpRecentAvg * Decimal("0.02") > pcpRecentAvg:
            pcpStatus = "red"
        else:
            pcpStatus = "yellow"

        if cardStatus == "red" or pcpStatus == "red":
            repathaNbrxVolumeBySpecialties.status = "red"
        elif cardStatus == "yellow" or pcpStatus == "yellow":
            repathaNbrxVolumeBySpecialties.status = "yellow"
        else:
            repathaNbrxVolumeBySpecialties.status = "green"

        repathaNbrxVolumeBySpecialties.cardiologists = cardiologists
        repathaNbrxVolumeBySpecialties.pcps = pcps
        repathaNbrxVolumeBySpecialties.href = f"https://sensing{env_brand_href}.nimbus.amgen.com/brand#repatha_leading_nbrx_volume_by_specialties"

        return repathaNbrxVolumeBySpecialties
    except Exception:
        logger.debug(traceback.print_exc())
        return None


# TODO convert to utility
def get_nbrx_fulfillment(token):
    logger.debug(f"Brand get_nbrx_fulfillment: start")
    try:
        headers = {
            "Authorization": "Bearer " + token.credentials,
            "content-type": "application/json",
        }
        data = {"brand_name": "REPATHA"}
        response = requests.post(
            f"https://brand-{env_brand}.nimbus.amgen.com/brand_services/us_leading/nbrx_fulfillment",
            headers=headers,
            json=data,
        )
        if response.status_code != 200:
            logger.debug(
                f"Brand nbrx_fulfillment response code: {response.status_code}"
            )
            return None

        nbrxFulfillment = NbrxFulfillment()
        nbrxFulfillmentDetails = []
        j = response.json()
        for d in j["data"]:
            det = NbrxFulfillmentDetails()
            det.label = d["Channel"]
            det.goal = d["NBRx Fulfillment"]
            det.previous = d["NBRx Fulfillment-R4W PY"]
            det.current = d["NBRx Fulfillment-R4W"]
            nbrxFulfillmentDetails.append(det)
            if det.label == "Overall":
                goal = Decimal(det.goal.replace("%", ""))
                current = Decimal(det.current.replace("%", ""))
                if goal + goal * Decimal("0.02") < current:
                    nbrxFulfillment.status = "green"
                elif goal - goal * Decimal("0.02") > current:
                    nbrxFulfillment.status = "red"
                else:
                    nbrxFulfillment.status = "yellow"

        nbrxFulfillment.href = (
            f"https://sensing{env_brand_href}.nimbus.amgen.com/brand#repatha_leading"
        )
        nbrxFulfillment.data = nbrxFulfillmentDetails

        return nbrxFulfillment
    except Exception:
        logger.debug(traceback.print_exc())
        return None


@router.get("/v1/repatha_net_sales")
def get_repatha_net_sales(token=Depends(is_authorized)):
    logger.debug(f"Brand net_sales: start")
    try:
        headers = {
            "Authorization": "Bearer " + token.credentials,
            "content-type": "application/json",
        }
        data = {"brand_name": "REPATHA"}
        response = requests.post(
            f"https://brand-{env_brand}.nimbus.amgen.com/brand_services/us_lagging/net_sales",
            headers=headers,
            json=data,
        )
        if response.status_code != 200:
            logger.debug(f"Brand net_sales response code: {response.status_code}")
            return None

        netSales = NetSales()
        # TODO NET SALES STATUS
        chart = []

        # chart.chartDetails = [ChartDetails]
        netSalesSummary = NetSalesSummary()
        weeklyAverage = NetSalesSummary()

        j = response.json()
        for trend_line_times in j["data"]["trend_line"]:
            chartDetails = Chart()
            chartDetails.label = trend_line_times["month"]
            if "net_sales_fcst" in trend_line_times:
                chartDetails.forecast = trend_line_times["net_sales_fcst"]
            if "net_sales_actual" in trend_line_times:
                chartDetails.value = trend_line_times["net_sales_actual"]
            chart.append(chartDetails)
            first = False

        for t in j["data"]["table"]:
            if t["name"] == "Net Sales":
                netSalesSummary.ytdLabel = t["YTD"]["Name"]
                netSalesSummary.ytd = t["YTD"]["Value"]
                netSalesSummary.ytgLabel = t["YTG"]["Name"]
                netSalesSummary.ytg = t["YTG"]["Value"]
                netSalesSummary.forecast = t["FY FCST"]["Value"]
                try:
                    netSalesSummary.status = (
                        "green" if t["YTG"]["is_positive"] == True else "red"
                    )
                except:
                    print("dont have ytg")
            if t["name"] == "Weekly Average":
                weeklyAverage.ytdLabel = t["YTD"]["Name"]
                weeklyAverage.ytd = t["YTD"]["Value"]
                weeklyAverage.ytgLabel = t["YTG"]["Name"]
                weeklyAverage.ytg = t["YTG"]["Value"]
                weeklyAverage.forecast = t["FY FCST"]["Value"]
                try:
                    weeklyAverage.status = (
                        "green" if t["YTG"]["is_positive"] == True else "red"
                    )
                except:
                    print("dont have ytg")
                ytd = Decimal(weeklyAverage.ytd.replace("M", ""))
                ytg = Decimal(weeklyAverage.ytg.replace("M", ""))
                forecast = Decimal(weeklyAverage.forecast.replace("M", ""))
                if ytd >= ytg and ytd > forecast + forecast * Decimal("0.02"):
                    netSales.status = "green"
                elif ytd < ytg or ytd < forecast - forecast * Decimal("0.02"):
                    netSales.status = "red"
                else:
                    netSales.status = "yellow"

        # u=j["data"]["us_lagging"]["net_sales"]
        # for t in j["data"]["us_lagging"]["net_sales"]:
        #     print(t)
        #     netSales.lastUpdated=t["Refresh Freequency"]
        netSales.chart = chart
        netSales.netSales = netSalesSummary
        netSales.weeklyAverage = weeklyAverage
        netSales.href = (
            f"https://sensing{env_brand_href}.nimbus.amgen.com/brand#repatha"
        )
        return netSales
    except Exception:
        logger.debug(traceback.print_exc())
        return None


@router.get(
    "/v1/repatha_hover_data",
)
def get_repatha_hover_data(token):
    logger.debug(f"Brand hover_data: start")
    headers = {
        "Authorization": "Bearer " + token.credentials,
        "content-type": "application/json",
    }
    data = {"brand_name": "REPATHA"}
    response = requests.post(
        f"https://brand-{env_brand}.nimbus.amgen.com//brand_services/hover/hover_data",
        headers=headers,
        json=data,
    )
    if response.status_code != 200:
        logger.debug(f"Brand hover_data response code: {response.status_code}")
        return None

    repatha_tooltip_data = repatha_hover_data()
    response_obj = repatha_tooltip_data.parse_obj(response.json()).data
    return response_obj


@router.get(
    "/v1/nbrx_demand",
)
def get_nbrx_demand(token=Depends(is_authorized)):
    logger.debug(f"Brand get_nbrx_demand: start")
    headers = {
        "Authorization": "Bearer " + token.credentials,
        "content-type": "application/json",
    }
    data = {"brand_name": "REPATHA", "brand_type": "nbrx", "speciality_group": ""}
    response = requests.post(
        f"https://brand-{env_brand}.nimbus.amgen.com/brand_services/us_lagging/demand_components_of_growth",
        headers=headers,
        json=data,
    )
    if response.status_code != 200:
        logger.debug(
            f"Brand demand_comp_of_growth response code: {response.status_code}"
        )
        return None

    nbrx = NetSales()
    nbrxChart = []
    nbrxNetSalesSummary = NetSalesSummary()
    nbrxWeeklyAverage = NetSalesSummary()
    j = response.json()

    for tl in j["data"]["volume"]["trendLine"]:
        chartDetails = Chart()
        chartDetails.label = tl["month"]
        if "net_sales_fcst" in tl:
            chartDetails.forecast = tl["net_sales_fcst"]
        if "net_sales_actual" in tl:
            chartDetails.value = tl["net_sales_actual"]
        nbrxChart.append(chartDetails)

    for t in j["data"]["volume"]["tableData"]:
        if t["name"] == "Volume":
            nbrxNetSalesSummary.ytdLabel = t["YTD"]["Name"]
            nbrxNetSalesSummary.ytd = t["YTD"]["Value"]
            nbrxNetSalesSummary.ytgLabel = t["YTG"]["Name"]
            nbrxNetSalesSummary.ytg = t["YTG"]["Value"]
            nbrxNetSalesSummary.forecast = t["FY FCST"]["Value"]
            try:
                nbrxNetSalesSummary.status = (
                    "green" if t["YTG"]["is_positive"] == True else "red"
                )
            except:
                print("dont have ytg")
        if t["name"] == "Weekly Average":
            nbrxWeeklyAverage.ytdLabel = t["YTD"]["Name"]
            nbrxWeeklyAverage.ytd = t["YTD"]["Value"]
            nbrxWeeklyAverage.ytgLabel = t["YTG"]["Name"]
            nbrxWeeklyAverage.ytg = t["YTG"]["Value"]
            nbrxWeeklyAverage.forecast = t["FY FCST"]["Value"]
            ytd = Decimal(nbrxWeeklyAverage.ytd.replace("K", ""))
            ytg = Decimal(nbrxWeeklyAverage.ytg.replace("K", ""))
            forecast = Decimal(nbrxWeeklyAverage.forecast.replace("K", ""))
            if ytd >= ytg and ytd > forecast + forecast * Decimal("0.02"):
                nbrx.status = "green"
            elif ytd < ytg or ytd < forecast - forecast * Decimal("0.02"):
                nbrx.status = "red"
            else:
                nbrx.status = "yellow"
            try:
                nbrxWeeklyAverage.status = (
                    "green" if t["YTG"]["is_positive"] == True else "red"
                )
            except:
                print("dont have ytg")

    nbrx.chart = nbrxChart
    nbrx.netSales = nbrxNetSalesSummary
    nbrx.weeklyAverage = nbrxWeeklyAverage
    nbrx.href = f"https://sensing{env_brand_href}.nimbus.amgen.com/brand#repatha"

    return nbrx


@router.get(
    "/v1/trx_demand",
)
def get_trx_demand(token=Depends(is_authorized)):
    logger.debug(f"Brand get_trx_demand: start")
    headers = {
        "Authorization": "Bearer " + token.credentials,
        "content-type": "application/json",
    }

    data = {"brand_name": "REPATHA", "brand_type": "trx", "speciality_group": ""}
    response = requests.post(
        f"https://brand-{env_brand}.nimbus.amgen.com/brand_services/us_lagging/demand_components_of_growth",
        headers=headers,
        json=data,
    )
    trx = NetSales()
    trxChart = []
    trxNetSalesSummary = NetSalesSummary()
    trxWeeklyAverage = NetSalesSummary()
    j = response.json()

    for tl in j["data"]["volume"]["trendLine"]:
        chartDetails = Chart()
        chartDetails.label = tl["month"]
        if "net_sales_fcst" in tl:
            chartDetails.forecast = tl["net_sales_fcst"]
        if "net_sales_actual" in tl:
            chartDetails.value = tl["net_sales_actual"]
        trxChart.append(chartDetails)

    for t in j["data"]["volume"]["tableData"]:
        if t["name"] == "Volume":
            trxNetSalesSummary.ytdLabel = t["YTD"]["Name"]
            trxNetSalesSummary.ytd = t["YTD"]["Value"]
            trxNetSalesSummary.ytgLabel = t["YTG"]["Name"]
            trxNetSalesSummary.ytg = t["YTG"]["Value"]
            trxNetSalesSummary.forecast = t["FY FCST"]["Value"]
            try:
                trxNetSalesSummary.status = (
                    "green" if t["YTG"]["is_positive"] == True else "red"
                )
            except:
                logger.debug("does not have ytg")
        if t["name"] == "Weekly Average":
            trxWeeklyAverage.ytdLabel = t["YTD"]["Name"]
            trxWeeklyAverage.ytd = t["YTD"]["Value"]
            trxWeeklyAverage.ytgLabel = t["YTG"]["Name"]
            trxWeeklyAverage.ytg = t["YTG"]["Value"]
            trxWeeklyAverage.forecast = t["FY FCST"]["Value"]
            try:
                trxWeeklyAverage.status = (
                    "green" if t["YTG"]["is_positive"] == True else "red"
                )
            except:
                logger.debug("Weekly Average does not have ytg")
            ytd = Decimal(trxWeeklyAverage.ytd.replace("K", ""))
            ytg = Decimal(trxWeeklyAverage.ytg.replace("K", ""))
            forecast = Decimal(trxWeeklyAverage.forecast.replace("K", ""))
            if ytd >= ytg and ytd > forecast + forecast * Decimal("0.02"):
                trx.status = "green"
            elif ytd < ytg or ytd < forecast - forecast * Decimal("0.02"):
                trx.status = "red"
            else:
                trx.status = "yellow"

    trx.chart = trxChart
    trx.netSales = trxNetSalesSummary
    trx.weeklyAverage = trxWeeklyAverage
    trx.href = (
        f"https://sensing{env_brand_href}.nimbus.amgen.com/brand#repatha_trx_demand"
    )

    return trx


# END BRAND

# SUPPLY
def get_supply_ANC(token) -> ANC:
    logger.debug(f"Supply get_supply_ANC: start")
    headers = {
        "Authorization": "Bearer " + token.credentials,
        "content-type": "application/json",
    }
    response = requests.get(
        f"https://supply-{env_supply}.nimbus.amgen.com/v1/capital/portfolio/projects/data.json",
        headers=headers,
    )
    if response.status_code != 200:
        logger.debug(f"Supply ANC response code: {response.status_code}")
        return None

    j = response.json()
    anc = ANC()
    anc.owners = Owners()
    anc.owners.ceoStaffSponsors = []
    anc.owners.operatingTeamOwners = []
    anc.owners.ceoStaffSponsors.append("Esteban Santos")
    anc.owners.operatingTeamOwners.append("Arleen Paulino")
    anc.href = f"https://sensing{env_supply_href}.nimbus.amgen.com/supply/dashboard"
    for s in j["series"]:
        if s["projectShortName"] == "ANC FleX Batch DS Manufacturing Facility":
            anc.status = s["overallAlert"].lower()
            scope = ANCDetails()
            scope.status = s["scopeAlert"].lower()
            scope.text = getAlertLabel(s["scopeAlert"].lower())
            timeline = ANCDetails()
            timeline.status = s["completionDateAlert"].lower()
            timeline.text = s["forecastCompletionDate"]
            value = ANCDetails()
            value.status = s["valueAlert"].lower()
            value.text = getAlertLabel(s["valueAlert"].lower())
            anc.status = value.status.lower()
            cost = ANCDetails()
            cost.status = s["fundingAlert"].lower()
            cost.text = s["forecastFunding"]
            risk = ANCDetails()
            risk.status = s["riskAlert"].lower()
            risk.text = s["risk"]

            anc.scope = scope
            anc.timeline = timeline
            anc.value = value
            anc.cost = cost
            anc.risk = risk

            break

    return anc


def get_aoh(token) -> AOH:
    logger.debug(f"Supply get_aoh: start")
    headers = {
        "Authorization": "Bearer " + token.credentials,
        "content-type": "application/json",
    }
    response = requests.get(
        f"https://supply-{env_supply}.nimbus.amgen.com/v1/capital/portfolio/projects/data.json",
        headers=headers,
    )

    if response.status_code != 200:
        logger.debug(f"Supply aoh response code: {response.status_code}")
        return None
    # response_obj = repatha_aoh_comp_of_growth.parse_obj(response.json())
    # return response.json()
    j = response.json()
    anc = AOH()
    anc.owners = Owners()
    anc.owners.ceoStaffSponsors = []
    anc.owners.operatingTeamOwners = []
    anc.owners.ceoStaffSponsors.append("Esteban Santos")
    anc.owners.operatingTeamOwners.append("Arleen Paulino")
    anc.href = f"https://sensing{env_supply_href}.nimbus.amgen.com/supply/dashboard"
    for s in j["series"]:
        if s["projectShortName"] == "AOH - B1 Packaging Facility":
            scope = AOHDetails()
            scope.status = s["scopeAlert"].lower()
            scope.text = getAlertLabel(s["scopeAlert"].lower())
            timeline = AOHDetails()
            timeline.status = s["completionDateAlert"].lower()
            timeline.text = s["forecastCompletionDate"]
            value = AOHDetails()
            value.status = s["valueAlert"].lower()
            value.text = getAlertLabel(s["valueAlert"].lower())
            anc.status = value.status.lower()
            cost = AOHDetails()
            cost.status = s["fundingAlert"].lower()
            cost.text = s["forecastFunding"]
            risk = AOHDetails()
            risk.status = s["riskAlert"].lower()
            risk.text = s["risk"]

            anc.scope = scope
            anc.timeline = timeline
            anc.value = value
            anc.cost = cost
            anc.risk = risk
            break
    return anc


# needs refinement
def get_supply_InventoryBelowTarget(token) -> InventoryBelowTarget:
    logger.debug(f"Supply get_supply_InventoryBelowTarget: start")
    headers = {
        "Authorization": "Bearer " + token.credentials,
        "content-type": "application/json",
    }
    response = requests.get(
        f"https://supply-{env_supply}.nimbus.amgen.com/v1/read/agility/commercialproductssupply/expand/data.json",
        headers=headers,
    )
    if response.status_code != 200:
        logger.debug(
            f"Supply InventoryBelowTarget response code: {response.status_code}"
        )
        return None
    j = response.json()
    inventoryBelowTarget = InventoryBelowTarget()
    inventoryBelowTarget.href = (
        f"https://sensing{env_supply_href}.nimbus.amgen.com/supply/dashboard"
    )
    for s in j["skusBelowSss"]["skusBelowMinTarget"]:
        if s["productName"] == "REPATHA":
            # inventoryBelowTarget.status = s["fdp"]["status"].lower()
            fdp = FDP()
            fdp.status = s["fdp"]["status"].lower()
            fdp.countries = s["fdp"]["countries"]
            fdp.reasonCodes = s["fdp"]["reasonCodes"]
            fdp.value = s["fdp"]["value"]
            if fdp.status == "green":
                fdp.statusText = "Above OSS"
            elif fdp.status == "yellow":
                fdp.statusText = "Below OSS"
            else:
                fdp.statusText = "Below SSS"
            inventoryBelowTarget.fdp = fdp
            break

    return inventoryBelowTarget


# END SUPPLY


def getAlertLabel(alert):
    match (alert):
        case "green":
            return "No Change"
        case "red":
            return "At Risk"
        case "yellow":
            return "Needs Attention"
        case _:
            return "--"


# PIPELINE
@router.get("/v1/get_pipeline_metrics")
def get_pipeline_metrics(token=Depends(is_authorized)):
    """
    s3 method for /api/v4/key_upcoming_events
    ---
    responses:
      200:
        description: Athena s3 info for bucket
        (s3://aws-athena-query-results-291403363365-us-west-2/)
    """
    logger.debug(f"Pipeline get_pipeline_metrics: start")
    pipeline = Pipeline()
    pipeline.csp = PipelineCSP()
    npm = PipelineMilestone()
    nf = PipelineMilestone()
    nal = PipelineMilestone()

    pm = pipeline_metrics.get_key_products_tpp(token, "5193088.09")
    owners = Owners()
    owners.ceoStaffSponsors = []
    owners.operatingTeamOwners = []
    owners.ceoStaffSponsors.append(pm[0]["ceo_staff_sponsor"])
    owners.operatingTeamOwners.append(pm[0]["operating_team_owner"])
    pipeline.owners = owners

    key = f"{Constant.REDIS_KEY_PREFIX}__get_pipeline_metrics_v3__"
    j = DataHelper.get_data(
        "get_pipeline_metrics",
        key,
        read_file(Constant.REPATHA_MILESTONSES_SQL),
        [],
        "repatha_metrics.py",
    )
    npmSet = False
    nfSet = False
    nalSet = False
    for ms in j:
        if (
            ms["activity_type"] in ["PRI_AN_FLASH", "FLASH_MEMO", "INT_AN_FLASH"]
            and not npmSet
        ):
            npmSet = True
            npm.status = ms["milestone_status"].lower()
            npm.statusLabel = ms["milestone_status"].lower()
            npm.msDate = ms["end_date_current_approved_cab"]
            npm.msShortName = ms["milestone_short_name"]
            npm.nkmSnapDate = ms["date_variance"]
            npm.nkmTransitionDateReason = ms["transition_date_reason"]
            npm.nkmSnapDate = ms["snap_date"]
            npm.geographicArea = ms["geographic_area"]
            pipeline.npm = npm
        if ms["activity_type"] in ["MA_SUB_DATE_US"] and not nfSet:
            nfSet = True
            nf.status = ms["milestone_status"].lower()
            nf.statusLabel = ms["milestone_status"].lower()
            nf.msDate = ms["end_date_current_approved_cab"]
            nf.msShortName = ms["milestone_short_name"]
            nf.dateVariance = ms["date_variance"]
            nf.nkmTransitionDateReason = ms["transition_date_reason"]
            nf.nkmSnapDate = ms["snap_date"]
            nf.geographicArea = ms["geographic_area"]
            pipeline.nf = nf
        if ms["activity_type"] in ["BLA/NDA APP"] and not nalSet:
            nalSet = True
            nal.status = ms["milestone_status"].lower()
            nal.statusLabel = ms["milestone_status"].lower()
            nal.msDate = ms["end_date_current_approved_cab"]
            nal.msShortName = ms["milestone_short_name"]
            nal.dateVariance = ms["date_variance"]
            nal.nkmTransitionDateReason = ms["transition_date_reason"]
            nal.nkmSnapDate = ms["snap_date"]
            nal.geographicArea = ms["geographic_area"]
            pipeline.nal = nal

    return pipeline


# END PIPELINE

# PEOPLE
@router.get("/v1/get_people_metrics")
def get_people_metrics(token=Depends(is_authorized)):
    """
    s3 method for /api/v4/key_upcoming_events
    ---
    responses:
      200:
        description: Athena s3 info for bucket
    """
    logger.debug(f"People get_people_metrics: start")
    headers = {
        "Authorization": "Bearer " + token.credentials,
        "content-type": "application/json",
    }

    people = People()
    talentAcquisition = TalentAcquisition()
    engagementScore = EngagementScore()
    turnover = Turnover()
    chart = []
    chartAmgen = []

    talentAcquisition.href = f"https://sensing{env_people_href}.nimbus.amgen.com/people"
    engagementScore.href = f"https://sensing{env_people_href}.nimbus.amgen.com/people"
    turnover.href = f"https://sensing{env_people_href}.nimbus.amgen.com/people"
    # Engagement and Talent Acquisition
    try:
        response = requests.get(
            f"https://people-{env_people}.nimbus.amgen.com/api/v1/key-product/key-product-data/Repatha",
            headers=headers,
        )
        if response.status_code != 200:
            logger.debug(f"People response code: {response.status_code}")
        # return None

        j = response.json()

        for to in j["turnover_data"][0]["data"]:
            chartDetails = Chart()
            chartDetails.label = to["date"]
            chartDetails.value = to["value"]
            chart.append(chartDetails)

        turnover.chart = chart

        engagementScore.benchmark = j["engagement_data"][0]["data"][0]["benchmark"]
        engagementScore.productEngagementScore = j["engagement_data"][0]["data"][0][
            "product_engagement_score"
        ]
        engagementScore.productChange = j["engagement_data"][0]["data"][0][
            "product_change"
        ]
        engagementScore.date = j["engagement_data"][0]["data"][0]["date"]
        engagementScore.previousDate = j["engagement_data"][0]["data"][0][
            "previous_date"
        ]

        for ta in j["acquisition_data"][0]["data"]:
            if ta["status"] == "Open Reqs ":
                talentAcquisition.openRequisitions = ta["total_hires"]
            if ta["status"] == "Average Open Days":
                talentAcquisition.avgOpenDays = ta["total_hires"]

        # get amgen benchmark
        response = requests.get(
            f"https://people-{env_people}.nimbus.amgen.com/api/v1/culture/engagement-historical-trend?function=Amgen",
            headers=headers,
        )
        j = response.json()
        engagementScore.amgenAverage = j["data"][-1]["amgen_value"]
        if engagementScore.productEngagementScore >= engagementScore.amgenAverage:
            engagementScore.status = "green"
        else:
            engagementScore.status = "red"
    except Exception:
        engagementScore = None
        talentAcquisition = None
        logger.debug(traceback.print_exc())
    try:
        # turnover benchmark
        response = requests.get(
            f"https://people-{env_people}.nimbus.amgen.com/api/v1/talent-retention/talent-retention-data?function=Amgen",
            headers=headers,
        )
        j = response.json()

        for to in j["turnover_by_trends_data"][0]["data"]["amgen_data"]:
            chartDetails = Chart()
            dateStr = to["date"]
            dateStr = dateStr.replace("'", "")
            dateStr = dateStr[0:3] + " 01, 20" + dateStr[-2:]
            # Jan 25, 2021

            date = datetime.strptime(dateStr, "%b %d, %Y").date()
            chartDetails.label = date  # to["date"]
            chartDetails.value = to["total_turnover"]
            chartAmgen.append(chartDetails)

        for cd in chart:
            cdl = str(cd.label).strip()
            for cda in chartAmgen:
                cdal = str(cda.label).strip()
                if cdl == cdal:
                    cd.forecast = cda.value
        try:
            if chart[-1].value <= chart[-1].forecast:
                turnover.status = "green"
            else:
                turnover.status = "red"
        except:
            logger.debug(traceback.print_exc())
            turnover.status = "gray"
    except Exception:
        turnover = None
        logger.debug(traceback.print_exc())

    people.turnover = turnover
    people.engagementScore = engagementScore
    people.talentAcquisition = talentAcquisition
    return people


# END PEOPLE


def comm_permissions(
    commercial: Commercial, page_permissions, key, cache, agendaItemId
):
    agendaItem = get_agenda_item(agendaItemId)
    commercial.agendaItemId = agendaItemId
    commercial.owners = agendaItem.owners
    commercial.title = agendaItem.name
    commercial.scope = agendaItem.scope
    commercial.statusReason = agendaItem.statusReason
    commercial.keyInsights = agendaItem.keyInsights

    if (
        cache
        and page_permissions["supply"]
        and page_permissions["people"]
        and page_permissions["pipeline"]
        and page_permissions["brand"]
    ):
        logger.debug(f"comm_permissions: caching commercial object")
        DataHelper.cache_object("commercial", key, [], "repatha_metrics.py", commercial)
        return commercial
    if not page_permissions["supply"]:
        commercial.supply.anc = None
        commercial.supply.aoh = None
        commercial.supply.cogsReduction = None
        commercial.supply.inventoryBelowTarget = None
        logger.debug(
            f"comm_permissions: limiting commercial object response based on SUPPLY permissions"
        )
    if not page_permissions["people"]:
        commercial.people.turnover = None
        commercial.people.engagementScore = None
        commercial.people.talentAcquisition = None
        logger.debug(
            f"comm_permissions: limiting commercial object response based on PEOPLE permissions"
        )
    if not page_permissions["pipeline"]:
        commercial.pipeline = None
        logger.debug(
            f"comm_permissions: limiting commercial object response based on PIPELINE permissions"
        )
    if not page_permissions["brand"]:
        commercial.brand.netSales = None
        commercial.brand.nbrxDemand = None
        commercial.brand.trxDemand = None
        commercial.brand.idnAccountWins = None
        commercial.brand.nbrxFulfillment = None
        commercial.brand.nbrxVolume = None
        commercial.brand.shareOfVoice = None
        logger.debug(
            f"comm_permissions: limiting commercial object response based on BRAND permissions"
        )
    return commercial


@router.get("/v1/commercial")
def get_commercial(agendaItemId: int = 0, token=Depends(is_authorized)):
    tic = time.perf_counter()
    logger.debug(f"get_commercial: start")
    page_permissions = get_page_permissions(token.credentials)
    if (
        not page_permissions["supply"]
        and not page_permissions["people"]
        and not page_permissions["pipeline"]
        and not page_permissions["brand"]
    ):
        raise HTTPException(status_code=403)

    key = f"{Constant.REDIS_KEY_PREFIX}__commercial__"
    data = DataHelper.get_cached_object("commercial", key, [], "repatha_metrics.py")
    if data:
        toc = time.perf_counter()
        logger.debug(f"get_commercial: refresh timer {toc - tic:0.4f} seconds CACHED")
        return comm_permissions(data, page_permissions, key, False, agendaItemId)

    brand = Brand()
    pipeline = Pipeline()
    supply = Supply()
    try:
        pipeline = get_pipeline_metrics(token)
    except:
        logger.debug(traceback.print_exc())
        pipeline = None
    try:
        supply.anc = get_supply_ANC(token)
    except:
        logger.debug(traceback.print_exc())
        supply.anc = None
    try:
        supply.aoh = get_aoh(token)
    except:
        logger.debug(traceback.print_exc())
        supply.aoh = None
    try:
        supply.inventoryBelowTarget = get_supply_InventoryBelowTarget(token)
    except:
        logger.debug(traceback.print_exc())
        supply.inventoryBelowTarget = None

    brand.nbrxVolume = get_repatha_nbrx_volume_by_specialties(token)
    brand.nbrxFulfillment = get_nbrx_fulfillment(token)
    brand.netSales = get_repatha_net_sales(token)
    try:
        brand.trxDemand = get_trx_demand(token)
    except Exception:
        logger.debug(traceback.print_exc())
        brand.trxDemand = None
    try:
        brand.nbrxDemand = get_nbrx_demand(token)
    except Exception:
        logger.debug(traceback.print_exc())
        brand.nbrxDemand = None
    brand.shareOfVoice = ShareOfVoice()
    brand.idnAccountWins = IdnAccountWins()
    tooltip_data = get_repatha_hover_data(token)
    if tooltip_data:
        try:
            brand.netSales.lastUpdatedData = RepathaNetSalesLastUpdatedDetails()
            brand.netSales.lastUpdatedData.dataSource = (
                tooltip_data.us_lagging.net_sales.Data_Source
            )
            brand.netSales.lastUpdatedData.refreshFreequency = (
                tooltip_data.us_lagging.net_sales.Refresh_Freequency
            )
            brand.netSales.lastUpdated = (
                tooltip_data.us_lagging.net_sales.Refresh_Freequency
            )
            brand.nbrxDemand.lastUpdated = (
                tooltip_data.us_lagging.demand_components_of_growth.Refresh_Freequency
            )
            brand.trxDemand.lastUpdated = (
                tooltip_data.us_lagging.demand_components_of_growth.Refresh_Freequency
            )
            brand.nbrxFulfillment.lastUpdatedData = (
                RepathaNbrxFulFillmentLastUpdatedDataDetails()
            )
            brand.nbrxFulfillment.lastUpdatedData.dataSource = (
                tooltip_data.us_leading.nbrx_fulfillment.Data_Source
            )
            brand.nbrxFulfillment.lastUpdatedData.refreshFrequency = (
                tooltip_data.us_leading.nbrx_fulfillment.Refresh_Freequency
            )
            brand.nbrxVolume.lastUpdatedData = (
                RepathaNbrxVolumeBySpecialtiesDetailsLastUpdatedData()
            )
            brand.nbrxVolume.lastUpdatedData.contributionBySpecialty = (
                RepathaNbrxVolumeLastUpdatedDataRefreshDetails()
            )
            brand.nbrxVolume.lastUpdatedData.contributionBySpecialty.refreshFrequency = (
                tooltip_data.us_leading.nbrx_volume_by_specialties.volume_by_specialties.Refresh_Freequency
            )
            brand.nbrxVolume.lastUpdatedData.contributionBySpecialty.dataSource = (
                tooltip_data.us_leading.nbrx_volume_by_specialties.volume_by_specialties.Data_Source
            )
            brand.nbrxVolume.lastUpdatedData.currentVsPrevious = (
                RepathaNbrxVolumeLastUpdatedDataRefreshDetails()
            )
            brand.nbrxVolume.lastUpdatedData.currentVsPrevious.refreshFrequency = (
                tooltip_data.us_leading.nbrx_volume_by_specialties.c4w_vs_p4w.Refresh_Freequency
            )
            brand.nbrxVolume.lastUpdatedData.currentVsPrevious.dataSource = (
                tooltip_data.us_leading.nbrx_volume_by_specialties.c4w_vs_p4w.Data_Source
            )
            brand.nbrxVolume.lastUpdatedData.recentGoal = (
                RepathaNbrxVolumeLastUpdatedDataRefreshDetails()
            )
            brand.nbrxVolume.lastUpdatedData.recentGoal.refreshFrequency = (
                tooltip_data.us_leading.nbrx_volume_by_specialties.r4w_goal.Refresh_Freequency
            )
            brand.nbrxVolume.lastUpdatedData.recentGoal.dataSource = (
                tooltip_data.us_leading.nbrx_volume_by_specialties.r4w_goal.Data_Source
            )
        except Exception:
            logger.debug(traceback.print_exc())

    commercial = Commercial()
    commercial.brand = brand
    commercial.pipeline = pipeline
    commercial.supply = supply
    try:
        commercial.people = get_people_metrics(token)
    except Exception:
        people = People()
        people.turnover = None
        people.engagementScore = None
        people.talentAcquisition = None
        commercial.people = people
        logger.debug(traceback.print_exc())

    commercial.status = calculate_commercial_repatha_status(commercial)
    toc = time.perf_counter()
    logger.debug(f"get_commercial: refresh timer {toc - tic:0.4f} seconds NOT CACHED")
    return comm_permissions(commercial, page_permissions, key, True, agendaItemId)
