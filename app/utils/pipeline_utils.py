from ..loggerFactory import LoggerFactory
import requests
import os
from ..models.common import Owners, ExternalLink
from ..models.pipeline import (
    CommercialPipeline,
    CommercialPipelineProject,
    CommercialPipelineProjectSection,
    CommercialPipelineStatusTooltip,
)
import traceback
from ..dataHelper import DataHelper
from ..constant import Constant
from ..files import read_file


logger = LoggerFactory.get_logger(__name__)
env = os.getenv("PA_ENV", "not found")


env_pipline = ""

env_pipline_href = ""

if env == "dev" or env == "test":
    env_pipline = "api-" + env
    env_pipline_href = "-" + env
elif env == "staging":
    env_pipline = "api-stg"
    env_pipline_href = "-stg"
elif env == "rts":
    env_pipline = "api"


class PipelineUtils:
    def get_project_details(token, name):
        logger.debug(f"Pipeline get_project_details: start")
        try:
            whereStr = ""
            oderByStr = "order by end_date_current_approved_cab"

            if name == "Otezla":
                whereStr = """and ipp_pub.name in ('5438070.02','5438139.01','5438069.09')
                        and i.activity_type in ('BLA/NDA APP','MA_SUB_DATE_US','PRI_AN_FLASH', 
                        'FLASH_MEMO','INT_AN_FLASH','MA_SUB_DATE_US_COND', 
                        'MA_SUB_DATE_EX_US_COND', 'MA_SUB_DATE_US', 'MA_SUB_DATE_EX_US',
                        'LAU_US', 'LAU_EU','E2L_PORTAL','LAU_OTHER'))"""
            if name == "Repatha":
                whereStr = """and ipp_pub.name in ('5193088.09')
                        and i.activity_type in ('BLA/NDA APP','MA_SUB_DATE_US','PRI_AN_FLASH', 
                        'FLASH_MEMO','INT_AN_FLASH','MA_SUB_DATE_US_COND', 
                        'MA_SUB_DATE_EX_US_COND', 'MA_SUB_DATE_US', 'MA_SUB_DATE_EX_US',
                        'LAU_US', 'LAU_EU','E2L_PORTAL','LAU_OTHER'))"""

            key = f"{Constant.REDIS_KEY_PREFIX}__get_project_details__" + name
            j = DataHelper.get_data(
                "get_pipeline_metrics",
                key,
                read_file(Constant.COMMERCIAL_PIPELINE_DYNAMIC_SQL)
                + whereStr
                + oderByStr,
                [],
                "pipeline_utils.py",
            )

            return j
        except Exception:
            logger.debug(traceback.print_exc())
            return None

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

    def create_tooltip(ms):
        tooltip = CommercialPipelineStatusTooltip()
        tooltip.varianceDays = int(ms["date_variance"])
        tooltip.baselineDate = ms["snap_date"]  # Is this right?
        tooltip.reason = ms["transition_date_reason"]
        tooltip.dataSource = "Mercury"  # Not sure what this is
        return tooltip

    def create_section(title, ms):
        section = CommercialPipelineProjectSection()
        section.title = title
        section.textLines = [
            ms["study_short_description"].strip(),
            ms["geographic_area"] + " " + ms["milestone_short_name"],
        ]
        section.date = ms["end_date_current_approved_cab"]
        section.status = ms["milestone_status"].lower()
        section.statusTooltip = PipelineUtils.create_tooltip(ms)
        return section

    def get_pipeline_metrics(token, name):

        try:
            logger.debug(f"Pipeline get_pipeline_metrics: start")
            pipeline = CommercialPipeline()
            pipeline.projects = []
            external_link = ExternalLink()
            external_link.label = "GO TO MERCURY"
            external_link.isSensingExternal = True

            if name == "Repatha":
                project = CommercialPipelineProject()
                project.title = "VESALIUS-CV"
                project.sections = []
                project.externalLinks = []
                owners = Owners()
                owners.ceoStaffSponsors = []
                owners.operatingTeamOwners = []

                external_link.href = f"https://portfolio-analytics.amgen.com/dashboard/program-level?Product=Repatha&Prioritized%20Agenda%20Toggle=Entire%20Portfolio&Project=Repatha%20VESALIUS%20CV"
                project.externalLinks.append(external_link)

                pm = PipelineUtils.get_key_products_tpp(token, "5193088.09")

                if len(pm) == 0:
                    project.owners = None
                else:
                    owners.ceoStaffSponsors.append(pm[0]["ceo_staff_sponsor"])
                    owners.operatingTeamOwners.append(pm[0]["operating_team_owner"])
                    project.owners = owners

                j = PipelineUtils.get_project_details(token, name)

                npmSet = nfSet = nalSet = False
                next_priority_milestone_section = None
                next_filing_section = None
                next_approval_or_launch_section = None
                for ms in j:
                    if (
                        ms["activity_type"]
                        in ["PRI_AN_FLASH", "FLASH_MEMO", "INT_AN_FLASH"]
                        and not npmSet
                    ):
                        npmSet = True
                        next_priority_milestone_section = PipelineUtils.create_section(
                            "NEXT PRIORITY STUDY MILESTONE", ms
                        )

                    if ms["activity_type"] in ["MA_SUB_DATE_US"] and not nfSet:
                        nfSet = True
                        next_filing_section = PipelineUtils.create_section(
                            "NEXT FILING", ms
                        )

                    if ms["activity_type"] in ["BLA/NDA APP"] and not nalSet:
                        nalSet = True
                        next_approval_or_launch_section = PipelineUtils.create_section(
                            "NEXT APPROVAL OR LAUNCH", ms
                        )

                if next_approval_or_launch_section:
                    project.sections.append(next_approval_or_launch_section)

                if next_filing_section:
                    project.sections.append(next_filing_section)

                if next_priority_milestone_section:
                    project.sections.append(next_priority_milestone_section)

                pipeline.projects.append(project)

            if name == "Otezla":
                j = PipelineUtils.get_project_details(token, name)

                for projectCode in ["5438070.02", "5438139.01", "5438069.09"]:
                    project = CommercialPipelineProject()
                    project.sections = []
                    project.externalLinks = []
                    owners = Owners()
                    owners.ceoStaffSponsors = []
                    owners.operatingTeamOwners = []

                    pm = PipelineUtils.get_key_products_tpp(token, projectCode)

                    if len(pm) == 0:
                        project.owners = None
                    else:
                        owners.ceoStaffSponsors.append(pm[0]["ceo_staff_sponsor"])
                        owners.operatingTeamOwners.append(pm[0]["operating_team_owner"])
                        project.owners = owners

                    pm = PipelineUtils.get_key_products_tpp(token, projectCode)

                    if projectCode == "5438070.02":
                        project.title = "Pediatric Plaque Psoriasis (Peds Plaque PsO)"
                        external_link.href = "https://portfolio-analytics.amgen.com/dashboard/program-level?Product=Otezla&Prioritized%20Agenda%20Toggle=Entire%20Portfolio&Project=Otezla%20PsO%20%5C(Peds%20Plaque%5C)"
                    elif projectCode == "5438139.01":
                        project.title = "Daily Dosing (QD)"
                        external_link.href = "https://portfolio-analytics.amgen.com/dashboard/program-level?Product=Otezla&Prioritized%20Agenda%20Toggle=Entire%20Portfolio&Project=Otezla%20Daily%20Dosing"
                    elif projectCode == "5438069.09":
                        project.title = "Japan Palmoplantar Pustulosis (PPP)"
                        external_link.href = "https://portfolio-analytics.amgen.com/dashboard/program-level?Product=Otezla&Prioritized%20Agenda%20Toggle=Entire%20Portfolio&Project=Otezla%20PsO%20%5C(Peds%20Plaque%5C)"

                    project.externalLinks.append(external_link)
                    nfSet = nalSet = False
                    for ms in j:
                        if (
                            ms["activity_type"]
                            in ["MA_SUB_DATE_US", "MA_SUB_DATE_EX_US"]
                            and ms["new_name"] == projectCode
                            and not nfSet
                        ):
                            nfSet = True
                            section = PipelineUtils.create_section("NEXT FILING", ms)
                            project.sections.append(section)

                        if (
                            ms["activity_type"] in ["BLA/NDA APP", "LAU_US", "LAU_EU"]
                            and ms["new_name"] == projectCode
                            and not nalSet
                        ):
                            nalSet = True
                            section = PipelineUtils.create_section(
                                "NEXT APPROVAL OR LAUNCH", ms
                            )
                            project.sections.append(section)
                    pipeline.projects.append(project)
            # Calculate Project Status
            project_index = -1
            for project in pipeline.projects:
                project_index += 1
                one_green = False
                section_index = -1
                pipeline.projects[project_index].status = "gray"
                logger.debug(
                    f"Caluclating Status for Commercial Pipeline index {project_index}"
                )
                for section in project.sections:
                    section_index += 1
                    if section.status == "red" or section.status == "delayed":
                        pipeline.projects[project_index].status = "red"
                        break
                    elif (
                        section.status == "yellow"
                        or section.status == "subject to change"
                    ):
                        pipeline.projects[project_index].status = "yellow"
                        break
                    elif (
                        section.status == "accelerated"
                        or section.status == "on track"
                        or section.status == "green"
                    ):
                        one_green = True
                if one_green and pipeline.projects[project_index].status == "gray":
                    logger.debug(f"set_project_status setting {project_index} to green")
                    pipeline.projects[project_index].status = "green"

            return pipeline
        except Exception:
            pipeline = CommercialPipeline()
            pipeline.projects = []
            logger.debug(traceback.print_exc())
            return pipeline
