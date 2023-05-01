from ..loggerFactory import LoggerFactory
import os
import requests
from typing import List
from ..models.common import Owners, ExternalLink
from ..models.supply import (
    Location,
    LocationDetails,
    Supply,
    InventoryBelowTarget,
    CogsReduction,
    FDP,
)


logger = LoggerFactory.get_logger(__name__)

env = os.getenv("PA_ENV", "not found")


env_supply = ""
env_supply_href = ""

if env == "dev" or env == "test":
    env_supply = "api-" + env
    env_supply_href = "-" + env
elif env == "staging":
    env_supply = "api-" + env
    env_supply_href = "-stg"
elif env == "rts":
    env_supply = env


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


class SupplyUtils:
    def get_supply_locations(token) -> List[Location]:
        logger.debug(f"Supply get_supply_locations: start")

        headers = {
            "Authorization": "Bearer " + token.credentials,
            "content-type": "application/json",
        }

        response = requests.get(
            f"https://supply-{env_supply}.nimbus.amgen.com/v1/capital/portfolio/projects/data.json",
            headers=headers,
        )
        if response.status_code != 200:
            logger.debug(f"Supply location response code: {response.status_code}")
            return None

        j = response.json()

        locations = []
        external_link = ExternalLink()
        external_link.href = (
            f"https://sensing{env_supply_href}.nimbus.amgen.com/supply/dashboard"
        )
        external_link.label = "GO TO SUPPLY PAGE"

        for s in j["series"]:
            if s["projectShortName"] == "ANC FleX Batch DS Manufacturing Facility":
                anc = Location()
                anc.title = "ANC"
                anc.owners = Owners()
                anc.owners.ceoStaffSponsors = []
                anc.owners.operatingTeamOwners = []
                anc.owners.ceoStaffSponsors.append("Esteban Santos")
                anc.owners.operatingTeamOwners.append("Arleen Paulino")
                anc.href = f"https://sensing{env_supply_href}.nimbus.amgen.com/supply/dashboard"

                anc.externalLinks = []
                anc.externalLinks.append(external_link)

                anc.status = s["overallAlert"].lower()
                scope = LocationDetails()
                scope.status = s["scopeAlert"].lower()
                scope.text = getAlertLabel(s["scopeAlert"].lower())
                timeline = LocationDetails()
                timeline.status = s["completionDateAlert"].lower()
                timeline.text = s["forecastCompletionDate"]
                value = LocationDetails()
                value.status = s["valueAlert"].lower()
                value.text = getAlertLabel(s["valueAlert"].lower())
                anc.status = value.status.lower()
                cost = LocationDetails()
                cost.status = s["fundingAlert"].lower()
                cost.text = s["forecastFunding"]
                risk = LocationDetails()
                risk.status = s["riskAlert"].lower()
                risk.text = s["risk"]

                anc.scope = scope
                anc.timeline = timeline
                anc.value = value
                anc.cost = cost
                anc.risk = risk

            if s["projectShortName"] == "AOH - B1 Packaging Facility":
                aoh = Location()
                aoh.title = "AOH"
                aoh.owners = Owners()
                aoh.owners.ceoStaffSponsors = []
                aoh.owners.operatingTeamOwners = []
                aoh.owners.ceoStaffSponsors.append("Esteban Santos")
                aoh.owners.operatingTeamOwners.append("Arleen Paulino")
                aoh.href = f"https://sensing{env_supply_href}.nimbus.amgen.com/supply/dashboard"

                aoh.externalLinks = []
                aoh.externalLinks.append(external_link)

                aoh.status = s["overallAlert"].lower()
                scope = LocationDetails()
                scope.status = s["scopeAlert"].lower()
                scope.text = getAlertLabel(s["scopeAlert"].lower())
                timeline = LocationDetails()
                timeline.status = s["completionDateAlert"].lower()
                timeline.text = s["forecastCompletionDate"]
                value = LocationDetails()
                value.status = s["valueAlert"].lower()
                value.text = getAlertLabel(s["valueAlert"].lower())
                aoh.status = value.status.lower()
                cost = LocationDetails()
                cost.status = s["fundingAlert"].lower()
                cost.text = s["forecastFunding"]
                risk = LocationDetails()
                risk.status = s["riskAlert"].lower()
                risk.text = s["risk"]

                aoh.scope = scope
                aoh.timeline = timeline
                aoh.value = value
                aoh.cost = cost
                aoh.risk = risk

        if anc.title:
            locations.append(anc)
        if aoh.title:
            locations.append(aoh)

        return locations

    # needs refinement
    def get_supply_InventoryBelowTarget(token, name: str) -> InventoryBelowTarget:
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
        external_link = ExternalLink()
        external_link.href = (
            f"https://sensing{env_supply_href}.nimbus.amgen.com/supply/dashboard"
        )
        external_link.label = "GO TO SUPPLY PAGE"
        inventoryBelowTarget.externalLinks = []
        inventoryBelowTarget.externalLinks.append(external_link)

        for s in j["skusBelowSss"]["skusBelowMinTarget"]:
            if s["productName"] == name.upper():
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
