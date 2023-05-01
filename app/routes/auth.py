from ..auth.auth_manager import AuthManager
from ..auth.data_auth_config import AUTH_CONFIG
from ..redisconnection import RedisClusterConnection, redis, ttl
from fastapi import APIRouter, Depends
from ..AuthUtil import (
    is_authorized,
    Depends,
    get_page_permissions,
    is_authorized_valid_amgen_user,
)

auth_manager = AuthManager(AUTH_CONFIG)

redis_ = redis()
redis_wrapper = RedisClusterConnection()

router = APIRouter(
    prefix="/api",
    tags=["Auth"],
    responses={403: {"description": "Not found"}},
)


@router.get("/v1/authorization")
def get_authorization(token=Depends(is_authorized_valid_amgen_user)):
    permissions = auth_manager.get_all_permissions(token.credentials)
    return permissions


# TODO REFACTOR
@router.get("/v1/authorization/all")
def get_authorization_pages(token=Depends(is_authorized_valid_amgen_user)):
    permissions = get_page_permissions(token.credentials)
    return permissions
