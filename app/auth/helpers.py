import os
from functools import lru_cache, wraps

import jwt
import requests
from jwt.algorithms import RSAAlgorithm
from ..utils.timer import time_this
from werkzeug.exceptions import InternalServerError

env = os.getenv("PA_ENV", "dev")


def get_query_subcomponent_parent_key(component_name: str):
    return f"{component_name}Components"


@lru_cache(1)
@time_this
def call_jwk(uri):
    r = requests.get(uri)
    if r.status_code != requests.codes.ok:
        raise InternalServerError(f"JWKS Query returned {r.status_code} {r.text}")

    return r.json()


@time_this
def get_jwk_public_key():
    uri = ""
    if env == "dev":
        uri = "https://amgentest.oktapreview.com/oauth2/ausjfltczqqfjN16U0h7/v1/keys"
    elif env == "test":
        uri = "https://amgentest.oktapreview.com/oauth2/ausjfltczqqfjN16U0h7/v1/keys"
    elif env == "staging":
        uri = "https://amgen.okta.com/oauth2/auslrtx7u2yavnvaJ0x7/v1/keys"
    elif env == "rts":
        uri = "https://amgen.okta.com/oauth2/auslrtx7u2yavnvaJ0x7/v1/keys"

    print(uri)
    data = call_jwk(uri)
    print(data)
    key_json = data["keys"]
    # key_json = os.getenv('OKTA_JWK')
    return RSAAlgorithm.from_jwk(key_json)


@time_this
def decode_token(token):
    aud = "api://Amgen-Enterprise-API-Services"
    # Try with first key but then try second if failure occurs
    public_key = get_jwk_public_key()
    data = jwt.decode(token, public_key, algorithms=["RS256"], audience=aud)
    return data


def get_user_name(token: str):
    token_payload = decode_token(token)
    # The email is in the `sub` field
    return token_payload["sub"].split("@")[0]
