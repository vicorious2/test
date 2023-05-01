import requests
from app.models.commercial import otezla_hover_data, repatha_hover_data
from ..loggerFactory import LoggerFactory
from .http_request_utils import HttpRequest
import os
from ..models.brand import (
    Brand,
    BasicTooltip,
    BasicTooltipRow,
    BasicTooltipSection,
    NbrxFulfillment,
    NbrxFulfillmentDetails,
    IdnAccountWins,
    ShareOfVoice,
    NetSalesSummary,
    NetSales,
    NbrxVolumeBySpecialtiesDetails,
    NbrxVolumeBySpecialties,
    CommercialBrandSalesDemandSectionTableRow,
    CommercialBrandSalesDemandSectionTable,
    CommercialBrandSalesDemandSection,
    brand_hover_data,
)
from ..models.common import Chart, ExternalLink
from decimal import Decimal
import traceback


logger = LoggerFactory.get_logger(__name__)
env = os.getenv("PA_ENV", "not found")

env_brand = ""

env_brand_href = ""

if env == "dev" or env == "test":
    env_brand = "api-" + env
    env_brand_href = "-" + env
elif env == "staging":
    env_brand = "api-stg"
    env_brand_href = "-stg"
elif env == "rts":
    env_brand = "api"


class BrandUtils:
    def build_net_sales_chart(j, chart):
        try:
            for trend_line_times in j["data"]["trend_line"]:
                chartDetails = Chart()
                chartDetails.label = trend_line_times["month"]
                if "net_sales_fcst" in trend_line_times:
                    chartDetails.forecast = trend_line_times["net_sales_fcst"]
                if "net_sales_actual" in trend_line_times:
                    chartDetails.value = trend_line_times["net_sales_actual"]
                chart.append(chartDetails)
        except Exception:
            logger.debug(traceback.print_exc())

    def build_nbrx_trx_chart(j, chart):
        try:
            for tl in j["data"]["volume"]["trendLine"]:
                chartDetails = Chart()
                chartDetails.label = tl["month"]
                if "net_sales_fcst" in tl:
                    chartDetails.forecast = tl["net_sales_fcst"]
                if "net_sales_actual" in tl:
                    chartDetails.value = tl["net_sales_actual"]
                chart.append(chartDetails)
        except Exception:
            logger.debug(traceback.print_exc())

    def build_net_sales_section_table(
        j,
        commercial_brand_sales_demand_section_table: list,
        commercial_brand_sales_demand_section: CommercialBrandSalesDemandSection,
    ):
        try:
            net_sales_section_table = CommercialBrandSalesDemandSectionTable()
            net_sales_section_table.title = "Net Sales"
            weekly_average_section_table = CommercialBrandSalesDemandSectionTable()
            weekly_average_section_table.title = "Weekly Average"
            net_sales_section_row = CommercialBrandSalesDemandSectionTableRow()
            weekly_average_section_row = CommercialBrandSalesDemandSectionTableRow()
            for t in j["data"]["table"]:
                if t["name"] == "Net Sales":
                    net_sales_section_row.ytdLabel = t["YTD"]["Name"]
                    net_sales_section_row.ytd = t["YTD"]["Value"]
                    net_sales_section_row.ytgLabel = t["YTG"]["Name"]
                    net_sales_section_row.ytg = t["YTG"]["Value"]
                    net_sales_section_row.forecastLabel = "FY FCST"
                    net_sales_section_row.forecast = t["FY FCST"]["Value"]
                    try:
                        net_sales_section_row.ytgStatus = (
                            "green" if t["YTG"]["is_positive"] == True else "red"
                        )
                    except:
                        logger.debug("YTG net_sales_section_row is_positive is missing")
                    net_sales_section_table.rows = []
                    net_sales_section_table.rows.append(net_sales_section_row)
                    commercial_brand_sales_demand_section_table.append(
                        net_sales_section_table
                    )
                if t["name"] == "Weekly Average":
                    weekly_average_section_row.ytdLabel = t["YTD"]["Name"]
                    weekly_average_section_row.ytd = t["YTD"]["Value"]
                    weekly_average_section_row.ytgLabel = t["YTG"]["Name"]
                    weekly_average_section_row.ytg = t["YTG"]["Value"]
                    weekly_average_section_row.forecastLabel = "FY FCST"
                    weekly_average_section_row.forecast = t["FY FCST"]["Value"]
                    try:
                        weekly_average_section_row.ytgStatus = (
                            "green" if t["YTG"]["is_positive"] == True else "red"
                        )
                    except:
                        logger.debug(
                            "YTG weekly_average_section_row is_positive is missing"
                        )
                    weekly_average_section_table.rows = []
                    weekly_average_section_table.rows.append(weekly_average_section_row)
                    commercial_brand_sales_demand_section_table.append(
                        weekly_average_section_table
                    )
                    ytd = Decimal(weekly_average_section_row.ytd.replace("M", ""))
                    ytg = Decimal(weekly_average_section_row.ytg.replace("M", ""))
                    forecast = Decimal(
                        weekly_average_section_row.forecast.replace("M", "")
                    )
                    if ytd >= ytg and ytd > forecast + forecast * Decimal("0.02"):
                        commercial_brand_sales_demand_section.status = "green"
                    elif ytd < ytg or ytd < forecast - forecast * Decimal("0.02"):
                        commercial_brand_sales_demand_section.status = "red"
                    else:
                        commercial_brand_sales_demand_section.status = "yellow"

        except Exception:
            logger.debug(traceback.print_exc())

    def build_nbrx_trx_section_table(
        j,
        commercial_brand_sales_demand_section_table: list,
        commercial_brand_sales_demand_section: CommercialBrandSalesDemandSection,
    ):
        try:
            net_sales_section_table = CommercialBrandSalesDemandSectionTable()
            net_sales_section_table.title = "Volume"
            weekly_average_section_table = CommercialBrandSalesDemandSectionTable()
            weekly_average_section_table.title = "Weekly Average"
            net_sales_section_row = CommercialBrandSalesDemandSectionTableRow()
            weekly_average_section_row = CommercialBrandSalesDemandSectionTableRow()
            for t in j["data"]["volume"]["tableData"]:
                if t["name"] == "Volume":
                    net_sales_section_row.ytdLabel = t["YTD"]["Name"]
                    net_sales_section_row.ytd = t["YTD"]["Value"]
                    net_sales_section_row.ytgLabel = t["YTG"]["Name"]
                    net_sales_section_row.ytg = t["YTG"]["Value"]
                    net_sales_section_row.forecastLabel = "FY FCST"
                    net_sales_section_row.forecast = t["FY FCST"]["Value"]
                    try:
                        net_sales_section_row.ytgStatus = (
                            "green" if t["YTG"]["is_positive"] == True else "red"
                        )
                    except:
                        logger.debug("YTG net_sales_section_row is_positive is missing")
                    net_sales_section_table.rows = []
                    net_sales_section_table.rows.append(net_sales_section_row)
                    commercial_brand_sales_demand_section_table.append(
                        net_sales_section_table
                    )
                if t["name"] == "Weekly Average":
                    weekly_average_section_row.ytdLabel = t["YTD"]["Name"]
                    weekly_average_section_row.ytd = t["YTD"]["Value"]
                    weekly_average_section_row.ytgLabel = t["YTG"]["Name"]
                    weekly_average_section_row.ytg = t["YTG"]["Value"]
                    weekly_average_section_row.forecastLabel = "FY FCST"
                    weekly_average_section_row.forecast = t["FY FCST"]["Value"]
                    try:
                        weekly_average_section_row.ytgStatus = (
                            "green" if t["YTG"]["is_positive"] == True else "red"
                        )
                    except:
                        logger.debug(
                            "YTG weekly_average_section_row is_positive is missing"
                        )
                    weekly_average_section_table.rows = []
                    weekly_average_section_table.rows.append(weekly_average_section_row)
                    commercial_brand_sales_demand_section_table.append(
                        weekly_average_section_table
                    )
                    ytd = Decimal(weekly_average_section_row.ytd.replace("K", ""))
                    ytg = Decimal(weekly_average_section_row.ytg.replace("K", ""))
                    forecast = Decimal(
                        weekly_average_section_row.forecast.replace("K", "")
                    )
                    if ytd >= ytg and ytd > forecast + forecast * Decimal("0.02"):
                        commercial_brand_sales_demand_section.status = "green"
                    elif ytd < ytg or ytd < forecast - forecast * Decimal("0.02"):
                        commercial_brand_sales_demand_section.status = "red"
                    else:
                        commercial_brand_sales_demand_section.status = "yellow"

        except Exception:
            logger.debug(traceback.print_exc())

    def get_commercial_brand_sales_demand_section(
        chart_type, archetypeLinkId: str, data, token
    ):
        try:
            commercial_brand_sales_demand_section = CommercialBrandSalesDemandSection()
            commercial_brand_sales_demand_section.tables = []
            commercial_brand_sales_demand_section.status = "gray"
            j = None
            chart = []

            if archetypeLinkId == "Otezla":
                tooltip_data = get_otezla_hover_data(token=token, data=data)
            else:  # ToDo: refactor and add repatha condition
                tooltip_data = get_brand_hover_data(token, data)

            if chart_type == "Net Sales":
                logger.debug(f"Building Net Sales")
                url = f"https://brand-{env_brand}.nimbus.amgen.com/brand_services/us_lagging/net_sales"
                j = HttpRequest.http_post(url, data, token)
                if not j:
                    return None
                commercial_brand_sales_demand_section.title = chart_type
                commercial_brand_sales_demand_section.chartTitle = None
                commercial_brand_sales_demand_section.externalLinks = []
                external_link = ExternalLink()
                external_link.label = "GO TO BRAND PAGE"
                external_link.href = (
                    f"https://sensing{env_brand_href}.nimbus.amgen.com/brand#"
                    + archetypeLinkId.lower()
                )
                commercial_brand_sales_demand_section.externalLinks.append(
                    external_link
                )

                BrandUtils.build_net_sales_chart(j, chart)
                commercial_brand_sales_demand_section.chart = chart
                BrandUtils.build_net_sales_section_table(
                    j,
                    commercial_brand_sales_demand_section.tables,
                    commercial_brand_sales_demand_section,
                )
                if tooltip_data:
                    basic_tt = BasicTooltip()
                    basic_tt.sections = []
                    brand_tt = BasicTooltipSection()

                    brand_tt.rows = []
                    brand_tt_data_source = BasicTooltipRow()
                    brand_tt_refresh_frequency = BasicTooltipRow()

                    brand_tt_data_source.label = "Data Source:"
                    brand_tt_data_source.text = (
                        tooltip_data.us_lagging.net_sales.Data_Source
                    )

                    brand_tt_refresh_frequency.label = "Refresh Frequency:"
                    brand_tt_refresh_frequency.text = (
                        tooltip_data.us_lagging.net_sales.Refresh_Freequency
                    )

                    brand_tt.rows.append(brand_tt_data_source)
                    brand_tt.rows.append(brand_tt_refresh_frequency)

                    basic_tt.sections.append(brand_tt)

                    commercial_brand_sales_demand_section.tooltip = basic_tt

            if chart_type == "NBRx Demand" or chart_type == "TRx Demand":
                url = f"https://brand-{env_brand}.nimbus.amgen.com/brand_services/us_lagging/demand_components_of_growth"
                j = HttpRequest.http_post(url, data, token)
                if not j:
                    return None
                commercial_brand_sales_demand_section.title = chart_type
                commercial_brand_sales_demand_section.chartTitle = None
                commercial_brand_sales_demand_section.externalLinks = []
                external_link = ExternalLink()
                external_link.label = "GO TO BRAND PAGE"
                external_link.href = (
                    f"https://sensing{env_brand_href}.nimbus.amgen.com/brand#"
                    + archetypeLinkId.lower()
                )
                if chart_type == "TRx Demand":
                    external_link.href = external_link.href + "_trx_demand"
                commercial_brand_sales_demand_section.externalLinks.append(
                    external_link
                )

                if archetypeLinkId == "Otezla":
                    commercial_brand_sales_demand_section.chartTitle = (
                        "Dermatology – Advanced Systemics Market"
                    )
                    if chart_type == "TRx Demand":
                        commercial_brand_sales_demand_section.title = (
                            "TRx Days of Therapy (DOT) Demand"
                        )

                if not j:
                    return None
                BrandUtils.build_nbrx_trx_chart(j, chart)
                commercial_brand_sales_demand_section.chart = chart
                BrandUtils.build_nbrx_trx_section_table(
                    j,
                    commercial_brand_sales_demand_section.tables,
                    commercial_brand_sales_demand_section,
                )

                if tooltip_data:

                    basic_tt = BasicTooltip()
                    basic_tt.sections = []
                    brand_tt = BasicTooltipSection()

                    brand_tt.rows = []
                    brand_tt_data_source = BasicTooltipRow()
                    brand_tt_refresh_frequency = BasicTooltipRow()

                    brand_tt_data_source.label = "Data Source:"
                    brand_tt_data_source.text = (
                        tooltip_data.us_lagging.demand_components_of_growth.Data_Source
                    )

                    brand_tt_refresh_frequency.label = "Refresh Frequency:"
                    brand_tt_refresh_frequency.text = (
                        tooltip_data.us_lagging.demand_components_of_growth.Refresh_Freequency
                    )

                    brand_tt.rows.append(brand_tt_data_source)
                    brand_tt.rows.append(brand_tt_refresh_frequency)

                    basic_tt.sections.append(brand_tt)

                    commercial_brand_sales_demand_section.tooltip = basic_tt

            return commercial_brand_sales_demand_section
        except Exception:
            logger.debug(traceback.print_exc())
            return None

    def get_nbrx_fulfillment(data, archetypeLinkId: str, token):
        logger.debug(f"Brand get_nbrx_fulfillment: start")
        if archetypeLinkId == "Otezla":
            tooltip_data = get_otezla_hover_data(token=token, data=data)
        else:  # ToDo: refactor and add repatha condition
            tooltip_data = get_brand_hover_data(token, data)
        try:
            url = f"https://brand-{env_brand}.nimbus.amgen.com/brand_services/us_leading/nbrx_fulfillment"
            j = HttpRequest.http_post(url, data, token)
            if not j:
                return None

            nbrxFulfillment = NbrxFulfillment()
            nbrxFulfillmentDetails = []
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
                f"https://sensing{env_brand_href}.nimbus.amgen.com/brand#"
                + archetypeLinkId.lower()
                + "__leading"
            )
            nbrxFulfillment.externalLinks = []
            external_link = ExternalLink()
            external_link.label = "GO TO BRAND PAGE"
            external_link.href = (
                f"https://sensing{env_brand_href}.nimbus.amgen.com/brand#"
                + archetypeLinkId.lower()
                + "__leading"
            )
            nbrxFulfillment.externalLinks.append(external_link)
            if tooltip_data:
                basic_tt = BasicTooltip()
                basic_tt.sections = []
                brand_tt = BasicTooltipSection()

                brand_tt.rows = []
                brand_tt_data_source = BasicTooltipRow()
                brand_tt_refresh_frequency = BasicTooltipRow()

                brand_tt_data_source.label = "Data Source:"
                brand_tt_data_source.text = (
                    tooltip_data.us_leading.nbrx_fulfillment.Data_Source
                )

                brand_tt_refresh_frequency.label = "Refresh Frequency:"
                brand_tt_refresh_frequency.text = (
                    tooltip_data.us_leading.nbrx_fulfillment.Refresh_Freequency
                )

                brand_tt.rows.append(brand_tt_data_source)
                brand_tt.rows.append(brand_tt_refresh_frequency)

                basic_tt.sections.append(brand_tt)

                nbrxFulfillment.tooltip = basic_tt
            nbrxFulfillment.data = nbrxFulfillmentDetails
            return nbrxFulfillment
        except Exception:
            logger.debug(traceback.print_exc())
            return None

    def get_nbrx_volume_by_specialties(data, archetypeLinkId: str, token):
        tooltip_data = get_brand_hover_data(token, data)
        logger.debug(f"Brand get_nbrx_volume_by_specialties: start")
        try:

            url = f"https://brand-{env_brand}.nimbus.amgen.com/brand_services/us_leading/nbrx_writer_pcp_card"
            j = HttpRequest.http_post(url, data, token)
            if not j:
                return None

            cardRecentAvg = Decimal("0.0")
            cardRecentGoal = Decimal("0.0")
            cardStatus = "gray"
            pcpRecentAvg = Decimal("0.0")
            pcpRecentGoal = Decimal("0.0")
            pcpStatus = "gray"

            cardiologists = []
            pcps = []
            for d in j["data"]:
                if "NBRx Writer - CARD" in d:
                    for card in d["NBRx Writer - CARD"]:
                        det = NbrxVolumeBySpecialtiesDetails()
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
                        det = NbrxVolumeBySpecialtiesDetails()
                        det.label = pcp["Name"]
                        det.currentVsPrevious = pcp["C4W_P4W"]
                        det.recentAvg = pcp["R4W"]
                        det.recentGoal = pcp["R4W_Goal"]
                        pcps.append(det)
                        if pcp["Name"] == "Avg NBRx/Writer":
                            pcpRecentAvg = Decimal(det.recentAvg)
                            pcpRecentGoal = Decimal(det.recentGoal)

            # TODO: Refactor
            nbrx_volume_by_specialties = NbrxVolumeBySpecialties()
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
                nbrx_volume_by_specialties.status = "red"
            elif cardStatus == "yellow" or pcpStatus == "yellow":
                nbrx_volume_by_specialties.status = "yellow"
            else:
                nbrx_volume_by_specialties.status = "green"

            nbrx_volume_by_specialties.cardiologists = cardiologists
            nbrx_volume_by_specialties.pcps = pcps
            # TODO REMOVE
            nbrx_volume_by_specialties.href = (
                f"https://sensing{env_brand_href}.nimbus.amgen.com/brand#"
                + archetypeLinkId.lower()
                + "_leading_nbrx_volume_by_specialties"
            )

            nbrx_volume_by_specialties.externalLinks = []
            external_link = ExternalLink()
            external_link.label = "GO TO BRAND PAGE"
            external_link.href = (
                f"https://sensing{env_brand_href}.nimbus.amgen.com/brand#"
                + archetypeLinkId.lower()
                + "_leading_nbrx_volume_by_specialties"
            )
            nbrx_volume_by_specialties.externalLinks.append(external_link)
            if tooltip_data:
                basic_tt = BasicTooltip()
                basic_tt.sections = []

                # volume_by_specialties

                brand_tt_v = BasicTooltipSection()
                brand_tt_v.title = "% CONTRIBUTION BY SPECIALTY"
                brand_tt_v.rows = []
                brand_tt_v_data_source = BasicTooltipRow()
                brand_tt_v_refresh_frequency = BasicTooltipRow()

                brand_tt_v_data_source.label = "Data Source:"
                brand_tt_v_data_source.text = (
                    tooltip_data.us_leading.nbrx_volume_by_specialties.volume_by_specialties.Data_Source
                )

                brand_tt_v_refresh_frequency.label = "Refresh Frequency:"
                brand_tt_v_refresh_frequency.text = (
                    tooltip_data.us_leading.nbrx_volume_by_specialties.volume_by_specialties.Refresh_Freequency
                )

                brand_tt_v.rows.append(brand_tt_v_data_source)
                brand_tt_v.rows.append(brand_tt_v_refresh_frequency)

                basic_tt.sections.append(brand_tt_v)

                # c4w_vs_p4w

                brand_tt_c = BasicTooltipSection()
                brand_tt_c.title = "WRITERS TABLE (C4W VS P4W, R4W AVG)"
                brand_tt_c.rows = []
                brand_tt_c_data_source = BasicTooltipRow()
                brand_tt_c_refresh_frequency = BasicTooltipRow()

                brand_tt_c_data_source.label = "Data Source:"
                brand_tt_c_data_source.text = (
                    tooltip_data.us_leading.nbrx_volume_by_specialties.c4w_vs_p4w.Data_Source
                )

                brand_tt_c_refresh_frequency.label = "Refresh Frequency:"
                brand_tt_c_refresh_frequency.text = (
                    tooltip_data.us_leading.nbrx_volume_by_specialties.c4w_vs_p4w.Refresh_Freequency
                )

                brand_tt_c.rows.append(brand_tt_c_data_source)
                brand_tt_c.rows.append(brand_tt_c_refresh_frequency)

                basic_tt.sections.append(brand_tt_c)

                # r4w_goal
                brand_tt_r = BasicTooltipSection()
                brand_tt_r.title = "WRITERS TABLE (R4W GOAL)"
                brand_tt_r.rows = []
                brand_tt_r_data_source = BasicTooltipRow()
                brand_tt_r_refresh_frequency = BasicTooltipRow()

                brand_tt_r_data_source.label = "Data Source:"
                brand_tt_r_data_source.text = (
                    tooltip_data.us_leading.nbrx_volume_by_specialties.r4w_goal.Data_Source
                )

                brand_tt_r_refresh_frequency.label = "Refresh Frequency:"
                brand_tt_r_refresh_frequency.text = (
                    tooltip_data.us_leading.nbrx_volume_by_specialties.r4w_goal.Refresh_Freequency
                )

                brand_tt_r.rows.append(brand_tt_r_data_source)
                brand_tt_r.rows.append(brand_tt_r_refresh_frequency)

                basic_tt.sections.append(brand_tt_r)

                nbrx_volume_by_specialties.tooltip = basic_tt

            return nbrx_volume_by_specialties
        except Exception:
            logger.debug(traceback.print_exc())
            return None


def get_brand_hover_data(token, data):
    logger.debug(f"Brand hover_data: start")

    #     url = (
    #         f"https://brand-{env_brand}.nimbus.amgen.com//brand_services/hover/hover_data",
    #     )
    #    # response = HttpRequest.http_post(url, data, token)
    #     if not response:
    #         return None
    headers = {
        "Authorization": "Bearer " + token.credentials,
        "content-type": "application/json",
    }
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


def get_otezla_hover_data(token, data):
    logger.debug(f"Brand hover_data: start")

    headers = {
        "Authorization": "Bearer " + token.credentials,
        "content-type": "application/json",
    }
    response = requests.post(
        f"https://brand-{env_brand}.nimbus.amgen.com//brand_services/hover/hover_data",
        headers=headers,
        json=data,
    )
    if response.status_code != 200:
        logger.debug(f"Brand hover_data response code: {response.status_code}")
        return None

    repatha_tooltip_data = otezla_hover_data()
    response_obj = repatha_tooltip_data.parse_obj(response.json()).data
    return response_obj
