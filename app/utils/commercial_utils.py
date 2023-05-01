import re
import traceback
from ..loggerFactory import LoggerFactory
from ..dataHelper import DataHelper
from ..models.commercial_v2 import CommercialV2, SummaryInfo
from ..models.agenda_items_v2 import AgendaItem
from ..routes.agenda_items_v2 import get_agenda_item, User, update_agenda_item
from ..constant import Constant

logger = LoggerFactory.get_logger(__name__)


class CommUtils:
    def comm_permissions(
        commercial: CommercialV2,
        agendaItem: AgendaItem,
        page_permissions,
        key,
        cache,
        user,
    ):
        full_permissions = False
        if (
            page_permissions["supply"]
            and page_permissions["people"]
            and page_permissions["pipeline"]
            and page_permissions["brand"]
        ):
            full_permissions = True
        CommUtils.set_non_cached_data(commercial, agendaItem, full_permissions, user)
        if cache and full_permissions:
            logger.debug(f"comm_permissions: caching commercial object")
            DataHelper.cache_object(
                "commercial", key, [], "repatha_metrics.py", commercial
            )
            return commercial
        if not page_permissions["supply"]:
            commercial.supply.locations = []
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
            commercial.pipeline.projects = []
            logger.debug(
                f"comm_permissions: limiting commercial object response based on PIPELINE permissions"
            )
        if not page_permissions["brand"]:
            commercial.brand.salesDemandSections = []
            commercial.brand.idnAccountWins = None
            commercial.brand.nbrxFulfillment = None
            commercial.brand.nbrxVolume = None
            commercial.brand.psoBioNaiveShare = None
            commercial.brand.specPharmNbrxCommFulfillRate = None
            commercial.brand.copayEnrollmentRate = None
            commercial.brand.targetsAtFrequency = None
            commercial.brand.frequency = None
            commercial.brand.shareOfVoice = None
            logger.debug(
                f"comm_permissions: limiting commercial object response based on BRAND permissions"
            )
        return commercial

    def set_non_cached_data(
        commercial: CommercialV2, agendaItem: AgendaItem, full_permissions, user
    ):
        commercial.title = agendaItem.name
        commercial.owners = agendaItem.owners
        commercial.agendaItemId = agendaItem.agendaItemId

        # Check if we need to change agenda item
        commercial.summaryInfo = SummaryInfo()

        current_status = agendaItem.status
        new_status = CommUtils.calculate_commercial_status(commercial)
        commercial.summaryInfo.status = new_status

        logger.debug(
            f"current_status: {current_status} new_status: {new_status} full_permissions: {full_permissions}"
        )
        if current_status != new_status and full_permissions:
            commercial.summaryInfo.status = new_status
            agendaItem.status = commercial.summaryInfo.status
            agendaItem.statusReason = commercial.summaryInfo.reason
            update_agenda_item(agendaItem, user)
            True

        commercial.summaryInfo.scope = agendaItem.scope
        commercial.summaryInfo.keyInsights = agendaItem.keyInsights

        # DO NOT CACHE END

    def calculate_brand_status(commercial: CommercialV2):
        brand_sales_demand_overall_status = CommUtils.get_list_status(
            commercial.brand.salesDemandSections
        )
        if (
            brand_sales_demand_overall_status == Constant.PA_STATUS_RED
            or CommUtils.get_obj_status_str(commercial.brand.idnAccountWins)
            == Constant.PA_STATUS_RED
            or CommUtils.get_obj_status_str(commercial.brand.nbrxFulfillment)
            == Constant.PA_STATUS_RED
            or CommUtils.get_obj_status_str(commercial.brand.nbrxVolume)
            == Constant.PA_STATUS_RED
            or CommUtils.get_obj_status_str(commercial.brand.psoBioNaiveShare)
            == Constant.PA_STATUS_RED
            or CommUtils.get_obj_status_str(
                commercial.brand.specPharmNbrxCommFulfillRate
            )
            == Constant.PA_STATUS_RED
            or CommUtils.get_obj_status_str(commercial.brand.copayEnrollmentRate)
            == Constant.PA_STATUS_RED
            or CommUtils.get_obj_status_str(commercial.brand.targetsAtFrequency)
            == Constant.PA_STATUS_RED
            or CommUtils.get_obj_status_str(commercial.brand.frequency)
            == Constant.PA_STATUS_RED
            or CommUtils.get_obj_status_str(commercial.brand.shareOfVoice)
            == Constant.PA_STATUS_RED
        ):
            return Constant.PA_STATUS_RED
        elif (
            brand_sales_demand_overall_status == Constant.PA_STATUS_YELLOW
            or CommUtils.get_obj_status_str(commercial.brand.idnAccountWins)
            == Constant.PA_STATUS_YELLOW
            or CommUtils.get_obj_status_str(commercial.brand.nbrxFulfillment)
            == Constant.PA_STATUS_YELLOW
            or CommUtils.get_obj_status_str(commercial.brand.nbrxVolume)
            == Constant.PA_STATUS_YELLOW
            or CommUtils.get_obj_status_str(commercial.brand.psoBioNaiveShare)
            == Constant.PA_STATUS_YELLOW
            or CommUtils.get_obj_status_str(
                commercial.brand.specPharmNbrxCommFulfillRate
            )
            == Constant.PA_STATUS_YELLOW
            or CommUtils.get_obj_status_str(commercial.brand.copayEnrollmentRate)
            == Constant.PA_STATUS_YELLOW
            or CommUtils.get_obj_status_str(commercial.brand.targetsAtFrequency)
            == Constant.PA_STATUS_YELLOW
            or CommUtils.get_obj_status_str(commercial.brand.frequency)
            == Constant.PA_STATUS_YELLOW
            or CommUtils.get_obj_status_str(commercial.brand.shareOfVoice)
            == Constant.PA_STATUS_YELLOW
        ):
            return Constant.PA_STATUS_YELLOW
        elif (
            brand_sales_demand_overall_status == Constant.PA_STATUS_GREEN
            or CommUtils.get_obj_status_str(commercial.brand.idnAccountWins)
            == Constant.PA_STATUS_GREEN
            or CommUtils.get_obj_status_str(commercial.brand.nbrxFulfillment)
            == Constant.PA_STATUS_GREEN
            or CommUtils.get_obj_status_str(commercial.brand.nbrxVolume)
            == Constant.PA_STATUS_GREEN
            or CommUtils.get_obj_status_str(commercial.brand.psoBioNaiveShare)
            == Constant.PA_STATUS_GREEN
            or CommUtils.get_obj_status_str(
                commercial.brand.specPharmNbrxCommFulfillRate
            )
            == Constant.PA_STATUS_GREEN
            or CommUtils.get_obj_status_str(commercial.brand.copayEnrollmentRate)
            == Constant.PA_STATUS_GREEN
            or CommUtils.get_obj_status_str(commercial.brand.targetsAtFrequency)
            == Constant.PA_STATUS_GREEN
            or CommUtils.get_obj_status_str(commercial.brand.frequency)
            == Constant.PA_STATUS_GREEN
            or CommUtils.get_obj_status_str(commercial.brand.shareOfVoice)
            == Constant.PA_STATUS_GREEN
        ):
            return Constant.PA_STATUS_GREEN
        else:
            return Constant.PA_STATUS_GRAY

    def calculate_supply_status(commercial: CommercialV2):
        supply_loacations_overall_status = CommUtils.get_list_status(
            commercial.supply.locations
        )
        if (
            supply_loacations_overall_status == Constant.PA_STATUS_RED
            or CommUtils.get_obj_status_str(commercial.supply.cogsReduction)
            == Constant.PA_STATUS_RED
            or CommUtils.get_obj_status_str(commercial.supply.inventoryBelowTarget)
            == Constant.PA_STATUS_RED
        ):
            return Constant.PA_STATUS_RED
        elif (
            supply_loacations_overall_status == Constant.PA_STATUS_YELLOW
            or CommUtils.get_obj_status_str(commercial.supply.cogsReduction)
            == Constant.PA_STATUS_YELLOW
            or CommUtils.get_obj_status_str(commercial.supply.inventoryBelowTarget)
            == Constant.PA_STATUS_YELLOW
        ):
            return Constant.PA_STATUS_YELLOW
        elif (
            supply_loacations_overall_status == Constant.PA_STATUS_GREEN
            or CommUtils.get_obj_status_str(commercial.supply.cogsReduction)
            == Constant.PA_STATUS_GREEN
            or CommUtils.get_obj_status_str(commercial.supply.inventoryBelowTarget)
            == Constant.PA_STATUS_GREEN
        ):
            return Constant.PA_STATUS_GREEN
        else:
            return Constant.PA_STATUS_GRAY

    def calculate_people_status(commercial: CommercialV2):
        if (
            CommUtils.get_obj_status_str(commercial.people.engagementScore)
            == Constant.PA_STATUS_RED
            or CommUtils.get_obj_status_str(commercial.people.talentAcquisition)
            == Constant.PA_STATUS_RED
            or CommUtils.get_obj_status_str(commercial.people.turnover)
            == Constant.PA_STATUS_RED
        ):
            return Constant.PA_STATUS_RED
        elif (
            CommUtils.get_obj_status_str(commercial.people.engagementScore)
            == Constant.PA_STATUS_YELLOW
            or CommUtils.get_obj_status_str(commercial.people.talentAcquisition)
            == Constant.PA_STATUS_YELLOW
            or CommUtils.get_obj_status_str(commercial.people.turnover)
            == Constant.PA_STATUS_YELLOW
        ):
            return Constant.PA_STATUS_YELLOW
        elif (
            CommUtils.get_obj_status_str(commercial.people.engagementScore)
            == Constant.PA_STATUS_GREEN
            or CommUtils.get_obj_status_str(commercial.people.talentAcquisition)
            == Constant.PA_STATUS_GREEN
            or CommUtils.get_obj_status_str(commercial.people.turnover)
            == Constant.PA_STATUS_GREEN
        ):
            return Constant.PA_STATUS_GREEN
        else:
            return Constant.PA_STATUS_GRAY

    def calculate_commercial_status(commercial: CommercialV2) -> str:
        try:
            overall_brand_status = "gray"
            overall_pipeline_status = "gray"
            overall_supply_status = "gray"
            overall_people_status = "gray"

            overall_brand_status = CommUtils.calculate_brand_status(commercial)
            overall_pipeline_status = CommUtils.get_list_status(
                commercial.pipeline.projects
            )
            overall_supply_status = CommUtils.calculate_supply_status(commercial)
            overall_people_status = CommUtils.calculate_people_status(commercial)

            if (
                overall_brand_status == Constant.PA_STATUS_RED
                or overall_pipeline_status == Constant.PA_STATUS_RED
                or overall_supply_status == Constant.PA_STATUS_RED
                or overall_people_status == Constant.PA_STATUS_RED
            ):
                CommUtils.set_status_reason_commercial(
                    commercial,
                    overall_brand_status,
                    overall_pipeline_status,
                    overall_supply_status,
                    overall_people_status,
                    Constant.PA_STATUS_RED,
                )
                return Constant.PA_STATUS_RED
            if (
                overall_brand_status == Constant.PA_STATUS_YELLOW
                or overall_pipeline_status == Constant.PA_STATUS_YELLOW
                or overall_supply_status == Constant.PA_STATUS_YELLOW
                or overall_people_status == Constant.PA_STATUS_YELLOW
            ):
                CommUtils.set_status_reason_commercial(
                    commercial,
                    overall_brand_status,
                    overall_pipeline_status,
                    overall_supply_status,
                    overall_people_status,
                    Constant.PA_STATUS_RED,
                )
                return Constant.PA_STATUS_YELLOW
            if (
                overall_brand_status == Constant.PA_STATUS_GRAY
                and overall_pipeline_status == Constant.PA_STATUS_GRAY
                and overall_supply_status == Constant.PA_STATUS_GRAY
                and overall_people_status == Constant.PA_STATUS_GRAY
            ):
                CommUtils.set_status_reason_commercial(
                    commercial,
                    overall_brand_status,
                    overall_pipeline_status,
                    overall_supply_status,
                    overall_people_status,
                    Constant.PA_STATUS_RED,
                )
                return Constant.PA_STATUS_GRAY
            commercial.summaryInfo.reason = (
                " Brand, Pipeline, Supply and People metrics."
            )
            return Constant.PA_STATUS_GREEN
        except:
            logger.debug(traceback.print_exc())
            commercial.summaryInfo.reason = " an error occurred calculating the status or you do not have permissions to calculate status"
            return Constant.PA_STATUS_GRAY

    def set_status_reason_commercial(
        commercial: CommercialV2,
        overall_brand_status: str,
        overall_pipeline_status: str,
        overall_supply_status: str,
        overall_people_status: str,
        status: str,
    ):
        commercial.summaryInfo.reason = ""
        if overall_brand_status == status:
            commercial.summaryInfo.reason = commercial.summaryInfo.reason + " Brand,"
        if overall_pipeline_status == status:
            commercial.summaryInfo.reason = commercial.summaryInfo.reason + " Pipeline,"
        if overall_supply_status == status:
            commercial.summaryInfo.reason = commercial.summaryInfo.reason + " Supply,"

        if overall_people_status == status:
            commercial.summaryInfo.reason = commercial.summaryInfo.reason + " People,"

        commercial.summaryInfo.reason = commercial.summaryInfo.reason[
            0 : len(commercial.summaryInfo.reason) - 1
        ]
        if commercial.summaryInfo.reason.count(",") > 0:
            old = ","
            new = " and"
            maxreplace = 1
            commercial.summaryInfo.reason = new.join(
                commercial.summaryInfo.reason.rsplit(old, maxreplace)
            )
        commercial.summaryInfo.reason = commercial.summaryInfo.reason + " metrics."

    def get_list_status(status_list: list):
        one_green = False
        for item in status_list:
            if item.status == "red":
                return "red"
            elif item.status == "yellow":
                return "yellow"
            elif item.status == "green":
                one_green = True

        if one_green:
            return "green"
        return "gray"

    def get_obj_status_str(obj):
        if obj is None:
            return "gray"
        else:
            return obj.status
