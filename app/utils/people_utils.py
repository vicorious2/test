from datetime import datetime

from ..models.people import (
    CommercialPeopleEngagementScore,
    PeopleWhenTooltip,
    People,
    TalentAcquisition,
    Turnover,
)
from ..loggerFactory import LoggerFactory
from .http_request_utils import HttpRequest
import os
from ..models.common import Chart, ExternalLink
from decimal import Decimal
import traceback
import requests


logger = LoggerFactory.get_logger(__name__)
env = os.getenv("PA_ENV", "not found")

env_people = ""

env_people_href = ""

if env == "dev" or env == "test":
    env_people = "api-" + env
    env_people_href = "-" + env
elif env == "staging":
    env_people = "api-stg"
    env_people_href = "-stg"
elif env == "rts":
    env_people = "api"


class PeopleUtils:
    def get_people_engagement_score(function, product, token):
        """
        People engagement score
        ---
        responses:
        200:
            Amgen: Sensing Prioritized Agenda API
        """
        logger.debug(f"People get_engagement_score: start")
        result = []
        try:
            url = (
                f"https://people-{env_people}.nimbus.amgen.com/api/v1/culture/engagement-historical-trend?function="
                + function
            )
            historic = HttpRequest.http_get(url, token)
            if not historic:
                return None
            url_key_products = (
                f"https://people-{env_people}.nimbus.amgen.com/api/v1/key-product/key-product-engagement-data/"
                + product
            )
            key_products = HttpRequest.http_get(url_key_products, token)
            if not key_products:
                return None

            for histo in historic["data"]:
                for key_product in key_products["data"]:
                    if (
                        datetime.strptime(histo["date"], "%b '%d").strftime("%Y-%m-%d")
                        == key_product["date"]
                    ):
                        data = {
                            "benchmark": histo["benchmark"],
                            "previous_date": key_product["previous_date"],
                            "amgen_value": histo["amgen_value"],
                        }
                        result.append(data)
                        break

            return result
        except Exception:
            logger.debug(traceback.print_exc())
            return None

    def get_people_turnover(function, product, token):
        """
        People turnover
        ---
        responses:
        200:
            Amgen: Sensing Prioritized Agenda API
        """
        logger.debug(f"People get_people_turnover: start")
        result = []
        try:
            url = (
                f"https://people-{env_people}.nimbus.amgen.com/api/v1/key-product/key-product-turnover-data/"
                + product
            )
            turnover = HttpRequest.http_get(url, token)
            if not turnover:
                return None

            for turno in turnover["data"]:
                dateStr = turno["date"]
                dateStr = dateStr.replace("'", "")
                dateStr = dateStr[0:3] + " 01, 20" + dateStr[-2:]
                # Jan 25, 2021

                date = datetime.strptime(dateStr, "%b %d, %Y").date()

                data = {
                    "date": date,
                    "value": turno["value"],
                }
                result.append(data)
                break

            return result
        except Exception:
            logger.debug(traceback.print_exc())
            return None

    def get_people_talent_acquisition(function, product, token):
        """
        People talent acquisition
        ---
        responses:
        200:
            Amgen: Sensing Prioritized Agenda API
        """
        logger.debug(f"People get_people_talent_acquisition: start")
        result = []
        try:
            url = (
                f"https://people-{env_people}.nimbus.amgen.com/api/v1/key-product/key-product-acquisition-data/"
                + product
            )
            talent_acquisition = HttpRequest.http_get(url, token)
            if not talent_acquisition:
                return None

            for talent in talent_acquisition["data"]:
                if talent["status"].trim() in ("Open Reqs", "Average Open Days"):
                    data = {
                        "total_hires": talent["total_hires"],
                        "date": talent["date"],
                    }
                    result.append(data)
                    break

            return result
        except Exception:
            logger.debug(traceback.print_exc())
            return None

    def get_people(product, function, token):
        people = People()
        talentAcquisition = TalentAcquisition()
        engagementScore = CommercialPeopleEngagementScore()
        turnover = Turnover()
        chart = []
        chartAmgen = []

        tooltip = PeopleWhenTooltip()

        tooltip.greenText = "when Repatha engagement score is at or above Amgen Average engagement score."
        tooltip.redText = (
            "when Repatha engagement score is below Amgen Average engagement score."
        )
        engagementScore.tooltip = tooltip

        talentAcquisition.href = (
            f"https://sensing{env_people_href}.nimbus.amgen.com/people"
        )
        engagementScore.href = (
            f"https://sensing{env_people_href}.nimbus.amgen.com/people"
        )
        turnover.href = f"https://sensing{env_people_href}.nimbus.amgen.com/people"
        # Engagement and Talent Acquisition
        try:
            response = HttpRequest.get(
                f"https://people-{env_people}.nimbus.amgen.com/api/v1/key-product/key-product-data/"
                + product,
                token,
            )
            if not response:
                logger.debug(f"People response empty")
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
            response = HttpRequest.get(
                f"https://people-{env_people}.nimbus.amgen.com/api/v1/culture/engagement-historical-trend?function="
                + function,
                token,
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
            response = HttpRequest.get(
                f"https://people-{env_people}.nimbus.amgen.com/api/v1/talent-retention/talent-retention-data?function="
                + function,
                token,
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

    def get_people_metrics(token, name):
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
        engagementScore = CommercialPeopleEngagementScore()
        turnover = Turnover()
        chart = []
        chartAmgen = []
        external_link = ExternalLink()
        external_link.href = f"https://sensing{env_people_href}.nimbus.amgen.com/people"
        external_link.label = "GO TO PEOPLE PAGE"
        tooltip = PeopleWhenTooltip()

        tooltip.greenText = (
            "when "
            + name
            + " engagement score is at or above Amgen Average engagement score."
        )
        tooltip.redText = (
            "when "
            + name
            + " engagement score is below Amgen Average engagement score."
        )
        engagementScore.tooltip = tooltip

        talentAcquisition.href = (
            f"https://sensing{env_people_href}.nimbus.amgen.com/people"
        )
        talentAcquisition.externalLinks = []
        talentAcquisition.externalLinks.append(external_link)
        engagementScore.href = (
            f"https://sensing{env_people_href}.nimbus.amgen.com/people"
        )
        engagementScore.externalLinks = []
        engagementScore.externalLinks.append(external_link)
        turnover.href = f"https://sensing{env_people_href}.nimbus.amgen.com/people"
        turnover.externalLinks = []
        turnover.externalLinks.append(external_link)
        # Engagement and Talent Acquisition
        try:
            response = requests.get(
                f"https://people-{env_people}.nimbus.amgen.com/api/v1/key-product/key-product-data/"
                + name,
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
