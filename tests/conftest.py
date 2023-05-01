import pytest
from fastapi.testclient import TestClient
from app.constant import Constant
import boto3
import os
from dotenv import load_dotenv
from pathlib import Path

# temp remove ENV
dotenv_path = Path(Constant.ENV_PATH)
load_dotenv(dotenv_path=dotenv_path)

# Overwrite dynamodb access keys
os.environ["AWS_DYNAMO_ACCESS_KEY_ID"] = "testing"
os.environ["AWS_DYNAMO_SECRET_ACCESS_KEY"] = "testing"


@pytest.fixture
def test_client():
    from app.main import app

    yield TestClient(app)


@pytest.fixture
def test_client_bad():
    from app.main import app

    yield TestClient(app, raise_server_exceptions=True)


@pytest.fixture
def aws_credentials():
    # Mock AWS Credentials for moto
    os.environ["AWS_ACCESS_KEY_ID"] = os.getenv("AWS_ACCESS_KEY")
    os.environ["AWS_SECRET_ACCESS_KEY"] = os.getenv("AWS_SECRET_KEY")
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"


@pytest.fixture
def aws_credentials_bad():
    # Mock AWS Credentials for moto
    os.environ["AWS_ACCESS_KEY_ID"] = "wrong key"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "wrong secret"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"


@pytest.fixture
def mock_athena(aws_credentials):
    with mock_athena():
        conn = boto3.client("athena", region_name=Constant.AWS_REGION)
        yield conn
