import time
from fastapi import APIRouter, Depends, HTTPException

from ..AuthUtil import is_authorized, get_page_permissions, get_user_name_and_email
from ..loggerFactory import LoggerFactory

# Import Models
from ..models.brand import (
    Brand,
    BasicTooltip,
    BasicTooltipSection,
    BasicTooltipRow,
    IdnAccountWins,
    ShareOfVoice,
    PsoBioNaiveShare,
    SpecPharmNbrxCommFulfillRate,
    CopayEnrollmentRate,
    TargetsAtFrequency,
    Frequency,
)
from ..models.agenda_items_v2 import User
from ..models.pipeline import CommercialPipeline
from ..models.commercial import Commercial
from ..models.people import People
from ..models.supply import Supply, CogsReduction
from ..models.common import SummaryInfo
from ..models.commercial_v2 import CommercialV2, PeopleTemp, SupplyTemp
from ..utils.brand_utils import BrandUtils, get_otezla_hover_data
from ..utils.pipeline_utils import PipelineUtils
from ..utils.supply_utils import SupplyUtils
from ..routes.agenda_items_v2 import get_agenda_item
from ..utils.people_utils import PeopleUtils
from ..constant import Constant
from ..dataHelper import DataHelper
from ..utils.commercial_utils import CommUtils


router = APIRouter(
    prefix="/api",
    tags=["Commercial Metrics"],
)

logger = LoggerFactory.get_logger(__name__)


