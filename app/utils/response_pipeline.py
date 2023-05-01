"""
Format response for key events controller
"""
from ..constant import Constant
from itertools import groupby
from operator import itemgetter


def format_response_pipeline_metrics(response: any):
    """
    method for format_response_key_products_csp from AWS Athena
    ---
    """
    # items_sorted = sorted(response[1], key= itemgetter(key_group)) ##key_events_label
    if response is None:
        return []
    return [
        {
            "new_name": d["new_name"],
            "product": d["product"],
            "project_type": d["project_type"],
            "milestone_category": d["milestone_category"],
            "milestone_short_name": d["milestone_short_name"],
            "ipp_short_name": d["ipp_short_name"],
            "project_type": d["project_type"],
            "activity_type": d["activity_type"],
            "ipp_study_number": d["ipp_study_number"],
            "study_short_description": d["study_short_description"],
            "geographic_area": d["geographic_area"],
            "end_date_current_approved_cab": d["end_date_current_approved_cab"],
            "date_variance": d["date_variance"],
            "milestone_status": d["milestone_status"],
            "transition_date_reason": d["transition_date_reason"],
            "snap_date": d["snap_date"],
            "geographic_area": d["geographic_area"],
        }
        for d in response[1] or []
    ]
