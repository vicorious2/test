import requests
import os
from ..dataHelper import DataHelper
from ..constant import Constant

from fastapi import APIRouter, Depends, HTTPException

from ..AuthUtil import is_authorized, get_page_permissions
from ..loggerFactory import LoggerFactory
from ..routes.agenda_items_v2 import get_agenda_item
from ..models.common import Owners

logger = LoggerFactory.get_logger(__name__)

from ..utils.agenda_items_utils_v2 import (
    calculate_pipline_status,
)
from app.models.pipeline import (
    CriticalToolTip,
    NextPriorityLaunch,
    NextPriorityMilestone,
    NextToolTip,
    PriorityCriticalPathStudyEnrollmenP,
    Pipeline,
)

from ..routes.agenda_items_v2 import get_agenda_item

router = APIRouter(
    prefix="/api",
    tags=["Pipeline Metrics"],
    dependencies=[Depends(is_authorized)],
    responses={403: {"description": "Not found"}},
)

env = os.getenv("PA_ENV", "not found")

env_brand = ""
env_people = ""
env_pipline = env  # currently not used
env_supply = ""
envAlt = ""

if env == "dev":
    envAlt = "-dev"
elif env == "test":
    envAlt = "-test"
elif env == "staging":
    envAlt = "-stg"
elif env == "rts":
    envAlt = ""


def get_key_products_csp_current_month(token, name) -> any:
    headers = {
        "Authorization": "Bearer " + token.credentials,
        "content-type": "application/json",
    }
    logger.debug(f"get_key_products_csp_current_month: getting csp for {name}")
    response = requests.get(
        f"https://pipeline-api-{os.environ['PA_ENV']}.nimbus.amgen.com/api/v1/key_products/csp_current_month"
        + "?name="
        + name,
        headers=headers,
    )
    j = response.json()
    # response_obj = pipeline_key_products_csp_current_month_data.parse_obj(response.json())
    return j


def get_key_products_ipp_pub(token) -> any:
    headers = {
        "Authorization": "Bearer " + token.credentials,
        "content-type": "application/json",
    }
    response = requests.get(
        f"https://pipeline-api-{os.environ['PA_ENV']}.nimbus.amgen.com/api/v1/key_products/ipp_pub",
        headers=headers,
    )
    j = response.json()
    return j


def get_key_products_tpp(token, name) -> any:
    headers = {
        "Authorization": "Bearer " + token.credentials,
        "content-type": "application/json",
    }
    response = requests.get(
        f"https://pipeline-api-{os.environ['PA_ENV']}.nimbus.amgen.com/api/v1/product/tpp"
        + "?name="
        + name,
        headers=headers,
    )
    j = response.json()
    return j


def get_agenda_items(token) -> any:
    headers = {
        "Authorization": "Bearer " + token.credentials,
        "content-type": "application/json",
    }
    response = requests.get(
        f"https://prioritized-agenda-api-{os.environ['PA_ENV']}.nimbus.amgen.com/api/v1/agenda_items"
        + "?is_active=true",
        headers=headers,
    )
    j = response.json()
    return j


def get_next_priority_launch(
    ipp_pub: any, next_priority_launch: NextPriorityLaunch
) -> NextPriorityLaunch:

    next_priority_launch.e2lIppShortName = ipp_pub["e2l_ipp_short_name"]
    next_priority_launch.e2lLauDate = ipp_pub["e2l_lau_date"]
    next_priority_launch.e2lLauDateVariance = abs(int(ipp_pub["e2l_lau_date_variance"]))
    next_priority_launch.e2lLauDesc = ipp_pub["e2l_lau_desc"]
    next_priority_launch.e2lLauStatus = ipp_pub["e2l_lau_status"]
    next_priority_launch.e2lSnapDate = ipp_pub["e2l_snap_date"]
    next_priority_launch.e2lTransitionDateReason = ipp_pub["e2l_transition_date_reason"]

    tool_tip_launch = NextToolTip()
    tool_tip_launch.varianceDays = abs(int(ipp_pub["e2l_lau_date_variance"]))
    tool_tip_launch.baselineDate = ipp_pub["e2l_snap_date"]
    tool_tip_launch.reason = ipp_pub["e2l_ipp_short_name"]
    next_priority_launch.tooltip = tool_tip_launch

    return next_priority_launch


def get_next_milestone(
    ipp_pub: any, next_priority_milestone: NextPriorityMilestone
) -> NextPriorityMilestone:

    tool_tip_milestone = NextToolTip()
    tool_tip_milestone.varianceDays = abs(int(ipp_pub["nkm_date_variance"]))
    tool_tip_milestone.baselineDate = ipp_pub["nkm_snap_date"]
    tool_tip_milestone.reason = ipp_pub["nkm_study_short_description"]

    next_priority_milestone.nkmDate = ipp_pub["nkm_date"]
    next_priority_milestone.nkmDateVariance = abs(int(ipp_pub["nkm_date_variance"]))
    next_priority_milestone.nkmDescription = ipp_pub["nkm_description"]
    next_priority_milestone.nkmMilestoneShortName = ipp_pub["nkm_milestone_short_name"]
    next_priority_milestone.nkmSnapDate = ipp_pub["nkm_snap_date"]
    next_priority_milestone.nkmStatus = ipp_pub["nkm_status"]
    next_priority_milestone.nkmTransitionDateReason = ipp_pub[
        "nkm_transition_date_reason"
    ]
    next_priority_milestone.nkmStudyShortDescription = ipp_pub[
        "nkm_study_short_description"
    ]

    next_priority_milestone.tooltip = tool_tip_milestone

    return next_priority_milestone


