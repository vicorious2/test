import json
import os
import re
import time
from functools import lru_cache

import jwt
import requests
from fastapi import Depends, HTTPException
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
    OAuth2PasswordBearer,
)
from jwt.algorithms import RSAAlgorithm
from starlette.config import Config

from app.models.agenda_items import User

from .constant import Constant
from .loggerFactory import LoggerFactory

from .utils.timer import time_this
from werkzeug.exceptions import InternalServerError

logger = LoggerFactory.get_logger(__name__)
env = os.getenv("PA_ENV", "dev")


class AuthUtil:
    # Load environment variables
    config = Config(".env")

    # Define the auth scheme and access token URL
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Bearer
bearer = HTTPBearer()

authUtil = AuthUtil()


def decode_token(token):
    logger.debug(f"decode_token: start")
    aud = "api://Amgen-Enterprise-API-Services"
    public_keys = get_jwk_public_keys()

    try:
        key_json = public_keys["keys"][0]
        public_key = RSAAlgorithm.from_jwk(key_json)
        data = jwt.decode(token, public_key, algorithms=["RS256"], audience=aud)
        logger.debug(f"decode_token: primary key used")
        return data
    except:
        logger.debug(f"decode_token: primary key failed")

    key_json = public_keys["keys"][1]
    public_key = RSAAlgorithm.from_jwk(key_json)
    data = jwt.decode(token, public_key, algorithms=["RS256"], audience=aud)
    logger.debug(f"decode_token: seccondary key used")
    return data


def is_authorized(token: HTTPAuthorizationCredentials = Depends(bearer)):
    # dev & test
    # rts-sensinglt-nonprod,rts-ceo-plus-nonprod,rts-executives-nonprod,rts-opteam-nonprod,rts-opteam-plus-nonprod,rts-randd-nonprod,rts-finance-nonprod,rts-pacore-nonprod,rts-master

    logger.debug(f"is_authorized: started")
    try:
        logger.debug(f"is_authorized: pre-ldap groups")
        pages = get_page_permissions(token.credentials)
        user_name = get_user_name(token.credentials)
        logger.debug(f"is_authorized: post-ldap groups")
        if pages["prioritizedAgenda"]:
            logger.debug(f"is_authorized: user {user_name} is authorized")
            return token
    except Exception as ex:
        logger.error(f"Error while checking for access: {ex}")
        raise HTTPException(status_code=403)
    logger.debug(f"is_authorized: user {user_name} is NOT authorized")
    raise HTTPException(status_code=403)


def is_authorized_valid_amgen_user(
    token: HTTPAuthorizationCredentials = Depends(bearer),
):
    # dev & test
    # rts-sensinglt-nonprod,rts-ceo-plus-nonprod,rts-executives-nonprod,rts-opteam-nonprod,rts-opteam-plus-nonprod,rts-randd-nonprod,rts-finance-nonprod,rts-pacore-nonprod,rts-master

    logger.debug(f"is_authorized_valid_amgen_user: started")
    try:
        logger.debug(f"is_authorized_valid_amgen_user: pre-ldap groups")
        pages = get_page_permissions(token.credentials)
        user_name = get_user_name(token.credentials)
        logger.debug(f"is_authorized_valid_amgen_user: post-ldap groups")
        logger.debug(
            f"is_authorized_valid_amgen_user: user {user_name} can chek page access "
        )
        return token
    except Exception as ex:
        logger.error(f"Error while checking for access: {ex}")
        raise HTTPException(status_code=403)
    logger.debug(f"is_authorized: user {user_name} is NOT authorized")
    raise HTTPException(status_code=403)


@lru_cache(128)
def get_ldap_groups(token: str):
    # The email is in the `sub` field
    user_name = get_user_name(token)
    adGroups = []
    ldapUri = ""
    if env == "dev":
        ldapUri = "https://authorization-api-dev.nimbus.amgen.com/authorization/graphql"
    elif env == "test":
        ldapUri = (
            "https://authorization-api-test.nimbus.amgen.com/authorization/graphql"
        )
    elif env == "staging":
        ldapUri = "https://authorization-api-stg.nimbus.amgen.com/authorization/graphql"
    elif env == "rts":
        ldapUri = "https://authorization-api.nimbus.amgen.com/authorization/graphql"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    query = f"""\
        query {{
            getUserDetails(username: "{user_name}") {{
                userName
                userGroups {{
                    adGroups
                    ldapGroups
                }}
            }}
        }}
    """.replace(
        " ", ""
    )
    api_payload = {"query": query}

    logger.debug(f"Calling LDAP {ldapUri}")
    tic = time.perf_counter()
    try:
        response = requests.post(ldapUri, json=api_payload, headers=headers)
    except Exception as ex:
        return ["NOT AUTHORIZED"]

    toc = time.perf_counter()
    logger.debug(f"LDAP Call took {toc - tic:0.4f} seconds")
    if response.status_code != requests.codes.ok:
        raise HTTPException(
            status_code=500,
            detail=f"LDAP Query returned {response.status_code} {response.text}",
        )
    response = response.json()
    adGroups = (
        response.get("data", {})
        .get("getUserDetails", {})
        .get("userGroups", {})
        .get("adGroups", [])
    )
    # privalged non-privaleged exception
    if user_name in Constant.AUTH_USERS_EXCEPTION:
        adGroups.append("rts-sensinglt")
        logger.debug(f"{user_name} has an been added to rts-sensinglt")
    # privalged exception
    if user_name in Constant.AUTH_USERS_EXCEPTION_NOTIFICATION:
        adGroups.append("rts-pipeline")
        logger.debug(f"{user_name} has an been added to rts-pipeline")
    adGroups = [group.lower() for group in adGroups]
    return adGroups