@router.get("/v2/commercial")
def get_commercial(agendaItemId: int = 0, token=Depends(is_authorized)):
    tic = time.perf_counter()
    logger.debug(f"get_commercial V2: start")
    page_permissions = get_page_permissions(token.credentials)
    if (
        not page_permissions["supply"]
        and not page_permissions["people"]
        and not page_permissions["pipeline"]
        and not page_permissions["brand"]
    ):
        raise HTTPException(status_code=403)

    # Start
    agendaItem = get_agenda_item(agendaItemId)
    if agendaItem.archetype != "Commercial":
        raise HTTPException(
            status_code=400,
            detail=f"Not Commercial type",
        )
    if not agendaItem.archetypeLinkId:
        raise HTTPException(
            status_code=400,
            detail=f"Lind ID is missing",
        )
    user = User()
    user = get_user_name_and_email(token)

    key = f"{Constant.REDIS_KEY_PREFIX}__commercial_V2__" + str(agendaItemId)
    data = DataHelper.get_cached_object("commercial", key, [], "repatha_metrics.py")
    if data:
        toc = time.perf_counter()
        logger.debug(f"get_commercial: refresh timer {toc - tic:0.4f} seconds CACHED")
        return CommUtils.comm_permissions(
            data, agendaItem, page_permissions, key, False, user
        )

    commercial = CommercialV2()
    brand = Brand()
    supply = Supply()
    supply.locations = []
    data_net_sales = ""
    data_nbrx_demand = ""
    data_trx_demand = ""

    if agendaItem.archetypeLinkId == "Otezla":
        tooltip_data = get_otezla_hover_data(token=token, data={"brand_name": "OTEZLA"})
        data_net_sales = {"brand_name": "OTEZLA"}
        data_nbrx_demand = {
            "brand_name": "OTEZLA",
            "brand_type": "nbrx",
            "speciality_group": "DERM",
        }
        data_trx_demand = {
            "brand_name": "OTEZLA",
            "brand_type": "trx",
            "speciality_group": "DERM",
        }
        brand.psoBioNaiveShare = PsoBioNaiveShare()
        psoBioNaiveShare_tt = BasicTooltip()
        psoBioNaiveShare_tt.sections = []

        psoBioNaiveShare_tt_section = BasicTooltipSection()
        psoBioNaiveShare_tt_section.rows = []

        psoBioNaiveShare_tt_ds = BasicTooltipRow()
        psoBioNaiveShare_tt_ds.label = "Data Source:"
        psoBioNaiveShare_tt_ds.text = (
            tooltip_data.us_leading.pso_bio_naive_share.Refresh_Freequency
        )

        psoBioNaiveShare_tt_rf = BasicTooltipRow()
        psoBioNaiveShare_tt_rf.label = "Refresh Frequency:"
        psoBioNaiveShare_tt_rf.text = (
            tooltip_data.us_leading.pso_bio_naive_share.Refresh_Freequency
        )

        psoBioNaiveShare_tt_section.rows.append(psoBioNaiveShare_tt_ds)
        psoBioNaiveShare_tt_section.rows.append(psoBioNaiveShare_tt_rf)

        psoBioNaiveShare_tt.sections.append(psoBioNaiveShare_tt_section)

        brand.psoBioNaiveShare.tooltip = psoBioNaiveShare_tt

        brand.specPharmNbrxCommFulfillRate = SpecPharmNbrxCommFulfillRate()

        specPharmNbrxCommFulFillRate_tt = BasicTooltip()
        specPharmNbrxCommFulFillRate_tt.sections = []

        specPharmNbrxCommFulFillRate_tt_section = BasicTooltipSection()
        specPharmNbrxCommFulFillRate_tt_section.rows = []

        specPharmNbrxCommFulFillRate_tt_ds = BasicTooltipRow()
        specPharmNbrxCommFulFillRate_tt_ds.label = "Data Source:"
        specPharmNbrxCommFulFillRate_tt_ds.text = (
            tooltip_data.us_leading.nbrx_fulfillment.Data_Source
        )

        specPharmNbrxCommFulFillRate_tt_rf = BasicTooltipRow()
        specPharmNbrxCommFulFillRate_tt_rf.label = "Refresh Frequency:"
        specPharmNbrxCommFulFillRate_tt_rf.text = (
            tooltip_data.us_leading.nbrx_fulfillment.Refresh_Freequency
        )

        specPharmNbrxCommFulFillRate_tt_section.rows.append(
            specPharmNbrxCommFulFillRate_tt_ds
        )
        specPharmNbrxCommFulFillRate_tt_section.rows.append(
            specPharmNbrxCommFulFillRate_tt_rf
        )

        specPharmNbrxCommFulFillRate_tt.sections.append(
            specPharmNbrxCommFulFillRate_tt_section
        )

        brand.specPharmNbrxCommFulfillRate.tooltip = specPharmNbrxCommFulFillRate_tt

        brand.copayEnrollmentRate = CopayEnrollmentRate()

        copayEnrollmentRate_tt = BasicTooltip()
        copayEnrollmentRate_tt.sections = []

        copayEnrollmentRate_tt_section = BasicTooltipSection()
        copayEnrollmentRate_tt_section.rows = []

        copayEnrollmentRate_tt_ds = BasicTooltipRow()
        copayEnrollmentRate_tt_ds.label = "Data Source:"
        copayEnrollmentRate_tt_ds.text = (
            tooltip_data.us_leading.copay_penetration.Data_Source
        )

        copayEnrollmentRate_tt_rf = BasicTooltipRow()
        copayEnrollmentRate_tt_rf.label = "Refresh Frequency:"
        copayEnrollmentRate_tt_rf.text = (
            tooltip_data.us_leading.copay_penetration.Refresh_Freequency
        )

        copayEnrollmentRate_tt_section.rows.append(copayEnrollmentRate_tt_ds)
        copayEnrollmentRate_tt_section.rows.append(copayEnrollmentRate_tt_rf)

        copayEnrollmentRate_tt.sections.append(specPharmNbrxCommFulFillRate_tt_section)

        brand.copayEnrollmentRate.tooltip = copayEnrollmentRate_tt

        brand.targetsAtFrequency = TargetsAtFrequency()
        brand.frequency = Frequency()

        brand.shareOfVoice = ShareOfVoice()
        shareOfVoice_tt = BasicTooltip()
        shareOfVoice_tt.sections = []

        shareOfVoice_tt_section = BasicTooltipSection()
        shareOfVoice_tt_section.rows = []

        shareOfVoice_tt_ds = BasicTooltipRow()
        shareOfVoice_tt_ds.label = "Data Source:"
        shareOfVoice_tt_ds.text = tooltip_data.us_execution.share_of_voice.Data_Source

        shareOfVoice_tt_rf = BasicTooltipRow()
        shareOfVoice_tt_rf.label = "Refresh Frequency:"
        shareOfVoice_tt_rf.text = (
            tooltip_data.us_execution.share_of_voice.Refresh_Freequency
        )

        shareOfVoice_tt_section.rows.append(shareOfVoice_tt_ds)
        shareOfVoice_tt_section.rows.append(shareOfVoice_tt_rf)

        shareOfVoice_tt.sections.append(specPharmNbrxCommFulFillRate_tt_section)

        brand.shareOfVoice.tooltip = shareOfVoice_tt

    elif agendaItem.archetypeLinkId == "Repatha":
        data_net_sales = {"brand_name": "REPATHA"}
        data_nbrx_demand = {
            "brand_name": "REPATHA",
            "brand_type": "nbrx",
            "speciality_group": "",
        }
        data_trx_demand = {
            "brand_name": "REPATHA",
            "brand_type": "trx",
            "speciality_group": "",
        }
        data_nbrx_volume_by_specialties = {"brand_name": "REPATHA"}
        data_nbrx_fulfillment = {"brand_name": "REPATHA"}
        brand.idnAccountWins = IdnAccountWins()
        brand.shareOfVoice = ShareOfVoice()
        brand.nbrxFulfillment = BrandUtils.get_nbrx_fulfillment(
            data_nbrx_fulfillment, agendaItem.archetypeLinkId, token
        )
        brand.nbrxVolume = BrandUtils.get_nbrx_volume_by_specialties(
            data_nbrx_volume_by_specialties, agendaItem.archetypeLinkId, token
        )
        supply.locations = SupplyUtils.get_supply_locations(token)
        supply.cogsReduction = CogsReduction()

    brand.salesDemandSections = []
    net_sales = BrandUtils.get_commercial_brand_sales_demand_section(
        "Net Sales", agendaItem.archetypeLinkId, data_net_sales, token
    )
    if net_sales:
        brand.salesDemandSections.append(net_sales)

    nbrx_demand = BrandUtils.get_commercial_brand_sales_demand_section(
        "NBRx Demand", agendaItem.archetypeLinkId, data_nbrx_demand, token
    )
    if nbrx_demand:
        brand.salesDemandSections.append(nbrx_demand)
    trx_demand = BrandUtils.get_commercial_brand_sales_demand_section(
        "TRx Demand", agendaItem.archetypeLinkId, data_trx_demand, token
    )
    if nbrx_demand:
        brand.salesDemandSections.append(trx_demand)

    commercial.brand = brand

    commercial.pipeline = PipelineUtils.get_pipeline_metrics(
        token, agendaItem.archetypeLinkId
    )

    supply.inventoryBelowTarget = SupplyUtils.get_supply_InventoryBelowTarget(
        token, agendaItem.archetypeLinkId
    )
    commercial.supply = supply
    commercial.people = PeopleUtils.get_people_metrics(
        token, agendaItem.archetypeLinkId
    )

    toc = time.perf_counter()
    logger.debug(f"get_commercial: refresh timer {toc - tic:0.4f} seconds NOT CACHED")
    return CommUtils.comm_permissions(
        commercial, agendaItem, page_permissions, key, True, user
    )
