"""
Athena fetch data
"""
from ..loggerFactory import LoggerFactory
from ..db import athena_connection
import time


##
# params['query'] = SELECT product,
# x.milestone_category, description, y.milestone_category,
# date_of_the_day, geographic_area, project_type, activity_type
# FROM edf_prd_cdl_clindev_ppm_publish.ipp_pub_act x
# INNER JOIN edf_prd_cdl_clindev_ppm_publish.milestone_reference y
# ON x.milestone_category = y.milestone_category
# where activity_type in ('PRI_AN_FLASH', 'FLASH_MEMO')
#
# params['database'] =
# edf_prd_cdl_clindev_ppm_publish
#
# params['bucket'] =
# aws-athena-query-results-291403363365-us-west-2
#
# params['path'] =
# OPTIONAL ('s3://' + params['bucket'] + '/' + params['path'])
#
#
logger = LoggerFactory.get_logger(__name__)


def query_results(params, wait=True):
    tic = time.perf_counter()
    client = athena_connection.athena_client

    ## This function executes the query and returns the query execution ID
    response_query_execution_id = client.start_query_execution(
        QueryString=params["query"],
        QueryExecutionContext={"Database": params["database"]},
        ResultConfiguration={
            "OutputLocation": "s3://" + params["bucket"] + "/" + params["path"]
        },
    )

    if not wait:
        return response_query_execution_id["QueryExecutionId"]
    else:
        response_get_query_details = client.get_query_execution(
            QueryExecutionId=response_query_execution_id["QueryExecutionId"]
        )
        status = "RUNNING"
        iterations = 600  # ~10 min

        # logger.debug("Status: %s", status)
        # logger.debug("Iterations: %s", str(iterations))

        while iterations > 0:
            iterations = iterations - 1
            response_get_query_details = client.get_query_execution(
                QueryExecutionId=response_query_execution_id["QueryExecutionId"]
            )
            status = response_get_query_details["QueryExecution"]["Status"]["State"]
            # logger.debug("Iteration: %s", str(iterations))
            # logger.debug("Status iteration: %s", status)

            if (status == "FAILED") or (status == "CANCELLED"):
                toc = time.perf_counter()
                logger.debug(
                    f"Athena query {status}. Call took {toc - tic:0.4f} seconds"
                )
                return None  # pragma: no cover

            elif status == "SUCCEEDED":
                toc = time.perf_counter()
                logger.debug(
                    f"Athena Query Succeded with {str(iterations)} Iterations remaining. Call took {toc - tic:0.4f} seconds"
                )
                location = response_get_query_details["QueryExecution"][
                    "ResultConfiguration"
                ]["OutputLocation"]

                ## Function to get output results
                response_query_result = client.get_query_results(
                    QueryExecutionId=response_query_execution_id["QueryExecutionId"]
                )

                if len(response_query_result["ResultSet"]["Rows"]) > 1:
                    header = response_query_result["ResultSet"]["Rows"][0]
                    rows = response_query_result["ResultSet"]["Rows"][1:]

                    header = [
                        obj["VarCharValue"] if obj else None for obj in header["Data"]
                    ]
                    result = [
                        dict(zip(header, get_var_char_values(row))) for row in rows
                    ]
                    return location, result
                else:
                    return location, None  # pragma: no cover


def get_var_char_values(d_row):
    return [obj["VarCharValue"] if obj else None for obj in d_row["Data"]]
