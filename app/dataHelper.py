from distutils.log import debug
import os
import time
import json
import jsonpickle

from .athena import athena
from .constant import Constant
from .loggerFactory import LoggerFactory
from .redisconnection import RedisClusterConnection, redis, ttl
from .utils.responsekeyevents import format_response_key_events_v4
from .utils.responseproducts import (
    format_response_products,
    format_response_products_tpp,
    format_response_products_tpp_link,
)
from .utils.response_pipeline import format_response_pipeline_metrics
from .utils.response_agenda_items import format_response_agenda_items_v1

from cryptography.fernet import Fernet


logger = LoggerFactory.get_logger(__name__)
redis_ = redis()
redis_wrapper = RedisClusterConnection()
f = Fernet(os.environ["ENC_KEY"])


class DataHelper:
    def get_data(route: str, key: str, queryStr: str, query_params, fileName: str):
        logger.debug(f"{fileName} {route}: start")
        tic = time.perf_counter()
        param_str = "Parameters:"
        for idx, p in enumerate(query_params):
            if (idx % 2) == 0:
                param_str = param_str + " pname: " + p
            else:
                param_str = param_str + " pvalue: " + p

        data = redis_.get(key)
        if data:
            toc = time.perf_counter()
            logger.debug(
                f"{fileName} route: "
                + route
                + " "
                + param_str
                + f" took {toc - tic:0.4f} seconds CACHED"
            )
            return json.loads(f.decrypt(data))

        params = {
            "query": queryStr,
            "database": Constant.SCHEMA_CLINDEV_PPM_PUBLISH,
            "bucket": Constant.BUCKET,
            "path": "",
        }
        match route:
            # key events
            case "key_upcoming_events_v4":
                data = format_response_key_events_v4(athena.query_results(params))
            # products
            case "product":
                data = format_response_products(
                    athena.query_results(params), query_params[1]
                )
            case "tpp":
                data = format_response_products_tpp(
                    athena.query_results(params), query_params[1].replace(" ", "")
                )
            case "tpp_link":
                data = format_response_products_tpp_link(
                    athena.query_results(params), query_params[1]
                )
            case "agenda_items":
                data = format_response_agenda_items_v1()
            case "get_pipeline_metrics":
                for x in range(6):
                    res = athena.query_results(params)
                    if res is not None:
                        logger.debug(f"get_pipeline_metrics: a reponse was generated")
                        data = format_response_pipeline_metrics(res)
                        break
                    logger.debug(
                        f"get_pipeline_metrics: an empty reponse was generated"
                    )
                    time.sleep(5)

        string_data = json.dumps(data)
        token = f.encrypt(bytes(string_data.encode()))
        redis_.set(key, token, ttl)
        toc = time.perf_counter()
        logger.debug(
            f"{fileName} route: "
            + route
            + " "
            + param_str
            + f" took {toc - tic:0.4f} seconds NOT CACHED"
        )
        return data

    def get_cached_object(route: str, key: str, query_params, fileName: str):
        logger.debug(f"get_cached_object: {fileName} {route}: start")
        tic = time.perf_counter()
        param_str = "Parameters:"
        for idx, p in enumerate(query_params):
            if (idx % 2) == 0:
                param_str = param_str + " pname: " + p
            else:
                param_str = param_str + " pvalue: " + p

        data = redis_.get(key)
        if data:
            toc = time.perf_counter()
            logger.debug(
                f"get_cached_object: {fileName} route: "
                + route
                + " "
                + param_str
                + f" took {toc - tic:0.4f} seconds CACHED"
            )
            return jsonpickle.decode(f.decrypt(data))

        return None

    def cache_object(route: str, key: str, query_params, fileName: str, data):
        logger.debug(f"cache_object: {fileName} {route}: start")
        tic = time.perf_counter()
        param_str = "Parameters:"
        for idx, p in enumerate(query_params):
            if (idx % 2) == 0:
                param_str = param_str + " pname: " + p
            else:
                param_str = param_str + " pvalue: " + p

        string_data = jsonpickle.encode(data)
        token = f.encrypt(bytes(string_data.encode()))
        redis_.set(key, token, ttl)
        toc = time.perf_counter()
        logger.debug(
            f"cache_object: {fileName} route: "
            + route
            + " "
            + param_str
            + f" took {toc - tic:0.4f} seconds NOT CACHED"
        )
        return data
