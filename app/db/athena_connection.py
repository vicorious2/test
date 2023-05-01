"""
Athena connection
"""
import os
from pathlib import Path
import boto3
from ..constant import Constant
from dotenv import load_dotenv
from ..loggerFactory import LoggerFactory

logger = LoggerFactory.get_logger(__name__)

# temp remove ENV
dotenv_path = Path(Constant.ENV_PATH)
load_dotenv(dotenv_path=dotenv_path)


AWS_REGION = "us-west-2"
AWS_ACCESS_KEY = os.environ["AWS_DB_ACCESS_KEY_ID"]
AWS_SECRET_KEY = os.environ["AWS_DB_SECRET_ACCESS_KEY"]
BUCKET = "aws-athena-query-results-291403363365-us-west-2"

athena_client = boto3.client(
    "athena",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=AWS_REGION,
)
