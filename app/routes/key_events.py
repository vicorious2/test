import json
from operator import imod
import os
import time

from fastapi import APIRouter, Depends
from cryptography.fernet import Fernet

from ..AuthUtil import is_authorized
from ..utils.responsekeyevents import format_response_V2, format_response_V3
from ..files import read_file
from ..athena import athena
from ..constant import Constant
from ..redisconnection import RedisClusterConnection, redis, ttl
from ..loggerFactory import LoggerFactory
from ..dataHelper import DataHelper

logger = LoggerFactory.get_logger(__name__)


tags_metadata = [
    {"name": "Key Events", "description": "Get APIs to populate key events"}
]

router = APIRouter(
    prefix="/api",
    tags=["Pipeline"],
    dependencies=[Depends(is_authorized)],
    responses={403: {"description": "Not found"}},
)

redis_ = redis()
redis_wrapper = RedisClusterConnection()
f = Fernet(os.environ["ENC_KEY"])


@router.get("/v4/key_upcoming_events")
def key_upcoming_events_v4():
    """
    s3 method for /api/v4/key_upcoming_events
    ---
    responses:
      200:
        description: Athena s3 info for bucket
        (s3://aws-athena-query-results-291403363365-us-west-2/)
    """
    key = f"{Constant.REDIS_KEY_PREFIX}__key_upcoming_events_v4__"
    return DataHelper.get_data(
        "key_upcoming_events_v4",
        key,
        read_file(Constant.KEY_UPCOMING_EVENTS_SQL_PATH_FILE_V4),
        [],
        "key_events.py",
    )


@router.get("/v4/key_upcoming_events_CLEAR_CACHE")
def key_upcoming_events_v4_DEL(key: str):
    """
    s3 method for /api/v2/key_upcoming_events
    ---
    responses:
      200:
        description: Athena s3 info for bucket
        (s3://aws-athena-query-results-291403363365-us-west-2/)
    """
    redis_.delete(key)
    return True