def get_critical_path_study(current_month: any):

    priorities_critial_paths = []
    for e in current_month:
        priority_critial_path = PriorityCriticalPathStudyEnrollmenP()
        critical = CriticalToolTip()
        priority_critial_path.study = e["study_short_description"]
        priority_critial_path.fseDate = e["fse_date"]

        critical.study = e["study_short_description"]
        critical.studyNumber = e["ipp_study_number"]
        try:
            critical.lastMonthPctEnr = float(e["perc_to_plan_subject_enrollment"])
        except:
            pass
        try:
            critical.lastMonthActualEnr = e["actual_cumulative_subjects_enrolled"]
        except:
            pass
        try:
            critical.lastMonthPlanEnr = e["latest_planned_cumulative_subjects_enrolled"]
        except:
            pass

        priority_critial_path.enrStatus = e["enr_status"]
        if priority_critial_path.enrStatus == "pending subject enrollment":
            priority_critial_path.enrStatus = "enrollment not started"
        priority_critial_path.tooltip = critical
        priorities_critial_paths.append(priority_critial_path)

    return priorities_critial_paths


def calculate_ceo_owner(tpp: any, ipp_pub: any) -> Owners:
    owners = Owners()
    ceoStaffSponsor = []
    operatingTeamOwner = []
    for f in tpp:
        if f["ceo_staff_sponsor"]:
            ceoStaffSponsor.append(f["ceo_staff_sponsor"])
        if f["operating_team_owner"]:
            operatingTeamOwner.append(f["operating_team_owner"])

    ceoStaffSponsor = set(ceoStaffSponsor)
    operatingTeamOwner = set(operatingTeamOwner)

    for c in ceoStaffSponsor:
        owners.ceoStaffSponsors.append(c)

    operatingTeamOwnerStr = ""
    for c in operatingTeamOwner:
        owners.operatingTeamOwners.append(c)

    owners.operatingTeamOwner = operatingTeamOwnerStr

    return owners


