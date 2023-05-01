"""
Constant class
"""


class Constant:
    """
    Constant class
    """

    PA_STATUS_GREEN = "green"
    PA_STATUS_YELLOW = "yellow"
    PA_STATUS_GRAY = "gray"
    PA_STATUS_RED = "red"
    PA_STATUS_ENROLMENT_NOT_STARTED = "enrollment not started"
    AWS_REGION = "us-west-2"
    BUCKET = "aws-athena-query-results-291403363365-us-west-2"
    CATEGORIES = [
        "Flash Memos",
        "Filings",
        "Launches",
        "Portals",
        "Competitive Intelligence",
    ]
    CATEGORIES_V2 = ["Flash Memos", "Filings", "Launches", "Portals"]
    ENV_PATH = "../.env"
    REDIS_KEY_PREFIX = "PRIORITIZED_AGENDA"

    SCHEMA_CLINDEV_PPM_PUBLISH = "edf_prd_cdl_clindev_ppm_publish"
    CLICKTROUGH = "https://portfolio-analytics.amgen.com/dashboard/key-events-dashboard-key-events-dashboard"

    KEY_UPCOMING_EVENTS_SQL_PATH_FILE = "../sql/key_events.sql"
    KEY_UPCOMING_EVENTS_SQL_PATH_FILE_V2 = "../sql/keyEvents/key_events_v2.sql"
    KEY_UPCOMING_EVENTS_SQL_PATH_FILE_V3 = "../sql/keyEvents/key_events_ci.sql"
    KEY_UPCOMING_EVENTS_SQL_PATH_FILE_V4 = "../sql/keyEvents/key_events_v4.sql"
    REPATHA_MILESTONSES_SQL = "../sql/commercial/repatha_milestones.sql"
    COMMERCIAL_PIPELINE_DYNAMIC_SQL = (
        "../sql/commercial/commercial_pipeline_dynamic.sql"
    )
    FILTER_PRODUCTS_SQL_PATH_FILE = "../sql/filter_products.sql"
    FILTER_PRODUCTS_SQL_PATH_FILE_v2 = "../sql/filterProducts/filter_products_all.sql"
    PRODUCTS_DETAILS_BY_PRODUCT_FILE = "../sql/project_details_by_product.sql"
    PRODUCTS_DETAILS_BY_PRODUCT_FILE_V2 = (
        "../sql/filterProducts/filter_projects_details.sql"
    )
    PRODUCTS_TPP_FILE = "../sql/filterProducts/filter_products_tpp.sql"
    PRODUCTS_TPP_LINK_FILE = "../sql/filterProducts/filter_products_tpp_link.sql"

    # test

    # test
    AUTH_USERS_EXCEPTION = [
        "mmille17",
        "tworrell",
        "alindart",
        "rpatel27",
        "dallen04",
        "elee14",
        "zsunoo",
        "wbusath",
        "apeddire",
        "svc-sensing-non-prd",
    ]
    # test
    AUTH_USERS_EXCEPTION_NOTIFICATION = ["sedukull", "aluce", "sjameel", "akeshri"]