def get_page_permissions(token: str):
    # The email is in the `sub` field
    user_name = get_user_name(token)
    adGroups = []
    ldapUri = ""
    if env == "dev":
        ldapUri = "https://authorization-api-dev.nimbus.amgen.com/authorization/graphql"
    elif env == "test":
        ldapUri = (
            "https://authorization-api-test.nimbus.amgen.com/authorization/graphql"
        )
    elif env == "staging":
        ldapUri = "https://authorization-api-stg.nimbus.amgen.com/authorization/graphql"
    elif env == "rts":
        ldapUri = "https://authorization-api.nimbus.amgen.com/authorization/graphql"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    query = f"""\
        query{{
            sensingAuthorization(username:"{user_name}"){{
                prioritizedAgenda
                supply
                people
                pipeline
                brand
            }}
        }}
    """.replace(
        " ", ""
    )
    api_payload = {"query": query}

    logger.debug(f"Calling LDAP {ldapUri}")
    tic = time.perf_counter()
    try:
        response = requests.post(ldapUri, json=api_payload, headers=headers)
    except Exception as ex:
        return ["NOT AUTHORIZED"]

    toc = time.perf_counter()
    logger.debug(f"LDAP Call took {toc - tic:0.4f} seconds")
    if response.status_code != requests.codes.ok:
        raise HTTPException(
            status_code=500,
            detail=f"LDAP Query returned {response.status_code} {response.text}",
        )
    response = response.json()
    pages = response.get("data", {}).get("sensingAuthorization", {})
    logger.debug(f"get_page_permissions: User: {user_name} has access to: {pages}")
    return pages


@lru_cache(1)
def get_jwk_public_keys():
    try:
        uri = ""
        if env == "dev":
            uri = (
                "https://amgentest.oktapreview.com/oauth2/ausjfltczqqfjN16U0h7/v1/keys"
            )
        elif env == "test":
            uri = (
                "https://amgentest.oktapreview.com/oauth2/ausjfltczqqfjN16U0h7/v1/keys"
            )
        elif env == "staging":
            uri = "https://amgen.okta.com/oauth2/auslrtx7u2yavnvaJ0x7/v1/keys"
        elif env == "rts":
            uri = "https://amgen.okta.com/oauth2/auslrtx7u2yavnvaJ0x7/v1/keys"
        r = requests.get(uri)
    except:
        logger.error(f"get_jwk_public_key: failed")

    if r.status_code != requests.codes.ok:
        raise HTTPException(
            status_code=500, detail=f"JWKS Query returned {r.status_code} {r.text}"
        )
    regex = re.compile("[<>&]")
    data_string = json.dumps(r.json())

    if regex.search(data_string) == None:
        return r.json()
    raise HTTPException(status_code=406)


@lru_cache(128)
def get_user_name(token: str):
    payload = decode_token(token)
    user_name = payload["sub"].split("@")[0]
    return user_name


def get_user_name_and_email(
    token: HTTPAuthorizationCredentials = Depends(bearer),
) -> User:
    payload = decode_token(token.credentials)
    username = payload["sub"].split("@")[0]
    email = payload["sub"]
    return User(username=username, email=email)


def generate_okta_token():
    try:
        logger.info("Generating okta token from service account")
        url = ""
        un = os.getenv("SERVICE_ACCOUNT_USERNAME")
        pw = os.getenv("SERVICE_ACCOUNT_PASSWORD")
        if env == "dev":
            url = "https://platform-services-dev.amgen.com/api/v1/authentication"
        elif env == "test":
            url = "https://platform-services-dev.amgen.com/api/v1/authentication"
        elif env == "staging":
            url = "https://platform-services.amgen.com/api/v1/authentication"
        elif env == "rts":
            url = "https://platform-services.amgen.com/api/v1/authentication"

        if not pw:
            logger.info("get SERVICE_ACCOUNT_PASS failed")
            un = os.getenv("SERVICE_ACCOUNT_USERNAME")
            pw = os.getenv("SERVICE_ACCOUNT_PASSWORD")
        else:
            logger.info("generate_okta_token: Loading data with service account")

        data = {
            "username": un,
            "password": pw,
            "cost_center": "14872",
            "calling_application_name": "RT-Sensing",
        }
        response = requests.post(url, json=data)
        if response.status_code != 200:
            logger.error(
                f"generate_okta_token failed {str(response.status_code)} {response.json()}"
            )
            raise Exception("generate_okta_token failed")
        j = response.json()
        token = j["result"]["access_token"]
        return token
    except Exception as e:
        logger.error(e)


def get_authz_details(token: str, graphql_payload: dict) -> dict:
    ldapUri = ""
    if env == "dev":
        ldapUri = "https://authorization-api-dev.nimbus.amgen.com/authorization/graphql"
    elif env == "test":
        ldapUri = (
            "https://authorization-api-test.nimbus.amgen.com/authorization/graphql"
        )
    elif env == "staging":
        ldapUri = "https://authorization-api-stg.nimbus.amgen.com/authorization/graphql"
    elif env == "rts":
        ldapUri = "https://authorization-api.nimbus.amgen.com/authorization/graphql"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    @time_this
    def call_ldap(uri):
        return requests.post(uri, json=graphql_payload, headers=headers)

    response = call_ldap(ldapUri)
    if response.status_code != requests.codes.ok:
        raise InternalServerError(
            f"LDAP Query returned {response.status_code} {response.text}"
        )
    response = response.json()
    return response
