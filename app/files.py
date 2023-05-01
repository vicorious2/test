"""
high level support for doing this and that.
"""

import os

from .loggerFactory import LoggerFactory

logger = LoggerFactory.get_logger(__name__)


def read_file(path_file):
    """
    read_file
    responses:
      variable with content
    """
    content = ""
    with open(os.path.join(os.path.dirname(__file__), path_file), "r") as input_file:
        content += input_file.read()
    return content


def read_file_sql_with_params(path_file, params: dict, finalsentence: str):
    """
    read_file
    responses:
      variable with content
    """
    content = ""
    with open(os.path.join(os.path.dirname(__file__), path_file), "r") as input_file:
        content += input_file.read()
    where = True
    for key, value in params.items():
        if value:
            if where:
                content += (
                    " WHERE "
                    + key
                    + " = "
                    + (value if isinstance(value, int) else "'" + value + "'")
                )
                where = False
            else:
                content += (
                    " AND "
                    + key
                    + " = "
                    + (value if isinstance(value, int) else "'" + value + "'")
                )
    content += " " + finalsentence
    logger.debug("Content file: %s", content)
    return content
