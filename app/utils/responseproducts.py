"""
Format response for products controller
"""


def format_response_products(response: any, name: str):
    """
    method for format_response from AWS Athena
    ---
    """
    if response is None:
        return []
    if name:
        return [
            {
                "amg_number": d["amg_number"],
                "product": d["product"],
                "names": d["names"],
                "trade_name": d["trade_name"],
                "notepad": d["notepad"],
                "modality": d["modality"],
                "target": d["target"],
                "current_phase": d["current_phase"],
                "medical_therapeutic_areas": d["medical_therapeutic_areas"],
                "generic_name": d["generic_name"],
                "lead_indication_descriptions": d["lead_indication_descriptions"],
                "business_partners": d["business_partners"],
                "portfolio_priority": d["portfolio_priority"],
                "project_type": d["project_type"],
            }
            for d in response[1]
            if d["product"] == name or []
        ]
    else:
        return [
            {
                "amg_number": d["amg_number"],
                "product": d["product"],
                "names": d["names"],
                "trade_name": d["trade_name"],
                "notepad": d["notepad"],
                "modality": d["modality"],
                "target": d["target"],
                "current_phase": d["current_phase"],
                "medical_therapeutic_areas": d["medical_therapeutic_areas"],
                "generic_name": d["generic_name"],
                "lead_indication_descriptions": d["lead_indication_descriptions"],
                "business_partners": d["business_partners"],
                "portfolio_priority": d["portfolio_priority"],
                "project_type": d["project_type"],
            }
            for d in response[1] or []
        ]


def format_response_products_tpp(response: any, name: str):
    """
    method for format_response from AWS Athena
    ---
    """
    if response is None:
        return []
    if name:
        return [
            {
                "tpp_summary_of_change": d["tpp_summary_of_change"],
                "tpp_link": d["tpp_link"],
                "indications": d["indications"],
                "key_markets_of_entry": d["key_markets_of_entry"],
                "ceo_staff_sponsor": d["ceo_staff_sponsor"],
                "operating_team_owner": d["operating_team_owner"],
                "business_lead": d["business_lead"],
                "name": d["name"],
            }
            for d in response[1]
            if d["name"] in name.split(",") or []
        ]
    else:
        return [
            {
                "tpp_summary_of_change": d["tpp_summary_of_change"],
                "tpp_link": d["tpp_link"],
                "indications": d["indications"],
                "key_markets_of_entry": d["key_markets_of_entry"],
                "ceo_staff_sponsor": d["ceo_staff_sponsor"],
                "operating_team_owner": d["operating_team_owner"],
                "business_lead": d["business_lead"],
                "name": d["name"],
            }
            for d in response[1] or []
        ]


def format_response_products_tpp_link(response: any, product: str):
    """
    method for format_response from AWS Athena
    ---
    """
    if response is None:
        return []
    if product:
        return [
            {
                "product": d["product"],
                "tpp_link": d["tpp_link"],
                "link_desciption": d["link_desciption"],
            }
            for d in response[1]
            if d["product"] in product or []
        ]
    else:
        return [
            {
                "product": d["product"],
                "tpp_link": d["tpp_link"],
                "link_desciption": d["link_desciption"],
            }
            for d in response[1] or []
        ]


def format_response_products_ext(response: any, product: str):
    """
    method for format_response from AWS Athena
    ---
    """
    if response is None:
        return []
    if product:
        return [
            {
                "product": d["product"],
                "generic_name": d["generic_name"],
                "trade_name": d["trade_name"],
                "trade_name": d["trade_name"],
                "amg_number": d["amg_number"],
                "notepad": d["notepad"],
                "medical_therapeutic_area": d["medical_therapeutic_area"],
                "competitor_products": d["competitor_products"],
                "competitors": d["competitors"],
            }
            for d in response[1]
            if d["product"] == product or []
        ]
    else:
        return [
            {
                "product": d["product"],
                "generic_name": d["generic_name"],
                "trade_name": d["trade_name"],
                "trade_name": d["trade_name"],
                "amg_number": d["amg_number"],
                "notepad": d["notepad"],
                "medical_therapeutic_area": d["medical_therapeutic_area"],
                "competitor_products": d["competitor_products"],
                "competitors": d["competitors"],
            }
            for d in response[1] or []
        ]


def format_response_valuation_sum_supply(response: any, product: str):
    """
    method for format_response from AWS Athena
    ---
    """
    if response is None:
        return []
    if product:
        return [
            {
                "amg_number": d["amg_number"],
                "product": d["product"],
                "rnpv_m_sum": d["rnpv_m_sum"],
            }
            for d in response[1]
            if d["product"].lower() in [x.lower() for x in product.split(",")] or []
        ]
    else:
        return [
            {
                "amg_number": d["amg_number"],
                "product": d["product"],
                "rnpv_m_sum": d["rnpv_m_sum"],
            }
            for d in response[1] or []
        ]