@router.get("/v1/pipeline")
def get_pipeline_by_id(agendaItemId: int = 0, token=Depends(is_authorized)):
    logger.debug(f"get_pipeline_by_id: getting agenda item")
    if not get_page_permissions(token.credentials)["pipeline"]:
        raise HTTPException(status_code=403)
    pipeline = Pipeline()
    agenda_item = get_agenda_item(agendaItemId)
    # todo check Architype
    product = agenda_item.archetypeLinkId.lower()
    key = f"{Constant.REDIS_KEY_PREFIX}__pipeline__agendaItemId_" + str(agendaItemId)
    data = DataHelper.get_cached_object("pipeline", key, [], "pipeline.py")
    if data:
        pipeline = data
        pipeline.statusReason = agenda_item.statusReason
        pipeline.keyInsights = agenda_item.keyInsights
        pipeline.scope = agenda_item.scope
        return pipeline
    logger.debug(f"get_pipeline_by_id: {product} is not cached going to ipp_pub")
    ipp_pub = get_key_products_ipp_pub(token)
    ipp_pub_product = ""
    tpp = []
    current_month = []
    priorities_critial_paths = []
    owners = Owners()
    owners.ceoStaffSponsors = []
    owners.operatingTeamOwners = []
    next_priority_milestone = NextPriorityMilestone()
    next_priority_launch = NextPriorityLaunch()

    for d in ipp_pub:
        if d["product"].lower() == product:

            ipp_pub_product = d["product"]
            logger.debug(f"get_pipeline_by_id: found {product} setting values")
            names = d["names"]
            pipeline.title = d["ipp_short_name"]
            tpp = get_key_products_tpp(token, names)
            ceoStaffSponsor = []
            operatingTeamOwner = []
            for f in tpp:
                if f["ceo_staff_sponsor"]:
                    ceoStaffSponsor.append(f["ceo_staff_sponsor"])
                if f["operating_team_owner"]:
                    operatingTeamOwner.append(f["operating_team_owner"])

            ceoStaffSponsor = set(ceoStaffSponsor)
            operatingTeamOwner = set(operatingTeamOwner)

            for c in ceoStaffSponsor:
                owners.ceoStaffSponsors.append(c)

            for c in operatingTeamOwner:
                owners.operatingTeamOwners.append(c)

            current_month = get_key_products_csp_current_month(token, names)

            next_priority_launch.e2lIppShortName = d["e2l_ipp_short_name"]
            next_priority_launch.e2lLauDate = d["e2l_lau_date"]
            next_priority_launch.e2lLauDateVariance = abs(
                int(d["e2l_lau_date_variance"])
            )
            next_priority_launch.e2lLauDesc = d["e2l_lau_desc"]
            next_priority_launch.e2lLauStatus = d["e2l_lau_status"]
            next_priority_launch.e2lSnapDate = d["e2l_snap_date"]
            next_priority_launch.e2lTransitionDateReason = d[
                "e2l_transition_date_reason"
            ]

            tool_tip_launch = NextToolTip()
            tool_tip_launch.varianceDays = abs(int(d["e2l_lau_date_variance"]))
            tool_tip_launch.baselineDate = d["e2l_snap_date"]
            if d["e2l_transition_date_reason"]:
                tool_tip_launch.reason = d["e2l_transition_date_reason"]
            else:
                tool_tip_launch.reason = "Missing Reason"

            next_priority_launch.tooltip = tool_tip_launch

            tool_tip_milestone = NextToolTip()

            # next_priority_launch status
            if (
                str(d["e2l_lau_status"]) == "Off Track"
                or str(d["e2l_lau_status"]) == "Delayed"
            ):
                next_priority_launch.status = "red"
            elif str(d["e2l_lau_status"]).lower() == "subject to change":
                next_priority_launch.status = "yellow"
            else:
                next_priority_launch.status = "green"

            # next_priority_milestone status
            if str(d["nkm_status"]) == "Off Track" or str(d["nkm_status"]) == "Delayed":
                next_priority_milestone.status = "red"
            elif str(d["nkm_status"]).lower() == "subject to change":
                next_priority_milestone.status = "yellow"
            else:
                next_priority_milestone.status = "green"

            if d["nkm_date_variance"]:
                tool_tip_milestone.varianceDays = abs(int(d["nkm_date_variance"]))
                next_priority_milestone.nkmDateVariance = abs(
                    int(d["nkm_date_variance"])
                )
            else:
                tool_tip_milestone.varianceDays = 0
                next_priority_milestone.nkmDateVariance = 0

            tool_tip_milestone.baselineDate = d["nkm_snap_date"]

            if d["nkm_study_short_description"]:
                next_priority_milestone.nkmStudyShortDescription = d[
                    "nkm_study_short_description"
                ]
            else:
                next_priority_milestone.nkmStudyShortDescription = ""

            if d["nkm_transition_date_reason"]:
                tool_tip_milestone.reason = d["nkm_transition_date_reason"]
            else:
                tool_tip_milestone.reason = "Missing Reason"

            next_priority_milestone.nkmDate = d["nkm_date"]
            next_priority_milestone.nkmDescription = d["nkm_description"]
            next_priority_milestone.nkmMilestoneShortName = d[
                "nkm_milestone_short_name"
            ]
            next_priority_milestone.nkmSnapDate = d["nkm_snap_date"]
            next_priority_milestone.nkmStatus = d["nkm_status"]
            next_priority_milestone.nkmTransitionDateReason = d[
                "nkm_transition_date_reason"
            ]

            next_priority_milestone.tooltip = tool_tip_milestone

            for e in current_month:
                priority_critial_path = PriorityCriticalPathStudyEnrollmenP()
                critical = CriticalToolTip()
                priority_critial_path.study = e["study_short_description"]
                priority_critial_path.fseDate = e["fse_date"]

                critical.study = e["study_short_description"]
                critical.studyNumber = e["ipp_study_number"]
                try:
                    critical.lastMonthPctEnr = float(
                        e["perc_to_plan_subject_enrollment"]
                    )
                except:
                    pass
                try:
                    critical.lastMonthActualEnr = e[
                        "actual_cumulative_subjects_enrolled"
                    ]
                except:
                    pass
                try:
                    critical.lastMonthPlanEnr = e[
                        "latest_planned_cumulative_subjects_enrolled"
                    ]
                except:
                    pass

                priority_critial_path.enrStatus = e["enr_status"]
                if priority_critial_path.enrStatus == "pending subject enrollment":
                    priority_critial_path.enrStatus = "enrollment not started"
                priority_critial_path.tooltip = critical
                priorities_critial_paths.append(priority_critial_path)
                # break

    pipeline.agendaItemId = agendaItemId
    pipeline.href = (
        f"https://sensing{envAlt}.nimbus.amgen.com/pipeline?key-products="
        + ipp_pub_product.replace(" ", "+")
    )
    pipeline.owners = owners
    pipeline.nextLaunch = next_priority_launch
    pipeline.nextMilestone = next_priority_milestone
    pipeline.criticalPathStudy = priorities_critial_paths
    logger.debug(f"get_pipeline_by_id: pre-calc status")
    pipeline.status = calculate_pipline_status(pipeline)
    pipeline.statusReason = agenda_item.statusReason
    pipeline.keyInsights = agenda_item.keyInsights
    pipeline.scope = agenda_item.scope
    logger.debug(f"get_pipeline_by_id: post-calc status")
    DataHelper.cache_object("pipeline", key, [], "pipeline.py", pipeline)
    return pipeline
