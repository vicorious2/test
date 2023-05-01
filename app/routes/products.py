import os
import json
import time

from fastapi import APIRouter, Depends
import requests

from ..AuthUtil import is_authorized
from ..utils.responseproducts import (
    format_response_products,
    format_response_products_tpp,
    format_response_products_tpp_link,
)
from ..redisconnection import redis, ttl
from ..files import read_file
from ..athena import athena
from ..constant import Constant
from ..loggerFactory import LoggerFactory
from ..dataHelper import DataHelper

logger = LoggerFactory.get_logger(__name__)
redis_ = redis()

tags_metadata = [
    {
        "name": "Product Refernce",
        "description": "Get APIs to populate product Refernce",
    },
]

router = APIRouter(
    prefix="/api",
    tags=["Pipeline"],
    dependencies=[Depends(is_authorized)],
    responses={403: {"description": "Not found"}},
)


@router.get("/v1/product/clear_cache")
def clear_cache(key: str):
    redis_.delete(key)
    return True


@router.get("/v1/product")
def products(product: str = ""):
    """
    s3 method for /api/v1/product
    ---
    responses:
      200:
        description: Athena s3 info for bucket
        (s3://aws-athena-query-results-291403363365-us-west-2/)
    """
    key = f"{Constant.REDIS_KEY_PREFIX}__product__" + product
    return DataHelper.get_data(
        "product",
        key,
        read_file(Constant.FILTER_PRODUCTS_SQL_PATH_FILE_v2),
        ["product", product],
        "products.py",
    )


@router.get("/v1/product/tpp")
def products_tpp(name: str = ""):
    """
    s3 method for /api/v1/product/tpp
    ---
    responses:
      200:
        description: Athena s3 info for bucket
        (s3://aws-athena-query-results-291403363365-us-west-2/)
    """
    key = f"{Constant.REDIS_KEY_PREFIX}__product_tpp__" + name
    return DataHelper.get_data(
        "tpp", key, read_file(Constant.PRODUCTS_TPP_FILE), ["name", name], "products.py"
    )


@router.get("/v1/product/tpp_link")
def products_tpp_link(product: str = ""):
    """
    s3 method for /api/v1/product/tpp_link
    ---
    responses:
      200:
        description: Athena s3 info for bucket
        (s3://aws-athena-query-results-291403363365-us-west-2/)

    """
    key = f"{Constant.REDIS_KEY_PREFIX}__product_tpp_link__" + product
    return DataHelper.get_data(
        "tpp_link",
        key,
        read_file(Constant.PRODUCTS_TPP_LINK_FILE),
        ["product", product],
        "products.py",
    )
